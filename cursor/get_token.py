from micloud import MiCloud
import asyncio

async def get_xiaomi_devices():
    # 替换成您的米家账号和密码
    username = "pspbird@21cn.com"
    password = "haha98@163"
    
    mc = MiCloud(username, password)
    
    try:
        # 登录
        logged_in = await mc.login()
        if logged_in:
            print("登录成功！")
            
            # 获取设备列表
            devices = await mc.get_devices()
            
            # 查找小爱音箱
            for device in devices:
                if device.get('localip') == '192.168.1.45':  # 使用我们找到的IP
                    print("\n找到小爱音箱：")
                    print(f"名称: {device.get('name')}")
                    print(f"型号: {device.get('model')}")
                    print(f"Token: {device.get('token')}")
                    print(f"IP: {device.get('localip')}")
                    return
            
            print("未找到IP为 192.168.1.45 的设备")
            
        else:
            print("登录失败！")
            
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(get_xiaomi_devices()) 