from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QTextEdit, QPushButton, QProgressBar, QMessageBox,
                           QFileDialog, QDialog, QLabel, QLineEdit)
from PyQt6.QtCore import pyqtSignal
import os
import shutil

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('设置')
        layout = QVBoxLayout(self)
        
        # Chrome路径设置
        chrome_layout = QHBoxLayout()
        chrome_layout.addWidget(QLabel('Chrome路径:'))
        self.chrome_path = QLineEdit(self.config.chrome_path)
        chrome_layout.addWidget(self.chrome_path)
        browse_btn = QPushButton('浏览...')
        browse_btn.clicked.connect(self.browse_chrome)
        chrome_layout.addWidget(browse_btn)
        layout.addLayout(chrome_layout)
        
        # 确定和取消按钮
        buttons = QHBoxLayout()
        ok_btn = QPushButton('确定')
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
    def browse_chrome(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择Chrome浏览器",
            "",
            "Chrome (chrome.exe)"
        )
        if path:
            self.chrome_path.setText(path)
            
    def get_settings(self):
        return {
            'chrome_path': self.chrome_path.text()
        }

class MainWindow(QMainWindow):
    # 定义信号
    start_processing = pyqtSignal(list)  # 开始处理信号
    start_chrome = pyqtSignal()  # 启动Chrome信号
    process_imported_video = pyqtSignal(str)  # 处理导入的视频信号
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle('抖音视频文案提取')
        self.setGeometry(100, 100, 800, 600)
        
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 顶部按钮区域
        top_buttons = QHBoxLayout()
        
        # 启动Chrome按钮
        self.chrome_button = QPushButton('启动Chrome')
        self.chrome_button.clicked.connect(self.on_chrome_clicked)
        top_buttons.addWidget(self.chrome_button)
        
        # 开始按钮
        self.start_button = QPushButton('开始处理')
        self.start_button.clicked.connect(self.on_start_clicked)
        self.start_button.setEnabled(False)  # 初始禁用
        top_buttons.addWidget(self.start_button)
        
        # 在顶部按钮区域添加设置按钮
        self.settings_button = QPushButton('设置')
        self.settings_button.clicked.connect(self.show_settings)
        top_buttons.addWidget(self.settings_button)
        
        layout.addLayout(top_buttons)
        
        # 链接输入框
        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText('请输入抖音视频链接，每行一个...')
        layout.addWidget(self.url_input)
        
        # 进度条
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # 日志显示框
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        
        # 底部按钮区域
        bottom_buttons = QHBoxLayout()
        
        # 查看视频按钮
        self.view_video_button = QPushButton('查看视频')
        self.view_video_button.clicked.connect(lambda: self.open_folder('video'))
        bottom_buttons.addWidget(self.view_video_button)
        
        # 查看音频按钮
        self.view_audio_button = QPushButton('查看音频')
        self.view_audio_button.clicked.connect(lambda: self.open_folder('audio'))
        bottom_buttons.addWidget(self.view_audio_button)
        
        # 查看文案按钮
        self.view_text_button = QPushButton('查看文案')
        self.view_text_button.clicked.connect(lambda: self.open_folder('text'))
        bottom_buttons.addWidget(self.view_text_button)
        
        # 导入视频按钮
        self.import_video_button = QPushButton('导入视频')
        self.import_video_button.clicked.connect(self.import_videos)
        bottom_buttons.addWidget(self.import_video_button)
        
        layout.addLayout(bottom_buttons)
        
    def open_folder(self, folder_type):
        """打开指定类型的文件夹"""
        folder_map = {
            'video': 'video',
            'audio': 'audio',
            'text': 'text'
        }
        
        folder = folder_map.get(folder_type)
        if folder and os.path.exists(folder):
            # 在Windows上使用explorer打开文件夹
            os.startfile(os.path.abspath(folder))
        else:
            QMessageBox.warning(self, "提示", f"文件夹 {folder} 不存在！")
            
    def on_chrome_clicked(self):
        """Chrome按钮点击事件"""
        self.chrome_button.setEnabled(False)
        self.start_chrome.emit()
        
    def on_start_clicked(self):
        """开始按钮点击事件"""
        urls = self.url_input.toPlainText().strip().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        if urls:
            self.start_processing.emit(urls)
            self.start_button.setEnabled(False)
            self.chrome_button.setEnabled(False)
        else:
            QMessageBox.warning(self, "提示", "请输入视频链接！")
            
    def log(self, message):
        """添加日志"""
        self.log_output.append(message)
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def chrome_started(self):
        """Chrome启动成功"""
        self.start_button.setEnabled(True)
        self.log("Chrome启动成功！")
        
    def chrome_failed(self, error):
        """Chrome启动失败"""
        self.chrome_button.setEnabled(True)
        self.log(f"Chrome启动失败：{error}")
        QMessageBox.critical(self, "错误", f"Chrome启动失败：{error}")
        
    def processing_finished(self):
        """处理完成"""
        self.start_button.setEnabled(True)
        self.chrome_button.setEnabled(True)
        self.progress_bar.setValue(100)
        
    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            self.config.chrome_path = settings['chrome_path']
            self.config.save_config()

    def import_videos(self):
        """导入视频文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4)"
        )
        if files:
            for file in files:
                # 复制视频到video目录
                video_name = os.path.basename(file)
                video_id = os.path.splitext(video_name)[0]  # 使用文件名作为video_id
                target_path = os.path.join(self.config.download_path, f"{video_id}.mp4")
                
                # 确保video目录存在
                if not os.path.exists(self.config.download_path):
                    os.makedirs(self.config.download_path)
                    
                # 复制文件
                shutil.copy2(file, target_path)
                self.log(f"导入视频: {video_name}")
                
                # 发送处理信号
                self.process_imported_video.emit(target_path) 