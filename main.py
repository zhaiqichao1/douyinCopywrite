#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from controllers.main_controller import MainController

def resource_path(relative_path):
    """获取资源的绝对路径，用于PyInstaller打包"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

if __name__ == "__main__":
    # 确保必要的目录存在
    for directory in ["video", "audio", "text"]:
        os.makedirs(directory, exist_ok=True)
    
    # 设置环境变量以禁用自动下载浏览器
    os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "1"
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"
    
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("抖音视频下载与文案提取")
    
    # 设置应用图标
    icon_path = resource_path("assets/icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 创建主控制器并运行
    controller = MainController()
    sys.exit(controller.run()) 