import asyncio
import hashlib
import os
import re
import subprocess
import requests
import aiohttp
from playwright.async_api import async_playwright
from PyQt6.QtCore import QObject, pyqtSignal

class VideoDownloader(QObject):
    # 定义信号
    log_message = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    download_finished = pyqtSignal()
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        
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
            
            # 下载视频
            video_path = os.path.join(self.config.download_path, f"{video_id}.mp4")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.config.headers) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(video_path, "wb") as f:
                            f.write(content)
                        self.log_message.emit(f"视频下载成功：{video_path}")
                        
                        # 提取音频
                        audio_path = os.path.join(self.config.audio_path, f"{video_id}.wav")
                        try:
                            subprocess.run([
                                self.config.ffmpeg_path,
                                '-i', video_path,
                                '-vn',
                                '-acodec', 'pcm_s16le',
                                '-ar', '16000',
                                '-ac', '1',
                                '-y',
                                audio_path
                            ], check=True, capture_output=True)
                            
                            self.log_message.emit(f"音频提取成功：{audio_path}")
                            await asyncio.sleep(1)
                            await self.speech_recognition(audio_path, video_id)
                            
                        except subprocess.CalledProcessError as e:
                            self.log_message.emit(f"音频提取失败：{e.stderr.decode()}")
                    else:
                        self.log_message.emit(f"下载失败：{response.status}")
                        
        except Exception as e:
            self.log_message.emit(f"下载视频时出错: {str(e)}")

    async def download_videos(self, urls):
        """下载视频"""
        try:
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
        video_downloaded = False
        
        async def handle_response(response):
            nonlocal video_downloaded
            try:
                if response.ok and not video_downloaded:
                    url = response.url
                    # 只处理带音频的视频文件
                    if 'douyinvod.com' in url:
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
        """使用 SiliconFlow API 进行语音识别"""
        try:
            self.log_message.emit("开始识别...")
            
            if not os.path.exists(audio_file):
                self.log_message.emit(f"音频文件不存在: {audio_file}")
                return None
                
            url = "https://api.siliconflow.cn/v1/audio/transcriptions"
            headers = {
                "Authorization": "Bearer sk-bwbkhneomtuzuxywnsbjbsftnzousbvmzfoqpwqdsezvnvsw",
            }
            
            files = {
                'file': ('audio.wav', open(audio_file, 'rb'), 'audio/wav'),
                'model': (None, 'FunAudioLLM/SenseVoiceSmall'),
            }
            
            self.log_message.emit("正在发送识别请求...")
            response = requests.post(url, headers=headers, files=files)
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('text', '').strip()
                
                if text:
                    text_file = os.path.join(self.config.text_path, f"{video_id}.txt")
                    with open(text_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                    self.log_message.emit(f"识别结果已保存: {text_file}")
                    self.log_message.emit(f"识别到的文本: {text}")
                    return text
                else:
                    self.log_message.emit("API返回结果为空")
                    return None
            else:
                self.log_message.emit(f"API请求失败: {response.status_code}")
                self.log_message.emit(f"错误信息: {response.text}")
                return None
                
        except Exception as e:
            self.log_message.emit(f"语音识别失败: {str(e)}")
            return None
            
    # ... 其他方法保持不变 ... 