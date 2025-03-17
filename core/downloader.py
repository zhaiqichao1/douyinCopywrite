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
import traceback
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse, parse_qs, urlencode, quote

import aiohttp
import requests
from PyQt6.QtCore import QObject, pyqtSignal


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
    """抖音视频下载器，使用API接口获取视频数据"""
    
    # 定义信号
    log_message = pyqtSignal(str)  # 日志信号
    progress_updated = pyqtSignal(int)  # 进度信号
    download_finished = pyqtSignal(bool, str)  # 下载完成信号，参数：是否成功、文件路径
    
    # API接口地址
    API_BASE_URL = "http://47.83.189.189:1001"
    FETCH_VIDEO_API = "/api/hybrid/video_data"  # 更新为新的API端点
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.download_path = config.download_path
        self.audio_path = config.audio_path
        self.text_path = config.text_path
        self.download_audio = config.download_audio
        self.download_cover = config.download_cover
        self.headers = config.headers.copy()
        self.timeout = 30  # 请求超时时间
        
        # 确保下载目录存在
        os.makedirs(self.download_path, exist_ok=True)
        os.makedirs(self.audio_path, exist_ok=True)
        os.makedirs(self.text_path, exist_ok=True)
        
        # 创建下载记录文件
        self.download_records_file = os.path.join(os.path.dirname(self.download_path), "downloaded.json")
        self.downloaded_ids = self._load_download_records()
        
        # 更新User-Agent
        self._update_user_agent()
    
    def _update_user_agent(self):
        """随机更新User-Agent"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        self.headers['User-Agent'] = random.choice(user_agents)
    
    async def parse_share_url(self, share_text: str) -> Dict:
        """解析分享链接，提取抖音视频ID
        
        Args:
            share_text: 抖音分享文本或链接
            
        Returns:
            dict: 视频ID和原始URL
        """
        try:
            # 提取链接
            self.log_message.emit(f"解析分享文本...")
            pattern = r'https?://[^\s,，。；;]+(?:v\.douyin\.com|douyin\.com|iesdouyin\.com)[^\s,，。；;]+'
            match = re.search(pattern, share_text)
            
            if not match:
                self.log_message.emit(f"未找到抖音链接")
                return None
                
            url = match.group(0).strip()
            self.log_message.emit(f"提取到链接: {url}")
            
            # 处理短链接
            if "v.douyin.com" in url:
                self.log_message.emit(f"处理短链接...")
                redirect_url = self._get_redirect_url(url)
                if redirect_url:
                    url = redirect_url
                    self.log_message.emit(f"短链接重定向到: {url}")
            
            # 提取视频ID
            video_id = self._extract_video_id(url)
            if not video_id:
                self.log_message.emit(f"无法从链接中提取视频ID: {url}")
                return None
                
            self.log_message.emit(f"视频ID: {video_id}")
            
            # 返回视频ID和原始URL
            return {"aweme_id": video_id, "original_url": url}
            
        except Exception as e:
            self.log_message.emit(f"解析分享链接时出错: {str(e)}")
            self.log_message.emit(traceback.format_exc())
            return None
    
    def _get_redirect_url(self, url: str) -> str:
        """获取短链接的重定向URL
        
        Args:
            url: 短链接URL
            
        Returns:
            str: 重定向后的URL
        """
        try:
            # 添加随机延迟，避免频繁请求
            time.sleep(random.uniform(0.5, 1.5))
            
            response = requests.head(
                url, 
                headers=self.headers,
                allow_redirects=True,
                timeout=self.timeout
            )
            
            return response.url
        except Exception as e:
            self.log_message.emit(f"获取重定向URL时出错: {str(e)}")
            return None
    
    def _extract_video_id(self, url: str) -> str:
        """
        从URL中提取视频ID
        :param url: 视频URL或分享内容
        :return: 视频ID或None
        """
        try:
            # 首先尝试从文本中提取抖音短链接
            short_url = self._extract_douyin_short_url(url)
            if short_url:
                # 如果找到短链接，获取重定向后的URL
                url = self._get_redirect_url(short_url)
                self.log_message.emit(f"重定向到: {url}")
            
            # 方法1：直接从路径中提取
            path_patterns = [
                r'/video/(\d+)',
                r'/share/video/(\d+)'
            ]
            
            for pattern in path_patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            # 方法2：从查询字符串中提取
            query_patterns = [
                r'video_id=(\d+)',
                r'item_ids=(\d+)'
            ]
            
            for pattern in query_patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            # 方法3：解析URL获取查询参数
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            id_params = ['aweme_id', 'item_ids', 'id']
            for param in id_params:
                if param in query_params:
                    return query_params[param][0]
            
            return None
        except Exception as e:
            self.log_message.emit(f"提取视频ID时出错: {str(e)}")
            return None
    
    def _extract_douyin_short_url(self, text: str) -> str:
        """
        从文本中提取抖音短链接
        :param text: 包含抖音链接的文本
        :return: 抖音短链接或空字符串
        """
        try:
            # 匹配抖音短链接的正则表达式
            patterns = [
                r'https?://v\.douyin\.com/\w+/?',
                r'https?://www\.iesdouyin\.com/\w+/?',
                r'https?://www\.douyin\.com/video/\d+'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    # 确保短链接以双斜杠结尾
                    short_url = matches[0]
                    if short_url.endswith('/'):
                        short_url = short_url[:-1] + '//'
                    else:
                        short_url = short_url + '//'
                    return short_url
            
            return ""
        except Exception as e:
            self.log_message.emit(f"提取短链接时出错: {str(e)}")
            return ""
    
    async def _fetch_video_info(self, aweme_id: str) -> Dict:
        """
        从API获取视频信息
        :param aweme_id: 视频ID或分享URL
        :return: 视频信息字典
        """
        try:
            # 首先尝试从文本中提取抖音短链接
            short_url = self._extract_douyin_short_url(aweme_id)
            
            # 构建API请求URL
            if short_url:
                # 如果找到短链接，直接使用它
                encoded_url = quote(short_url)
                api_url = f"{self.API_BASE_URL}{self.FETCH_VIDEO_API}?url={encoded_url}&minimal=false"
                self.log_message.emit(f"使用短链接请求: {short_url}")
            elif aweme_id.startswith("http"):
                # 对URL进行编码
                # 确保URL以双斜杠结尾
                if aweme_id.endswith('/'):
                    aweme_id = aweme_id[:-1] + '//'
                else:
                    aweme_id = aweme_id + '//'
                encoded_url = quote(aweme_id)
                api_url = f"{self.API_BASE_URL}{self.FETCH_VIDEO_API}?url={encoded_url}&minimal=false"
            else:
                # 作为ID处理，需要构建一个抖音URL
                douyin_url = f"https://www.douyin.com/video/{aweme_id}"
                encoded_url = quote(douyin_url)
                api_url = f"{self.API_BASE_URL}{self.FETCH_VIDEO_API}?url={encoded_url}&minimal=false"
            
            # 发送HTTP请求
            timeout = aiohttp.ClientTimeout(total=30)  # 设置30秒超时
            headers = {
                "User-Agent": self.headers['User-Agent']
            }
            
            # 记录请求URL
            self.log_message.emit(f"正在请求视频数据: {api_url}")
            
            # 尝试多次请求，增加稳定性
            for attempt in range(3):  # 最多尝试3次
                try:
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(api_url, headers=headers) as response:
                            if response.status != 200:
                                error_text = await response.text()
                                self.log_message.emit(f"API请求失败 (尝试 {attempt+1}/3): {response.status}, {error_text}")
                                if attempt < 2:  # 如果不是最后一次尝试，则继续
                                    await asyncio.sleep(1)  # 等待一秒后重试
                                    continue
                                return {}
                            
                            # 解析JSON响应
                            result = await response.json()
                            
                            # 检查API响应 - 修改此处，API成功返回code=200
                            if result.get("code") != 200:
                                error_msg = result.get("message", "未知错误")
                                self.log_message.emit(f"API返回错误: {error_msg}")
                                if attempt < 2:  # 如果不是最后一次尝试，则继续
                                    await asyncio.sleep(1)  # 等待一秒后重试
                                    continue
                                return {}
                            
                            if "data" not in result:
                                self.log_message.emit("API返回数据格式错误，缺少data字段")
                                if attempt < 2:  # 如果不是最后一次尝试，则继续
                                    await asyncio.sleep(1)  # 等待一秒后重试
                                    continue
                                return {}
                            
                            self.log_message.emit(f"成功获取视频信息")
                            return result["data"]
                except Exception as e:
                    self.log_message.emit(f"请求异常 (尝试 {attempt+1}/3): {str(e)}")
                    if attempt < 2:  # 如果不是最后一次尝试，则继续
                        await asyncio.sleep(1)  # 等待一秒后重试
                        continue
            
            return {}  # 所有尝试均失败
                    
        except Exception as e:
            self.log_message.emit(f"获取视频信息时出错: {str(e)}")
            return {}
    
    async def download_video(self, share_url: str) -> bool:
        """
        下载单个视频
        :param share_url: 视频分享URL或ID
        :return: 是否成功
        """
        try:
            # 解析分享URL获取视频ID
            self.log_message.emit(f"开始处理: {share_url}")
            
            # 尝试从文本中提取链接
            short_url = self._extract_douyin_short_url(share_url)
            if short_url:
                self.log_message.emit(f"从分享文本中提取到链接: {short_url}")
                share_url = short_url
            
            # 获取视频数据
            video_data = await self._fetch_video_info(share_url)
            
            if not video_data:
                self.log_message.emit("无法获取视频数据，下载失败")
                self.download_finished.emit(False, "")
                return False
                
            # 从返回的数据中提取aweme_id
            aweme_id = video_data.get("aweme_id")
            if not aweme_id:
                self.log_message.emit("无法获取视频ID，下载失败")
                self.download_finished.emit(False, "")
                return False
            
            # 检查是否已下载
            if self._is_downloaded(aweme_id):
                existing_file = self._find_downloaded_file(aweme_id)
                if existing_file:
                    self.log_message.emit(f"视频已下载，跳过: {existing_file}")
                    self.download_finished.emit(True, existing_file)
                    return True
                else:
                    self.log_message.emit(f"视频记录存在但文件未找到，将重新下载")
            
            # 获取视频描述作为文件名
            desc = video_data.get("desc", "未命名")
            author_nickname = video_data.get("author", {}).get("nickname", "未知作者")
            
            # 处理图片集合
            if video_data.get("images"):
                self.log_message.emit("检测到图片集合，开始下载图片...")
                return await self._download_image_collection(video_data, f"{author_nickname}-{desc}")
                
            # 处理视频
            self.log_message.emit("开始下载视频...")
            filename = f"{author_nickname}-{desc}"
            return await self._download_video_file(video_data, filename)
            
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            self.log_message.emit(f"下载视频时出错: {str(e)}\n{error_traceback}")
            self.download_finished.emit(False, "")
            return False
    
    async def _download_image_collection(self, video_data: Dict, collection_name: str) -> bool:
        """
        下载图片集合
        :param video_data: 视频数据
        :param collection_name: 集合名称
        :return: 是否成功
        """
        try:
            # 从API返回中提取图片列表
            images = video_data.get("images", [])
            if not images:
                self.log_message.emit("图片集合数据无效")
                return False
            
            # 创建文件夹
            folder_path = os.path.join(self.config.download_path, collection_name)
            os.makedirs(folder_path, exist_ok=True)
            
            self.log_message.emit(f"开始下载图片集合: {collection_name}, 共{len(images)}张图片")
            
            # 下载每张图片
            success_count = 0
            for i, image_info in enumerate(images):
                # 获取图片URL
                url_list = image_info.get("url_list", [])
                if not url_list:
                    self.log_message.emit(f"图片 {i+1} 没有可用的URL")
                    continue
                
                # 选择最高清晰度
                image_url = url_list[0]
                
                # 下载图片
                img_filename = f"{i+1:03d}.jpg"
                img_path = os.path.join(folder_path, img_filename)
                
                if await self._download_file(image_url, img_path):
                    success_count += 1
                    self.log_message.emit(f"图片 {i+1}/{len(images)} 下载成功")
                else:
                    self.log_message.emit(f"图片 {i+1}/{len(images)} 下载失败")
                
                # 更新进度
                progress = int((i + 1) / len(images) * 100)
                self.progress_updated.emit(progress)
                
                # 适当延迟，避免请求过快
                await asyncio.sleep(0.3)
            
            # 添加到下载记录
            aweme_id = video_data.get("aweme_id")
            if aweme_id:
                self._add_download_record(aweme_id)
                
            self.log_message.emit(f"图片集合下载完成: {success_count}/{len(images)}张")
            
            # 发送下载完成信号
            self.download_finished.emit(True, folder_path)
            return success_count > 0
            
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            self.log_message.emit(f"下载图片集合时出错: {str(e)}\n{error_traceback}")
            self.download_finished.emit(False, "")
            return False
    
    async def _download_video_file(self, video_data: Dict, filename: str) -> bool:
        """
        下载视频文件
        :param video_data: 视频数据
        :param filename: 文件名
        :return: 是否成功
        """
        try:
            # 从API返回中提取视频下载地址
            if "video" not in video_data or not video_data["video"]:
                self.log_message.emit("视频数据中没有video字段")
                return False
                
            video = video_data["video"]
            
            # 优先使用无水印的高清版本
            video_url = None
            
            # 尝试获取play_addr_h264中的高清地址
            if "play_addr_h264" in video and video["play_addr_h264"]:
                url_list = video["play_addr_h264"].get("url_list", [])
                if url_list:
                    # 选择第一个可用的URL
                    video_url = url_list[0]
                    self.log_message.emit(f"使用H264高清地址: {video_url[:100]}...")
            
            # 如果没有找到高清地址，尝试使用play_addr
            if not video_url and "play_addr" in video and video["play_addr"]:
                url_list = video["play_addr"].get("url_list", [])
                if url_list:
                    video_url = url_list[0]
                    self.log_message.emit(f"使用标准清晰度地址: {video_url[:100]}...")
            
            # 如果还是没有，尝试使用download_addr
            if not video_url and "download_addr" in video and video["download_addr"]:
                url_list = video["download_addr"].get("url_list", [])
                if url_list:
                    video_url = url_list[0]
                    self.log_message.emit(f"使用下载地址: {video_url[:100]}...")
            
            if not video_url:
                self.log_message.emit("无法获取视频下载地址")
                return False
            
            # 准备文件路径 - 添加.mp4扩展名
            safe_filename = self._generate_safe_filename(filename)
            filepath = os.path.join(self.config.download_path, f"{safe_filename}.mp4")
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 下载视频
            self.log_message.emit(f"开始下载视频: {os.path.basename(filepath)}")
            video_size = video.get("play_addr_h264", {}).get("data_size") or video.get("play_addr", {}).get("data_size")
            if video_size:
                self.log_message.emit(f"视频大小: {self._format_size(video_size)}")
            
            # 执行下载
            success = await self._download_file(video_url, filepath)
            if not success:
                self.log_message.emit("视频下载失败")
                return False
            
            self.log_message.emit(f"视频下载成功: {filepath}")
            
            # 添加到下载记录
            aweme_id = video_data.get("aweme_id")
            if aweme_id:
                self._add_download_record(aweme_id)
            
            # 下载封面
            if self.config.download_cover:
                try:
                    cover_url = None
                    # 尝试获取静态封面
                    if "cover" in video and video["cover"]:
                        url_list = video["cover"].get("url_list", [])
                        if url_list:
                            cover_url = url_list[0]
                    
                    # 尝试获取动态封面
                    if not cover_url and "dynamic_cover" in video and video["dynamic_cover"]:
                        url_list = video["dynamic_cover"].get("url_list", [])
                        if url_list:
                            cover_url = url_list[0]
                    
                    if cover_url:
                        cover_path = f"{os.path.splitext(filepath)[0]}_cover.jpg"
                        await self._download_file(cover_url, cover_path)
                        self.log_message.emit(f"封面下载成功: {cover_path}")
                except Exception as e:
                    self.log_message.emit(f"下载封面时出错: {str(e)}")
            
            # 提取音频
            if self.config.download_audio:
                audio_file = await self._extract_audio(filepath, aweme_id)
                if audio_file:
                    self.log_message.emit(f"音频提取成功: {audio_file}")
                    
                    # 如果配置了提取文案，尝试识别音频
                    if self.config.extract_text:
                        await self.speech_recognition(audio_file, aweme_id)
                
            # 发送下载完成信号
            self.download_finished.emit(True, filepath)
            return True
            
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            self.log_message.emit(f"处理视频下载时出错: {str(e)}\n{error_traceback}")
            self.download_finished.emit(False, "")
            return False
    
    async def download_videos(self, urls: List[str]) -> None:
        """
        批量下载多个视频
        :param urls: 视频URL列表
        """
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 设置初始状态
            total = len(urls)
            processed = 0
            successful = 0
            failed = 0
            skipped = 0
            
            self.log_message.emit(f"开始处理 {total} 个视频链接...")
            
            # 遍历链接列表
            for i, url in enumerate(urls):
                # 更新进度
                progress = int((processed / total) * 100)
                self.progress_updated.emit(progress)
                
                # 添加延迟，避免请求过快
                if i > 0:
                    delay = random.uniform(1, 3)
                    self.log_message.emit(f"等待 {delay:.1f} 秒后处理下一个链接...")
                    await asyncio.sleep(delay)
                
                self.log_message.emit(f"处理第 {i+1}/{total} 个链接: {url}")
                
                try:
                    success = await self.download_video(url)
                    if success:
                        successful += 1
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
                    self.log_message.emit(f"处理链接时出错: {str(e)}")
            
            # 计算耗时
            end_time = time.time()
            duration = end_time - start_time
            minutes = int(duration / 60)
            seconds = int(duration % 60)
            
            # 显示最终结果
            self.log_message.emit("=" * 50)
            self.log_message.emit(f"下载完成! 共处理 {total} 个链接，用时 {minutes}分{seconds}秒")
            self.log_message.emit(f"成功: {successful}, 失败: {failed}, 跳过: {skipped}")
            self.log_message.emit("=" * 50)
            
            # 设置进度为100%
            self.progress_updated.emit(100)
            
            # 发送下载完成信号
            self.download_finished.emit(True, "")
            
        except Exception as e:
            self.log_message.emit(f"批量下载过程中出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            self.download_finished.emit(False, "")

    async def _download_file(self, url: str, filepath: str) -> bool:
        """
        下载文件到指定路径
        :param url: 文件URL
        :param filepath: 保存路径
        :return: 是否成功
        """
        try:
            # 创建目录
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 如果文件已存在，跳过下载
            if os.path.exists(filepath):
                self.log_message.emit(f"文件已存在: {filepath}")
                return True
            
            # 设置超时
            timeout = aiohttp.ClientTimeout(total=60)
            
            # 下载文件
            self.log_message.emit(f"开始下载: {url[:100]}...")
            
            # 使用aiohttp下载
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status != 200:
                        self.log_message.emit(f"下载失败，HTTP状态码: {response.status}")
                        return False
                    
                    # 获取文件大小
                    total_size = int(response.headers.get('content-length', 0))
                    if total_size:
                        self.log_message.emit(f"文件大小: {self._format_size(total_size)}")
                    
                    # 下载文件
                    with open(filepath, 'wb') as f:
                        downloaded = 0
                        async for chunk in response.content.iter_chunked(1024*1024):  # 1MB chunks
                            f.write(chunk)
                            downloaded += len(chunk)
                        
                    # 更新进度
                    if total_size > 0:
                        progress = int((downloaded / total_size) * 100)
                        self.progress_updated.emit(min(progress, 99))  # 最大99%，留1%给后续处理
            
            # 验证文件是否已下载
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                self.log_message.emit(f"下载完成: {filepath}")
                return True
            else:
                self.log_message.emit(f"下载失败: 文件不存在或大小为0")
                return False
            
        except Exception as e:
            self.log_message.emit(f"下载文件时出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            
            # 如果文件下载了一部分，删除它
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    self.log_message.emit(f"已删除不完整的文件: {filepath}")
                except:
                    pass
            
            return False

    def _is_downloaded(self, aweme_id: str) -> bool:
        """
        检查视频是否已下载
        :param aweme_id: 视频ID
        :return: 是否已下载
        """
        return aweme_id in self.downloaded_ids
    
    def _find_downloaded_file(self, aweme_id: str) -> str:
        """
        查找已下载的视频文件
        :param aweme_id: 视频ID
        :return: 文件路径，如果未找到返回空字符串
        """
        # 查找对应ID的视频文件
        for filename in os.listdir(self.download_path):
            if aweme_id in filename and os.path.isfile(os.path.join(self.download_path, filename)):
                return os.path.join(self.download_path, filename)
        
        # 查找是否有对应ID的文件夹（图片集合）
        for dirname in os.listdir(self.download_path):
            if aweme_id in dirname and os.path.isdir(os.path.join(self.download_path, dirname)):
                return os.path.join(self.download_path, dirname)
        
        return ""
    
    def _add_download_record(self, aweme_id: str):
        """
        添加下载记录
        :param aweme_id: 视频ID
        """
        # 添加到内存中的集合
        self.downloaded_ids.add(aweme_id)
        
        # 保存到文件
        try:
            with open(self.download_records_file, "w", encoding="utf-8") as f:
                json.dump(list(self.downloaded_ids), f)
        except Exception as e:
            self.log_message.emit(f"保存下载记录时出错: {str(e)}")
    
    def _load_download_records(self) -> Set[str]:
        """
        加载下载记录
        :return: 已下载视频ID集合
        """
        try:
            if os.path.exists(self.download_records_file):
                with open(self.download_records_file, "r", encoding="utf-8") as f:
                    return set(json.load(f))
            return set()
        except Exception as e:
            self.log_message.emit(f"加载下载记录时出错: {str(e)}")
            return set()
    
    def _generate_safe_filename(self, name: str) -> str:
        """
        生成安全的文件名
        :param name: 原始文件名
        :return: 安全的文件名
        """
        # 替换不安全字符
        safe_name = re.sub(r'[\\/*?:"<>|]', "_", name)
        
        # 移除开头和结尾的空格和点
        safe_name = safe_name.strip(" .")
        
        # 限制长度 (Windows路径长度限制)
        if len(safe_name) > 50:
            safe_name = safe_name[:47] + "..."
            
        # 如果最终为空，使用默认名称
        if not safe_name:
            safe_name = "unnamed"
        
        return safe_name
        
    def _format_size(self, size_bytes: int) -> str:
        """
        格式化文件大小
        :param size_bytes: 字节大小
        :return: 格式化后的字符串
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    async def _extract_audio(self, video_path: str, aweme_id: str) -> Optional[str]:
        """
        从视频中提取音频
        :param video_path: 视频路径
        :param aweme_id: 视频ID
        :return: 音频文件路径
        """
        try:
            # 检查ffmpeg是否可用
            if not os.path.exists(self.config.ffmpeg_path):
                self.log_message.emit(f"错误: ffmpeg不存在，无法提取音频: {self.config.ffmpeg_path}")
                return None
            
            # 生成音频文件名
            audio_filename = f"{os.path.splitext(os.path.basename(video_path))[0]}.mp3"
            audio_path = os.path.join(self.config.audio_path, audio_filename)
            
            # 检查是否已存在
            if os.path.exists(audio_path):
                self.log_message.emit(f"音频文件已存在: {audio_path}")
                return audio_path
            
            # 创建目录
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)
            
            # 调用ffmpeg提取音频
            self.log_message.emit(f"从视频提取音频: {video_path}")
            
            cmd = [
                self.config.ffmpeg_path,
                "-i", video_path,
                "-vn",  # 不处理视频
                "-sn",  # 不处理字幕
                "-dn",  # 不处理数据
                "-c:a", "libmp3lame",  # 使用MP3编码器
                "-q:a", "4",  # 音质设置 (0-9, 0最好)
                "-y",  # 覆盖已有文件
                audio_path
            ]
            
            # 执行命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await process.communicate()
            
            # 检查结果
            if process.returncode != 0:
                error = stderr.decode('utf-8', errors='ignore')
                self.log_message.emit(f"提取音频失败: {error}")
                return None
            
            # 验证文件是否成功创建
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                self.log_message.emit(f"音频提取成功: {audio_path}")
                return audio_path
            else:
                self.log_message.emit("音频提取失败: 文件未创建或大小为0")
                return None
                
        except Exception as e:
            self.log_message.emit(f"提取音频时出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            return None

    async def speech_recognition(self, audio_file, video_id):
        """
        对音频文件进行语音识别
        :param audio_file: 音频文件路径
        :param video_id: 视频ID
        :return: 是否成功
        """
        try:
            # 检查音频文件是否存在
            if not os.path.exists(audio_file):
                self.log_message.emit(f"错误: 音频文件不存在: {audio_file}")
                return False
                
            # 生成文本文件名
            text_filename = f"{os.path.splitext(os.path.basename(audio_file))[0]}_文案.txt"
            text_path = os.path.join(self.config.text_path, text_filename)
            
            # 检查是否已存在
            if os.path.exists(text_path):
                self.log_message.emit(f"文案文件已存在: {text_path}")
                with open(text_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                if text_content.strip():
                    self.log_message.emit(f"已有文案内容: {text_content[:100]}...")
                    return True
                else:
                    self.log_message.emit("文案文件存在但内容为空，将重新识别")
            
            # 创建目录
            os.makedirs(os.path.dirname(text_path), exist_ok=True)
            
            # 初始化识别器
            recognizer = SpeechRecognizer(self.config)
            
            # 执行识别
            self.log_message.emit(f"开始识别音频: {audio_file}")
            self.progress_updated.emit(10)  # 设置初始进度
            
            # 使用run_in_executor在线程池中运行CPU密集型任务
            loop = asyncio.get_event_loop()
            text_result = await loop.run_in_executor(
                None, 
                recognizer.recognize,
                audio_file
            )
            
            self.progress_updated.emit(90)  # 更新进度
            
            # 检查结果
            if text_result:
                # 保存到文件
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(text_result)
                
                self.log_message.emit(f"文案识别成功: {text_path}")
                self.log_message.emit(f"文案内容: {text_result[:100]}...")
                self.progress_updated.emit(100)  # 完成
                return True
            else:
                self.log_message.emit("文案识别失败: 未能识别出文字")
                self.progress_updated.emit(0)  # 重置进度
                return False
            
        except Exception as e:
            self.log_message.emit(f"语音识别时出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            self.progress_updated.emit(0)  # 重置进度
            return False

    async def process_imported_video(self, video_path: str) -> bool:
        """
        处理导入的视频，提取音频并识别文案
        :param video_path: 视频文件路径
        :return: 是否成功
        """
        try:
            # 生成视频ID (使用文件名的哈希值)
            video_id = hashlib.md5(os.path.basename(video_path).encode()).hexdigest()
            
            self.log_message.emit(f"开始处理导入的视频: {video_path}")
            
            # 检查视频文件是否存在
            if not os.path.exists(video_path):
                self.log_message.emit(f"错误: 视频文件不存在: {video_path}")
                return False
            
            # 提取音频
            audio_file = await self._extract_audio(video_path, video_id)
            if audio_file:
                self.log_message.emit(f"音频提取成功: {audio_file}")
                
                # 进行语音识别
                if self.config.extract_text:
                    success = await self.speech_recognition(audio_file, video_id)
                    if success:
                        self.log_message.emit("视频处理完成!")
                        self.download_finished.emit(True, audio_file)
                    else:
                        self.log_message.emit("语音识别失败")
                        self.download_finished.emit(False, "")
                        return False
                else:
                    self.log_message.emit("视频处理完成 (未启用文案提取)")
                    self.download_finished.emit(True, audio_file)
                    return True
            else:
                self.log_message.emit("音频提取失败")
                self.download_finished.emit(False, "")
                return False
                
        except Exception as e:
            self.log_message.emit(f"处理导入视频时出错: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc())
            self.download_finished.emit(False, "")
            return False
            
    async def import_audio(self, audio_path: str) -> bool:
        """
        导入音频文件并识别文案
        :param audio_path: 音频文件路径
        :return: 是否成功
        """
        try:
            # 生成音频ID (使用文件名的哈希值)
            audio_id = hashlib.md5(os.path.basename(audio_path).encode()).hexdigest()
            
            self.log_message.emit(f"开始处理导入的音频: {audio_path}")
            
            # 检查音频文件是否存在
            if not os.path.exists(audio_path):
                self.log_message.emit(f"错误: 音频文件不存在: {audio_path}")
                return False
                
            # 检查文件格式，如果不是MP3，尝试转换
            ext = os.path.splitext(audio_path)[1].lower()
            target_path = os.path.join(self.config.audio_path, f"{os.path.splitext(os.path.basename(audio_path))[0]}.mp3")
            
            if ext != '.mp3':
                # 使用ffmpeg转换
                if os.path.exists(self.config.ffmpeg_path):
                    cmd = [
                        self.config.ffmpeg_path,
                        "-i", audio_path,
                        "-vn",  # 不处理视频
                        "-c:a", "libmp3lame",  # 使用MP3编码器
                        "-q:a", "4",  # 音质设置 (0-9, 0最好)
                        "-y",  # 覆盖已有文件
                        target_path
                    ]
                    
                    # 执行命令
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    _, stderr = await process.communicate()
                    
                    # 检查结果
                    if process.returncode != 0:
                        error = stderr.decode('utf-8', errors='ignore')
                        self.log_message.emit(f"音频转换失败: {error}")
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