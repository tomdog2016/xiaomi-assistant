from miio.discovery import Discovery
import time
import socket
import codecs

def find_devices():
    try:
        disc = Discovery()
        print("正在搜索设备，这可能需要几秒钟...")
        # 使用正确的 discover() 方法
        devices = disc.discover()
        
        found = False
        for device in devices:
            print("\n发现设备：")
            print(f"IP: {device.ip}")
            print(f"Token: {codecs.encode(device.token, 'hex').decode() if device.token else 'Unknown'}")
            print(f"设备信息: {device.info}")
            
            if device.ip == '192.168.1.45':
                found = True
                print("\n=== 找到目标设备！===")
                print(f"IP: {device.ip}")
                print(f"Token: {codecs.encode(device.token, 'hex').decode() if device.token else 'Unknown'}")
                print("===================")
        
        if not found:
            print("\n未找到 IP 为 192.168.1.45 的设备")
            print("请确保：")
            print("1. 小爱音箱已开机并连接到网络")
            print("2. 电脑和小爱音箱在同一个网络下")
            print("3. IP 地址正确")
            
    except Exception as e:
        print(f"搜索设备时出错: {str(e)}")
        print("\n详细错误信息:")
        import traceback
        traceback.print_exc()
        print("\n尝试以下解决方案：")
        print("1. 确保网络连接正常")
        print("2. 关闭防火墙")
        print("3. 以管理员权限运行脚本")

if __name__ == "__main__":
    find_devices() 