import asyncio
import hashlib
import os
import re
import subprocess
import requests
import aiohttp
from playwright.async_api import async_playwright
from PyQt6.QtCore import QObject, pyqtSignal
import whisper

class VideoDownloader(QObject):
    # 定义信号
    log_message = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    download_finished = pyqtSignal()
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.model = None  # 初始化为 None
        
    async def load_whisper_model(self):
        """异步加载 Whisper 模型"""
        try:
            self.log_message.emit("正在加载 Whisper 模型...")
            self.log_message.emit("首次使用需要下载模型文件，可能需要几分钟时间...")
            
            # 检查 CUDA 是否可用
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.log_message.emit(f"使用设备: {device}")
            
            # 使用项目目录下的 models 文件夹
            model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
                self.log_message.emit(f"创建模型目录: {model_dir}")
            
            # 检查模型文件是否已存在
            model_path = os.path.join(model_dir, 'large-v2.pt')
            if not os.path.exists(model_path):
                self.log_message.emit("模型文件不存在，开始下载...")
                self.log_message.emit("large-v2 模型大小约 1.5GB，下载可能需要较长时间...")
                self.log_message.emit("请保持网络连接稳定...")
            else:
                self.log_message.emit("找到已下载的模型文件")
            
            # 在新线程中下载和加载模型
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(None, lambda: whisper.load_model("large-v2", device=device, download_root=model_dir))
            
            self.log_message.emit("Whisper 模型加载完成")
            self.log_message.emit(f"模型保存位置: {model_dir}")
            
        except Exception as e:
            self.log_message.emit(f"加载 Whisper 模型失败: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            raise e

    async def get_video_url(self, page, share_url: str) -> str:
        """获取视频地址"""
        try:
            # 提取短链接
            match = re.search(r'https://v\.douyin\.com/\w+', share_url)
            if not match:
                self.log_message.emit("未找到有效的抖音链接")
                return ""
                
            short_url = match.group(0)
            self.log_message.emit(f"获取到短链接: {short_url}")
            
            # 访问视频页面
            response = await page.goto(short_url, wait_until='domcontentloaded')
            if not response.ok:
                self.log_message.emit(f"页面加载失败: {response.status}")
                return ""
            
            self.log_message.emit("等待页面加载...")
            
            # 等待页面加载完成
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            
            return "success"
            
        except Exception as e:
            self.log_message.emit(f"访问视频页面失败: {str(e)}")
            return ""

    async def download_video(self, url, video_id):
        """下载视频并提取音频"""
        try:
            self.log_message.emit("开始下载：" + url)
            
            # 判断是否是音频文件
            is_audio = 'media-audio-und-mp4a' in url
            file_ext = '.m4a' if is_audio else '.mp4'
            
            # 根据类型选择保存路径
            save_path = os.path.join(
                self.config.audio_path if is_audio else self.config.download_path,
                f"{video_id}{file_ext}"
            )
            
            # 下载文件
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.config.headers) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(save_path, "wb") as f:
                            f.write(content)
                        self.log_message.emit(f"{'音频' if is_audio else '视频'}下载成功：{save_path}")
                        
                        if is_audio:
                            # 如果是音频文件，转换为wav格式
                            wav_path = os.path.join(self.config.audio_path, f"{video_id}.wav")
                            try:
                                cmd = [
                                    self.config.ffmpeg_path,
                                    '-i', save_path,
                                    '-acodec', 'pcm_s16le',
                                    '-ar', '16000',
                                    '-ac', '1',
                                    '-y',
                                    wav_path
                                ]
                                
                                process = subprocess.run(cmd, check=True, capture_output=True, text=True)
                                
                                if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                                    self.log_message.emit(f"音频转换成功：{wav_path}")
                                    await asyncio.sleep(1)
                                    await self.speech_recognition(wav_path, video_id)
                                else:
                                    self.log_message.emit("音频转换失败")
                                    
                            except subprocess.CalledProcessError as e:
                                self.log_message.emit(f"音频转换失败：{e.stderr}")
                                self.log_message.emit(f"FFmpeg 命令：{' '.join(cmd)}")
                                
                        else:
                            self.log_message.emit(f"下载失败：{response.status}")
                            
        except Exception as e:
            self.log_message.emit(f"下载处理时出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())

    async def download_videos(self, urls):
        """下载视频"""
        try:
            # 首先加载 Whisper 模型
            if self.model is None:
                await self.load_whisper_model()
                
            # 创建必要的目录
            for directory in [self.config.download_path, 
                            self.config.audio_path, 
                            self.config.text_path]:
                if not os.path.exists(directory):
                    os.makedirs(directory)
            
            async with async_playwright() as p:
                self.log_message.emit("正在连接到Chrome...")
                try:
                    browser = await p.chromium.connect_over_cdp(f"http://localhost:{self.config.chrome_debug_port}")
                    context = browser.contexts[0]
                    page = context.pages[0]
                    
                    self.log_message.emit("开始处理视频...")
                    total = len(urls)
                    success_count = 0
                    
                    for i, url in enumerate(urls, 1):
                        self.log_message.emit(f"\n处理第 {i}/{total} 个视频：{url}")
                        
                        video_id = await self.get_video_id(url)
                        if not video_id:
                            self.log_message.emit("无法获取视频ID，跳过")
                            continue
                        
                        # 检查是否已经下载并识别成功
                        text_file = os.path.join(self.config.text_path, f"{video_id}.txt")
                        if os.path.exists(text_file):
                            self.log_message.emit("该视频已经处理成功，跳过")
                            success_count += 1
                            continue
                        
                        try:
                            # 移除所有现有的响应监听器
                            await page.route('**/*', lambda route: route.continue_())
                            await page.unroute('**/*')
                            
                            # 设置新的拦截器
                            await self.set_interceptor(page, video_id)
                            # 访问视频页面
                            await self.get_video_url(page, url)
                            
                            # 等待文本文件生成
                            for _ in range(10):  # 最多等待10秒
                                if os.path.exists(text_file):
                                    success_count += 1
                                    break
                                await asyncio.sleep(1)
                            
                            # 如果文本文件已生成，继续处理下一个视频
                            if os.path.exists(text_file):
                                continue
                            
                        except Exception as e:
                            self.log_message.emit(f"处理视频时出错: {str(e)}")
                            continue
                        
                        # 更新进度
                        progress = int((i / total) * 100)
                        self.progress_updated.emit(progress)
                    
                    self.log_message.emit(f"\n处理完成！成功下载 {success_count}/{total} 个视频")
                    self.download_finished.emit()
                    
                except Exception as e:
                    self.log_message.emit(f"连接Chrome失败: {str(e)}")
                    self.log_message.emit("请确保Chrome已启动且开启了远程调试端口")
                
        except Exception as e:
            self.log_message.emit(f"错误: {str(e)}")
            
    async def get_video_id(self, share_url: str) -> str:
        """从分享链接中提取视频ID"""
        try:
            if 'v.douyin.com' in share_url:
                match = re.search(r'https://v\.douyin\.com/(\w+)', share_url)
                if match:
                    return match.group(1)
            self.log_message.emit("未找到有效的视频ID")
            return None
        except Exception as e:
            self.log_message.emit(f"提取视频ID失败: {str(e)}")
            return None
            
    async def set_interceptor(self, page, video_id):
        """设置拦截器"""
        processed_urls = []
        audio_downloaded = False
        video_downloaded = False
        
        async def handle_response(response):
            nonlocal audio_downloaded, video_downloaded
            try:
                if response.ok:
                    url = response.url
                    # 优先处理音频文件
                    if 'media-audio-und-mp4a' in url and not audio_downloaded:
                        url_hash = hashlib.md5(url.encode()).hexdigest()
                        if url_hash not in processed_urls:
                            processed_urls.append(url_hash)
                            self.log_message.emit(f"捕获到音频URL: {url}")
                            await self.download_video(url, video_id)
                            audio_downloaded = True
                    # 如果没有找到音频文件，再处理视频文件
                    elif 'douyinvod.com' in url and not video_downloaded and not audio_downloaded:
                        url_hash = hashlib.md5(url.encode()).hexdigest()
                        if url_hash not in processed_urls:
                            processed_urls.append(url_hash)
                            self.log_message.emit(f"捕获到视频URL: {url}")
                            await self.download_video(url, video_id)
                            video_downloaded = True
            except Exception as e:
                self.log_message.emit(f"处理响应时出错: {str(e)}")
        
        try:
            page.on('response', handle_response)
        except Exception as e:
            self.log_message.emit(f"设置拦截器失败: {str(e)}")
            
    async def speech_recognition(self, audio_file, video_id):
        """使用 Whisper 进行语音识别"""
        try:
            self.log_message.emit("开始识别...")
            
            # 重置进度条
            self.progress_updated.emit(0)
            
            # 确保使用绝对路径
            audio_file = os.path.abspath(audio_file)
            if not os.path.exists(audio_file):
                self.log_message.emit(f"音频文件不存在: {audio_file}")
                return None
                
            self.log_message.emit(f"正在使用 Whisper 进行识别: {audio_file}")
            # 使用已有的 transcribe_audio 方法
            text = self.transcribe_audio(audio_file)
            
            if text:
                text_file = os.path.join(self.config.text_path, f"{video_id}.txt")
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.log_message.emit(f"识别结果已保存: {text_file}")
                self.log_message.emit(f"识别到的文本: {text}")
                # 完成时设置进度为100%
                self.progress_updated.emit(100)
                return text
            else:
                self.log_message.emit("识别结果为空")
                return None
                
        except Exception as e:
            self.log_message.emit(f"语音识别失败: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            return None
            
    async def process_imported_video(self, video_path):
        """处理导入的视频文件"""
        try:
            # 确保模型已加载
            if self.model is None:
                await self.load_whisper_model()
            
            video_id = os.path.splitext(os.path.basename(video_path))[0]
            
            # 检查是否已经处理过
            text_file = os.path.join(self.config.text_path, f"{video_id}.txt")
            if os.path.exists(text_file):
                self.log_message.emit("该视频已经处理过，跳过")
                return
            
            # 提取音频
            audio_path = os.path.join(self.config.audio_path, f"{video_id}.wav")
            try:
                # 修改 FFmpeg 命令，添加音频流检测
                cmd = [
                    self.config.ffmpeg_path,
                    '-i', video_path,
                    '-vn',  # 不处理视频
                    '-acodec', 'pcm_s16le',  # 音频编码
                    '-ar', '16000',  # 采样率
                    '-ac', '1',  # 单声道
                    '-f', 'wav',  # 强制输出格式为 wav
                    '-y',  # 覆盖已存在的文件
                    '-map', '0:a:0',  # 指定第一个音频流
                    audio_path
                ]
                
                # 先检查视频是否包含音频流
                probe_cmd = [
                    self.config.ffmpeg_path,
                    '-i', video_path,
                    '-show_streams',
                    '-select_streams', 'a',
                    '-loglevel', 'error'
                ]
                
                try:
                    probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
                    if not probe_result.stdout.strip():
                        self.log_message.emit("视频文件不包含音频流")
                        return
                        
                    # 如果有音频流，继续处理
                    process = subprocess.run(cmd, check=True, capture_output=True, text=True)
                    
                    # 检查文件是否成功创建
                    if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                        self.log_message.emit(f"音频提取成功：{audio_path}")
                        await asyncio.sleep(1)
                        await self.speech_recognition(audio_path, video_id)
                    else:
                        self.log_message.emit("音频文件创建失败或为空")
                        
                except subprocess.CalledProcessError as e:
                    self.log_message.emit(f"音频提取失败：{e.stderr}")
                    self.log_message.emit(f"FFmpeg 命令：{' '.join(cmd)}")
            except Exception as e:
                self.log_message.emit(f"音频提取失败：{str(e)}")
            
        except Exception as e:
            self.log_message.emit(f"处理导入视频时出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            
    def transcribe_audio(self, audio_path):
        """使用whisper转写音频"""
        try:
            if self.model is None:
                self.log_message.emit("Whisper 模型未加载")
                return None
                
            # 检查文件路径
            audio_path = os.path.abspath(audio_path)
            if not os.path.exists(audio_path):
                self.log_message.emit(f"音频文件不存在: {audio_path}")
                return None
                
            self.log_message.emit(f"开始转写音频文件: {audio_path}")
            
            # 设置 FFMPEG_PATH 环境变量
            os.environ["FFMPEG_PATH"] = self.config.ffmpeg_path
            
            # 使用 whisper 进行转写
            self.log_message.emit("正在加载音频...")
            self.progress_updated.emit(10)
            
            # 使用 whisper 进行转写
            self.log_message.emit("开始转写...")
            self.progress_updated.emit(30)
            
            result = self.model.transcribe(
                audio_path,
                verbose=True,  # 显示详细信息
                language='zh'  # 指定语言为中文
            )
            
            if result and "text" in result:
                self.log_message.emit("转写完成")
                self.progress_updated.emit(90)
                return result["text"]
            else:
                self.log_message.emit("转写结果无效")
                return None
                
        except Exception as e:
            self.log_message.emit(f"转写失败: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            return None
            
    async def process_imported_audio(self, audio_path):
        """处理导入的音频文件"""
        try:
            # 确保模型已加载
            if self.model is None:
                await self.load_whisper_model()
            
            # 获取文件名作为ID
            audio_id = os.path.splitext(os.path.basename(audio_path))[0]
            
            # 检查是否已经处理过
            text_file = os.path.join(self.config.text_path, f"{audio_id}.txt")
            if os.path.exists(text_file):
                self.log_message.emit("该音频已经处理过，跳过")
                return
            
            # 如果不是wav格式，需要转换
            wav_path = os.path.join(self.config.audio_path, f"{audio_id}.wav")
            if not audio_path.lower().endswith('.wav'):
                try:
                    cmd = [
                        self.config.ffmpeg_path,
                        '-i', audio_path,
                        '-acodec', 'pcm_s16le',
                        '-ar', '16000',
                        '-ac', '1',
                        '-y',
                        wav_path
                    ]
                    
                    process = subprocess.run(cmd, check=True, capture_output=True, text=True)
                    
                    if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                        self.log_message.emit(f"音频转换成功：{wav_path}")
                        audio_path = wav_path
                    else:
                        self.log_message.emit("音频转换失败")
                        return
                        
                except subprocess.CalledProcessError as e:
                    self.log_message.emit(f"音频转换失败：{e.stderr}")
                    self.log_message.emit(f"FFmpeg 命令：{' '.join(cmd)}")
                    return
            else:
                # 如果已经是wav格式，复制到audio目录
                import shutil
                shutil.copy2(audio_path, wav_path)
                audio_path = wav_path
            
            # 进行语音识别
            await self.speech_recognition(audio_path, audio_id)
            
        except Exception as e:
            self.log_message.emit(f"处理导入音频时出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            
    # ... 其他方法保持不变 ... 