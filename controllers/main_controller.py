import sys
import asyncio
import subprocess
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
        self.window = MainWindow()
        self.config = Config()
        self.downloader = VideoDownloader(self.config)
        
        # 连接信号
        self.window.start_chrome.connect(self.start_chrome)
        self.window.start_processing.connect(lambda urls: self.start_processing(urls))
        self.downloader.log_message.connect(self.window.log)
        self.downloader.progress_updated.connect(self.window.update_progress)
        self.downloader.download_finished.connect(self.window.processing_finished)
        
    def start_chrome(self):
        """启动Chrome"""
        if not self.config.chrome_path:
            self.window.chrome_failed("未找到Chrome浏览器，请确保已安装Chrome")
            return
            
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
        
    def run(self):
        """运行应用"""
        self.window.show()
        return self.app.exec() 