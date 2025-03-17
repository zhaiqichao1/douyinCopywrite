import os
import json
from pathlib import Path

class Config:
    def __init__(self):
        # 语音识别引擎配置
        self.speech_recognition_engine = "whisper"  # 默认引擎
        self.speech_recognition_config = {
            "whisper": {
                "model": "base",  # 可选 tiny/base/small/medium/large
                "language": "zh"
            },
            "google": {
                "language": "zh-CN"
            },
            "baidu": {
                "app_id": "",
                "api_key": "",
                "secret_key": ""
            },
            "ali": {
                "access_key_id": "",
                "access_key_secret": ""
            },
            "xunfei": {
                "app_id": "",
                "api_key": "",
                "api_secret": ""
            },
            "paddlespeech": {
                "model": "conformer_wenetspeech"
            }
        }
        
        self.config_file = "config.json"
        self.load_config()
        
    def load_config(self):
        """加载配置"""
        default_config = {
            # 下载设置
            "download_path": "video",        # 视频下载目录
            "audio_path": "audio",           # 音频保存目录
            "text_path": "text",             # 文案保存目录
            "ffmpeg_path": "lib/ffmpeg.exe", # ffmpeg路径
            
            # 功能开关
            "download_audio": True,          # 是否同时提取音频
            "download_cover": True,          # 是否同时下载封面
            "extract_text": True,            # 是否提取文案
            
            # Cookie设置
            "douyin_cookie": "",             # 抖音cookie
            
            # API设置
            "use_api": True,                 # 是否使用API获取数据
            "api_timeout": 30,               # API超时时间(秒)
            "max_retries": 3,                # 最大重试次数

            # 语音识别引擎配置
            "speech_recognition_engine": self.speech_recognition_engine,
            "speech_recognition_config": self.speech_recognition_config
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    # 更新默认配置，但保留当前实例的默认值
                    for key, value in saved_config.items():
                        if key == "speech_recognition_config":
                            # 深度更新配置
                            for engine, config in value.items():
                                if engine in self.speech_recognition_config:
                                    self.speech_recognition_config[engine].update(config)
                        else:
                            default_config[key] = value
        except Exception as e:
            print(f"加载配置出错: {str(e)}")
            
        # 设置属性
        for key, value in default_config.items():
            setattr(self, key, value)
        
        # 确保目录存在
        for path_name in ["download_path", "audio_path", "text_path"]:
            path = getattr(self, path_name)
            os.makedirs(path, exist_ok=True)
            
    def save_config(self):
        """保存配置"""
        config_data = {
            "download_path": self.download_path,
            "audio_path": self.audio_path,
            "text_path": self.text_path,
            "ffmpeg_path": self.ffmpeg_path,
            "download_audio": self.download_audio,
            "download_cover": self.download_cover,
            "extract_text": self.extract_text,
            "douyin_cookie": self.douyin_cookie,  # 添加Cookie配置
            "use_api": self.use_api,
            "api_timeout": self.api_timeout,
            "max_retries": self.max_retries,
            "speech_recognition_engine": self.speech_recognition_engine,
            "speech_recognition_config": self.speech_recognition_config
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        
    # 请求头配置
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Referer': 'https://www.douyin.com/',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    }

    # 文件路径配置
    download_path = "video"  # 视频下载目录
    audio_path = "audio"    # 音频文件目录
    text_path = "text"      # 文案保存目录
    
    # 其他配置
    ffmpeg_path = "lib/ffmpeg.exe"  # ffmpeg路径 