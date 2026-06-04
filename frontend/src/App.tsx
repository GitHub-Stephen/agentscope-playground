import { useState, useRef, useEffect } from "react";
import "./App.css";

const API_BASE = "http://localhost:8000";

interface Message {
  role: "user" | "agent";
  content: string;
  sessionId?: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "agent",
      content: "你好！我是 AgentScope Playground 的 ChatAgent。有什么想聊的？",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [health, setHealth] = useState<string>("检查中...");
  const bottomRef = useRef<HTMLDivElement>(null);

  // 页面加载时检查后端连接
  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((r) => r.json())
      .then((data) => {
        setConnected(true);
        setHealth("已连接");
      })
      .catch(() => {
        setConnected(false);
        setHealth("未连接");
      });
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg.content }),
      });
      const data = await res.json();
      const agentMsg: Message = {
        role: "agent",
        content: data.reply,
        sessionId: data.session_id,
      };
      setMessages((prev) => [...prev, agentMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "agent",
          content: "⚠️ 后端连接失败，请确认 FastAPI 是否已启动",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      {/* 顶栏 */}
      <header className="header">
        <h1>AgentScope Playground</h1>
        <div className="status">
          <span className={`dot ${connected ? "dot-ok" : "dot-err"}`} />
          <span className="status-text">{health}</span>
        </div>
      </header>

      {/* 聊天区 */}
      <main className="chat-area">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="avatar">{msg.role === "agent" ? "🤖" : "👤"}</div>
            <div className="bubble">
              <p>{msg.content}</p>
              {msg.sessionId && (
                <span className="session-tag">session: {msg.sessionId}</span>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message agent">
            <div className="avatar">🤖</div>
            <div className="bubble thinking">
              <span className="dot-pulse" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </main>

      {/* 输入区 */}
      <footer className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入消息..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>
          {loading ? "..." : "发送"}
        </button>
      </footer>
    </div>
  );
}

export default App;
