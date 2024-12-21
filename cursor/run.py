import asyncio
from main import XiaoAiGeminiBridge
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def main():
    bridge = XiaoAiGeminiBridge(
        xiaomi_token=os.getenv('XIAOMI_TOKEN'),
        xiaomi_ip=os.getenv('XIAOMI_IP'),
        gemini_api_key=os.getenv('GEMINI_API_KEY')
    )
    await bridge.start()

if __name__ == "__main__":
    asyncio.run(main()) 