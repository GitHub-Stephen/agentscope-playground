"""AgentScope Playground - FastAPI 后端

提供 AgentScope Agent 的 API，供前端 React 调用。
第一周目标：跑通 Agent 聊天。
"""

import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── 自动加载 .env 文件（如果有的话） ──
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    for line in env_path.read_text().strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# ── AgentScope 2.0 ──
from agentscope.agent import Agent
from agentscope.message import Msg
from agentscope.model import DeepSeekChatModel
from agentscope.credential import DeepSeekCredential

# ── 初始化 Agent ──
api_key = os.getenv("DEEPSEEK_API_KEY", "")
if not api_key:
    print("⚠️  未设置 DEEPSEEK_API_KEY，Agent 无法使用")
    print("   请在 backend/.env 里添加: DEEPSEEK_API_KEY=你的key")
    agent = None
else:
    model = DeepSeekChatModel(
        credential=DeepSeekCredential(api_key=api_key),
        model="deepseek-chat",
    )
    agent = Agent(
        name="小助手",
        system_prompt="你是一个热心的助手，回答简洁明了。",
        model=model,
    )
    print("✅ Agent 初始化成功，等待对话...")

app = FastAPI(title="AgentScope Playground API", version="0.1.0")

# 允许前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 数据模型 ──

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str


# ── 路由 ──

@app.get("/")
def root():
    return {"status": "ok", "name": "AgentScope Playground", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """AgentScope Agent 聊天接口"""
    if agent is None:
        return ChatResponse(
            reply="❌ Agent 未初始化，请先配置 DEEPSEEK_API_KEY",
            session_id=req.session_id or "default",
        )

    msg = Msg(
        name="user",
        role="user",
        content=[{"type": "text", "text": req.message}],
    )
    response = await agent.reply(msg)

    # 从 response 里提取文本
    reply_text = response.content[0].text if hasattr(response.content[0], "text") else str(response.content)

    return ChatResponse(
        reply=reply_text,
        session_id=req.session_id or "default",
    )
