"""
Day3: Context 压缩机制摸拟演示
师父带徒弟 — 感受一下 AgentScope 的 context 怎么"瘦身"

核心流程：
  1. context 慢慢堆消息 → 超 80% 触发
  2. 一分为二：旧的去压缩，最近的留下
  3. 旧对话喂给 LLM 生成摘要 → 用摘要替换
  4. context 瘦身成功
"""

from agentscope.agent import ContextConfig


def print_section(title):
    print()
    print("=" * 50)
    print(f"  {title}")
    print("=" * 50)


# =========================================
# Step 0: 看看 ContextConfig 有哪些旋钮
# =========================================
print_section("0. 默认配置一览")

cfg = ContextConfig()
print(f"触发器阈值:   {cfg.trigger_ratio:.0%} 的模型窗口")
print(f"保留比例:       {cfg.reserve_ratio:.0%} 给最近消息")
print(f"工具结果上限:   {cfg.tool_result_limit} tokens")
print()

# 假设用 deepseek-chat 模型，窗口 65536
MODEL_WINDOW = 65536
trigger_line = int(MODEL_WINDOW * cfg.trigger_ratio)
reserve_line = int(MODEL_WINDOW * cfg.reserve_ratio)

print(f"假设模型窗口 = {MODEL_WINDOW} tokens（deepseek-chat）")
print(f"  → context 超过 {trigger_line} tokens 就会触发压缩")
print(f"  → 压缩后保留最近 {reserve_line} tokens 的对话")
print(f"  → 旧对话要缩到 {MODEL_WINDOW - trigger_line} tokens 以内")

# =========================================
# Step 1: 模拟 context 慢慢塞满
# =========================================
print_section("1. 模拟：context 从空到满")

# 用列表模拟 context，每条消息算 500 tokens
messages = []
tokens_per_msg = 500

i = 1
while i * tokens_per_msg < trigger_line:
    messages.append(f"[第{i}轮] 用户说xxx，助手回复xxx...")
    current_tokens = i * tokens_per_msg
    pct = current_tokens / MODEL_WINDOW * 100
    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    print(f"  msg#{i:3d}  | {bar} | {current_tokens:6d} tokens ({pct:5.1f}%)")
    i += 1

# 最后一条刚好超阈值
messages.append(f"[第{i}轮] 这条一加上，context 就超 80% 了！")
current_tokens = (i) * tokens_per_msg
pct = current_tokens / MODEL_WINDOW * 100
print(f"  msg#{i:3d}  | {'█' * 20} |超 80%！ 压缩即将触发...")

print()
print(f"  → 一共 {len(messages)} 轮对话，context 已膨胀到 ~{current_tokens} tokens")

# =========================================
# Step 2: 一分为二
# =========================================
print_section("2. 压缩：把 context 一分为二")

# 从后往前数：保留最近的 reserve_ratio 的 token
reserved_tokens = int(MODEL_WINDOW * cfg.reserve_ratio)
msgs_to_reserve_count = reserved_tokens // tokens_per_msg

msgs_to_compress = messages[:-msgs_to_reserve_count]
msgs_to_reserve = messages[-msgs_to_reserve_count:]

print(f"  保留最近的 {reserved_tokens} tokens")
print(f"  → 旧对话（去压缩）: {len(msgs_to_compress)} 条")
print(f"  → 最近消息（保留）: {len(msgs_to_reserve)} 条")
print()
print("  《去压缩的旧消息》")
for m in msgs_to_compress[:3]:
    print(f"    {m}")
print(f"    ... 共 {len(msgs_to_compress)} 条")
print()
print("  《保留的最近消息》")
for m in msgs_to_reserve:
    print(f"    {m}")

# =========================================
# Step 3: 模拟 LLM 生成摘要
# =========================================
print_section("3. LLM 把旧对话浓缩成结构化摘要")

# 这是 LLM 实际会生成的摘要（模拟）
summary = """<system-info>Here is a summary of your previous work
# Task Overview
用户在学习 AgentScope 的 context 压缩机制，想知道 context 满了怎么办。

# Current State
已掌握核心原理：context 超 80% 触发压缩，旧对话被 LLM 浓缩成结构化摘要，
最近的 10% 对话保留不动。

# Important Discoveries
1. 压缩不是裁剪，是用摘要替换旧对话，信息不丢失
2. 有 3 层兜底机制（reserve 降级、逐条剔除、offloader 落盘）
3. 边界消息按 content block 粒度拆分，保证 tool_call/result 成对

# Next Steps
可以继续探索 Offloader 机制，或者 ReAct 循环。

# Context to Preserve
用户偏好师父带徒弟节奏，做笔记到 source-notes/ 目录。
</system-info>"""

print(summary)
print()
print(f"  摘要共 ~{len(summary)} 字符 ≈ 约 200 tokens")

# =========================================
# Step 4: 压缩完成
# =========================================
print_section("4. 压缩完成！context 瘦身效果")

after_compress_tokens = (
    len(summary) // 4  # 粗略按 4 字符 ≈ 1 token
    + len(msgs_to_reserve) * tokens_per_msg
)
compressed_pct = after_compress_tokens / MODEL_WINDOW * 100

before = current_tokens
after = after_compress_tokens
print(f"  压缩前: {before:6d} tokens ({before/MODEL_WINDOW*100:.1f}%)")
print(f"  压缩后: {after:6d} tokens ({compressed_pct:.1f}%)")
print(f"  瘦身:   {before - after:6d} tokens ({(1 - after/before)*100:.0f}%)")
print()

bar_before = "█" * int(before / MODEL_WINDOW * 100 / 5)
bar_after = "█" * int(compressed_pct / 5)
print(f"  压缩前: [{bar_before.ljust(20, '░')}] {before/MODEL_WINDOW*100:.0f}%")
print(f"  压缩后: [{bar_after.ljust(20, '░')}]  {compressed_pct:.0f}%")
print()
print("  现在 Agent 可以继续愉快地聊天了 🎉")
