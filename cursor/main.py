import json
import asyncio
import google.generativeai as genai
from miio import Device
from datetime import datetime

class XiaoAiGeminiBridge:
    def __init__(self, xiaomi_token, xiaomi_ip, gemini_api_key):
        self.xiaomi_device = Device(ip=xiaomi_ip, token=xiaomi_token)
        # 初始化 Gemini
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        # 保存对话历史
        self.conversation_history = []
        
    async def listen_for_command(self):
        """监听小爱音箱的语音命令"""
        try:
            # 获取语音命令
            # 注意：这里使用的命令可能需要根据您的小爱音箱型号调整
            response = self.xiaomi_device.send('get_prop', ['current_status'])
            if response and 'voice_command' in response:
                command = response['voice_command']
                print(f"收到语音命令: {command}")
                return command
            return None
        except Exception as e:
            print(f"监听命令时出错: {str(e)}")
            return None

    async def speak_response(self, text):
        """通过小爱音箱播放响应"""
        try:
            # 使用 TTS 命令播放响应
            self.xiaomi_device.send('player_play_tts', {'text': text})
            print(f"播放响应: {text}")
        except Exception as e:
            print(f"播放响应时出错: {str(e)}") 