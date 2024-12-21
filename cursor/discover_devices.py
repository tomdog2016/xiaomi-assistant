import os
import asyncio
from miservice.miioservice import MiIOService
from miservice.miioservice import MiAccount

async def discover_xiaomi_devices():
    print("正在搜索小米设备...")
    
    # 设置米家账号信息
    username = "pspbird@21cn.com"
    password = "haha98@163"
    
    try:
        # 创建 MiAccount（修正初始化方式）
        print("登录米家账号...")
        account = MiAccount(
            username=username,
            password=password
        )
        await account.login()
        
        # 使用已登录的账号创建 MiIOService
        print("连接米家服务...")
        service = MiIOService(account)
        
        print("获取设备列表...")
        devices = await service.device_list()
        
        target_ip = '192.168.1.45'
        found = False
        
        print("\n发现的设备：")
        for device in devices:
            print(f"\n设备信息：")
            print(f"名称: {device.get('name', 'Unknown')}")
            print(f"型号: {device.get('model', 'Unknown')}")
            print(f"IP: {device.get('localip', 'Unknown')}")
            
            if device.get('localip') == target_ip:
                found = True
                print("\n=== 找到目标设备！===")
                print(f"名称: {device.get('name')}")
                print(f"型号: {device.get('model')}")
                print(f"Token: {device.get('token')}")
                print(f"IP: {device.get('localip')}")
                print("===================")
                return device.get('localip'), device.get('token')
        
        if not found:
            print(f"\n未找到 IP 为 {target_ip} 的设备")
            
    except Exception as e:
        print(f"获取设备信息失败: {str(e)}")
        print("\n请确保：")
        print("1. 账号密码正确")
        print("2. 设备已在米家 APP 中添加")
        print("3. 网络连接正常")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(discover_xiaomi_devices()) 