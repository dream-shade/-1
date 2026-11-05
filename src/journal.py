"""每日 AI 复盘日记 —— 修复版
用法：在本文件所在目录（或任意目录）运行 python journal.py
输入今日记录，单独一行输入 eof / eod / EOF / exit / quit / done 结束，或直接按 Ctrl+Z 再回车结束。
"""

import os
import re
import sys
from datetime import date
from pathlib import Path

from openai import OpenAI

# 控制台编码兜底：避免 Windows GBK 终端打印 emoji / 中文时报错
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ==================== 路径固定到脚本所在目录（关键修复） ====================
# 以前用的是相对路径 "key.txt" / "my_journal.md"，
# 只要运行时的工作目录不是 D:\mycode，文件就会跑到别的地方去（或读不到密钥）。
BASE_DIR = Path(__file__).resolve().parent
KEY_PATH = BASE_DIR / "key.txt"
JOURNAL_PATH = BASE_DIR / "my_journal.md"

# 是否把「发给 AI 的原文」也一起存进日记。
# False（默认）：只存 AI 总结，日记干净，不会塞进导师发的一大段任务单。
# True：原文 + AI 总结都存。
SAVE_RAW = False


def drop_sections_for(text, day):
    """删掉指定日期的全部记录段，用来「替换」而不是越堆越多"""
    out, skipping = [], False
    for ln in text.split("\n"):
        if ln.strip() == f"## {day}":
            skipping = True
            continue
        if skipping and re.match(r"^## 20\d\d-\d\d-\d\d", ln.strip()):
            skipping = False
        if not skipping:
            out.append(ln)
    return "\n".join(out)


def explain_error(e):
    """把报错翻译成人话，直接告诉你下一步干什么"""
    code = getattr(e, "status_code", None)
    msg = str(e)
    print("─" * 52)
    if code == 401 or "Authentication" in msg or "authentication_error" in msg:
        print("原因：API Key 无效 —— 平台上被删除、重新生成过或被禁用")
        print("解决：打开 https://platform.deepseek.com/api_keys")
        print("      重新生成一个 Key，完整覆盖粘贴进 key.txt")
        print("      （不要有空格、换行，不要漏掉开头的 sk-）")
        print("      注意：Key 只在创建那一次完整显示，关掉就再也看不到了")
    elif code == 402 or "Insufficient Balance" in msg:
        print("原因：DeepSeek 账户余额不足")
        print("解决：去 https://platform.deepseek.com/top_up 充值后再跑一次")
    elif code == 429:
        print("原因：请求太频繁被限流，等一分钟再试")
    elif code is not None and 500 <= code < 600:
        print(f"原因：DeepSeek 服务端异常（{code}）——不是你的问题，稍后重试即可")
    elif any(k in msg for k in ("Connection", "Timeout", "timed out", "ConnectTimeout")):
        print("原因：连不上 DeepSeek —— 网络或代理问题，检查网络后重试")
    else:
        print("原因：未知错误，完整信息见上方")
    print("─" * 52)
BASE_DIR = Path(__file__).resolve().parent
KEY_FILE = BASE_DIR / "key.txt"


# ==================== 1. 读取密钥并提前自检 ====================
try:
    keys = KEY_FILE.read_text(encoding="utf-8").strip().splitlines()
   
    DS_KEY = keys[3].strip()       # DeepSeek 密钥
except FileNotFoundError:
    print(f"找不到密钥文件：{KEY_PATH}")
    sys.exit(1)

if not DS_KEY:
    print("key.txt 内容为空，请填入 DeepSeek API Key。")
    sys.exit(1)

client = OpenAI(api_key=DS_KEY, base_url="https://api.deepseek.com", timeout=60)

# 先用 1 个 token 探一下，别让你辛辛苦苦打完一大段才发现 Key 是坏的
print("正在检查 API Key 是否有效...")
api_ok = True
try:
    client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "ping"}],
        max_tokens=1,
        timeout=30,
    )
    print("✅ API Key 正常，可以开始写今天的记录了。\n")
