import os
import shutil
from datetime import datetime

def backup_files():
    # 创建备份目录
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d')}"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"创建备份目录: {backup_dir}")
    
    # 创建icons目录
    icons_backup_dir = os.path.join(backup_dir, "icons")
    if not os.path.exists(icons_backup_dir):
        os.makedirs(icons_backup_dir)
        print(f"创建图标备份目录: {icons_backup_dir}")
    
    # 要备份的文件列表
    files_to_backup = [
        "xiaomi_assistant.py",
        "get_mi_token.py",
        "requirements.txt",
        ".env",
        "device_info.txt"
    ]
    
    # 复制文件
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_dir, file))
            print(f"备份文件: {file}")
    
    # 复制icons目录下的所有文件
    if os.path.exists("icons"):
        for icon in os.listdir("icons"):
            if icon.endswith(".svg"):
                shutil.copy2(
                    os.path.join("icons", icon),
                    os.path.join(icons_backup_dir, icon)
                )
                print(f"备份图标: {icon}")
    
    print("\n备份完成!")

if __name__ == "__main__":
    backup_files()
