import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
import sounddevice as sd
import numpy as np
import wave
import keyboard
import threading
import time
from pathlib import Path
from aip import AipSpeech
import tempfile
from playsound import playsound

# 加载环境变量
load_dotenv()

# 配置Google Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("请在.env文件中设置GOOGLE_API_KEY")

# 配置百度语音API
BAIDU_APP_ID = os.getenv('BAIDU_APP_ID')
BAIDU_API_KEY = os.getenv('BAIDU_API_KEY')
BAIDU_SECRET_KEY = os.getenv('BAIDU_SECRET_KEY')

if not all([BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY]):
    raise ValueError("请在.env文件中设置百度语音API相关配置")

# 初始化Gemini模型
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

# 初始化百度语音客户端
baidu_client = AipSpeech(BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY)

class XiaomiGeminiAssistant:
    def __init__(self):
        self.recording = False
        self.audio_frames = []
        self.sample_rate = int(os.getenv('SAMPLE_RATE', '16000'))
        self.channels = int(os.getenv('CHANNELS', '1'))
        self.recordings_dir = Path('recordings')
        self.recordings_dir.mkdir(exist_ok=True)
        self.speech_language = os.getenv('SPEECH_LANGUAGE', 'zh')
        self.asr_dev_pid = int(os.getenv('ASR_DEV_PID', '1537'))
        
    def record_audio(self):
        """录制音频"""
        self.recording = True
        self.audio_frames = []
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f'录音状态: {status}')
            if self.recording:
                self.audio_frames.append(indata.copy())
        
        # 开始录音
        with sd.InputStream(callback=audio_callback,
                          channels=self.channels,
                          samplerate=self.sample_rate):
            print("正在录音...按空格键停止")
            keyboard.wait('space')
            self.recording = False
        
        # 保存录音
        if self.audio_frames:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = self.recordings_dir / f"recording_{timestamp}.wav"
            audio_data = np.concatenate(self.audio_frames, axis=0)
            self.save_wave_file(filename, audio_data)
            return filename
        return None
    
    def save_wave_file(self, filename, audio_data):
        """保存音频文件"""
        with wave.open(str(filename), 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
        print(f"录音已保存: {filename}")
    
    def process_voice_command(self, audio_file):
        """语音识别"""
        try:
            with open(audio_file, 'rb') as f:
                audio_data = f.read()
            
            # 调用百度语音识别API
            result = baidu_client.asr(audio_data, 'wav', self.sample_rate, {
                'dev_pid': self.asr_dev_pid,
            })
            
            if result['err_no'] == 0:
                return result['result'][0]
            else:
                print(f"语音识别错误: {result['err_msg']}")
                return None
        except Exception as e:
            print(f"语音识别出错: {str(e)}")
            return None
    
    def get_gemini_response(self, text):
        """获取Gemini的回应"""
        try:
            response = chat.send_message(text)
            return response.text
        except Exception as e:
            return f"抱歉，出现了错误：{str(e)}"
    
    def text_to_speech(self, text):
        """文字转语音"""
        try:
            # 调用百度语音合成API
            result = baidu_client.synthesis(text, self.speech_language, 1, {
                'vol': 5,  # 音量，范围：0-15
                'spd': 5,  # 语速，范围：0-15
                'pit': 5,  # 音调，范围：0-15
                'per': 0,  # 发音人，0为女声，1为男声，3为情感合成-度逍遥，4为情感合成-度丫丫
            })

            # 判断是否合成成功
            if not isinstance(result, dict):
                # 创建临时文件保存音频
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                    f.write(result)
                    temp_file = f.name

                # 播放合成的语音
                try:
                    playsound(temp_file)
                except Exception as e:
                    print(f"播放语音失败: {str(e)}")
                finally:
                    # 删除临时文件
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                return True
            else:
                print(f"语音合成失败: {result}")
                return False
        except Exception as e:
            print(f"语音合成出错: {str(e)}")
            return False
    
    def run(self):
        """运行助手"""
        print("小爱Gemini助手已启动！")
        print("按空格键开始录音，再次按空格键停止。")
        print("按 'q' 退出程序")
        
        while True:
            if keyboard.is_pressed('q'):
                print("\n程序已退出")
                break
                
            if keyboard.is_pressed('space'):
                print("\n开始新的对话...")
                audio_file = self.record_audio()
                if audio_file:
                    # 语音转文字
                    text = self.process_voice_command(audio_file)
                    if text:
                        print(f"\n你说: {text}")
                        
                        # 获取Gemini响应
                        response = self.get_gemini_response(text)
                        print(f"\nGemini: {response}")
                        
                        # 文字转语音
                        if self.text_to_speech(response):
                            print("语音播放完成")
                        else:
                            print("语音合成或播放失败")
            
            time.sleep(0.1)

if __name__ == "__main__":
    assistant = XiaomiGeminiAssistant()
    assistant.run()
