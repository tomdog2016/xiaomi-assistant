import click
import subprocess
import json
import os
import requests
from miio.device import Device
from miio.discovery import Discovery
from micloud import MiCloud
from micloud.micloudexception import MiCloudException

def get_token_via_micloud():
    """通过小米云服务获取token"""
    print("\n方法2: 通过小米云服务")
    
    username = input("请输入小米账号: ")
    password = input("请输入密码: ")
    
    try:
        mc = MiCloud()
        print("\n正在登录小米账号...")
        mc.login(username, password)
        
        print("\n获取设备列表...")
        devices = mc.get_devices()
        
        for device in devices:
            if 'xiaomi.wifispeaker.' in device.get('model', ''):
                print(f"\n发现小爱音箱:")
                print(f"名称: {device.get('name')}")
                print(f"型号: {device.get('model')}")
                print(f"Token: {device.get('token')}")
                print(f"设备ID: {device.get('did')}")
                print(f"IP地址: {device.get('localip')}")
                print(f"MAC地址: {device.get('mac')}")
    
    except MiCloudException as e:
        print(f"登录失败: {e}")
    except Exception as e:
        print(f"获取设备信息失败: {e}")

def get_token_via_miio(ip=None):
    """使用miio discover获取token"""
    print("方法1: 使用miio discover")
    print("正在搜索设备...")
    
    try:
        discovered_devices = Discovery().discover()
        
        if not discovered_devices:
            print("未发现任何设备")
            return
        
        for device in discovered_devices:
            if ip and device.ip != ip:
                continue
                
            print(f"\n发现设备:")
            print(f"IP地址: {device.ip}")
            print(f"Token: {device.token}")
            print(f"设备ID: {device.did}")
            
    except Exception as e:
        print(f"搜索设备失败: {e}")

def get_token_via_cloud():
    """通过小米云服务获取token"""
    print("\n方法2: 通过小米云服务")
    print("1. 安装米家APP")
    print("2. 登录你的小米账号")
    print("3. 在米家APP中找到你的小爱音箱")
    print("4. 点击右上角的'...'")
    print("5. 选择'设备信息'")
    print("6. 在底部可以找到Token")

def get_token_via_backup():
    """通过备份米家APP数据获取token"""
    print("\n方法3: 通过备份米家APP数据")
    print("1. 在Android手机上安装米家APP")
    print("2. 登录你的小米账号")
    print("3. 使用adb备份米家APP数据:")
    print("   adb backup -f backup.ab -noapk com.xiaomi.smarthome")
    print("4. 解密备份文件:")
    print("   java -jar abe.jar unpack backup.ab backup.tar")
    print("5. 解压backup.tar，在数据库文件中可以找到token")

@click.command()
@click.option('--ip', '-i', help='设备IP地址（可选）')
@click.option('--method', '-m', type=click.Choice(['miio', 'cloud', 'micloud', 'backup']), default='micloud', help='获取token的方法')
def main(ip, method):
    """获取小爱音箱的token"""
    print("获取小爱音箱Token的方法：\n")
    
    if method == 'miio':
        get_token_via_miio(ip)
    elif method == 'cloud':
        get_token_via_cloud()
    elif method == 'micloud':
        get_token_via_micloud()
    else:
        get_token_via_backup()
        
    print("\n注意：")
    print("1. Token是设备的重要凭证，请妥善保管")
    print("2. 如果以上方法都无法获取token，可以尝试重置设备")
    print("3. 重置后需要重新配对设备")

if __name__ == "__main__":
    main()
