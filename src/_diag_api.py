# 临时诊断：查明 DeepSeek API 调用失败的具体原因
import sys
from pathlib import Path
from openai import OpenAI

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
my_key = (BASE / "key.txt").read_text(encoding="utf-8").strip()
print("key 长度:", len(my_key), "| 前缀:", my_key[:5], "| 后缀:", my_key[-4:])

client = OpenAI(api_key=my_key, base_url="https://api.deepseek.com", timeout=60)

try:
    r = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "回复两个字：正常"}],
        max_tokens=10,
    )
    print("API 成功 ->", r.choices[0].message.content)
except Exception as e:
    print("失败类型:", type(e).__name__)
    print("完整错误:", e)
    st = getattr(e, "status_code", None)
    print("HTTP 状态码:", st)
    body = getattr(e, "body", None)
    print("响应体:", body)
    resp = getattr(e, "response", None)
    if resp is not None:
        try:
            print("响应文本:", resp.text)
        except Exception:
            pass
