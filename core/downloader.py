#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import hashlib
import json
import os
import random
import re
import subprocess
import time
from typing import Dict, List, Optional, Tuple

import aiohttp
import speech_recognition as sr
import whisper
from PyQt6.QtCore import QObject, pyqtSignal
from playwright.async_api import async_playwright


class SpeechRecognizer:
    # 引擎名称映射 - 只保留 Whisper 和 PaddleSpeech
    ENGINE_MAP = {
        "whisper": "whisper",
        "Whisper (OpenAI)": "whisper",
        "paddlespeech": "paddlespeech",
        "PaddleSpeech": "paddlespeech"
    }
    
    def __init__(self, config):
        """初始化语音识别器"""
        self.config = config
        
        # 获取选择的引擎，如果不在映射中，默认使用 whisper
        engine_name = config.speech_recognition_engine
        self.engine = self.ENGINE_MAP.get(engine_name, "whisper")
        print(f"选择的语音识别引擎: {self.engine}")
        
        # whisper模型
        self.whisper_model = None
        self.engine_config = config.speech_recognition_config
        
        # 获取各引擎配置 - 只保留需要的配置
        self.whisper_config = self.engine_config.get('whisper', {})
        self.paddle_config = self.engine_config.get('paddlespeech', {})
        
        # 获取 ffmpeg 路径
        self.ffmpeg_path = config.ffmpeg_path
        
    def recognize(self, audio_path):
        """识别音频文件，返回识别结果"""
        try:
            print(f"使用引擎: {self.engine} 识别音频")
            
            # 严格检查当前选择的引擎并调用对应方法
            if self.engine == "whisper":
                try:
                    import whisper
                    return self._whisper_recognize(audio_path)
                except ImportError:
                    print("Warning: Whisper库未安装，请使用pip install openai-whisper安装")
                    return None
            elif self.engine == "paddlespeech":
                return self._paddlespeech_recognize(audio_path)
            else:
                print(f"不支持的语音识别引擎: {self.engine}，将使用whisper引擎")
                try:
                    import whisper
                    return self._whisper_recognize(audio_path)
                except ImportError:
                    print("Warning: Whisper库未安装，请使用pip install openai-whisper安装")
                    return None
                
        except Exception as e:
            print(f"语音识别出错: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None
            
    def _whisper_recognize(self, audio_path):
        """使用Whisper识别音频"""
        try:
            import whisper
            
            model_name = self.whisper_config.get('model', 'base')
            language = self.whisper_config.get('language', 'zh')
            
            print(f"使用Whisper模型 {model_name} 识别音频...")
            
            # 检查是否已有加载好的模型
            if self.whisper_model:
                print("使用已加载的Whisper模型")
                model = self.whisper_model
            else:
                # 加载模型
                print(f"加载Whisper {model_name} 模型...")
                model = whisper.load_model(model_name)
                self.whisper_model = model
                
            # 输出设备信息
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"使用设备: {device}")
            
            # 识别音频
            result = model.transcribe(audio_path, language=language)
            text = result.get('text', '')
            
            print(f"Whisper识别完成，文本长度: {len(text)} 字符")
            return text
        except Exception as e:
            print(f"Whisper识别出错: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None
            
    def _paddlespeech_recognize(self, audio_path):
        """使用PaddleSpeech识别音频"""
        try:
            # 确认PaddleSpeech已安装
            from paddlespeech.cli.asr.infer import ASRExecutor
            
            model = self.paddle_config.get('model', 'conformer_wenetspeech')
            
            # 初始化ASR执行器
            asr = ASRExecutor()
            
            # 识别音频
            print(f"使用PaddleSpeech模型 {model} 识别音频...")
            result = asr(audio_file=audio_path, model=model)
            return result
        except ImportError:
            print("PaddleSpeech未安装，请按照官方文档安装: https://github.com/PaddlePaddle/PaddleSpeech")
            return None
        except Exception as e:
            print(f"PaddleSpeech识别出错: {str(e)}")
            return None
            
    def _xunfei_recognize(self, audio_path):
        """使用讯飞语音识别API识别音频"""
        try:
            import websocket
            import hmac
            import base64
            import hashlib
            import json
            import time
            from urllib.parse import urlencode
            import ssl
            from wsgiref.handlers import format_date_time
            from datetime import datetime
            from time import mktime
            
            # 获取API配置
            app_id = self.xunfei_config.get('app_id', '')
            api_key = self.xunfei_config.get('api_key', '')
            api_secret = self.xunfei_config.get('api_secret', '')
            
            if not app_id or not api_key or not api_secret:
                print("讯飞语音识别API配置不完整")
                return None
            
            # 讯飞API参数和URL
            url = 'wss://iat-api.xfyun.cn/v2/iat'
            host = "iat-api.xfyun.cn"
            
            # 读取音频文件
            with open(audio_path, 'rb') as f:
                file_content = f.read()
            
            # 讯飞需要进行Base64编码
            base64_audio = base64.b64encode(file_content).decode('utf-8')
            
            # 生成认证需要的数据
            class XunfeiRecognizer:
                def __init__(self):
                    self.result = ""
                
                def create_url(self):
                    now = datetime.now()
                    date = format_date_time(mktime(now.timetuple()))
                    
                    # 拼接字符串
                    signature_origin = f"host: {host}\ndate: {date}\nGET /v2/iat HTTP/1.1"
                    
                    # 进行hmac-sha256签名
                    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                          digestmod=hashlib.sha256).digest()
                    
                    # 加密签名
                    signature_sha_base64 = base64.b64encode(signature_sha).decode('utf-8')
                    
                    # 构建authorization
                    authorization_origin = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
                    
                    # 再次进行base64编码
                    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
                    
                    # 拼接鉴权参数
                    v = {
                        "authorization": authorization,
                        "date": date,
                        "host": host
                    }
                    # 拼接URL
                    return url + '?' + urlencode(v)
                
                def on_message(self, ws, message):
                    # 处理返回的消息
                    data = json.loads(message)
                    code = data["code"]
                    if code != 0:
                        print(f"讯飞语音识别出错，错误码: {code}, 错误信息: {data}")
                        ws.close()
                        return
                        
                    if data["data"]["status"] == 2:  # 识别结束
                        self.result += "".join([x["text"] for x in data["data"]["result"]["ws"]])
                        ws.close()
                
                def on_error(self, ws, error):
                    print(f"讯飞语音识别出错: {error}")
                    ws.close()
                
                def on_close(self, ws, close_status_code, close_msg):
                    pass
                
                def on_open(self, ws):
                    """发送音频数据"""
                    # 构建请求参数
                    data = {
                        "common": {
                            "app_id": app_id
                        },
                        "business": {
                            "language": "zh_cn",
                            "domain": "iat",
                            "accent": "mandarin",
                            "dwa": "wpgs",
                            "vad_eos": 10000  # 静默检测阈值
                        },
                        "data": {
                            "status": 0,
                            "format": "audio/L16;rate=16000",
                            "encoding": "raw",
                            "audio": base64_audio
                        }
                    }
                    ws.send(json.dumps(data))
                    # 发送结束标志
                    data["data"]["status"] = 2
                    data["data"]["audio"] = ""
                    ws.send(json.dumps(data))
            
            # 进行识别
            print("使用讯飞语音识别...")
            recognizer = XunfeiRecognizer()
            websocket.enableTrace(False)
            ws_url = recognizer.create_url()
            ws = websocket.WebSocketApp(ws_url,
                                      on_message=recognizer.on_message,
                                      on_error=recognizer.on_error,
                                      on_close=recognizer.on_close)
            ws.on_open = recognizer.on_open
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            
            return recognizer.result
            
        except ImportError:
            print("讯飞语音识别需要安装websocket-client库，请使用pip install websocket-client安装")
            return None
        except Exception as e:
            print(f"讯飞语音识别出错: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def _ali_recognize(self, audio_path):
        """使用阿里云语音识别API识别音频"""
        try:
            import json
            import os
            from aliyunsdkcore.client import AcsClient
            from aliyunsdkcore.request import CommonRequest
            import base64
            
            # 获取API配置
            access_key_id = self.ali_config.get('access_key_id', '')
            access_key_secret = self.ali_config.get('access_key_secret', '')
            
            if not access_key_id or not access_key_secret:
                print("阿里云语音识别API配置不完整")
                return None
                
            # 创建ACS客户端
            client = AcsClient(access_key_id, access_key_secret, 'cn-shanghai')
            
            # 准备请求
            request = CommonRequest()
            request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
            request.set_version('2019-02-28')
            request.set_action_name('CreateToken')
            
            # 获取Token
            response = client.do_action_with_exception(request)
            token_json = json.loads(response.decode('utf-8'))
            token = token_json.get('Token', {}).get('Id')
            
            if not token:
                print("获取阿里云语音识别Token失败")
                return None
                
            # 读取音频文件
            with open(audio_path, 'rb') as f:
                audio_content = f.read()
                
            # 进行Base64编码
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            
            # 构建识别请求
            rec_request = CommonRequest()
            rec_request.set_domain('nls-filetrans.cn-shanghai.aliyuncs.com')
            rec_request.set_version('2018-08-17')
            rec_request.set_action_name('SubmitTask')
            rec_request.set_method('POST')
            
            # 设置任务参数
            task_params = {
                'appkey': access_key_id,
                'token': token,
                'file_link': '',  # 不使用文件链接
                'first_channel_only': True,
                'version': '4.0',
                'enable_inverse_text_normalization': True,
                'enable_punctuation_prediction': True,
                'enable_words': False,
                'enable_sample_rate_adaptive': True,
                'speech_noise_threshold': 0.5,
                'format': os.path.splitext(audio_path)[1][1:],  # 文件格式
                'sample_rate': 16000,
                'audio': audio_base64
            }
            
            rec_request.add_body_params('Task', json.dumps(task_params))
            rec_request.add_body_params('Type', 'asr')
            
            # 发送请求
            print("使用阿里云语音识别...")
            response = client.do_action_with_exception(rec_request)
            result = json.loads(response.decode('utf-8'))
            
            if result.get('StatusCode') == 'REQUEST_EMPTY_BODY':
                print("阿里云语音识别API返回错误: 请求体为空")
                return None
                
            task_id = result.get('TaskId')
            if not task_id:
                print(f"阿里云语音识别API返回错误: {result}")
                return None
                
            # 查询识别结果
            get_result_request = CommonRequest()
            get_result_request.set_domain('nls-filetrans.cn-shanghai.aliyuncs.com')
            get_result_request.set_version('2018-08-17')
            get_result_request.set_action_name('GetTaskResult')
            get_result_request.set_method('GET')
            get_result_request.add_query_param('TaskId', task_id)
            
            # 等待并获取识别结果
            for _ in range(30):  # 最多等待30次
                time.sleep(3)  # 每3秒查询一次结果
                result_response = client.do_action_with_exception(get_result_request)
                get_result = json.loads(result_response.decode('utf-8'))
                
                status = get_result.get('StatusText')
                if status == 'RUNNING':
                    print("阿里云语音识别中...")
                    continue
                elif status == 'SUCCESS':
                    # 提取结果
                    result = get_result.get('Result')
                    sentences = json.loads(result).get('Sentences', [])
                    text = ' '.join([s.get('Text', '') for s in sentences])
                    return text
                else:
                    print(f"阿里云语音识别任务失败: {get_result}")
                    return None
                    
            print("阿里云语音识别超时")
            return None
        except ImportError:
            print("阿里云语音识别需要安装aliyun-python-sdk-core，请使用pip install aliyun-python-sdk-core安装")
            return None
        except Exception as e:
            print(f"阿里云语音识别出错: {str(e)}")
            return None

class VideoDownloader(QObject):
    """抖音视频下载器，参考TikTokDownloader项目"""
    
    # 定义信号
    log_message = pyqtSignal(str)  # 日志信号
    progress_updated = pyqtSignal(int)  # 进度信号
    download_finished = pyqtSignal()  # 下载完成信号
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.download_path = config.download_path
        self.audio_path = config.audio_path
        self.text_path = config.text_path
        self.ffmpeg_path = config.ffmpeg_path
        self.download_audio = config.download_audio
        self.download_cover = config.download_cover
        self.extract_text = config.extract_text
        
        # 初始化语音识别器
        self.speech_recognizer = None
        
        # Whisper模型
        self.whisper_model = None
        self.model_load_progress = 0
        
        self.log_message.emit("初始化下载器...")
        
        # 确保下载目录存在
        os.makedirs(self.download_path, exist_ok=True)
        os.makedirs(self.audio_path, exist_ok=True)
        os.makedirs(self.text_path, exist_ok=True)
        
        self.model = None  # 初始化为 None
        self.last_share_text = ""  # 保存最后一次的分享文本
        
        # 设置请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Referer": "https://www.douyin.com/",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Cookie": ""  # 可以在设置中添加Cookie
        }
        
        # 下载设置
        self.max_retries = 3
        self.timeout = 30
        self.chunk_size = 1024 * 1024  # 1MB
        
    async def load_whisper_model(self):
        """异步加载 Whisper 模型"""
        try:
            self.log_message.emit("=== 开始加载 Whisper 语音识别模型 ===")
            self.log_message.emit("首次使用需要下载模型文件，这可能需要几分钟到几十分钟时间（取决于您的网络速度）")
            
            # 检查 CUDA 是否可用
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.log_message.emit(f"设备类型: {device} {'(GPU加速可用)' if device == 'cuda' else '(CPU模式)'}")
            
            # 使用项目目录下的 models 文件夹
            model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
                self.log_message.emit(f"创建模型目录: {model_dir}")
            
            # 检查模型文件是否已存在
            model_path = os.path.join(model_dir, 'large-v2.pt')
            if os.path.exists(model_path):
                model_size = os.path.getsize(model_path) / (1024 * 1024)  # MB
                self.log_message.emit(f"找到已下载的模型文件 (大小: {model_size:.1f} MB)")
                
                # 验证模型文件
                if model_size < 100:  # 模型文件应该超过1GB，如果太小可能损坏
                    self.log_message.emit("警告: 模型文件大小异常，可能已损坏，将重新下载")
                    try:
                        os.remove(model_path)
                        self.log_message.emit("已删除可能损坏的模型文件")
                    except Exception as e:
                        self.log_message.emit(f"无法删除损坏的模型文件: {str(e)}")
            else:
                self.log_message.emit("模型文件不存在，需要下载")
                self.log_message.emit("large-v2 模型大小约 1.5GB，下载可能需要较长时间...")
                self.log_message.emit("请保持网络连接稳定并等待下载完成...")
            
            # 在新线程中下载和加载模型
            self.log_message.emit("开始加载模型（这可能需要几分钟时间，请耐心等待）...")
            loop = asyncio.get_event_loop()
            
            # 定义回调函数以监控进度
            def load_with_progress():
                try:
                    print("开始加载Whisper模型...")
                    start_time = time.time()
                    model = whisper.load_model("large-v2", device=device, download_root=model_dir)
                    duration = time.time() - start_time
                    print(f"Whisper模型加载完成，用时: {duration:.1f}秒")
                    return model
                except Exception as e:
                    print(f"加载模型出错: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    raise e
            
            # 执行加载
            self.model = await loop.run_in_executor(None, load_with_progress)
            
            if self.model is None:
                self.log_message.emit("错误: 模型加载失败，返回值为None")
                return False
            
            self.log_message.emit("=== Whisper 模型加载成功! ===")
            self.log_message.emit(f"模型类型: large-v2 (支持中文和多种语言)")
            self.log_message.emit(f"模型位置: {model_dir}")
            self.log_message.emit("现在可以开始进行语音识别")
            return True
            
        except Exception as e:
            self.log_message.emit(f"加载 Whisper 模型失败: {str(e)}")
            self.log_message.emit("可能的原因:")
            self.log_message.emit("1. 网络连接不稳定，无法下载模型")
            self.log_message.emit("2. 磁盘空间不足（需要至少2GB空间）")
            self.log_message.emit("3. 内存不足（建议至少8GB内存）")
            self.log_message.emit("4. 模型文件已损坏")
            
            import traceback
            self.log_message.emit(traceback.format_exc())
            return False

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

    async def download_video(self, video_info: Dict) -> bool:
        """下载视频 (专注于douyinvod.com域名链接)"""
        try:
            # 获取视频ID和标题
            aweme_id = video_info.get("aweme_id")
            if not aweme_id:
                self.log_message.emit("错误: 视频信息中缺少ID")
                return False
                
            video_desc = video_info.get("desc", f"抖音视频 {aweme_id}")
            author = video_info.get("author", {}).get("nickname", "未知作者")
            
            # 构建文件路径
            video_path = os.path.join(self.config.download_path, f"{aweme_id}.mp4")
            temp_path = os.path.join(self.config.download_path, f"{aweme_id}_temp.mp4")
            
            # 检查是否已下载
            if os.path.exists(video_path) and os.path.getsize(video_path) > 100*1024:
                if self._validate_video_file(video_path):
                    self.log_message.emit(f"视频已存在: {video_path}")
                    return True
                else:
                    self.log_message.emit("现有视频文件无效，将重新下载")
                    try:
                        os.remove(video_path)
                    except:
                        pass
            
            # 清理可能存在的临时文件
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            
            self.log_message.emit(f"开始下载视频: {video_desc}")
            self.log_message.emit(f"作者: {author}")
            
            # 获取下载链接列表
            download_urls = []
            
            # 从各种可能的位置获取下载链接
            if "video_urls" in video_info:
                download_urls.extend(video_info["video_urls"])
                
            if "download_url" in video_info and video_info["download_url"]:
                download_urls.append(video_info["download_url"])
            
            if "video" in video_info:
                if "play_addr" in video_info["video"]:
                    url_list = video_info["video"]["play_addr"].get("url_list", [])
                    download_urls.extend(url_list)
                    
                if "download_addr" in video_info["video"]:
                    url_list = video_info["video"]["download_addr"].get("url_list", [])
                    download_urls.extend(url_list)
            
            # 如果没有URL，重新获取视频详情
            if not download_urls and aweme_id and not aweme_id.startswith("unknown_"):
                self.log_message.emit("尝试从视频信息中提取下载地址...")
                web_info = await self._get_video_detail_web(aweme_id)
                if web_info:
                    if "video_urls" in web_info:
                        download_urls.extend(web_info["video_urls"])
                    
                    if "download_url" in web_info and web_info["download_url"]:
                        download_urls.append(web_info["download_url"])
                        
                    if "video" in web_info:
                        if "play_addr" in web_info["video"]:
                            url_list = web_info["video"]["play_addr"].get("url_list", [])
                            download_urls.extend(url_list)
                            
                        if "download_addr" in web_info["video"]:
                            url_list = web_info["video"]["download_addr"].get("url_list", [])
                            download_urls.extend(url_list)
            
            # 去重并过滤空链接
            download_urls = [url for url in download_urls if url and url.startswith('http')]
            download_urls = list(dict.fromkeys(download_urls))  # 去重
            
            # 按照优先级排序：优先使用douyinvod.com域名的链接
            if download_urls:
                douyinvod_urls = [url for url in download_urls if "douyinvod.com" in url]
                other_urls = [url for url in download_urls if "douyinvod.com" not in url]
                download_urls = douyinvod_urls + other_urls  # douyinvod链接优先
                
                self.log_message.emit(f"找到 {len(download_urls)} 个候选下载链接")
                
                # 如果有多个候选链接，只使用第一个douyinvod.com链接
                download_url = download_urls[0]
                self.log_message.emit(f"使用下载链接: {download_url}")
                
                # 构建请求头
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                    "Referer": "https://www.douyin.com/",
                    "Accept": "*/*",
                    "Accept-Encoding": "identity;q=1, *;q=0",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Range": "bytes=0-",  # 支持断点续传
                    "Connection": "keep-alive"
                }
                
                # 如果有Cookie，添加到请求头
                if self.config.douyin_cookie:
                    headers["Cookie"] = self.config.douyin_cookie
                
                # 下载视频
                try:
                    self.log_message.emit(f"开始下载文件...")
                    start_time = time.time()
                    
                    async with aiohttp.ClientSession() as session:
                        # 首先尝试HEAD请求获取文件大小
                        total_size = 0
                        try:
                            async with session.head(download_url, headers=headers, timeout=10) as head_resp:
                                if head_resp.status == 200:
                                    total_size = int(head_resp.headers.get("Content-Length", 0))
                                    self.log_message.emit(f"文件大小: {self._format_size(total_size)}")
                        except Exception as e:
                            self.log_message.emit(f"获取文件大小失败: {str(e)}")
                        
                        # 下载视频
                        async with session.get(download_url, headers=headers, timeout=60) as response:
                            if response.status == 200 or response.status == 206:
                                # 确保目录存在
                                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                                
                                # 写入文件
                                with open(temp_path, "wb") as f:
                                    downloaded = 0
                                    chunk_size = 1024 * 1024  # 1MB
                                    last_log_time = time.time()
                                    last_progress_update = 0
                                    
                                    async for chunk in response.content.iter_chunked(chunk_size):
                                        if chunk:
                                            f.write(chunk)
                                            downloaded += len(chunk)
                                            
                                            # 更新进度条
                                            now = time.time()
                                            if total_size > 0:
                                                current_progress = min(100, int(downloaded / total_size * 100))
                                                # 只有当进度变化或超过100ms时才发出信号更新进度条
                                                if (current_progress != last_progress_update or 
                                                    now - last_log_time >= 0.1):
                                                    self.progress_updated.emit(current_progress)
                                                    last_progress_update = current_progress
                                                
                                                # 每3秒输出一次日志
                                                if now - last_log_time >= 3:
                                                    speed = downloaded / (now - start_time)
                                                    self.log_message.emit(
                                                        f"下载进度: {current_progress}% "
                                                        f"({self._format_size(downloaded)}/{self._format_size(total_size)})"
                                                    )
                                                    last_log_time = now
                                
                                # 检查下载的文件
                                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 100*1024:
                                    end_time = time.time()
                                    duration = end_time - start_time
                                    file_size = os.path.getsize(temp_path)
                                    avg_speed = file_size / duration if duration > 0 else 0
                                    
                                    self.log_message.emit(f"下载完成! 用时: {duration:.1f}秒, 大小: {self._format_size(file_size)}")
                                    
                                    # 确保进度条显示100%
                                    self.progress_updated.emit(100)
                                    
                                    if self._validate_video_file(temp_path):
                                        # 移动到最终位置
                                        if os.path.exists(video_path):
                                            os.remove(video_path)
                                        os.rename(temp_path, video_path)
                                        self.log_message.emit(f"下载成功: {video_path}")
                                        
                                        # 添加下载记录
                                        await self._add_download_record(aweme_id)
                                        
                                        # 处理额外内容
                                        await self._process_extra_content(video_info, video_path, aweme_id)
                                        return True
                                    else:
                                        self.log_message.emit("下载的视频文件无效")
                                else:
                                    self.log_message.emit("视频文件下载失败或过小")
                            else:
                                self.log_message.emit(f"下载请求失败，状态码: {response.status}")
                except Exception as e:
                    self.log_message.emit(f"下载过程中出错: {str(e)}")
            else:
                self.log_message.emit("无法获取任何视频下载链接")
            
            # 清理临时文件
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            
            self.log_message.emit("下载失败")
            return False
            
        except Exception as e:
            self.log_message.emit(f"下载视频过程中出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            return False

    async def _process_extra_content(self, video_info: Dict, video_path: str, aweme_id: str) -> None:
        """处理视频的额外内容，如音频提取和文案识别"""
        try:
            # 提取音频
            if self.config.download_audio or self.config.extract_text:
                self.log_message.emit(f"开始从视频中提取音频...")
                audio_path = await self._extract_audio(video_path, aweme_id)
                
                if audio_path and self.config.extract_text:
                    self.log_message.emit("开始执行语音识别...")
                    # 使用 speech_recognition 方法，它会根据用户选择的引擎进行处理
                    await self.speech_recognition(audio_path, aweme_id)
                    
            # 提取封面
            if self.config.download_cover:
                cover_url = self._extract_cover_url(video_info)
                if cover_url:
                    cover_path = os.path.join(self.download_path, f"{aweme_id}_封面.jpg")
                    self.log_message.emit(f"开始下载视频封面...")
                    
                    # 下载封面
                    success = await self._download_media(cover_url, cover_path)
                    if success:
                        self.log_message.emit(f"封面已保存: {cover_path}")
                    else:
                        self.log_message.emit("封面下载失败")
        except Exception as e:
            self.log_message.emit(f"处理额外内容时出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())

    def _validate_video_file(self, video_path: str) -> bool:
        """验证视频文件是否有效"""
        if not os.path.exists(video_path) or os.path.getsize(video_path) < 1024:  # 文件太小，肯定无效
            return False
            
        try:
            # 使用FFmpeg验证视频文件
            cmd = [
                self.config.ffmpeg_path,
                '-v', 'error',
                '-i', video_path,
                '-f', 'null',
                '-'
            ]
            result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            
            # 如果没有错误输出，视频有效
            if not result.stderr:
                return True
                
            # 检查是否存在严重错误
            stderr = result.stderr.decode('utf-8', errors='ignore')
            if 'moov atom not found' in stderr or 'Invalid data found' in stderr:
                self.log_message.emit(f"视频文件无效: {stderr}")
                return False
                
            # 有些小错误可以接受
            return True
        except Exception as e:
            self.log_message.emit(f"验证视频文件时出错: {str(e)}")
            # 如果验证过程出错，但文件存在且大小合理，仍然认为可能有效
            return os.path.getsize(video_path) > 100*1024  # 大于100KB可能是有效的
            
    async def _download_from_web(self, aweme_id: str, video_path: str) -> bool:
        """从网页直接下载视频 (参考 Evil0ctal/Douyin_TikTok_Download_API 项目)"""
        try:
            # 构建Douyin视频页面URL
            page_url = f"https://www.douyin.com/video/{aweme_id}"
            self.log_message.emit(f"尝试从网页下载视频: {page_url}")
            
            # 使用Playwright获取无水印视频
            async with async_playwright() as p:
                # 启动浏览器
                browser = await p.chromium.launch(headless=True)
                
                # 创建上下文
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800},
                )
                
                # 设置Cookie
                if self.config.douyin_cookie:
                    # 解析Cookie字符串并设置
                    cookies = []
                    for cookie_item in self.config.douyin_cookie.split(';'):
                        if '=' in cookie_item:
                            name, value = cookie_item.strip().split('=', 1)
                            cookies.append({
                                'name': name,
                                'value': value,
                                'domain': '.douyin.com',
                                'path': '/'
                            })
                    
                    if cookies:
                        await context.add_cookies(cookies)
                
                # 打开页面
                page = await context.new_page()
                
                # 设置请求拦截
                video_url = None
                
                async def handle_response(response):
                    nonlocal video_url
                    if video_url:
                        return
                        
                    url = response.url
                    # 检查是否是视频资源
                    if any(pattern in url for pattern in [
                        'v3-web.douyinvod.com', 
                        'v26-web.douyinvod.com', 
                        'v9-web.douyinvod.com',
                        '.amemv.com/obj/tos',
                        'video-tx.douyin'
                    ]) and any(ext in url for ext in ['.mp4', '.flv', '.webm']):
                        content_type = response.headers.get('content-type', '')
                        if 'video' in content_type.lower():
                            video_url = url
                            self.log_message.emit(f"拦截到视频URL: {url}")
                
                # 监听响应
                page.on('response', handle_response)
                
                # 访问页面
                self.log_message.emit(f"访问视频页面: {page_url}")
                try:
                    await page.goto(page_url, wait_until='networkidle', timeout=30000)
                except Exception as e:
                    self.log_message.emit(f"页面加载超时，但继续尝试: {str(e)}")
                
                # 等待视频元素加载
                await page.wait_for_timeout(5000)  # 等待5秒
                
                # 尝试播放视频
                try:
                    play_button = await page.query_selector('.xgplayer-play')
                    if play_button:
                        await play_button.click()
                        self.log_message.emit("点击播放按钮")
                        await page.wait_for_timeout(3000)
                except Exception as e:
                    self.log_message.emit(f"点击播放按钮失败: {str(e)}")
                
                # 如果还没有捕获到视频URL，尝试从视频元素获取
                if not video_url:
                    # 尝试获取视频元素
                    video_element = await page.query_selector('video')
                    if video_element:
                        src = await video_element.get_attribute('src')
                        if src:
                            video_url = src
                            self.log_message.emit(f"从视频元素获取到源: {src}")
                
                # 如果还没有找到视频URL，尝试从XHR请求中提取
                if not video_url:
                    self.log_message.emit("尝试从网络请求中查找视频URL...")
                    
                    # 定义拦截函数
                    video_data = None
                    
                    async def intercept_response(response):
                        nonlocal video_data
                        if "aweme/detail" in response.url:
                            try:
                                data = await response.json()
                                if data and "aweme_detail" in data:
                                    video_data = data
                                    self.log_message.emit("成功截获视频详情数据")
                            except:
                                pass
                    
                    # 设置拦截
                    page.on('response', intercept_response)
                    
                    # 刷新页面
                    await page.reload(wait_until='networkidle')
                    await page.wait_for_timeout(5000)
                    
                    # 从捕获的数据中提取URL
                    if video_data:
                        try:
                            # 提取无水印视频链接
                            play_addr = video_data.get("aweme_detail", {}).get("video", {}).get("play_addr", {})
                            url_list = play_addr.get("url_list", [])
                            
                            if url_list:
                                # 优先使用无水印URL
                                for url in url_list:
                                    self.log_message.emit(f"找到视频源: {url}")
                                    # 下载视频
                                    success = await self._download_media(url, os.path.join(self.config.download_path, f"{aweme_id}.mp4"))
                                    if success and self._validate_video_file(os.path.join(self.config.download_path, f"{aweme_id}.mp4")):
                                        self.log_message.emit("从网页直接下载视频成功")
                                        return {
                                            "aweme_id": aweme_id,
                                            "desc": f"抖音视频 {aweme_id}",
                                            "create_time": int(time.time()),
                                            "author": {"nickname": "未知作者"},
                                            "video": {
                                                "play_addr": {
                                                    "url_list": [url]
                                                },
                                                "cover": {
                                                    "url_list": []
                                                }
                                            }
                                        }
                        except Exception as e:
                            self.log_message.emit(f"从网页爬取视频详情失败: {str(e)}")
                            return None
                else:
                    self.log_message.emit("视频元素未找到")
                    return None
        except Exception as e:
            self.log_message.emit(f"从网页爬取视频详情失败: {str(e)}")
            return None

    def _extract_cover_url(self, video_info: Dict) -> Optional[str]:
        """从视频信息中提取封面图地址"""
        try:
            if "video" in video_info and "cover" in video_info["video"]:
                cover = video_info["video"]["cover"]
                url_list = cover.get("url_list", [])
                if url_list:
                    return url_list[0]
            return None
        except Exception:
            return None
            
    def _convert_iteminfo_to_detail(self, item: Dict) -> Dict:
        """将备用API的item格式转换为主API的detail格式"""
        # 标准化转换
        play_addr_list = []
        
        # 提取视频链接 (TikTokDownloader风格)
        if "video" in item:
            if "play_addr" in item["video"]:
                play_addr_list = item["video"]["play_addr"].get("url_list", [])
            elif "play_addr_lowbr" in item["video"]:
                play_addr_list = item["video"]["play_addr_lowbr"].get("url_list", [])
                
        # 补充为空的情况，构建MP4链接
        if not play_addr_list and "aweme_id" in item:
            play_addr_list = [
                f"https://aweme.snssdk.com/aweme/v1/play/?video_id={item['aweme_id']}&ratio=720p&line=0",
                f"https://api.amemv.com/aweme/v1/play/?video_id={item['aweme_id']}&ratio=720p&line=0"
            ]
            
        # 提取封面
        cover_list = []
        if "video" in item:
            if "cover" in item["video"]:
                cover_list = item["video"]["cover"].get("url_list", [])
            elif "origin_cover" in item["video"]:
                cover_list = item["video"]["origin_cover"].get("url_list", [])
                
        # 补充为空的情况
        if not cover_list and "aweme_id" in item:
            cover_list = [f"https://p3-sign.douyinpic.com/tos-cn-p-0015/{item['aweme_id']}~c5_720x720.jpeg"]
            
        # 构建标准化的输出格式
        converted_data = {
            "aweme_id": item.get("aweme_id", ""),
            "desc": item.get("desc", ""),
            "create_time": item.get("create_time", int(time.time())),
            "author": item.get("author", {"nickname": "未知作者"}),
            "video": {
                "play_addr": {
                    "url_list": play_addr_list
                },
                "cover": {
                    "url_list": cover_list
                }
            }
        }
        
        return converted_data

    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小显示"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.2f} GB"

    async def _should_skip_download(self, aweme_id: str, file_path: str) -> bool:
        """检查是否应该跳过下载 (参考TikTokDownloader项目)"""
        # 检查下载记录
        try:
            record_file = os.path.join(self.config.download_path, "downloaded_records.txt")
            if os.path.exists(record_file):
                with open(record_file, "r", encoding="utf-8") as f:
                    if aweme_id in [line.strip() for line in f]:
                        self.log_message.emit(f"视频 {aweme_id} 在下载记录中已存在")
                        return True
        except Exception as e:
            self.log_message.emit(f"读取下载记录时出错: {str(e)}")
            
        # 检查文件是否存在且有效
        if os.path.exists(file_path):
            if os.path.getsize(file_path) < 10 * 1024:  # 小于10KB的文件可能是错误的
                self.log_message.emit(f"文件存在但大小异常 ({self._format_size(os.path.getsize(file_path))}), 将重新下载")
                try:
                    os.remove(file_path)  # 删除可能损坏的文件
                except Exception as e:
                    self.log_message.emit(f"无法删除损坏的文件: {str(e)}")
                return False
                
            # 验证视频文件
            if self._validate_video_file(file_path):
                self.log_message.emit(f"文件已存在且有效: {file_path}")
                return True
            else:
                self.log_message.emit(f"文件存在但无效，将重新下载")
                try:
                    os.remove(file_path)  # 删除无效文件
                except Exception as e:
                    self.log_message.emit(f"无法删除无效文件: {str(e)}")
                return False
                
        return False
        
    async def _add_download_record(self, aweme_id: str) -> None:
        """添加下载记录 (参考TikTokDownloader项目)"""
        try:
            record_file = os.path.join(self.config.download_path, "downloaded_records.txt")
            with open(record_file, "a", encoding="utf-8") as f:
                f.write(f"{aweme_id}\n")
            self.log_message.emit(f"已添加下载记录: {aweme_id}")
        except Exception as e:
            self.log_message.emit(f"添加下载记录时出错: {str(e)}")

    async def _resolve_short_url(self, short_url: str) -> Optional[str]:
        """解析短链接，获取真实链接 (参考 Evil0ctal/Douyin_TikTok_Download_API 项目)"""
        try:
            self.log_message.emit(f"正在解析短链接: {short_url}")
            
            # 如果输入的已经是完整的视频链接，直接返回
            if '/video/' in short_url and 'douyin.com' in short_url:
                self.log_message.emit(f"输入的已经是完整视频链接")
                return short_url
                
            # 处理链接，确保它以http开头
            if not short_url.startswith('http'):
                if short_url.startswith('v.douyin.com'):
                    short_url = 'https://' + short_url
                else:
                    short_url = 'https://v.douyin.com/' + short_url.strip('/')
            
            # 设置请求头，模拟移动设备
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1'
            }
            
            # 添加Cookie如果有的话
            if self.config.douyin_cookie:
                headers['Cookie'] = self.config.douyin_cookie
            
            # 创建会话并设置重定向属性
            async with aiohttp.ClientSession() as session:
                # 首先尝试Head请求获取重定向信息
                try:
                    async with session.head(short_url, headers=headers, allow_redirects=False, timeout=10) as response:
                        if response.status in (301, 302):
                            location = response.headers.get('Location')
                            if location:
                                self.log_message.emit(f"HEAD请求获取到重定向URL: {location}")
                                return location
                except Exception as e:
                    self.log_message.emit(f"HEAD请求失败，尝试GET请求: {str(e)}")
                
                # 如果HEAD请求失败，尝试GET请求
                try:
                    # 不自动重定向，我们要手动处理重定向
                    async with session.get(short_url, headers=headers, allow_redirects=False, timeout=10) as response:
                        # 检查是否是重定向响应
                        if response.status in (301, 302):
                            location = response.headers.get('Location')
                            if location:
                                self.log_message.emit(f"GET请求获取到重定向URL: {location}")
                                return location
                        
                        # 如果没有重定向，但状态码是200，尝试从响应内容中获取
                        elif response.status == 200:
                            # 读取响应内容
                            text = await response.text()
                            
                            # 尝试从meta标签中提取重定向URL
                            meta_refresh = re.search(r'<meta[^>]*?url=(.*?)[\'"\s>]', text)
                            if meta_refresh:
                                redirect_url = meta_refresh.group(1)
                                self.log_message.emit(f"从meta标签获取到重定向URL: {redirect_url}")
                                return redirect_url
                            
                            # 尝试从JS中提取视频ID
                            video_id_match = re.search(r'\/video\/(\d+)', text)
                            if video_id_match:
                                video_id = video_id_match.group(1)
                                full_url = f"https://www.douyin.com/video/{video_id}"
                                self.log_message.emit(f"从页面内容提取到视频ID: {video_id}")
                                return full_url
                except Exception as e:
                    self.log_message.emit(f"GET请求处理失败: {str(e)}")
            
            # 如果上述方法都失败，则尝试使用备用方法
            self.log_message.emit("标准方法失败，尝试使用备用方法解析")
            return await self._resolve_short_url_backup(short_url)
            
        except Exception as e:
            self.log_message.emit(f"解析短链接时出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            return await self._resolve_short_url_backup(short_url)  # 失败时尝试备用方法

    def _generate_tokens(self, aweme_id: str) -> Tuple[str, str, str]:
        """生成请求需要的token和设备信息 (参考 Evil0ctal/Douyin_TikTok_Download_API 项目)"""
        try:
            # 生成13位的时间戳
            timestamp = str(int(time.time() * 1000))
            
            # 生成随机的msToken (类似于Evil0ctal项目的实现)
            msToken_length = random.randint(107, 143)
            msToken_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789="
            msToken = ''.join(random.choice(msToken_chars) for _ in range(msToken_length))
            
            # 生成X-Bogus签名 (模拟Evil0ctal项目的实现)
            # 实际项目中使用了复杂的算法，这里我们使用一个简化版
            x_bogus_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
            x_bogus_length = 22  # Evil0ctal项目中的X-Bogus通常是22位
            
            # 为了增加一些确定性，我们将aweme_id和timestamp作为种子
            seed = int(aweme_id) % 10000 + int(timestamp) % 10000
            random.seed(seed)
            
            # 前6位使用特定模式
            x_bogus = "".join(random.choice(x_bogus_chars) for _ in range(6))
            # 中间10位为时间戳信息的混合
            ts_part = [x_bogus_chars[int(d) * 6 % len(x_bogus_chars)] for d in timestamp[:10]]
            x_bogus += "".join(ts_part)
            # 后6位随机
            x_bogus += "".join(random.choice(x_bogus_chars) for _ in range(6))
            
            # 恢复随机种子
            random.seed()
            
            self.log_message.emit(f"生成msToken: {msToken[:10]}...（总长度: {len(msToken)}）")
            self.log_message.emit(f"生成X-Bogus: {x_bogus}")
            
            return msToken, x_bogus, timestamp
        except Exception as e:
            self.log_message.emit(f"生成token时出错: {str(e)}")
            # 出错时返回默认值
            return "", "", str(int(time.time() * 1000))

    def _generate_device_info(self) -> Tuple[str, str]:
        """生成设备ID和安装ID (参考 Evil0ctal/Douyin_TikTok_Download_API 项目)"""
        try:
            # 生成device_id (随机的11位数字)
            device_id = ''.join([str(random.randint(0, 9)) for _ in range(11)])
            
            # 生成install_id (随机的16位数字)
            install_id = ''.join([str(random.randint(0, 9)) for _ in range(16)])
            
            # 可选：使用UUID库生成更随机的ID
            # import uuid
            # device_id = str(uuid.uuid4()).replace('-', '')[:11]
            # install_id = str(uuid.uuid4()).replace('-', '')[:16]
            
            self.log_message.emit(f"生成device_id: {device_id}")
            self.log_message.emit(f"生成install_id: {install_id}")
            
            return device_id, install_id
        except Exception as e:
            self.log_message.emit(f"生成设备信息时出错: {str(e)}")
            # 出错时返回默认值
            return "12345678901", "1234567890123456"

    async def parse_share_url(self, share_text: str) -> Optional[Dict]:
        """解析分享链接并获取视频信息 (专注于网页抓取方法)"""
        try:
            # 保存最后一次的分享文本，用于提取标题等信息
            self.last_share_text = share_text
            self.log_message.emit(f"开始解析分享内容: {share_text}")
            
            # 从分享文本中提取短链接
            short_url_match = re.search(r'https?://v\.douyin\.com/\w+', share_text)
            if not short_url_match:
                self.log_message.emit("从分享文本中未找到抖音短链接")
                
                # 尝试直接从分享文本中提取视频ID
                video_id_match = re.search(r'video/(\d+)', share_text)
                if video_id_match:
                    aweme_id = video_id_match.group(1)
                    self.log_message.emit(f"从分享文本中提取到视频ID: {aweme_id}")
                    # 直接使用网页方法获取视频详情
                    video_info = await self._get_video_detail_web(aweme_id)
                    return video_info
                    
                return None
                
            short_url = short_url_match.group(0)
            self.log_message.emit(f"从分享文本中提取到链接: {short_url}")
            
            # 处理重定向，获取真实URL
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                }
                
                # 先使用HEAD请求获取重定向URL，这样更快
                async with aiohttp.ClientSession() as session:
                    self.log_message.emit(f"正在解析短链接: {short_url}")
                    async with session.head(short_url, headers=headers, allow_redirects=False, timeout=10) as response:
                        if response.status in (301, 302, 303, 307, 308):  # 重定向状态码
                            location = response.headers.get('Location')
                            if location:
                                self.log_message.emit(f"HEAD请求获取到重定向URL: {location}")
                                
                                # 提取视频ID
                                match = re.search(r'video/(\d+)', location)
                                if match:
                                    aweme_id = match.group(1)
                                    self.log_message.emit(f"从解析后的URL中提取到视频ID: {aweme_id}")
                                    
                                    # 直接使用网页方法获取视频详情
                                    video_info = await self._get_video_detail_web(aweme_id)
                                    return video_info
                            else:
                                self.log_message.emit("重定向响应中没有Location头")
                        else:
                            self.log_message.emit(f"短链接HEAD请求失败，状态码: {response.status}")
            except Exception as e:
                self.log_message.emit(f"解析短链接时出错: {str(e)}")
            
            # 备用方法：尝试使用多种模式匹配视频ID
            id_patterns = [
                r'video/(\d+)',
                r'note/(\d+)',
                r'/(\d{19})/?',
                r'[?&]item_id=(\d+)',
                r'[?&]id=(\d+)'
            ]
            
            for pattern in id_patterns:
                match = re.search(pattern, share_text)
                if match:
                    aweme_id = match.group(1)
                    self.log_message.emit(f"使用备用模式提取到视频ID: {aweme_id}")
                    # 直接使用网页方法获取视频详情
                    video_info = await self._get_video_detail_web(aweme_id)
                    return video_info
            
            # 尝试从分享文本中提取信息
            title = ""
            title_match = re.search(r'【(.*?)】', share_text)
            if title_match:
                title = title_match.group(1)
                self.log_message.emit(f"从分享文本中提取到标题: {title}")
            
            # 返回基本信息，防止程序崩溃
            self.log_message.emit("无法获取完整视频信息，返回基本信息")
            return {
                "aweme_id": f"unknown_{int(time.time())}",
                "desc": title or "抖音视频",
                "create_time": int(time.time()),
                "author": {"nickname": "未知作者"},
                "video": {
                    "play_addr": {"url_list": []},
                    "cover": {"url_list": []}
                }
            }
            
        except Exception as e:
            self.log_message.emit(f"解析分享链接时出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            
            # 返回基本信息以防止程序崩溃
            return {
                "aweme_id": f"unknown_{int(time.time())}",
                "desc": "未知抖音视频",
                "create_time": int(time.time()),
                "author": {"nickname": "未知作者"},
                "video": {
                    "play_addr": {"url_list": []},
                    "cover": {"url_list": []}
                }
            }

    async def _get_video_detail(self, aweme_id: str) -> Optional[Dict]:
        """获取视频详细信息（已废弃，直接使用网页抓取方法）"""
        self.log_message.emit(f"获取视频 {aweme_id} 的详细信息...")
        # 直接使用网页方法获取视频详情
        return await self._get_video_detail_web(aweme_id)

    # 移除或注释其他尝试API的方法
    # async def _get_video_detail_api1(self, aweme_id: str) -> Optional[Dict]:
    #     """API方法1 - 已禁用"""
    #     return None
    
    # async def _get_video_detail_api2(self, aweme_id: str) -> Optional[Dict]:
    #     """API方法2 - 已禁用"""
    #     return None
    
    # async def _get_video_detail_api3(self, aweme_id: str) -> Optional[Dict]:
    #     """API方法3 - 已禁用"""
    #     return None

    async def _get_video_detail_web(self, aweme_id: str) -> Optional[Dict]:
        """从网页中获取视频详情（优化超时问题）"""
        try:
            page_url = f"https://www.douyin.com/video/{aweme_id}"
            self.log_message.emit(f"尝试从网页获取视频详情: {page_url}")
            
            async with async_playwright() as p:
                # 启动浏览器
                browser = await p.chromium.launch(headless=True)
                
                # 创建上下文
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800},
                )
                
                # 设置Cookie
                if self.config.douyin_cookie:
                    # 解析Cookie字符串并设置
                    cookies = []
                    for cookie_item in self.config.douyin_cookie.split(';'):
                        if '=' in cookie_item:
                            name, value = cookie_item.strip().split('=', 1)
                            cookies.append({
                                'name': name,
                                'value': value,
                                'domain': '.douyin.com',
                                'path': '/'
                            })
                    
                    if cookies:
                        await context.add_cookies(cookies)
                
                # 打开页面
                page = await context.new_page()
                
                # 捕获网络请求
                video_data = None
                video_urls = []
                
                async def handle_response(response):
                    nonlocal video_data, video_urls
                    try:
                        url = response.url
                        
                        # 捕获视频详情API响应
                        if "aweme/detail" in url:
                            body = await response.text()
                            try:
                                data = json.loads(body)
                                if data and "aweme_detail" in data:
                                    video_data = data
                                    self.log_message.emit("成功截获视频详情数据")
                            except json.JSONDecodeError:
                                pass
                                
                        # 捕获视频URL
                        if any(domain in url for domain in ["douyinvod.com", ".amemv.com", "douyin"]) and \
                           any(ext in url for ext in [".mp4", ".flv", ".webm"]):
                            content_type = response.headers.get("content-type", "")
                            if "video" in content_type.lower():
                                self.log_message.emit(f"捕获到视频URL: {url}")
                                if url not in video_urls:
                                    video_urls.append(url)
                    except Exception as e:
                        pass
                
                # 监听响应
                page.on('response', handle_response)
                
                # 访问页面 - 使用domcontentloaded而不是networkidle，降低超时风险
                try:
                    self.log_message.emit(f"访问视频页面: {page_url}")
                    await page.goto(page_url, wait_until='domcontentloaded', timeout=15000)
                    
                    # 在页面加载后，增加额外的等待时间以捕获更多网络请求
                    for _ in range(3):  # 最多等待3秒
                        if video_data or video_urls:
                            self.log_message.emit("已捕获到数据，无需继续等待")
                            break
                        await page.wait_for_timeout(1000)  # 等待1秒
                        
                except Exception as e:
                    # 即使超时也继续，因为我们可能已经捕获了足够的数据
                    self.log_message.emit(f"页面加载未完成，但继续处理: {str(e)}")
                
                # 尝试找到并点击播放按钮
                try:
                    play_button = await page.query_selector('.xgplayer-play, .xgplayer-start')
                    if play_button:
                        await play_button.click()
                        self.log_message.emit("点击播放按钮以触发视频加载")
                        await page.wait_for_timeout(2000)  # 等待视频加载
                except Exception:
                    pass
                    
                # 尝试从DOM中提取视频元素URL
                try:
                    video_element = await page.query_selector('video')
                    if video_element:
                        src = await video_element.get_attribute('src')
                        if src and src.startswith('http') and src not in video_urls:
                            video_urls.append(src)
                            self.log_message.emit(f"从视频元素获取URL: {src}")
                except Exception:
                    pass
                
                # 如果通过拦截获取到了数据
                if video_data and "aweme_detail" in video_data:
                    self.log_message.emit("使用拦截到的视频详情数据")
                    # 提取视频信息
                    video_info = video_data["aweme_detail"]
                    
                    # 添加捕获到的视频URL
                    if video_urls and len(video_urls) > 0:
                        video_info["video_urls"] = video_urls
                        video_info["download_url"] = video_urls[0]  # 设置第一个URL为默认下载URL
                        
                    # 关闭浏览器
                    await browser.close()
                    return video_info
                else:
                    # 如果没有通过API获取到数据，但捕获到了视频URL
                    if video_urls and len(video_urls) > 0:
                        self.log_message.emit(f"未获取到完整详情，但找到了 {len(video_urls)} 个视频链接")
                        
                        # 尝试获取标题和作者信息
                        title = "抖音视频"
                        author = "未知作者"
                        
                        try:
                            title_element = await page.query_selector('.drama-name, .video-info-detail .title, .title-wrap .title')
                            if title_element:
                                title = await title_element.inner_text()
                                
                            author_element = await page.query_selector('.author-name, .info-wrap .nickname, .nickname')
                            if author_element:
                                author = await author_element.inner_text()
                        except Exception:
                            pass
                            
                        # 关闭浏览器
                        await browser.close()
                        
                        # 构建基本视频信息
                        return {
                            "aweme_id": aweme_id,
                            "desc": title or f"抖音视频 {aweme_id}",
                            "create_time": int(time.time()),
                            "author": {"nickname": author},
                            "video": {
                                "play_addr": {"url_list": video_urls},
                                "download_addr": {"url_list": video_urls},
                                "cover": {"url_list": []}
                            },
                            "video_urls": video_urls,
                            "download_url": video_urls[0]  # 设置第一个URL为默认下载URL
                        }
                
                # 尝试提取基本信息
                self.log_message.emit("尝试从页面提取基本信息...")
                title = f"抖音视频 {aweme_id}"
                author = "未知作者"
                
                try:
                    title_element = await page.query_selector('.drama-name, .video-info-detail .title, .title-wrap .title')
                    if title_element:
                        title = await title_element.inner_text()
                        
                    author_element = await page.query_selector('.author-name, .info-wrap .nickname, .nickname')
                    if author_element:
                        author = await author_element.inner_text()
                except Exception:
                    pass
                    
                # 关闭浏览器
                await browser.close()
                
                # 尝试构建基本信息
                self.log_message.emit(f"构建基本信息: {title} - {author}")
                return {
                    "aweme_id": aweme_id,
                    "desc": title,
                    "create_time": int(time.time()),
                    "author": {"nickname": author},
                    "video": {
                        "play_addr": {
                            "url_list": [
                                f"https://aweme.snssdk.com/aweme/v1/play/?video_id={aweme_id}&ratio=1080p&line=0"
                            ]
                        }
                    }
                }
                
        except Exception as e:
            self.log_message.emit(f"从网页获取视频详情时出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            
            # 返回基本信息以避免完全失败
            return {
                "aweme_id": aweme_id,
                "desc": f"抖音视频 {aweme_id}",
                "create_time": int(time.time()),
                "author": {"nickname": "未知作者"},
                "video": {
                    "play_addr": {
                        "url_list": [
                            f"https://aweme.snssdk.com/aweme/v1/play/?video_id={aweme_id}&ratio=1080p&line=0"
                        ]
                    }
                }
            }

    async def _download_media(self, url: str, filepath: str, headers=None) -> bool:
        """下载媒体文件 (参考 Evil0ctal/Douyin_TikTok_Download_API 项目)"""
        try:
            # 检查URL是否有效
            if not url or not url.startswith('http'):
                self.log_message.emit(f"无效的下载URL: {url}")
                return False
                
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            
            # 默认请求头
            default_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                "Referer": "https://www.douyin.com/",
                "Accept": "*/*",
                "Origin": "https://www.douyin.com",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Range": "bytes=0-"
            }
            
            # 合并自定义headers
            if headers:
                default_headers.update(headers)
                
            # 检查是否是部分下载的情况
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                if file_size > 0:
                    # 文件已经存在且有内容，检查是否需要继续下载
                    default_headers["Range"] = f"bytes={file_size}-"
                    self.log_message.emit(f"文件已存在，尝试断点续传 ({self._format_size(file_size)})")
            
            # 初始下载信息
            start_time = time.time()
            self.log_message.emit(f"开始下载: {url} -> {filepath}")
            
            # 创建异步HTTP会话
            retry_count = 0
            max_retries = 3
            
            while retry_count <= max_retries:
                try:
                    async with aiohttp.ClientSession() as session:
                        # 先发送HEAD请求获取文件大小
                        file_size = 0
                        try:
                            async with session.head(url, headers=default_headers) as head_resp:
                                if 'Content-Length' in head_resp.headers:
                                    file_size = int(head_resp.headers['Content-Length'])
                                    self.log_message.emit(f"文件大小: {self._format_size(file_size)}")
                        except Exception as e:
                            self.log_message.emit(f"无法获取文件大小: {str(e)}")
                        
                        # 下载文件
                        mode = 'ab' if os.path.exists(filepath) and 'Range' in default_headers else 'wb'
                        
                        async with session.get(url, headers=default_headers, timeout=30) as response:
                            if response.status not in (200, 206):  # 206是部分内容的状态码
                                self.log_message.emit(f"下载失败，HTTP状态码: {response.status}")
                                if retry_count < max_retries:
                                    retry_count += 1
                                    wait_time = 2 ** retry_count  # 指数退避
                                    self.log_message.emit(f"尝试重新下载 ({retry_count}/{max_retries})，等待 {wait_time} 秒...")
                                    await asyncio.sleep(wait_time)
                                    continue
                            
                            # 获取实际内容长度
                            if 'Content-Length' in response.headers:
                                content_length = int(response.headers['Content-Length'])
                            else:
                                content_length = 0
                                
                            # 如果是Range请求，检查是否返回了预期的部分内容
                            if 'Range' in default_headers and response.status != 206:
                                self.log_message.emit(f"服务器不支持断点续传，将重新下载")
                                mode = 'wb'  # 改为完全重写模式
                            
                            # 实际下载过程
                            with open(filepath, mode) as f:
                                downloaded = 0
                                chunk_size = 1024 * 1024  # 1MB
                                last_progress_time = time.time()
                                last_downloaded = 0
                                
                                async for chunk in response.content.iter_chunked(chunk_size):
                                    if chunk:
                                        f.write(chunk)
                                        downloaded += len(chunk)
                                        
                                        # 计算下载进度
                                        if file_size > 0:
                                            # 如果是断点续传，考虑已下载部分
                                            total_downloaded = downloaded
                                            if mode == 'ab' and 'Range' in default_headers:
                                                range_start = int(default_headers['Range'].split('=')[1].split('-')[0])
                                                total_downloaded += range_start
                                            
                                            progress = min(int(total_downloaded * 100 / file_size), 100)
                                            self.progress_updated.emit(progress)
                                            
                                            # 计算下载速度
                                            now = time.time()
                                            if now - last_progress_time >= 2:  # 每2秒更新一次
                                                speed = (downloaded - last_downloaded) / (now - last_progress_time)
                                                self.log_message.emit(
                                                    f"下载进度: {progress}% "
                                                    f"({self._format_size(total_downloaded)}/{self._format_size(file_size)}) "
                                                    f"速度: {self._format_size(speed)}/s"
                                                )
                                                last_progress_time = now
                                                last_downloaded = downloaded
                            
                            # 下载完成
                            end_time = time.time()
                            duration = end_time - start_time
                            total_size = os.path.getsize(filepath)
                            
                            # 验证文件大小
                            if file_size > 0 and total_size < file_size * 0.95:  # 允许5%的误差
                                self.log_message.emit(
                                    f"警告: 下载的文件大小 ({self._format_size(total_size)}) "
                                    f"小于预期 ({self._format_size(file_size)})"
                                )
                                if retry_count < max_retries:
                                    retry_count += 1
                                    self.log_message.emit(f"尝试重新下载 ({retry_count}/{max_retries})...")
                                    continue
                            
                            self.log_message.emit(
                                f"下载完成! 用时: {duration:.1f}秒, "
                                f"大小: {self._format_size(total_size)}, "
                                f"平均速度: {self._format_size(total_size/duration if duration > 0 else 0)}/s"
                            )
                            return True
                            
                except aiohttp.ClientError as e:
                    self.log_message.emit(f"下载出错: {str(e)}")
                    if retry_count < max_retries:
                        retry_count += 1
                        wait_time = 2 ** retry_count
                        self.log_message.emit(f"尝试重新下载 ({retry_count}/{max_retries})，等待 {wait_time} 秒...")
                        await asyncio.sleep(wait_time)
                    else:
                        return False
                except Exception as e:
                    self.log_message.emit(f"下载时发生未知错误: {str(e)}")
                    import traceback
                    self.log_message.emit(traceback.format_exc())
                    return False
                    
            self.log_message.emit(f"达到最大重试次数 ({max_retries})，下载失败")
            return False
                
        except Exception as e:
            self.log_message.emit(f"下载媒体文件时出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            return False

    async def download_videos(self, share_urls: List[str]):
        """批量下载视频"""
        try:
            if not share_urls:
                self.log_message.emit("没有提供任何链接")
                self.download_finished.emit()
                return
                
            # 记录开始时间
            start_time = time.time()
            
            # 初始化计数
            total_count = len(share_urls)
            success_count = 0
            skip_count = 0
            fail_count = 0
            
            self.log_message.emit(f"开始处理 {total_count} 个链接...")
            
            for i, share_url in enumerate(share_urls):
                # 更新进度
                progress = int((i / total_count) * 100)
                self.progress_updated.emit(progress)
                
                try:
                    self.log_message.emit(f"\n正在处理第 {i+1}/{total_count} 个链接: {share_url}")
                    
                    # 解析链接
                    video_info = await self.parse_share_url(share_url)
                    if not video_info:
                        self.log_message.emit("无法解析链接，跳过")
                        fail_count += 1
                        continue
                        
                    # 提取视频ID
                    aweme_id = video_info.get("aweme_id", "")
                    if not aweme_id:
                        self.log_message.emit("无法获取视频ID，跳过")
                        fail_count += 1
                        continue
                        
                    # 提取视频标题和作者
                    title = video_info.get("desc", f"抖音视频 {aweme_id}")
                    author = video_info.get("author", {}).get("nickname", "未知作者")
                    
                    # 生成安全的文件名
                    safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)
                    file_name = f"{aweme_id}.mp4"
                    
                    # 下载路径
                    file_path = os.path.join(self.download_path, file_name)
                    
                    # 检查是否需要跳过下载
                    if await self._should_skip_download(aweme_id, file_path):
                        self.log_message.emit(f"视频已下载，跳过: {title} - {author}")
                        skip_count += 1
                        continue
                        
                    # 下载视频
                    self.log_message.emit(f"开始下载: {title} - {author}")
                    
                    # 检查并获取下载URL
                    if "download_url" in video_info:
                        download_url = video_info["download_url"]
                    elif "video" in video_info and "play_addr" in video_info["video"]:
                        url_list = video_info["video"]["play_addr"]["url_list"]
                        if url_list:
                            # 选择最佳URL（无水印）
                            download_url = url_list[0].replace("playwm", "play")
                        else:
                            self.log_message.emit("无法获取下载链接，跳过")
                            fail_count += 1
                            continue
                    else:
                        self.log_message.emit("无法获取下载链接，跳过")
                        fail_count += 1
                        continue
                    
                    # 尝试下载
                    if await self._download_media(download_url, file_path):
                        self.log_message.emit(f"视频下载成功: {file_path}")
                        
                        # 添加到下载记录
                        await self._add_download_record(aweme_id)
                        
                        # 处理额外内容（如音频和封面）
                        # 这里调用_process_extra_content，确保使用用户选择的语音识别引擎
                        await self._process_extra_content(video_info, file_path, aweme_id)
                        
                        success_count += 1
                    else:
                        # 尝试使用网页方式下载
                        self.log_message.emit("直接下载失败，尝试通过网页方式获取...")
                        if await self._download_from_web(aweme_id, file_path):
                            self.log_message.emit(f"通过网页下载成功: {file_path}")
                            
                            # 添加到下载记录
                            await self._add_download_record(aweme_id)
                            
                            # 处理额外内容（如音频和封面）
                            await self._process_extra_content(video_info, file_path, aweme_id)
                            
                            success_count += 1
                        else:
                            self.log_message.emit(f"下载失败: {title}")
                            fail_count += 1
                except Exception as e:
                    self.log_message.emit(f"处理链接时出错: {str(e)}")
                    import traceback
                    self.log_message.emit(traceback.format_exc())
                    fail_count += 1
                    
                # 添加一点延迟，避免请求过快
                await asyncio.sleep(1)
                
            # 全部完成
            end_time = time.time()
            duration = end_time - start_time
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            
            self.log_message.emit(f"\n批量下载完成:")
            self.log_message.emit(f"总共: {total_count} 个链接")
            self.log_message.emit(f"成功: {success_count} 个")
            self.log_message.emit(f"跳过: {skip_count} 个")
            self.log_message.emit(f"失败: {fail_count} 个")
            self.log_message.emit(f"用时: {minutes}分{seconds}秒")
            
            self.progress_updated.emit(100)
            self.download_finished.emit()
            
        except Exception as e:
            self.log_message.emit(f"批量下载过程中发生错误: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            self.download_finished.emit()

    async def _extract_audio(self, video_path: str, aweme_id: str) -> Optional[str]:
        """从视频中提取音频 (用于语音识别)"""
        try:
            # 构建音频文件路径
            audio_path = os.path.join(self.config.audio_path, f"{aweme_id}.mp3")
            self.log_message.emit(f"从视频提取音频: {video_path} -> {audio_path}")
            
            # 检查音频文件是否已存在
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 10 * 1024:  # 大于10KB认为有效
                self.log_message.emit(f"音频文件已存在: {audio_path}")
                return audio_path
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)
            
            # 使用FFmpeg提取音频
            cmd = [
                self.config.ffmpeg_path,
                '-i', video_path,
                '-vn',  # 不处理视频
                '-acodec', 'libmp3lame',  # 使用MP3编码
                '-ar', '44100',  # 采样率
                '-ac', '2',  # 双声道
                '-b:a', '128k',  # 比特率
                '-y',  # 覆盖已有文件
                audio_path
            ]
            
            # 执行命令
            self.log_message.emit(f"执行FFmpeg命令提取音频...")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # 等待命令完成
            stdout, stderr = await process.communicate()
            
            # 检查是否成功
            if process.returncode == 0 and os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                self.log_message.emit(f"音频提取成功: {audio_path}")
                
                # 不再这里触发语音识别，由调用者负责
                # 返回音频路径
                return audio_path
            else:
                self.log_message.emit(f"音频提取失败: {stderr.decode('utf-8', errors='ignore') if stderr else '未知错误'}")
                return None
                
        except Exception as e:
            self.log_message.emit(f"提取音频过程中出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            return None

    async def speech_recognition(self, audio_file, video_id):
        """
        执行语音识别并保存结果
        
        此方法是所有语音识别的统一入口点，包括:
        1. 下载视频后的自动文案提取
        2. 导入视频后的文案提取
        3. 导入音频的文案提取
        
        该方法会根据用户在设置中选择的语音识别引擎来调用对应的识别方法，
        确保所有场景下都使用用户指定的引擎。
        """
        try:
            if not os.path.exists(audio_file):
                self.log_message.emit(f"错误: 音频文件不存在: {audio_file}")
                return False
                
            text_dir = self.config.text_path
            os.makedirs(text_dir, exist_ok=True)
            text_file = os.path.join(text_dir, f"{video_id}_文案.txt")
            
            # 获取选择的引擎 - 直接使用用户在设置中选择的引擎
            engine_name = self.config.speech_recognition_engine
            self.log_message.emit(f"使用 {engine_name} 引擎进行语音识别...")
            
            # 创建语音识别器实例
            recognizer = SpeechRecognizer(self.config)
            
            # 根据当前选择的引擎执行识别
            engine = recognizer.ENGINE_MAP.get(engine_name, "whisper")
            self.log_message.emit(f"识别引擎类型: {engine}")
            
            # 检查音频文件大小和时长
            try:
                file_size = os.path.getsize(audio_file)
                self.log_message.emit(f"音频文件大小: {self._format_size(file_size)}")
                
                # 尝试获取音频时长
                try:
                    import subprocess
                    cmd = [
                        self.config.ffmpeg_path,
                        "-i", audio_file,
                        "-hide_banner"
                    ]
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )
                    _, stderr = process.communicate()
                    
                    # 从FFmpeg输出中解析时长
                    import re
                    duration_match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", stderr)
                    if duration_match:
                        hours, minutes, seconds = duration_match.groups()
                        duration_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                        self.log_message.emit(f"音频时长: {int(duration_seconds//60)}分{int(duration_seconds%60)}秒")
                        
                        # 对于较长的音频文件，提供额外警告
                        if duration_seconds > 300 and engine == "google":  # 5分钟以上
                            self.log_message.emit("警告: 音频时长较长，Google语音识别可能会超时或失败，建议使用Whisper")
                except Exception as e:
                    self.log_message.emit(f"获取音频时长失败: {str(e)}")
            except Exception as e:
                self.log_message.emit(f"检查音频文件失败: {str(e)}")
            
            # 针对不同引擎的特殊处理
            if engine == "whisper":
                # 仅在使用Whisper时加载模型
                if not self.whisper_model:
                    self.log_message.emit("加载Whisper模型...")
                    await self.load_whisper_model()
                
                # 将模型传给识别器
                recognizer.whisper_model = self.whisper_model
            elif engine == "google":
                # 检查Google语音识别依赖
                try:
                    import speech_recognition as sr
                    self.log_message.emit("已安装speech_recognition库")
                except ImportError:
                    self.log_message.emit("错误: 未安装speech_recognition库，无法使用Google语音识别")
                    self.log_message.emit("请使用以下命令安装: pip install SpeechRecognition pyaudio")
                    return False
                    
                # 检查网络连接
                try:
                    import socket
                    socket.create_connection(("www.google.com", 80), timeout=5)
                    self.log_message.emit("网络连接正常，可以访问Google服务")
                except Exception:
                    self.log_message.emit("警告: 无法连接到Google服务，语音识别可能会失败")
            
            # 执行识别 - 调用统一的识别接口
            self.log_message.emit("开始识别音频内容...")
            text = recognizer.recognize(audio_file)
            
            if not text:
                self.log_message.emit("语音识别失败，未能识别出文本。")
                
                # 针对不同引擎提供帮助信息
                if engine == "google":
                    self.log_message.emit("\n可能的解决方案:")
                    self.log_message.emit("1. 确保已安装PyAudio库: pip install pyaudio")
                    self.log_message.emit("2. 确保网络可以访问Google服务")
                    self.log_message.emit("3. 音频文件可能太长，Google语音识别对较长音频支持有限")
                    self.log_message.emit("4. 尝试使用Whisper引擎，它对长音频有更好的支持")
                elif engine == "whisper":
                    self.log_message.emit("\n可能的解决方案:")
                    self.log_message.emit("1. 确保已安装Whisper库: pip install openai-whisper")
                    self.log_message.emit("2. 检查音频文件是否有效")
                    self.log_message.emit("3. 尝试使用不同大小的Whisper模型")
                
                return False
                
            # 保存识别结果
            with open(text_file, "w", encoding="utf-8") as f:
                f.write(text)
                
            self.log_message.emit(f"文案提取完成，已保存到: {text_file}")
            self.log_message.emit(f"文案内容:\n{text[:200]}..." if len(text) > 200 else f"文案内容:\n{text}")
            
            return True
            
        except Exception as e:
            self.log_message.emit(f"语音识别出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            return False

    async def process_imported_video(self, video_path: str) -> bool:
        """处理导入的视频文件，提取音频并识别文本
        :param video_path: 视频文件路径
        :return: 是否处理成功
        """
        try:
            # 获取文件名（不含扩展名）作为视频ID
            video_filename = os.path.basename(video_path)
            video_id = os.path.splitext(video_filename)[0]
            
            self.log_message.emit(f"开始处理导入的视频文件: {video_path}")
            self.log_message.emit(f"视频ID: {video_id}")
            
            # 提取音频
            audio_file = await self._extract_audio(video_path, video_id)
            if not audio_file:
                self.log_message.emit("提取音频失败")
                return False
                
            # 识别文本
            if self.config.extract_text:
                # 使用视频ID作为文件名
                await self.speech_recognition(audio_file, video_id)
            
            return True
        except Exception as e:
            self.log_message.emit(f"处理导入视频出错: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False
            
    async def import_audio(self, audio_path: str) -> bool:
        """导入音频文件直接进行文案提取，支持多种音频格式"""
        self.log_message.emit(f"开始处理导入的音频文件: {audio_path}")
        
        try:
            # 检查文件是否存在
            if not os.path.exists(audio_path):
                self.log_message.emit(f"错误: 音频文件不存在: {audio_path}")
                return False
                
            # 生成唯一ID
            audio_id = os.path.basename(audio_path).split('.')[0]
            if audio_id.isdigit() and len(audio_id) > 5:
                # 可能是有效的作品ID，直接使用
                pass
            else:
                # 生成基于文件名的唯一ID
                audio_id = hashlib.md5(os.path.basename(audio_path).encode()).hexdigest()[:16]
                
            self.log_message.emit(f"音频ID: {audio_id}")
            
            # 处理目标路径
            target_path = os.path.join(self.config.audio_path, f"{audio_id}.mp3")
            
            # 检查音频文件是否已处理过
            if os.path.exists(target_path):
                self.log_message.emit(f"该音频已处理过: {target_path}")
                # 直接使用已存在的文件，不尝试复制
            else:
                # 检查音频文件格式，如果不是MP3则转换
                _, ext = os.path.splitext(audio_path)
                if ext.lower() != '.mp3':
                    self.log_message.emit(f"音频文件格式为 {ext}，将转换为MP3格式")
                    
                    # 使用FFmpeg转换音频格式
                    try:
                        cmd = [
                            self.config.ffmpeg_path,
                            '-i', audio_path,
                            '-vn',  # 不处理视频
                            '-acodec', 'libmp3lame',  # 使用mp3编码器
                            '-q:a', '4',  # 质量设置，范围0-9，4是较好的质量
                            '-y',  # 覆盖输出文件
                            target_path
                        ]
                        
                        self.log_message.emit(f"执行FFmpeg命令转换音频...")
                        process = subprocess.Popen(
                            cmd, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                        )
                        
                        # 读取输出信息
                        for line in process.stderr:
                            if "time=" in line and "bitrate=" in line:
                                # 从FFmpeg输出中提取进度信息
                                matches = re.search(r'time=(\d+:\d+:\d+.\d+)', line)
                                if matches:
                                    progress_time = matches.group(1)
                                    self.log_message.emit(f"转换进度: {progress_time}")
                        
                        # 等待进程完成
                        process.wait()
                        
                        # 检查是否成功
                        if process.returncode != 0:
                            self.log_message.emit(f"FFmpeg转换音频失败，返回码: {process.returncode}")
                            return False
                        
                        self.log_message.emit(f"音频转换完成: {target_path}")
                    except Exception as e:
                        self.log_message.emit(f"转换音频过程中出错: {str(e)}")
                        import traceback
                        self.log_message.emit(traceback.format_exc())
                        return False
                else:
                    # 如果已经是MP3格式，尝试复制到目标路径
                    try:
                        import shutil
                        self.log_message.emit(f"复制音频文件到: {target_path}")
                        # 检查源文件和目标文件是否相同
                        if os.path.abspath(audio_path) != os.path.abspath(target_path):
                            shutil.copy2(audio_path, target_path)
                        else:
                            self.log_message.emit("源文件和目标文件相同，无需复制")
                    except PermissionError as e:
                        self.log_message.emit(f"无法访问文件，可能被其他程序占用: {str(e)}")
                        # 如果是权限错误，且源文件和目标文件名不同，尝试替代方案
                        if os.path.abspath(audio_path) != os.path.abspath(target_path):
                            try:
                                self.log_message.emit("尝试使用替代方法复制文件...")
                                with open(audio_path, 'rb') as src:
                                    with open(target_path, 'wb') as dst:
                                        dst.write(src.read())
                                self.log_message.emit("文件复制成功")
                            except Exception as e2:
                                self.log_message.emit(f"替代复制方法也失败: {str(e2)}")
                                # 如果替代方法也失败，但文件已存在，则继续处理
                                if not os.path.exists(target_path):
                                    return False
                        else:
                            self.log_message.emit("源文件和目标文件相同，将直接使用")
                    except Exception as e:
                        self.log_message.emit(f"复制文件过程中出错: {str(e)}")
                        import traceback
                        self.log_message.emit(traceback.format_exc())
                        # 如果文件不存在，则返回失败
                        if not os.path.exists(target_path):
                            return False
            
            # 进行语音识别
            if os.path.exists(target_path):
                self.log_message.emit("开始音频文件语音识别...")
                # 不要在这里提前加载Whisper模型，让speech_recognition方法根据选择的引擎决定
                success = await self.speech_recognition(target_path, audio_id)
                if success:
                    self.log_message.emit("音频处理完成!")
                    return True
                else:
                    self.log_message.emit("语音识别失败")
                    return False
            else:
                self.log_message.emit("错误: 目标音频文件不存在")
                return False
            
        except Exception as e:
            self.log_message.emit(f"处理导入音频过程中出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            return False

    # ... 其他方法保持不变 ... 