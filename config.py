import os
import json

def find_chrome():
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME')),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
        "/usr/bin/google-chrome"  # Linux
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

class Config:
    def __init__(self):
        self.config_file = "config.json"
        self.load_config()
        
    def load_config(self):
        """加载配置"""
        default_config = {
            "chrome_path": "",  # 默认为空，让用户设置
            "chrome_debug_port": 9222,
            "chrome_user_data_dir": "./chrome-data",
            "douyin_url": "https://www.douyin.com/",
            "download_path": "video",
            "audio_path": "audio",
            "text_path": "text",
            "ffmpeg_path": "lib/ffmpeg.exe"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    default_config.update(saved_config)
        except Exception:
            pass
            
        # 设置属性
        for key, value in default_config.items():
            setattr(self, key, value)
            
    def save_config(self):
        """保存配置"""
        config_data = {
            "chrome_path": self.chrome_path,
            "chrome_debug_port": self.chrome_debug_port,
            "chrome_user_data_dir": self.chrome_user_data_dir,
            "douyin_url": self.douyin_url,
            "download_path": self.download_path,
            "audio_path": self.audio_path,
            "text_path": self.text_path,
            "ffmpeg_path": self.ffmpeg_path
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)

    # 文件路径配置
    download_path = "video"  # 视频下载目录
    audio_path = "audio"    # 音频文件目录
    text_path = "text"      # 文案保存目录
    
    # 其他配置
    ffmpeg_path = "lib/ffmpeg.exe"  # ffmpeg路径
    
    # Chrome配置
    chrome_path = find_chrome()  # 自动查找Chrome路径
    chrome_debug_port = 9222     # 调试端口
    chrome_user_data_dir = "./chrome-data"  # 用户数据目录
    douyin_url = "https://www.douyin.com/"  # 抖音首页URL
    
    # Chrome启动参数
    chrome_args = [
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage"
    ]

    # 请求头配置
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.douyin.com/',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    # 启动脚本路径
    chrome_start_script = "start_chrome.bat" 