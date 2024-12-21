# 老汤的小米助手

一个用于管理小米智能设备的图形界面工具，支持设备发现、Token获取等功能。

## 功能特点

- 小米账号登录
- 设备列表查看
- 设备Token获取
- 美观的半透明界面
- 支持所有小米智能设备

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/xiaomi-assistant.git
cd xiaomi-assistant
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：
```bash
python xiaomi_assistant.py
```

2. 在界面中输入小米账号和密码
3. 点击登录按钮
4. 查看设备列表

## 配置

创建 `.env` 文件并添加以下内容：
```
MI_USERNAME=your_username
MI_PASSWORD=your_password
```

## 文件说明

- `xiaomi_assistant.py`: 主程序文件，包含图形界面实现
- `get_mi_token.py`: 小米账号登录和Token获取的核心实现
- `requirements.txt`: 项目依赖列表
- `icons/`: 图标文件目录

## 注意事项

- Token信息请妥善保管，不要分享给他人
- 建议定期修改密码以保证账号安全
- 如遇到问题，可以查看帮助或提交Issue

## 许可证

MIT License

## 作者

老汤
