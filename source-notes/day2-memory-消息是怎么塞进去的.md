# AgentScope 源码课：消息是怎么塞进 Memory 的？

> 系列：Coach 别跑！AgentScope 源码拆解
> 本篇：第 2 课 · Memory 的秘密抽屉
> 前情：第 1 课我们已经跑通了「创建 Agent → 对话」

---

## ① 「代码里根本没写『存盘』啊？」

教练，我反复看了好几遍昨天写的代码——

```python
agent = Agent(name="小助手", model=model, system_prompt="...")

q1 = Msg(role="user", content="我叫小聪聪")
r1 = await agent.reply(q1)

q2 = Msg(role="user", content="我叫什么名字？")
r2 = await agent.reply(q2)
# 👆 它居然答对了！但哪行代码告诉它「记住之前的话」？
```

没有 `save()`，没有 `memory.store()`，没有 `append()`。

**Agent 凭什么记得我叫小聪聪？**

---

## ② 「你递纸条的时候，已经存了」

教练推了推眼镜：你把 `agent.reply()` 当成一个「问问题」的动作，但它其实干了**四件事**。

用伪代码还原一下内部逻辑：

```
agent.reply(用户消息):
    ┌─────────────────────────────────────┐
    │ ① 把用户消息塞进抽屉                  │
    │    context.追加(用户消息)             │
    │                                     │
    │ ② 把整本对话发给大模型                 │
    │    prompt = context.全部内容()         │
    │    LLM.推理(prompt)                  │
    │                                     │
    │ ③ 把大模型的回复也塞进抽屉              │
    │    context.追加(LLM回复)              │
    │                                     │
    │ ④ 把回复返回给你                      │
    │    return LLM回复                    │
    └─────────────────────────────────────┘
```

**你递纸条的那一刻，它已经帮你存档了。**

---

## ③ 「那我看看抽屉里有什么」

徒弟好奇心起来了：那我能不能偷看一眼这个「抽屉」？

教练：能。它叫 `agent.state.context`，就是一个普普通通的 Python 列表。

```python
# 偷偷看一眼 Agent 的记忆抽屉
def 偷看抽屉(agent):
    抽屉 = agent.state.context
    print(f"抽屉里共有 {len(抽屉)} 条消息：")
    for 消息 in 抽屉:
        print(f"  [{消息.角色}] {消息.内容}")

# 开局：抽屉是空的
偷看抽屉(agent)
# → 抽屉里共有 0 条消息

# 第 1 轮
await agent.reply(Msg("我叫小聪聪"))
偷看抽屉(agent)
# → 抽屉里共有 2 条消息：
#    [user] 我叫小聪聪
#    [assistant] 你好小聪聪！

# 第 2 轮
await agent.reply(Msg("我今年 25 岁"))
偷看抽屉(agent)
# → 抽屉里共有 4 条消息：
#    [user] 我叫小聪聪
#    [assistant] 你好小聪聪！
#    [user] 我今年 25 岁
#    [assistant] 好的，记住了！
```

**真相大白**：每调用一次 `reply()`，抽屉里就多两条——你的话 + AI 的回话。

---

## ④ 「如果我偷偷把抽屉清空呢？」

徒弟露出坏笑：那我要是手动清空它呢？

```python
# 第 3 轮之前，偷偷清空抽屉
agent.state.context = []

await agent.reply(Msg("我叫什么名字？"))
# → Agent 回答：抱歉，我不清楚你的名字……
```

教练点头：**失忆了。**

因为大模型每次看到的是 `context` 里的全部内容。你清空了，它就等于「没见过之前的对话」。所以 Agent 的「记忆力」本质就是**这个列表还在不在**。

---

## ⑤ 「所以这个抽屉……」

徒弟若有所思：

| 我的理解 | 对不对 |
|---------|--------|
| context 是一个 Python list | ✅ |
| reply() 帮我往里塞，不用手动 append | ✅ |
| 每次调用塞两条（我的 + AI 的） | ✅ |
| 清空就失忆 | ✅ |
| 大模型本身不记东西，全看 context | ✅ |

教练笑：**满分。**

---

## ⑥ 课后作业

既然 `context` 是个 list，每次对话都往后追加……那如果聊了 100 轮呢？

> **问题**：context 会无限膨胀吗？AgentScope 有没有什么机制来防止它撑爆？

（提示：跟「压缩」有关。下节课揭晓。）

---

*本系列用伪代码讲解 AgentScope 源码原理，欢迎转发给同样好奇的朋友。*
*关注「小聪聪的 AI 学习笔记」，每周拆一个源码零件。*