except Exception as e:
    print(f"\n❌ API Key 自检未通过：{type(e).__name__}: {e}")
    explain_error(e)
    try:
        go_on = input("仍要继续输入吗？[y 继续（只存原始记录） / n 退出先修 Key]：").strip().lower()
    except EOFError:
        go_on = "y"
    if go_on not in {"y", "yes", ""}:
        print("已退出。修好 Key 后再来跑一次。")
        sys.exit(0)

# ==================== 2. 收集输入 ====================
today = date.today()
print(f"📅 今天：{today}")
print("输入今日成果，结束后单独一行输入 eof / eod / exit / quit / done（也可直接 Ctrl+Z 后回车）")

lines = []
try:
    while True:
        line = input()
        # 容错：忽略大小写和首尾空格（以前只认小写 "eof"，输入 "eod"/"EOF" 都不认，会一直卡着）
        if line.strip().lower() in {"eof", "eod", "exit", "quit", "end", "done"}:
            break
        lines.append(line)
except EOFError:
    # Ctrl+D / Ctrl+Z 直接结束输入 —— 以前这里会直接崩溃，一行都写不进去
    print()
    print("（检测到输入结束符，按当前内容提交）")
except KeyboardInterrupt:
    print("\n（已中断输入，按当前内容提交）")

user_record = "\n".join(lines).strip()

if not user_record:
    print("没有输入任何内容，未写入日记。")
    sys.exit(0)

# 防止手滑：内容过短（比如只敲了几个字母）时拦一下
if len(user_record) < 5:
    try:
        sure = input(f"内容只有 {len(user_record)} 个字：「{user_record}」，确定提交吗？(y/n) ").strip().lower()
    except EOFError:
        sure = "y"
    if sure not in {"y", "yes", ""}:
        print("已取消，未写入日记。")
        sys.exit(0)

# ==================== 3. 调用 AI 复盘 ====================
prompt = (
    f"以上是我今日的成果：{user_record}。"
    "请总结今天的记录，简要一点，最后仅把总结返回给我"
)

ai_reply = None
if api_ok:
    print(f"已收到 {len(user_record)} 字，正在交给 AI 复盘...")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            timeout=60,
        )
        ai_reply = (response.choices[0].message.content or "").strip()
        print(f"\nAI 总结：\n{ai_reply}\n")
    except Exception as e:
        print(f"\nAI 总结失败：{type(e).__name__}: {e}")
        explain_error(e)
        print("今天的原始记录仍会保存，不会丢失。")

# ==================== 4. 写入日记（永远执行） ====================
if ai_reply:
    if SAVE_RAW:
        body = f"**我的记录**\n{user_record}\n\n**AI 复盘**\n{ai_reply}\n"
    else:
        body = f"{ai_reply}\n"  # 只存总结，不存发给 AI 的原文
else:
    # AI 挂了才存原文 —— 否则你今天打的字就真没了
    body = f"{user_record}\n\n> AI 总结失败，以上为原始记录。\n"

block = f"\n## {today}\n\n{body}\n"

# 防重复：今天已经记过就让你选是追加还是替换
if JOURNAL_PATH.exists():
    old = JOURNAL_PATH.read_text(encoding="utf-8")
    count = len(re.findall(rf"^##\s*{today}\s*$", old, flags=re.M))
    if count:
        print(f"提示：今天已存在 {count} 条记录。")
        try:
            mode = input("直接回车 = 再追加一条；输入 r = 用本次替换掉今天已有的：").strip().lower()
        except EOFError:
            mode = ""
        if mode in {"r", "replace"}:
            JOURNAL_PATH.write_text(drop_sections_for(old, str(today)), encoding="utf-8")
            print("已清掉今天已有的记录，接下来写新的这一条。")

try:
    with JOURNAL_PATH.open("a", encoding="utf-8") as f:
        f.write(block)
        f.flush()
        os.fsync(f.fileno())  # 立刻落盘，防止程序被强制结束时内容还留在缓冲区
except Exception as e:
    print(f"写入失败：{type(e).__name__}: {e}")
    sys.exit(1)

print(f"✅ 已成功写入：{JOURNAL_PATH}")
print(f"   当前日记共 {len(JOURNAL_PATH.read_text(encoding='utf-8'))} 字")
print("--- 本次写入的内容 ---")
print(block)
