import os
import logging
import socket
import requests
from dotenv import load_dotenv
import google.generativeai as genai
import json
import time
import click
import struct

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

class XiaomiSpeaker:
    def __init__(self):
        # 小爱音箱配置
        self.speaker_ip = os.getenv('SPEAKER_IP')
        self.speaker_token = os.getenv('SPEAKER_TOKEN')
        
        if not all([self.speaker_ip, self.speaker_token]):
            raise ValueError("请在.env文件中设置SPEAKER_IP和SPEAKER_TOKEN")
        
        # 初始化Gemini
        self.gemini_key = os.getenv('GOOGLE_API_KEY')
        if not self.gemini_key:
            raise ValueError("请在.env文件中设置GOOGLE_API_KEY")
        
        genai.configure(api_key=self.gemini_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])
        logger.info("Gemini API初始化成功")

    def send_message(self, message):
        """直接发送消息到小爱音箱"""
        try:
            url = f"http://{self.speaker_ip}/api/text_to_speech"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.speaker_token}"
            }
            data = {"text": message}
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            logger.info(f"消息发送成功: {message}")
            return True
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")
            return False

    def get_status(self):
        """获取小爱音箱状态"""
        try:
            url = f"http://{self.speaker_ip}/api/status"
            headers = {"Authorization": f"Bearer {self.speaker_token}"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取状态失败: {str(e)}")
            return None

    def play_text(self, text):
        """使用TTS播放文本"""
        return self.send_message(text)

    def get_gemini_response(self, text):
        """获取Gemini的回应"""
        try:
            # 添加提示以获得更简洁的回答
            prompt = f"请用简洁的语言回答以下问题（控制在100字以内）：{text}"
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            logger.error(f"获取Gemini响应失败: {str(e)}")
            return f"抱歉，出现了错误：{str(e)}"

    @click.command()
    @click.option('--test', is_flag=True, help='运行测试模式')
    def run(self, test=False):
        """运行小爱音箱Gemini助手"""
        logger.info("小爱Gemini助手已启动")
        
        if test:
            # 测试模式
            test_text = "你好，我是Gemini助手。现在我们来测试一下语音功能。"
            logger.info("运行测试模式...")
            if self.play_text(test_text):
                logger.info("测试成功！")
            else:
                logger.error("测试失败！")
            return

        try:
            while True:
                # 获取设备状态
                status = self.get_status()
                if status:
                    logger.debug(f"设备状态: {status}")
                
                # TODO: 实现语音命令检测
                # 目前这部分需要进一步研究小爱音箱的API
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("程序已退出")
        except Exception as e:
            logger.error(f"运行时错误: {str(e)}")

if __name__ == "__main__":
    try:
        speaker = XiaomiSpeaker()
        speaker.run()
    except Exception as e:
        logger.error(f"程序启动失败: {str(e)}")
