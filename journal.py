from datetime import date
from openai import OpenAI

# 1. 获取今天日期（加括号！）
today = date.today()

# 2. 收集输入并构造提示词
print("输入今日成果,按eof结束")
lines=[]
while True:
    line=input()
    if line=="eof":
        break
    else:
        lines.append(line)
user_record="\n".join(lines)


prompt = f"以上是我今日的成果：{user_record}。请总结今天的记录，简要一点，最后仅把总结返回给我"

# 3. 读密钥
with open("key.txt", "r", encoding="utf-8") as f:
    my_key = f.read().strip()

# 4. 调 API
client = OpenAI(
    api_key=my_key,
    base_url="https://api.deepseek.com"
)

try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )
    ai_reply = response.choices[0].message.content
    print(f"AI 总结：{ai_reply}")

    # 5. 写入文件（用 write，不是 read）
    h = f"## {today}\n\n{ai_reply}\n\n"
    with open("my_journal.md", "a", encoding="utf-8") as f:
        f.write(h)
    print("✅ 已成功记入日记！")

except Exception as e:
    print(f"出错了：{e}")