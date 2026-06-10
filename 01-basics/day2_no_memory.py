# 演示：没有 Memory 的 Agent —— 问完就忘
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from agentscope.agent import Agent
from agentscope.message import Msg
from agentscope.model import DeepSeekChatModel
from agentscope.credential import DeepSeekCredential

# 加载 .env 文件中的 API Key
dotenv_path = Path(__file__).resolve().parent.parent / "backend" / ".env"
load_dotenv(dotenv_path)

async def main():
    # 1. 初始化模型（用 .env 里的 DeepSeek Key）
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("请在 backend/.env 中设置 DEEPSEEK_API_KEY")
    credential = DeepSeekCredential(api_key=api_key)
    model = DeepSeekChatModel(
        credential=credential,
        model="deepseek-chat",
    )

    # 2. 创建 Agent —— 但没有配置 Memory
    agent = Agent(
        name="健忘助手",
        model=model,
        system_prompt="你是一个助手。请尽可能简短回答。",
    )

    # 3. 连续问两个问题
    q1 = Msg(name="user", role="user", content=[{"type": "text", "text": "我叫小聪聪"}])
    r1 = await agent.reply(q1)
    print(f"用户: 我叫小聪聪")
    print(f"助手: {r1.content[0].text}\n")

    q2 = Msg(name="user", role="user", content=[{"type": "text", "text": "我叫什么名字？"}])
    r2 = await agent.reply(q2)
    print(f"用户: 我叫什么名字？")
    print(f"助手: {r2.content[0].text}")

asyncio.run(main())
