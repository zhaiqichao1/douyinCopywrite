import sys
import asyncio
import subprocess
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSlot
from ui.main_window import MainWindow
from core.downloader import VideoDownloader
from config import Config

class ChromeThread(QThread):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self._result = None
        
    def run(self):
        """启动Chrome"""
        try:
            # 使用start_chrome.bat启动Chrome
            subprocess.run(['start_chrome.bat'], 
                         shell=True, 
                         check=True)
            self.sleep(2)  # 等待Chrome启动
            self._result = True
        except Exception as e:
            self._result = str(e)
            
    def get_result(self):
        """获取运行结果"""
        return self._result

class DownloadThread(QThread):
    def __init__(self, downloader, urls):
        super().__init__()
        self.downloader = downloader
        self.urls = urls
        
    def run(self):
        """在新线程中运行下载任务"""
        asyncio.run(self.downloader.download_videos(self.urls))

class MainController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.config = Config()  # 先创建配置
        self.window = MainWindow()
        self.window.config = self.config  # 传递配置给窗口
        self.downloader = VideoDownloader(self.config)
        
        # 连接信号
        self.window.start_chrome.connect(self.start_chrome)
        self.window.start_processing.connect(lambda urls: self.start_processing(urls))
        self.downloader.log_message.connect(self.window.log)
        self.downloader.progress_updated.connect(self.window.update_progress)
        self.downloader.download_finished.connect(self.window.processing_finished)
        self.window.process_imported_video.connect(self.process_imported_video)
        
    def start_chrome(self):
        """启动Chrome"""
        if not self.config.chrome_path:
            self.window.chrome_failed("请先在设置中配置Chrome浏览器路径")
            return
            
        if not os.path.exists(self.config.chrome_path):
            self.window.chrome_failed("Chrome路径无效，请检查设置")
            return
            
        # 修改start_chrome.bat的内容
        with open('start_chrome.bat', 'w', encoding='utf-8') as f:
            f.write(f'@echo off\nstart "" "{self.config.chrome_path}" --remote-debugging-port={self.config.chrome_debug_port} --user-data-dir={self.config.chrome_user_data_dir} {self.config.douyin_url}')
        
        self.chrome_thread = ChromeThread(self.config)
        self.chrome_thread.finished.connect(self.chrome_finished)
        self.chrome_thread.start()
        
    def chrome_finished(self):
        """Chrome启动完成回调"""
        result = self.chrome_thread.get_result()
        if result is True:
            self.window.chrome_started()
        else:
            self.window.chrome_failed(result)
        
    def start_processing(self, urls):
        """开始处理视频"""
        self.download_thread = DownloadThread(self.downloader, urls)
        self.download_thread.start()
        
    def process_imported_video(self, video_path):
        """处理导入的视频"""
        async def process():
            await self.downloader.process_imported_video(video_path)
            
        self.import_thread = QThread()
        self.import_thread.run = lambda: asyncio.run(process())
        self.import_thread.start()
        
    def run(self):
        """运行应用"""
        self.window.show()
        return self.app.exec() 