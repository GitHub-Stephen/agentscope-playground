# Day 2：拆解 Memory —— 看看 Agent 是怎么"记笔记"的
# 原理：agent.state.context 是一个列表，每次对话自动追加消息
# 每次 reply() 前，整个 context 都会作为历史发给模型

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from agentscope.agent import Agent
from agentscope.message import Msg
from agentscope.model import DeepSeekChatModel
from agentscope.credential import DeepSeekCredential

# 加载 API Key
dotenv_path = Path(__file__).resolve().parent.parent / "backend" / ".env"
load_dotenv(dotenv_path)


def show_memory(agent: Agent, label: str):
    """打印当前 Memory 的内容"""
    ctx = agent.state.context
    print(f"\n{'='*50}")
    print(f"📓 Memory 状态 [{label}] — 共 {len(ctx)} 条消息")
    print(f"{'='*50}")
    if not ctx:
        print("  (空)")
    else:
        for i, msg in enumerate(ctx):
            # 提取消息内容
            text = msg.content[0].text if msg.content else "(无内容)"
            # 根据 role 显示 sender
            sender = msg.role  # 'user' 或 'assistant'
            preview = text[:50] + ("..." if len(text) > 50 else "")
            print(f"  [{i}] {sender}: {preview}")
    print(f"{'='*50}\n")


async def main():
    # 1. 初始化模型
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("请在 backend/.env 中设置 DEEPSEEK_API_KEY")

    credential = DeepSeekCredential(api_key=api_key)
    model = DeepSeekChatModel(
        credential=credential,
        model="deepseek-chat",
    )

    # 2. 创建 Agent
    agent = Agent(
        name="小助手",
        model=model,
        system_prompt="你是一个助手。请尽可能简短回答。",
    )

    # --- 开局：Memory 是空的 ---
    show_memory(agent, "开局")

    # --- 第 1 轮对话 ---
    print(">>> [第1轮] 用户说：我叫小聪聪")
    q1 = Msg(name="user", role="user", content=[{"type": "text", "text": "我叫小聪聪"}])
    r1 = await agent.reply(q1)
    print(f"<<< 助手回复：{r1.content[0].text}")
    show_memory(agent, "第1轮后")

    # --- 第 2 轮对话 ---
    print(">>> [第2轮] 用户问：我叫什么名字？")
    q2 = Msg(name="user", role="user", content=[{"type": "text", "text": "我叫什么名字？"}])
    r2 = await agent.reply(q2)
    print(f"<<< 助手回复：{r2.content[0].text}")
    show_memory(agent, "第2轮后")

    # --- 第 3 轮对话 ---
    print(">>> [第3轮] 用户说：我喜欢吃火锅")
    q3 = Msg(name="user", role="user", content=[{"type": "text", "text": "我喜欢吃火锅"}])
    r3 = await agent.reply(q3)
    print(f"<<< 助手回复：{r3.content[0].text}")
    show_memory(agent, "第3轮后")

    # --- 验证：它还记得全部信息吗？ ---
    print(">>> [第4轮] 用户问：我叫什么名字？我喜欢吃什么？")
    q4 = Msg(
        name="user",
        role="user",
        content=[{"type": "text", "text": "我叫什么名字？我喜欢吃什么？"}],
    )
    r4 = await agent.reply(q4)
    print(f"<<< 助手回复：{r4.content[0].text}")
    show_memory(agent, "第4轮后")

    print("\n✅ 总结：Memory 原理")
    print("   - agent.state.context 是一个 Python list")
    print("   - 每轮对话都会自动追加 user 消息 + assistant 回复")
    print("   - 下次 reply() 时，整个 context 作为历史发给 LLM")
    print(f'   - 所以模型能"记住"前面说过的话')


asyncio.run(main())
