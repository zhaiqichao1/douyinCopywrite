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
    chrome_debug_port = 9222  # 改用9222端口
    chrome_user_data_dir = "./chrome-data"  # 用户数据目录

    # 请求头配置
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Referer': 'https://www.douyin.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'Cookie': ' '.join([
            '__ac_nonce=067b08e0900bc54564e56',
            '__ac_signature=_02B4Z6wo00f017mtlrgAAIDDgb6mPvFfyB-5jZIAAInk9c',
            'ttwid=1%7CAjaI3SyYymuXykwpAa_ttojVoZDDyNH2TUqwEQvj72w%7C1739623945%7C46472907636f283e5ee26462458e296f8ae6c6b0ccda21cf4dc8c9de57f1d1bb',
            'sessionid=0bf8978843ce1b909f0073273bfe59f0',
            'sessionid_ss=0bf8978843ce1b909f0073273bfe59f0',
            'sid_tt=0bf8978843ce1b909f0073273bfe59f0',
            'uid_tt=0699716b932c9d6e3215b8b19c70be43',
            'uid_tt_ss=0699716b932c9d6e3215b8b19c70be43',
            'sid_ucp_v1=1.0.0-KGNhZTU0OGQ1ZGYyMzc4MzVhZTVhZDdkY2FlNTU1YzliMjU4Y2Q3YzIKIQitvdCK9PWnARCtnMK9BhjvMSAMMO2r0P8FOAdA9AdIBBoCbGYiIDBiZjg5Nzg4NDNjZTFiOTA5ZjAwNzMyNzNiZmU1OWYw',
            'ssid_ucp_v1=1.0.0-KGNhZTU0OGQ1ZGYyMzc4MzVhZTVhZDdkY2FlNTU1YzliMjU4Y2Q3YzIKIQitvdCK9PWnARCtnMK9BhjvMSAMMO2r0P8FOAdA9AdIBBoCbGYiIDBiZjg5Nzg4NDNjZTFiOTA5ZjAwNzMyNzNiZmU1OWYw'
        ])
    } 