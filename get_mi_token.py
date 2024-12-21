import requests
import json
import time
import hashlib
import base64
import logging
import os
from urllib.parse import urlencode, urlparse, parse_qs
import hmac

class MiAccount:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.login_response = None
        # 使用固定的PassportDeviceId
        self.passport_device_id = "3C861A5C-3E85-4293-A54B-DDDD65531D8F"
        # API服务器
        self.server = 'https://api.io.mi.com/app'
        self.session.headers.update({
            'User-Agent': 'APP/com.xiaomi.mihome APPV/6.0.103 iosPassportSDK/3.9.0 iOS/14.4 miHSTS'
        })
        self.logged_in = False

    def login(self):
        """登录小米账号"""
        try:
            print("\n开始登录小米账号...")
            
            # 准备登录参数
            login_url = "https://account.xiaomi.com/pass/serviceLogin?sid=xiaomiio&_json=true"
            headers = {
                'User-Agent': 'APP/com.xiaomi.mihome APPV/6.0.103 iosPassportSDK/3.9.0 iOS/14.4 miHSTS'
            }
            
            # 设置cookies
            cookies = {
                'PassportDeviceId': self.passport_device_id,
                'sdkVersion': '3.9'
            }
            
            # 获取设备ID
            response = self.session.get(login_url, headers=headers, cookies=cookies)
            print(f"设备ID响应状态: {response.status_code}")
            print(f"设备ID响应头: {dict(response.headers)}")
            
            # 从响应中提取_sign作为设备ID
            content = response.text.replace("&&&START&&&", "")
            data = json.loads(content)
            device_id = data.get("_sign")
            
            if not device_id:
                raise Exception("获取设备ID失败")
            print(f"获取到设备ID: {device_id}\n")

            # 计算密码hash
            hash_password = hashlib.md5(self.password.encode()).hexdigest().upper()
            
            # 准备登录数据
            login_data = {
                '_json': 'true',
                'callback': data.get('callback'),
                'sid': 'xiaomiio',
                'qs': data.get('qs'),
                '_sign': device_id,
                'user': self.username,
                'hash': hash_password
            }
            
            # 发送登录请求
            response = self.session.post(
                'https://account.xiaomi.com/pass/serviceLoginAuth2',
                data=login_data,
                headers=headers,
                cookies=cookies
            )
            print(f"登录响应状态: {response.status_code}")
            print(f"登录响应头: {dict(response.headers)}")
            
            # 解析登录响应
            content = response.text.replace("&&&START&&&", "")
            data = json.loads(content)
            
            # 检查登录结果
            if data.get('code') != 0:
                raise Exception(f"登录失败: {data.get('description')}")
                
            self.login_response = response
            location_url = data.get('location')
            if not location_url:
                raise Exception("获取登录重定向URL失败")
            print(f"获取到重定向URL: {location_url}")
            print("正在获取服务令牌...")
            
            # 获取服务令牌
            response = self.session.get(location_url)
            print(f"服务令牌响应状态: {response.status_code}")
            print(f"服务令牌响应头: {dict(response.headers)}")
            
            # 从cookies中获取服务令牌
            service_token = None
            for cookie in response.cookies:
                if cookie.name == 'serviceToken':
                    service_token = cookie.value
                    break
            
            if not service_token:
                raise Exception("未找到服务令牌")
            
            print(f"\n成功获取服务令牌: {service_token[:20]}...")
            
            return service_token

        except Exception as e:
            print(f"错误: {str(e)}")
            return None

    def sign_data(self, uri, data, ssecurity):
        """生成签名数据"""
        if not isinstance(data, str):
            data = json.dumps(data)
            
        # 生成nonce，确保长度为12字节
        current_time = int(time.time() / 60)
        random_bytes = os.urandom(8)
        time_bytes = current_time.to_bytes(4, 'big')
        nonce = base64.b64encode(random_bytes + time_bytes).decode()
        
        # 生成签名nonce
        hash_obj = hashlib.sha256()
        hash_obj.update(base64.b64decode(ssecurity))
        hash_obj.update(base64.b64decode(nonce))
        snonce = base64.b64encode(hash_obj.digest()).decode()
        
        # 生成签名字符串
        msg = '&'.join([uri, snonce, nonce, 'data=' + data])
        print(f"签名字符串: {msg}")
        
        # 使用HMAC-SHA256生成签名
        sign = hmac.new(
            key=base64.b64decode(snonce),
            msg=msg.encode(),
            digestmod=hashlib.sha256
        ).digest()
        
        # 返回签名数据
        return {
            '_nonce': nonce,
            'data': data,
            'signature': base64.b64encode(sign).decode()
        }

    def get_device_list(self, service_token):
        """获取设备列表"""
        try:
            # 从登录响应头中提取security信息
            extension_pragma = self.login_response.headers.get('extension-pragma', '')
            try:
                pragma_data = json.loads(extension_pragma)
                ssecurity = pragma_data.get('ssecurity', '')
            except Exception as e:
                raise Exception(f"无法解析extension-pragma: {str(e)}")

            # 准备请求头
            headers = {
                'User-Agent': 'APP/com.xiaomi.mihome APPV/6.0.103 iosPassportSDK/3.9.0 iOS/14.4 miHSTS',
                'x-xiaomi-protocal-flag-cli': 'PROTOCAL-HTTP2'
            }
            
            # 获取最新的userId
            user_id = None
            for cookie in self.session.cookies:
                if cookie.name == 'userId':
                    user_id = cookie.value
                    break
            
            if not user_id:
                raise Exception("未找到userId")
            
            # 设置cookies
            cookies = {
                'userId': user_id,
                'serviceToken': service_token,
                'PassportDeviceId': self.passport_device_id
            }
            
            # 准备签名数据
            uri = '/home/device_list'
            data = {
                "getVirtualModel": True,
                "getHuamiDevices": 0,
                "accessKey": "IOS00026747c5acafc2",
                "requestId": str(int(time.time() * 1000))
            }
            
            # 生成签名
            signed_data = self.sign_data(uri, data, ssecurity)
            
            # 发送请求
            url = self.server + uri
            response = requests.get(url, headers=headers, cookies=cookies, params=signed_data, verify=True)
            
            if response.status_code == 200:
                resp = response.json()
                if resp.get('code') == 0:
                    return resp.get('result', {}).get('list', [])
                else:
                    raise Exception(f"请求失败: {resp.get('message')}")
            else:
                raise Exception(f"请求失败，状态码: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"获取设备列表失败: {str(e)}")

def main():
    # 初始化服务
    account = MiAccount('your_username', 'your_password')
    
    try:
        # 登录
        service_token = account.login()
        if not service_token:
            print("登录失败")
            return
            
        print("\n登录成功!")
        
        # 获取设备列表
        devices = account.get_device_list(service_token)
        
        # 打印设备信息
        print("\n找到的设备:")
        for device in devices:
            if 'wifispeaker' in device.get('model', ''):
                print(f"\n设备名称: {device.get('name')}")
                print(f"设备型号: {device.get('model')}")
                print(f"设备ID: {device.get('did')}")
                print(f"MAC地址: {device.get('mac')}")
                print(f"Token: {device.get('token')}")
                print(f"在线状态: {device.get('isOnline')}")
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main()
