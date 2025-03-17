import os

from PyQt6.QtCore import pyqtSignal, Qt, QMetaObject, Q_ARG
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QProgressBar, QMessageBox,
                             QFileDialog, QDialog, QLabel, QLineEdit, QCheckBox,
                             QGroupBox, QComboBox)


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('设置')
        self.setMinimumWidth(600)  # 增加宽度以适应Cookie长文本
        layout = QVBoxLayout(self)
        
        # 下载设置组
        download_group = QGroupBox("下载设置")
        download_layout = QVBoxLayout(download_group)
        
        # 下载路径设置
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel('下载目录:'))
        self.download_path = QLineEdit(self.config.download_path)
        path_layout.addWidget(self.download_path)
        browse_btn = QPushButton('浏览...')
        browse_btn.clicked.connect(lambda: self.browse_folder(self.download_path))
        path_layout.addWidget(browse_btn)
        download_layout.addLayout(path_layout)
        
        # 音频路径设置
        audio_layout = QHBoxLayout()
        audio_layout.addWidget(QLabel('音频目录:'))
        self.audio_path = QLineEdit(self.config.audio_path)
        audio_layout.addWidget(self.audio_path)
        browse_audio_btn = QPushButton('浏览...')
        browse_audio_btn.clicked.connect(lambda: self.browse_folder(self.audio_path))
        audio_layout.addWidget(browse_audio_btn)
        download_layout.addLayout(audio_layout)
        
        # 文案路径设置
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel('文案目录:'))
        self.text_path = QLineEdit(self.config.text_path)
        text_layout.addWidget(self.text_path)
        browse_text_btn = QPushButton('浏览...')
        browse_text_btn.clicked.connect(lambda: self.browse_folder(self.text_path))
        text_layout.addWidget(browse_text_btn)
        download_layout.addLayout(text_layout)
        
        # FFmpeg路径设置
        ffmpeg_layout = QHBoxLayout()
        ffmpeg_layout.addWidget(QLabel('FFmpeg路径:'))
        self.ffmpeg_path = QLineEdit(self.config.ffmpeg_path)
        ffmpeg_layout.addWidget(self.ffmpeg_path)
        browse_ffmpeg_btn = QPushButton('浏览...')
        browse_ffmpeg_btn.clicked.connect(lambda: self.browse_file(self.ffmpeg_path, "FFmpeg (ffmpeg.exe)"))
        ffmpeg_layout.addWidget(browse_ffmpeg_btn)
        download_layout.addLayout(ffmpeg_layout)
        
        # 下载选项
        options_layout = QHBoxLayout()
        self.download_audio_checkbox = QCheckBox("提取音频")
        self.download_audio_checkbox.setChecked(self.config.download_audio)
        options_layout.addWidget(self.download_audio_checkbox)
        
        self.download_cover_checkbox = QCheckBox("下载封面")
        self.download_cover_checkbox.setChecked(self.config.download_cover)
        options_layout.addWidget(self.download_cover_checkbox)
        
        self.extract_text_checkbox = QCheckBox("提取文案")
        self.extract_text_checkbox.setChecked(self.config.extract_text)
        options_layout.addWidget(self.extract_text_checkbox)
        
        download_layout.addLayout(options_layout)
        
        layout.addWidget(download_group)
        
        # 浏览器设置组
        browser_group = QGroupBox("浏览器设置")
        browser_layout = QVBoxLayout(browser_group)
        
        # 浏览器类型选择
        browser_type_layout = QHBoxLayout()
        browser_type_layout.addWidget(QLabel('浏览器类型:'))
        self.browser_type = QComboBox()
        self.browser_type.addItems([
            "系统浏览器", 
            "自动下载浏览器"
        ])
        # 设置当前值
        self.browser_type.setCurrentIndex(0 if self.config.browser_type == "system" else 1)
        self.browser_type.currentIndexChanged.connect(self.toggle_browser_path)
        browser_type_layout.addWidget(self.browser_type)
        browser_layout.addLayout(browser_type_layout)
        
        # 浏览器路径设置
        browser_path_layout = QHBoxLayout()
        self.browser_path_label = QLabel('浏览器路径:')
        browser_path_layout.addWidget(self.browser_path_label)
        self.browser_path = QLineEdit(self.config.browser_executable_path)
        browser_path_layout.addWidget(self.browser_path)
        self.browse_browser_btn = QPushButton('浏览...')
        self.browse_browser_btn.clicked.connect(self.browse_browser)
        browser_path_layout.addWidget(self.browse_browser_btn)
        browser_layout.addLayout(browser_path_layout)
        
        # Chrome路径设置
        chrome_path_layout = QHBoxLayout()
        chrome_path_layout.addWidget(QLabel('Chrome路径:'))
        self.chrome_path = QLineEdit(self.config.chrome_path or "")
        chrome_path_layout.addWidget(self.chrome_path)
        browse_chrome_btn = QPushButton('浏览...')
        browse_chrome_btn.clicked.connect(lambda: self.browse_file(self.chrome_path, "Chrome (chrome.exe)"))
        chrome_path_layout.addWidget(browse_chrome_btn)
        browser_layout.addLayout(chrome_path_layout)
        
        # Edge路径设置
        edge_path_layout = QHBoxLayout()
        edge_path_layout.addWidget(QLabel('Edge路径:'))
        self.edge_path = QLineEdit(self.config.edge_path or "")
        edge_path_layout.addWidget(self.edge_path)
        browse_edge_btn = QPushButton('浏览...')
        browse_edge_btn.clicked.connect(lambda: self.browse_file(self.edge_path, "Edge (msedge.exe)"))
        edge_path_layout.addWidget(browse_edge_btn)
        browser_layout.addLayout(edge_path_layout)
        
        # 初始化浏览器路径可见性
        self.toggle_browser_path()
        
        layout.addWidget(browser_group)
        
        # 添加Cookie设置组
        cookie_group = QGroupBox("抖音Cookie设置（获取更好的下载效果）")
        cookie_layout = QVBoxLayout(cookie_group)
        
        # 添加说明标签
        cookie_desc = QLabel("请在浏览器中登录抖音后，按F12打开开发者工具，在网络选项卡中找到带有douyin.com的请求，" 
                           "复制其Cookie值粘贴到下面的文本框中。")
        cookie_desc.setWordWrap(True)
        cookie_layout.addWidget(cookie_desc)
        
        # Cookie文本框
        self.cookie_text = QTextEdit()
        self.cookie_text.setPlaceholderText("粘贴完整Cookie文本，例如: sessionid=xxx; passport_csrf_token=xxx; ...")
        self.cookie_text.setText(self.config.douyin_cookie)
        self.cookie_text.setMinimumHeight(80)
        cookie_layout.addWidget(self.cookie_text)
        

        layout.addWidget(cookie_group)
        
        # 语音识别设置组
        speech_group = QGroupBox("语音识别设置")
        speech_layout = QVBoxLayout(speech_group)
        
        # 引擎选择
        engine_layout = QHBoxLayout()
        engine_layout.addWidget(QLabel('识别引擎:'))
        self.speech_engine = QComboBox()
        self.speech_engine.addItems([
            "Whisper (OpenAI)", 
            "PaddleSpeech"
        ])
        
        # 设置当前选择的引擎
        engines = {
            "whisper": 0,
            "Whisper (OpenAI)": 0,
            "paddlespeech": 1,
            "PaddleSpeech": 1
        }
        
        # 从配置中获取当前引擎，并设置对应的索引
        current_engine = self.config.speech_recognition_engine
        self.speech_engine.setCurrentIndex(
            engines.get(current_engine, 0)
        )
        
        # 添加引擎选择的事件处理
        self.speech_engine.currentIndexChanged.connect(self.toggle_whisper_model)
        
        engine_layout.addWidget(self.speech_engine)
        speech_layout.addLayout(engine_layout)
        
        # Whisper模型选择
        self.whisper_model_layout = QHBoxLayout()
        self.whisper_model_label = QLabel('Whisper模型:')
        self.whisper_model = QComboBox()
        self.whisper_model.addItems([
            "tiny", "base", "small", "medium", "large"
        ])
        self.whisper_model.setCurrentText(
            self.config.speech_recognition_config.get('whisper', {}).get('model', 'base')
        )
        
        self.whisper_model_layout.addWidget(self.whisper_model_label)
        self.whisper_model_layout.addWidget(self.whisper_model)
        speech_layout.addLayout(self.whisper_model_layout)
        
        # 初始时根据当前引擎设置可见性
        self.toggle_whisper_model()
        
        layout.addWidget(speech_group)
        
        # 确定和取消按钮
        buttons = QHBoxLayout()
        ok_btn = QPushButton('确定')
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
    def toggle_browser_path(self):
        """切换浏览器路径输入框的可见性"""
        is_system_browser = self.browser_type.currentIndex() == 0
        self.browser_path_label.setVisible(is_system_browser)
        self.browser_path.setVisible(is_system_browser)
        self.browse_browser_btn.setVisible(is_system_browser)
        
    def browse_browser(self):
        """浏览选择浏览器路径"""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "选择浏览器",
            self.browser_path.text(),
            "浏览器 (*.exe);;所有文件 (*.*)"
        )
        if file:
            self.browser_path.setText(file)
        
    def import_cookie_from_chrome(self):
        """从Chrome浏览器导入抖音Cookie"""
        try:
            import browser_cookie3
            cookies = browser_cookie3.chrome(domain_name='.douyin.com')
            cookie_str = '; '.join([f"{cookie.name}={cookie.value}" for cookie in cookies])
            if cookie_str:
                self.cookie_text.setText(cookie_str)
                QMessageBox.information(self, "成功", "已从Chrome导入抖音Cookie")
            else:
                QMessageBox.warning(self, "警告", "未找到抖音Cookie，请确保已在Chrome中登录抖音")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入Cookie失败: {str(e)}")
            
    def import_cookie_from_edge(self):
        """从Edge浏览器导入抖音Cookie"""
        try:
            import browser_cookie3
            cookies = browser_cookie3.edge(domain_name='.douyin.com')
            cookie_str = '; '.join([f"{cookie.name}={cookie.value}" for cookie in cookies])
            if cookie_str:
                self.cookie_text.setText(cookie_str)
                QMessageBox.information(self, "成功", "已从Edge导入抖音Cookie")
            else:
                QMessageBox.warning(self, "警告", "未找到抖音Cookie，请确保已在Edge中登录抖音")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入Cookie失败: {str(e)}")
            
    def test_cookie(self):
        """测试Cookie是否有效"""
        cookie = self.cookie_text.toPlainText().strip()
        if not cookie:
            QMessageBox.warning(self, "警告", "请先输入Cookie")
            return
            
        QMessageBox.information(self, "提示", "开始测试Cookie，请稍候...")
        
        # 在新线程中执行测试，避免界面卡死
        import threading
        def do_test():
            try:
                import requests
                url = "https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=7000000000000000001"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/json",
                    "Cookie": cookie
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if "status_code" in data:
                        if data["status_code"] == 0:
                            QMetaObject.invokeMethod(self, "showSuccessMessage", 
                                                  Qt.ConnectionType.QueuedConnection,
                                                  Q_ARG(str, "Cookie有效，可以正常使用"))
                        else:
                            QMetaObject.invokeMethod(self, "showWarningMessage", 
                                                  Qt.ConnectionType.QueuedConnection,
                                                  Q_ARG(str, f"Cookie可能失效，错误信息: {data.get('status_msg', '未知错误')}"))
                    else:
                        QMetaObject.invokeMethod(self, "showWarningMessage", 
                                              Qt.ConnectionType.QueuedConnection,
                                              Q_ARG(str, "无法判断Cookie是否有效，请尝试下载测试"))
                else:
                    QMetaObject.invokeMethod(self, "showErrorMessage", 
                                          Qt.ConnectionType.QueuedConnection,
                                          Q_ARG(str, f"请求失败，状态码: {response.status_code}"))
            except Exception as e:
                QMetaObject.invokeMethod(self, "showErrorMessage", 
                                      Qt.ConnectionType.QueuedConnection,
                                      Q_ARG(str, f"测试出错: {str(e)}"))
                
        threading.Thread(target=do_test, daemon=True).start()
    
    # 用于线程安全的消息显示方法
    def showSuccessMessage(self, message):
        QMessageBox.information(self, "成功", message)
        
    def showWarningMessage(self, message):
        QMessageBox.warning(self, "警告", message)
        
    def showErrorMessage(self, message):
        QMessageBox.critical(self, "错误", message)
    
    def browse_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(
            self,
            "选择目录",
            line_edit.text()
        )
        if folder:
            line_edit.setText(folder)
            
    def browse_file(self, line_edit, filter_text):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            line_edit.text(),
            filter_text
        )
        if file:
            line_edit.setText(file)
            
    def get_settings(self):
        settings = {
            'download_path': self.download_path.text(),
            'audio_path': self.audio_path.text(),
            'text_path': self.text_path.text(),
            'ffmpeg_path': self.ffmpeg_path.text(),
            'download_audio': self.download_audio_checkbox.isChecked(),
            'download_cover': self.download_cover_checkbox.isChecked(),
            'extract_text': self.extract_text_checkbox.isChecked(),
            'douyin_cookie': self.cookie_text.toPlainText().strip(),
            'speech_recognition_engine': self.speech_engine.currentText(),
            'speech_recognition_config': self.config.speech_recognition_config,
            
            # 浏览器设置
            'browser_type': "system" if self.browser_type.currentIndex() == 0 else "auto",
            'browser_executable_path': self.browser_path.text(),
            'chrome_path': self.chrome_path.text(),
            'edge_path': self.edge_path.text()
        }
        
        # 更新Whisper模型配置
        settings['speech_recognition_config']['whisper']['model'] = self.whisper_model.currentText()
        
        return settings

    def toggle_whisper_model(self):
        """切换Whisper模型选择的可见性"""
        is_whisper = self.speech_engine.currentText() == "Whisper (OpenAI)"
        self.whisper_model_label.setVisible(is_whisper)
        self.whisper_model.setVisible(is_whisper)

