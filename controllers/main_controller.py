import asyncio
import sys
import traceback
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMessageBox

from config import Config
from core.downloader import VideoDownloader
from ui.main_window import MainWindow


class DownloadThread(QThread):
    error_occurred = pyqtSignal(str)  # 添加错误信号
    
    def __init__(self, downloader, urls):
        super().__init__()
        self.downloader = downloader
        self.urls = urls
        
    def run(self):
        """在新线程中运行下载任务"""
        try:
            asyncio.run(self.downloader.download_videos(self.urls))
        except Exception as e:
            # 捕获所有异常并发送到主线程
            error_msg = f"下载过程中发生错误: {str(e)}\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)

class VideoImportThread(QThread):
    error_occurred = pyqtSignal(str)  # 添加错误信号
    
    def __init__(self, downloader, video_path):
        super().__init__()
        self.downloader = downloader
        self.video_path = video_path
        
    def run(self):
        """在新线程中运行视频导入和处理任务"""
        try:
            asyncio.run(self.downloader.process_imported_video(self.video_path))
        except Exception as e:
            error_msg = f"视频处理过程中发生错误: {str(e)}\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)

class AudioImportThread(QThread):
    error_occurred = pyqtSignal(str)  # 添加错误信号
    
    def __init__(self, downloader, audio_path):
        super().__init__()
        self.downloader = downloader
        self.audio_path = audio_path
        
    def run(self):
        """在新线程中运行音频导入和处理任务"""
        try:
            asyncio.run(self.downloader.import_audio(self.audio_path))
        except Exception as e:
            error_msg = f"音频处理过程中发生错误: {str(e)}\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)

class MainController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.config = Config()  # 先创建配置
        self.window = MainWindow()
        self.window.config = self.config  # 传递配置给窗口
        self.downloader = VideoDownloader(self.config)
        
        # 连接信号
        self.window.start_processing.connect(self.start_processing)
        self.window.process_imported_video.connect(self.process_imported_video)
        self.window.process_imported_audio.connect(self.process_imported_audio)
        self.downloader.log_message.connect(self.window.log)
        self.downloader.progress_updated.connect(self.window.update_progress)
        self.downloader.download_finished.connect(self.processing_finished)
        
    def start_processing(self, urls):
        """开始处理视频"""
        self.window.log(f"开始处理 {len(urls)} 个链接...")
        self.window.log(f"正在使用远程API服务器处理视频下载请求...")
        
        # 更新用户界面状态
        try:
            self.window.processing = True
            self.window.start_button.setEnabled(False)
            self.window.start_button.setText("处理中...")
            self.window.progress_bar.setValue(0)
        except Exception as e:
            self.window.log(f"更新UI状态时出错: {str(e)}")
        
        # 创建并启动下载线程
        self.download_thread = DownloadThread(self.downloader, urls)
        self.download_thread.error_occurred.connect(self.handle_error)
        self.download_thread.start()
        
    def process_imported_video(self, video_path):
        """处理导入的视频"""
        self.window.log(f"处理导入的视频: {video_path}")
        
        # 创建新线程处理视频导入
        self.video_import_thread = VideoImportThread(self.downloader, video_path)
        self.video_import_thread.error_occurred.connect(self.handle_error)
        self.video_import_thread.start()
        
    def process_imported_audio(self, audio_path):
        """处理导入的音频"""
        self.window.log(f"处理导入的音频: {audio_path}")
        
        # 创建新线程处理音频导入
        self.audio_import_thread = AudioImportThread(self.downloader, audio_path)
        self.audio_import_thread.error_occurred.connect(self.handle_error)
        self.audio_import_thread.start()
    
    def handle_error(self, error_message):
        """处理线程中的错误"""
        # 记录错误日志
        self.window.log(f"错误: {error_message.split('Traceback')[0]}")
        
        # 尝试恢复UI状态
        try:
            self.window.processing = False
            self.window.start_button.setEnabled(True)
            self.window.start_button.setText("开始下载")
            self.window.status_label.setText("出错")
        except Exception as e:
            print(f"恢复UI状态时出错: {str(e)}")
        
        # 显示错误对话框
        QMessageBox.critical(self.window, "处理错误", 
                            f"处理过程中发生错误:\n{error_message.split('Traceback')[0]}\n\n详细信息已记录到日志。")
        
    def processing_finished(self, success, file_path):
        """处理完成的回调"""
        # 恢复UI状态
        try:
            self.window.processing = False
            self.window.start_button.setEnabled(True)
            self.window.start_button.setText("开始下载")
        except Exception as e:
            print(f"更新UI状态时出错: {str(e)}")
        
        # 处理完成消息
        if success:
            if file_path:
                self.window.log(f"处理完成: {file_path}")
            else:
                self.window.log("所有链接处理完成")
            self.window.processing_finished()
        else:
            self.window.log("处理失败，请检查日志或尝试其他链接")
        
    def run(self):
        """运行应用"""
        self.window.show()
        return self.app.exec() 