"""Day1 纪念：第一个 AgentScope 2.0 Agent
跑法：python3 01-basics/hello_agent.py
说明：不依赖前端和后端，直接调 DeepSeek 模型，终端看结果
"""

import os
import sys
import asyncio
from pathlib import Path

# .env 文件在 backend/ 目录下，从那里读
env_path = Path(__file__).resolve().parent.parent / "backend" / ".env"
if env_path.exists():
    for line in env_path.read_text().strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from agentscope.agent import Agent
from agentscope.message import Msg
from agentscope.model import DeepSeekChatModel
from agentscope.credential import DeepSeekCredential


async def main():
    # ---- 从环境变量读 Key ----
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    model_name = "deepseek-chat"

    if not api_key:
        print("❌ 未找到 DEEPSEEK_API_KEY")
        print(f"   在 {env_path} 里写 DEEPSEEK_API_KEY=你的key 即可")
        sys.exit(1)

    model = DeepSeekChatModel(
        credential=DeepSeekCredential(api_key=api_key),
        model=model_name,
    )

    agent = Agent(
        name="小助手",
        system_prompt="你是一个热心的助手，回答简洁明了。",
        model=model,
    )

    msg = Msg(
        name="user",
        role="user",
        content=[{"type": "text", "text": "你好！请用一句话介绍你自己。"}],
    )

    response = await agent.reply(msg)

    print(f"\n🤖 {response.name}: {response.content}")
    print("\n✅ 第一个 Agent 跑通啦！")


if __name__ == "__main__":
    asyncio.run(main())
