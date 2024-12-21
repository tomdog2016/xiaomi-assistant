import os
import google.generativeai as genai
from dotenv import load_dotenv

class GeminiService:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])
    
    def send_message(self, message: str) -> str:
        """发送消息到Gemini并获取回复"""
        try:
            response = self.chat.send_message(message)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def reset_chat(self):
        """重置对话历史"""
        self.chat = self.model.start_chat(history=[])