class MainWindow(QMainWindow):
    # 定义信号
    start_processing = pyqtSignal(list)  # 开始处理信号
    process_imported_video = pyqtSignal(str)  # 处理导入的视频信号
    process_imported_audio = pyqtSignal(str)  # 处理导入的音频信号
    
    def __init__(self):
        super().__init__()
        self.config = None  # 将在控制器中设置
        self.init_ui()
        
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle('抖音视频文案提取')
        self.setGeometry(100, 100, 800, 600)
        
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题标签
        title_label = QLabel("抖音视频下载与文案提取")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 描述标签
        desc_label = QLabel("输入抖音链接，自动下载视频并提取文案")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # 顶部按钮区域
        top_buttons = QHBoxLayout()
        
        # 开始按钮
        self.start_button = QPushButton('开始下载')
        self.start_button.setMinimumHeight(40)
        self.start_button.setFont(QFont("Microsoft YaHei", 10))
        self.start_button.setStyleSheet("background-color: #1E90FF; color: white; border-radius: 5px;")
        self.start_button.clicked.connect(self.on_start_clicked)
        top_buttons.addWidget(self.start_button)
        
        # 导入视频按钮
        self.import_video_button = QPushButton('导入视频')
        self.import_video_button.setMinimumHeight(40)
        self.import_video_button.setFont(QFont("Microsoft YaHei", 10))
        self.import_video_button.setStyleSheet("background-color: #32CD32; color: white; border-radius: 5px;")
        self.import_video_button.clicked.connect(self.import_videos)
        top_buttons.addWidget(self.import_video_button)
        
        # 导入音频按钮
        self.import_audio_button = QPushButton('导入音频')
        self.import_audio_button.setMinimumHeight(40)
        self.import_audio_button.setFont(QFont("Microsoft YaHei", 10))
        self.import_audio_button.setStyleSheet("background-color: #FF8C00; color: white; border-radius: 5px;")
        self.import_audio_button.clicked.connect(self.import_audio)
        top_buttons.addWidget(self.import_audio_button)
        
        # 清空按钮
        self.clear_button = QPushButton('清空链接')
        self.clear_button.setMinimumHeight(40)
        self.clear_button.setFont(QFont("Microsoft YaHei", 10))
        self.clear_button.clicked.connect(lambda: self.url_input.clear())
        top_buttons.addWidget(self.clear_button)
        
        # 在顶部按钮区域添加设置按钮
        self.settings_button = QPushButton('设置')
        self.settings_button.setMinimumHeight(40)
        self.settings_button.setFont(QFont("Microsoft YaHei", 10))
        self.settings_button.clicked.connect(self.show_settings)
        top_buttons.addWidget(self.settings_button)
        
        layout.addLayout(top_buttons)
        
        # 链接输入框
        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText('请输入抖音视频链接，每行一个...\n例如：https://v.douyin.com/XXXXXX/ 或 https://www.douyin.com/video/XXXXXXXX')
        self.url_input.setFont(QFont("Microsoft YaHei", 10))
        layout.addWidget(self.url_input)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)
        
        # 日志显示框
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Microsoft YaHei", 10))
        self.log_output.setStyleSheet("background-color: #f5f5f5; border-radius: 5px; padding: 5px;")
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
        
        layout.addLayout(bottom_buttons)
        
        # 初始日志
        self.log("欢迎使用抖音视频下载与文案提取工具\n请输入抖音链接或导入视频文件")
        
    def open_folder(self, folder_type):
        """打开指定类型的文件夹"""
        folder_map = {
            'video': self.config.download_path,
            'audio': self.config.audio_path,
            'text': self.config.text_path
        }
        
        folder = folder_map.get(folder_type)
        if folder and os.path.exists(folder):
            # 在Windows上使用explorer打开文件夹
            os.startfile(os.path.abspath(folder))
        else:
            QMessageBox.warning(self, "提示", f"文件夹 {folder} 不存在！")
        
    def on_start_clicked(self):
        """开始按钮点击事件"""
        urls = self.url_input.toPlainText().strip().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        if urls:
            self.start_processing.emit(urls)
            self.start_button.setEnabled(False)
        else:
            QMessageBox.warning(self, "提示", "请输入视频链接！")
            
    def log(self, message):
        """添加日志"""
        self.log_output.append(message)
        # 滚动到底部
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def processing_finished(self):
        """处理完成"""
        self.start_button.setEnabled(True)
        self.progress_bar.setValue(100)
        QMessageBox.information(self, "提示", "处理完成！")
        
    def show_settings(self):
        """显示设置对话框"""
        if not self.config:
            QMessageBox.warning(self, "错误", "配置未初始化")
            return
            
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            
            # 更新配置
            for key, value in settings.items():
                setattr(self.config, key, value)
                
            self.config.save_config()
            self.log("设置已保存")

    def import_videos(self):
        """导入视频文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.mov *.avi *.flv *.wmv)"
        )
        if files:
            for file in files:
                # 发送处理信号
                self.process_imported_video.emit(file)
                self.log(f"导入视频: {os.path.basename(file)}")
                
    def import_audio(self):
        """导入音频文件直接进行文案提取"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择音频文件",
            "",
            "音频文件 (*.mp3 *.wav *.m4a *.aac *.flac *.ogg)"
        )
        if files:
            for file in files:
                # 发送处理音频信号
                self.process_imported_audio.emit(file)
                self.log(f"导入音频: {os.path.basename(file)}")
                
    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(self, '确认退出', 
                                     '确定要退出程序吗？',
                                     QMessageBox.StandardButton.Yes | 
                                     QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
                                     
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore() 