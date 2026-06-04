# Day1：前后端联调 AgentScope 聊天应用

## 你按发送后，发生了什么？

```
浏览器 (5174) ──HTTP──> FastAPI (8000) ──> DeepSeek API
   ↑                              │
   你看到回复 ←── HTTP 响应 ←──────┘
```

### 第1步：前端把消息包装成请求

你在输入框敲 "你好"，点发送。React 代码做了这件事：

```js
fetch("http://localhost:8000/api/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message: "你好" }),
})
```

把 `"你好"` 打包成 JSON `{ message: "你好" }`，用 HTTP POST 发给后端。

**关键词：HTTP 请求、JSON 序列化**

---

### 第2步：后端收到请求，包装成 AgentScope 消息（Msg）

`backend/main.py` 收到请求后：

```python
msg = Msg(
    name="user",
    role="user",
    content=[{"type": "text", "text": "你好"}],
)
response = await agent.reply(msg)
```

把你发的文本包装成 AgentScope 的 `Msg` 对象（2.0 的 content 必须是 list 格式）。

**关键词：Msg 对象、Agent.reply()**

---

### 第3步：Agent 组装完整 prompt

`agent.reply(msg)` 内部做了：

- 取出 system_prompt：`"你是一个热心的助手，回答简洁明了。"`
- 取出你的消息：`"你好"`
- 拼成给大模型的完整 prompt

```
system: 你是一个热心的助手，回答简洁明了。
user: 你好
```

**这一步是 Agent 的核心价值：管理 system prompt、对话上下文、后续还有 Memory。**

---

### 第4步：调用 DeepSeek 模型

Agent 把拼好的 prompt 发给 `DeepSeekChatModel`，这个模型：

- 读取 API Key（从 `.env` 文件）
- 向 `https://api.deepseek.com/v1/chat/completions` 发请求
- 等 DeepSeek 服务器计算结果

**这一步就是等的那几秒钟。**

---

### 第5步：返回结果，一路传回浏览器

DeepSeek 返回文本 → `DeepSeekChatModel` → `Agent.reply()` → `main.py` → HTTP 响应

后端包装成 JSON：
```json
{ "reply": "你好！我是一个热心的AI助手...", "session_id": "default" }
```

前端 React 收到后，显示在聊天框里。

---

## 一句话总结

> 你打字 → 前端发 HTTP → 后端收到 → AgentScope 组装 prompt → 调 DeepSeek → 返回显示

---

## 你今天做了什么

- [x] 建了 Python 虚拟环境（agentscope-env）
- [x] 装了 agentscope 2.0 + fastapi + uvicorn
- [x] 后端接了 DeepSeek 模型
- [x] 前端 React 跑起来
- [x] 修了 CORS 跨域问题
- [x] 浏览器里跟 Agent 聊上了天

## 踩坑记录

| 问题 | 原因 | 解决 |
|---|---|---|
| 导入不了 ChatAgent | 2.0 改名为 Agent | 用 `from agentscope.agent import Agent` |
| 不认识 config_name | 2.0 模型要传实例对象 | 先实例化 DeepSeekChatModel 再传给 Agent |
| CORS 报错 | 前端端口是 5174，后端只允许 5173 | 在 allow_origins 里加上 5174 |
