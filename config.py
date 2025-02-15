import os

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