import os
import tarfile
import sqlite3
import json
from pathlib import Path

def extract_tar(tar_file, extract_path):
    """解压tar文件"""
    print(f"解压文件: {tar_file}")
    try:
        with tarfile.open(tar_file, 'r') as tar:
            tar.extractall(path=extract_path)
        print(f"解压完成，文件保存在: {extract_path}")
        return True
    except Exception as e:
        print(f"解压失败: {e}")
        return False

def find_db_files(path):
    """查找所有数据库文件"""
    db_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.db'):
                db_files.append(os.path.join(root, file))
    return db_files

def search_token_in_db(db_file):
    """在数据库中搜索token"""
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"\n检查表: {table_name}")
            
            # 获取表的所有列
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # 查询每一列
            for column in column_names:
                try:
                    cursor.execute(f"SELECT * FROM {table_name} WHERE {column} LIKE '%token%' OR {column} LIKE '%did%' OR {column} LIKE '%xiaomi%' OR {column} LIKE '%miio%';")
                    rows = cursor.fetchall()
                    if rows:
                        print(f"\n在表 {table_name} 的列 {column} 中找到可能的结果:")
                        for row in rows:
                            print(f"数据: {row}")
                except:
                    continue
                    
        conn.close()
    except Exception as e:
        print(f"读取数据库失败: {e}")

def search_token_in_files(path):
    """在所有文件中搜索token"""
    print(f"搜索路径: {path}")
    
    # 搜索数据库文件
    db_files = find_db_files(path)
    if db_files:
        print(f"\n找到 {len(db_files)} 个数据库文件")
        for db_file in db_files:
            print(f"\n分析数据库: {db_file}")
            search_token_in_db(db_file)
    else:
        print("未找到数据库文件")

    # 搜索JSON文件
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            for key, value in data.items():
                                if 'token' in str(value).lower() or 'did' in str(value).lower():
                                    print(f"\n在文件 {file} 中找到可能的结果:")
                                    print(f"Key: {key}")
                                    print(f"Value: {value}")
                except:
                    continue

def main():
    # 设置工作目录
    work_dir = Path('d:/nextcloud/work/xiaoai')
    backup_tar = work_dir / 'backup.tar'
    extract_dir = work_dir / 'backup_extracted'
    
    # 创建解压目录
    os.makedirs(extract_dir, exist_ok=True)
    
    # 解压文件
    if extract_tar(backup_tar, extract_dir):
        # 搜索token
        search_token_in_files(extract_dir)
    
    print("\n搜索完成！")
    print("如果没有找到token，请检查：")
    print("1. 备份文件是否正确生成")
    print("2. 是否有权限访问备份数据")
    print("3. 米家APP是否已登录")

if __name__ == "__main__":
    main()
