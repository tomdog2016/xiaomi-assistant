import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QTableWidget, QTableWidgetItem, QMessageBox,
                            QTabWidget, QGroupBox, QToolBar, QStatusBar)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QAction
from get_mi_token import MiAccount

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("老汤的小米助手")
        self.setMinimumSize(800, 600)
        
        # 设置应用图标
        self.setWindowIcon(QIcon("icons/app.svg"))
        
        # 设置窗口半透明
        self.setWindowOpacity(0.95)
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("准备就绪")
        
        # 创建主widget和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 创建标签页
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # 设备管理标签页
        device_tab = QWidget()
        device_layout = QVBoxLayout(device_tab)
        
        # 登录组
        login_group = QGroupBox("账号登录")
        login_layout = QHBoxLayout()
        
        # 用户名输入
        username_label = QLabel("用户名:")
        self.username_input = QLineEdit()
        login_layout.addWidget(username_label)
        login_layout.addWidget(self.username_input)
        
        # 密码输入
        password_label = QLabel("密码:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        login_layout.addWidget(password_label)
        login_layout.addWidget(self.password_input)
        
        # 登录按钮
        self.login_button = QPushButton("登录")
        self.login_button.clicked.connect(self.login)
        login_layout.addWidget(self.login_button)
        
        login_group.setLayout(login_layout)
        device_layout.addWidget(login_group)
        
        # 设备列表
        device_list_group = QGroupBox("设备列表")
        device_list_layout = QVBoxLayout()
        
        # 创建表格
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(6)
        self.device_table.setHorizontalHeaderLabels(["设备名称", "型号", "设备ID", "MAC地址", "Token", "状态"])
        self.device_table.horizontalHeader().setStretchLastSection(True)
        device_list_layout.addWidget(self.device_table)
        
        # 刷新按钮
        refresh_button = QPushButton("刷新设备列表")
        refresh_button.clicked.connect(self.refresh_devices)
        device_list_layout.addWidget(refresh_button)
        
        device_list_group.setLayout(device_list_layout)
        device_layout.addWidget(device_list_group)
        
        # 添加设备管理标签页
        tabs.addTab(device_tab, "设备管理")
        
        # 初始化成员变量
        self.mi_account = None
        self.service_token = None
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgba(240, 240, 240, 0.95);
            }
            QToolBar {
                background-color: rgba(230, 230, 230, 0.95);
                border: none;
                spacing: 10px;
                padding: 5px;
            }
            QStatusBar {
                background-color: rgba(230, 230, 230, 0.95);
                color: #666666;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid rgba(204, 204, 204, 0.8);
                border-radius: 5px;
                margin-top: 1ex;
                padding: 10px;
                background-color: rgba(255, 255, 255, 0.7);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QPushButton {
                background-color: rgba(76, 175, 80, 0.9);
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: rgba(69, 160, 73, 0.9);
            }
            QTableWidget {
                border: 1px solid rgba(204, 204, 204, 0.8);
                gridline-color: rgba(224, 224, 224, 0.8);
                background-color: rgba(255, 255, 255, 0.7);
            }
            QHeaderView::section {
                background-color: rgba(248, 249, 250, 0.9);
                padding: 4px;
                border: 1px solid rgba(204, 204, 204, 0.8);
                font-weight: bold;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid rgba(204, 204, 204, 0.8);
                border-radius: 3px;
                background-color: rgba(255, 255, 255, 0.7);
            }
            QTabWidget::pane {
                border: 1px solid rgba(204, 204, 204, 0.8);
                background-color: rgba(255, 255, 255, 0.7);
            }
            QTabBar::tab {
                background-color: rgba(230, 230, 230, 0.9);
                border: 1px solid rgba(204, 204, 204, 0.8);
                padding: 5px 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: rgba(255, 255, 255, 0.9);
            }
        """)

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
            self.mi_account = MiAccount(username, password)
            self.service_token = self.mi_account.login()
            
            if self.service_token:
                QMessageBox.information(self, "成功", "登录成功！")
                self.statusBar.showMessage("登录成功")
                self.refresh_devices()
            else:
                QMessageBox.warning(self, "错误", "登录失败，请检查用户名和密码")
                self.statusBar.showMessage("登录失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"登录时发生错误：{str(e)}")
            self.statusBar.showMessage("登录出错")

    def refresh_devices(self):
        if not self.mi_account or not self.service_token:
            QMessageBox.warning(self, "错误", "请先登录")
            return
            
        try:
            self.statusBar.showMessage("正在获取设备列表...")
            # 获取设备列表
            devices = self.mi_account.get_device_list(self.service_token)
            
            # 清空表格
            self.device_table.setRowCount(0)
            
            # 添加设备到表格
            for device in devices:
                row = self.device_table.rowCount()
                self.device_table.insertRow(row)
                
                # 设置单元格内容
                self.device_table.setItem(row, 0, QTableWidgetItem(device.get('name', '')))
                self.device_table.setItem(row, 1, QTableWidgetItem(device.get('model', '')))
                self.device_table.setItem(row, 2, QTableWidgetItem(device.get('did', '')))
                self.device_table.setItem(row, 3, QTableWidgetItem(device.get('mac', '')))
                self.device_table.setItem(row, 4, QTableWidgetItem(device.get('token', '')))
                self.device_table.setItem(row, 5, QTableWidgetItem('在线' if device.get('isOnline') else '离线'))
                
            # 调整列宽
            self.device_table.resizeColumnsToContents()
            self.statusBar.showMessage("设备列表已更新")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新设备列表时发生错误：{str(e)}")
            self.statusBar.showMessage("获取设备列表失败")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
