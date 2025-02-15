import asyncio
import hashlib
import os
import re
import subprocess
import sys
import aiohttp
import requests
from playwright.async_api import async_playwright


class Config:
    # 文件路径配置
    download_path = "video"  # 视频下载目录
    audio_path = "audio"    # 音频文件目录
    text_path = "text"      # 文案保存目录
    ffmpeg_path = "lib/ffmpeg.exe"  # ffmpeg路径
    
    # 请求头配置
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.douyin.com/',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }


async def get_video_url(page, share_url: str) -> str:
    """获取视频地址"""
    try:
        # 提取短链接
        match = re.search(r'https://v\.douyin\.com/\w+', share_url)
        if not match:
            print("未找到有效的抖音链接")
            return ""
            
        short_url = match.group(0)
        print(f"获取到短链接: {short_url}")
        
        # 访问视频页面
        response = await page.goto(short_url, wait_until='domcontentloaded')
        if not response.ok:
            print(f"页面加载失败: {response.status}")
            return ""
        
        print("等待页面加载...")
        
        # 等待视频元素出现
        selectors = ['.xg-video-container', '.video-player', 'video']
        for selector in selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                print(f"找到视频元素: {selector}")
                break
            except Exception:
                continue
        
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        
        return "success"
        
    except Exception as e:
        print(f"访问视频页面失败: {str(e)}")
        return ""


async def download_video(url, video_id):
    """下载视频并提取音频"""
    try:
        print("开始下载：" + url)
        
        # 下载视频
        video_path = os.path.join(Config.download_path, f"{video_id}.mp4")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=Config.headers) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(video_path, "wb") as f:
                        f.write(content)
                    print(f"视频下载成功：{video_path}")
                    
                    # 提取音频
                    audio_path = os.path.join(Config.audio_path, f"{video_id}.wav")
                    try:
                        subprocess.run([
                            Config.ffmpeg_path,
                            '-i', video_path,
                            '-vn',
                            '-acodec', 'pcm_s16le',
                            '-ar', '16000',
                            '-ac', '1',
                            '-y',
                            audio_path
                        ], check=True, capture_output=True)
                        
                        print(f"音频提取成功：{audio_path}")
                        await asyncio.sleep(1)
                        await speech_recognition(audio_path, video_id)
                        
                    except subprocess.CalledProcessError as e:
                        print(f"音频提取失败：{e.stderr.decode()}")
                else:
                    print(f"下载失败：{response.status}")
                    
    except Exception as e:
        print(f"下载视频时出错: {str(e)}")


async def speech_recognition(audio_file, video_id):
    """使用 SiliconFlow API 进行语音识别"""
    try:
        print("开始识别...")
        
        if not os.path.exists(audio_file):
            print(f"音频文件不存在: {audio_file}")
            return None
            
        url = "https://api.siliconflow.cn/v1/audio/transcriptions"
        headers = {
            "Authorization": "Bearer sk-bwbkhneomtuzuxywnsbjbsftnzousbvmzfoqpwqdsezvnvsw",
        }
        
        files = {
            'file': ('audio.wav', open(audio_file, 'rb'), 'audio/wav'),
            'model': (None, 'FunAudioLLM/SenseVoiceSmall'),
        }
        
        print("正在发送识别请求...")
        response = requests.post(url, headers=headers, files=files)
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('text', '').strip()
            
            if text:
                text_file = os.path.join(Config.text_path, f"{video_id}.txt")
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"识别结果已保存: {text_file}")
                print(f"识别到的文本: {text}")
                return text
            else:
                print("API返回结果为空")
                return None
        else:
            print(f"API请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"语音识别失败: {str(e)}")
        return None


async def get_video_id(share_url: str) -> str:
    """从分享链接中提取视频ID"""
    try:
        if 'v.douyin.com' in share_url:
            match = re.search(r'https://v\.douyin\.com/(\w+)', share_url)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"提取视频ID失败: {str(e)}")
    return None


async def set_interceptor(page, video_id):
    """设置拦截器"""
    processed_urls = []
    video_downloaded = False
    
    async def handle_response(response):
        nonlocal video_downloaded
        try:
            if response.ok and not video_downloaded:
                url = response.url
                # 只处理带音频的视频文件
                if ('douyinvod.com' in url and 
                    'media-video' not in url and 
                    ('media-audio' in url or '.mp4' in url)):
                    url_hash = hashlib.md5(url.encode()).hexdigest()
                    if url_hash not in processed_urls:
                        processed_urls.append(url_hash)
                        print(f"捕获到视频URL: {url}")
                        await download_video(url, video_id)
                        video_downloaded = True
        except Exception as e:
            print(f"处理响应时出错: {str(e)}")
    
    page.on('response', handle_response)


async def main():
    try:
        # 创建必要的目录
        for directory in [Config.download_path, Config.audio_path, Config.text_path]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        print("请输入抖音视频分享链接（每行一个，输入空行结束）：")
        urls = []
        while True:
            url = input().strip()
            if not url:
                break
            urls.append(url)
        
        if not urls:
            print("未输入任何链接")
            return
            
        async with async_playwright() as p:
            print("\n正在连接到Chrome...")
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = context.pages[0]
            
            print("\n开始处理视频...")
            for i, url in enumerate(urls, 1):
                print(f"\n处理第 {i} 个视频：{url}")
                video_id = await get_video_id(url)
                if not video_id:
                    print("无法获取视频ID，跳过")
                    continue
                    
                await set_interceptor(page, video_id)
                await get_video_url(page, url)
                await asyncio.sleep(2)
            
            print("\n所有视频处理完成！")
            
    except Exception as e:
        print(f"错误: {str(e)}")
        return False


if __name__ == "__main__":
    asyncio.run(main()) 