import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QTableWidget, QTableWidgetItem, QToolBar, QStatusBar,
                            QTextEdit, QDialog, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QAction
from get_mi_token import MiToken
from gemini_service import GeminiService

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("老汤的小米助手")
        self.setMinimumSize(800, 600)
        
        # 设置应用图标
        self.setWindowIcon(QIcon("icons/app.svg"))
        
        # 设置窗口半透明
        self.setWindowOpacity(0.95)
        
        # 初始化界面
        self.init_ui()
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("准备就绪")
        
        # 创建工具栏
        self.create_toolbar()
        
        # 初始化服务
        self.mi_token = None
        self.gemini_service = None
        try:
            self.gemini_service = GeminiService()
            self.statusBar.showMessage("Gemini API 已连接")
        except Exception as e:
            self.statusBar.showMessage(f"Gemini API 连接失败: {str(e)}")

    def init_ui(self):
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        layout = QVBoxLayout(central_widget)
        
        # 创建登录部分
        login_layout = QHBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("小米账号")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        login_button = QPushButton("登录")
        login_button.clicked.connect(self.login)
        
        login_layout.addWidget(self.username_input)
        login_layout.addWidget(self.password_input)
        login_layout.addWidget(login_button)
        
        layout.addLayout(login_layout)
        
        # 创建设备列表
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(4)
        self.device_table.setHorizontalHeaderLabels(["设备名称", "设备ID", "设备Token", "设备IP"])
        layout.addWidget(self.device_table)
        
        # 创建聊天部分
        chat_layout = QVBoxLayout()
        
        # 聊天历史显示区域
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        chat_layout.addWidget(self.chat_history)
        
        # 消息输入和发送区域
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("输入消息...")
        self.message_input.returnPressed.connect(self.send_message)
        
        send_button = QPushButton("发送")
        send_button.clicked.connect(self.send_message)
        
        clear_button = QPushButton("清除历史")
        clear_button.clicked.connect(self.clear_chat)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(send_button)
        input_layout.addWidget(clear_button)
        
        chat_layout.addLayout(input_layout)
        layout.addLayout(chat_layout)

    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # 刷新动作
        refresh_action = QAction(QIcon("icons/refresh.svg"), "刷新", self)
        refresh_action.setStatusTip("刷新设备列表")
        refresh_action.triggered.connect(self.refresh_devices)
        toolbar.addAction(refresh_action)

        toolbar.addSeparator()

        # 设置动作
        settings_action = QAction(QIcon("icons/settings.svg"), "设置", self)
        settings_action.setStatusTip("打开设置")
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)

        # 帮助动作
        help_action = QAction(QIcon("icons/help.svg"), "帮助", self)
        help_action.setStatusTip("查看帮助")
        help_action.triggered.connect(self.show_help)
        toolbar.addAction(help_action)

    def show_settings(self):
        QMessageBox.information(self, "设置", "设置功能正在开发中...")

    def show_help(self):
        QMessageBox.information(self, "帮助", "这是老汤的小米助手，用于管理小米智能设备。\n\n"
                              "使用方法：\n"
                              "1. 输入小米账号和密码登录\n"
                              "2. 点击刷新按钮获取设备列表\n"
                              "3. 在设备列表中查看所有设备信息")

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "错误", "请输入用户名和密码")
            return
            
        try:
            self.statusBar.showMessage("正在登录...")
            self.mi_token = MiToken(username, password)
            self.mi_token.login()
            
            self.statusBar.showMessage("登录成功")
            self.refresh_devices()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"登录时发生错误：{str(e)}")
            self.statusBar.showMessage("登录出错")

    def refresh_devices(self):
        if not self.mi_token:
            QMessageBox.warning(self, "错误", "请先登录")
            return
            
        try:
            self.statusBar.showMessage("正在获取设备列表...")
            # 获取设备列表
            devices = self.mi_token.get_device_list()
            
            # 清空表格
            self.device_table.setRowCount(0)
            
            # 添加设备到表格
            for device in devices:
                row = self.device_table.rowCount()
                self.device_table.insertRow(row)
                
                # 设置单元格内容
                self.device_table.setItem(row, 0, QTableWidgetItem(device.get('name', '')))
                self.device_table.setItem(row, 1, QTableWidgetItem(device.get('did', '')))
                self.device_table.setItem(row, 2, QTableWidgetItem(device.get('token', '')))
                self.device_table.setItem(row, 3, QTableWidgetItem(device.get('ip', '')))
                
            # 调整列宽
            self.device_table.resizeColumnsToContents()
            self.statusBar.showMessage("设备列表已更新")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新设备列表时发生错误：{str(e)}")
            self.statusBar.showMessage("获取设备列表失败")

    def send_message(self):
        """发送消息到Gemini并显示回复"""
        if not self.gemini_service:
            QMessageBox.warning(self, "错误", "Gemini API 未连接")
            return
            
        message = self.message_input.text().strip()
        if not message:
            return
            
        # 显示用户消息
        self.chat_history.append(f"<p style='color: blue;'>你: {message}</p>")
        self.message_input.clear()
        
        try:
            # 获取Gemini回复
            response = self.gemini_service.send_message(message)
            # 显示回复
            self.chat_history.append(f"<p style='color: green;'>Gemini: {response}</p>")
        except Exception as e:
            self.chat_history.append(f"<p style='color: red;'>错误: {str(e)}</p>")
        
        # 滚动到底部
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )
    
    def clear_chat(self):
        """清除聊天历史"""
        self.chat_history.clear()
        if self.gemini_service:
            self.gemini_service.reset_chat()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
