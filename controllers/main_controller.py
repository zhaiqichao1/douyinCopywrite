import asyncio
import sys

from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QApplication

from config import Config
from core.downloader import VideoDownloader
from ui.main_window import MainWindow


class DownloadThread(QThread):
    def __init__(self, downloader, urls):
        super().__init__()
        self.downloader = downloader
        self.urls = urls
        
    def run(self):
        """在新线程中运行下载任务"""
        asyncio.run(self.downloader.download_videos(self.urls))

class VideoImportThread(QThread):
    def __init__(self, downloader, video_path):
        super().__init__()
        self.downloader = downloader
        self.video_path = video_path
        
    def run(self):
        """在新线程中运行视频导入和处理任务"""
        asyncio.run(self.downloader.process_imported_video(self.video_path))

class AudioImportThread(QThread):
    def __init__(self, downloader, audio_path):
        super().__init__()
        self.downloader = downloader
        self.audio_path = audio_path
        
    def run(self):
        """在新线程中运行音频导入和处理任务"""
        asyncio.run(self.downloader.import_audio(self.audio_path))

class MainController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.config = Config()  # 先创建配置
        self.window = MainWindow()
        self.window.config = self.config  # 传递配置给窗口
        self.downloader = VideoDownloader(self.config)
        
        # 连接信号
        self.window.start_processing.connect(lambda urls: self.start_processing(urls))
        self.window.process_imported_video.connect(self.process_imported_video)
        self.window.process_imported_audio.connect(self.process_imported_audio)
        self.downloader.log_message.connect(self.window.log)
        self.downloader.progress_updated.connect(self.window.update_progress)
        self.downloader.download_finished.connect(self.window.processing_finished)
        
    def start_processing(self, urls):
        """开始处理视频"""
        self.window.log("开始处理视频...")
        self.download_thread = DownloadThread(self.downloader, urls)
        self.download_thread.start()
        
    def process_imported_video(self, video_path):
        """处理导入的视频"""
        self.window.log(f"处理导入的视频: {video_path}")



        # 创建新线程处理视频导入，避免UI卡死
        self.video_import_thread = VideoImportThread(self.downloader, video_path)
        self.video_import_thread.start()
        
    def process_imported_audio(self, audio_path):
        """处理导入的音频"""
        self.window.log(f"处理导入的音频: {audio_path}")
        
        # 创建新线程处理音频导入，避免UI卡死
        self.audio_import_thread = AudioImportThread(self.downloader, audio_path)
        self.audio_import_thread.start()
        
    def processing_finished(self):
        """处理完成的回调"""
        self.window.processing_finished()
        
    def run(self):
        """运行应用"""
        self.window.show()
        return self.app.exec() 