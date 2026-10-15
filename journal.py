from datetime import date
today=date.today
harvest=input("输入ai的总结"+"以上是我今日的成果，请总结今天的记录，简要一点，最后仅把总结返回给我")

from openai import OpenAI
with open("key.txt","r",encoding="utf-8") as f:
    my_key=f.read().strip()


client = OpenAI(
    api_key=my_key,
    base_url="https://api.deepseek.com"
)
response = client.chat.completions.create(
        model="deepseek-chat",  # 记得填写具体的模型名称
        messages=harvest
            )
ai_reply= response.choices[0].message.content
            # 注意：choices 是复数
print("AI:", response.choices[0].message.content)
h=f"{ai_reply}\n{today}"
with open("markdown.txt","a",encoding="utf-8") as f:
    f.read(h)
