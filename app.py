import streamlit as st
import os
import re
from datetime import date
from openai import OpenAI

st.title("🧠 我的 AI 第二大脑")

# 1. 读取密钥
with open("key.txt", "r", encoding="utf-8") as f:
    my_key = f.read().strip()

client = OpenAI(
    api_key=my_key,
    base_url="https://api.deepseek.com"
)

# ================= 侧边栏逻辑 =================
st.sidebar.title("📜 历史记录")

# 只有存在日记文件时，才执行侧边栏逻辑
if os.path.exists("my_journal.md"):
    with open("my_journal.md", "r", encoding="utf-8") as f:
        history_content = f.read()
    
    # 展开历史记录
    with st.sidebar.expander("点击展开过去的记忆"):
        st.markdown(history_content)
        
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 阶段性复盘")
    
    # 滑动条
    days_to_review = st.sidebar.slider("选择最近 N 天复盘", min_value=1, max_value=30, value=7)
    
    
    if st.sidebar.button("生成近期周报"):
        with st.spinner("AI 正在回顾你的历史..."):
            # 按日期切分（假设你的日记里日期格式是 ## 2026-10-19 这种）
            # 注意：如果以前的日记格式不同，这里可能匹配不到
            pattern = r"##\s*\d{4}-\d{2}-\d{2}" 
            blocks = re.split(pattern, history_content)
            valid_blocks = [b.strip() for b in blocks[1:] if b.strip()]
            
            recent_records = valid_blocks[-days_to_review:]
            
            if recent_records:
                combined_text = "\n---\n".join(recent_records)
                weekly_prompt = f"这是我最近 {days_to_review} 天的日记记录：\n{combined_text}\n请帮我汇总提炼，写一份阶段性的复盘周报，指出我的进步点和需要改进的地方。"
                
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": weekly_prompt}]
                )
                weekly_reply = response.choices[0].message.content
                
                st.info(f"📊 最近 {days_to_review} 天的 AI 周报生成完毕！")
                st.markdown(weekly_reply)
            else:
                st.sidebar.warning("没有找到符合条件的记录，可能是你的日记格式不匹配。")
else:
    st.sidebar.info("还没有历史记录哦，快在右侧写下第一篇吧！")


# ================= 主页面逻辑 =================
user_input = st.text_area("今天的收获？烦恼？", height=200)

if st.button("让 AI 替我复盘"):
    if user_input:
        with st.spinner("AI 正在思考..."):
            prompt = f"今日记录如下\n{user_input}\n请帮我总结并给我建议"
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}]
            )
            ai_reply = response.choices[0].message.content
            
            st.success("复盘完成")
            st.write(ai_reply)
            
            # 保存到文件
            today = date.today()
            with open("my_journal.md", "a", encoding="utf-8") as f:
                # 注意这里日期前面加上了 ## ，这样正则表达式才能抓取到
                f.write(f"\n\n## {today}\n\n**我的记录**\n{user_input}\n\n**AI 复盘**\n{ai_reply}")
            
            st.info("✅ 已自动保存！刷新网页左侧查看历史。")
    else:
        st.warning("请输入今天的记录哦！")