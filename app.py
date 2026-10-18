import streamlit as st
import os
from datetime import date
from openai import OpenAI
st.title("我的ai第二大脑")
with open("key.txt","r",encoding="utf-8") as f:
    my_key=f.read().strip()
client=OpenAI(
     api_key=my_key,
    base_url="https://api.deepseek.com"
)
st.sidebar.title("历史记录")
if os.path.exists("my_sum.md"):
    with open("my_journal.md","r",encoding="utf-8") as f:
        history_content=f.read()
    with st.sidebar.expander("点击展开过去的记忆"):
        st.markdown(history_content)
else:
    st.sidebar.info("还没有历史记录哦")

user_input=st.text_area("今天的收获？烦恼？",height=200)
if st.button("让ai替我复盘"):
    if user_input:
        with st.spinner("ai正在思考"):
            prompt=f"今日记录如下\n{user_input}\n请帮我总结并给我建议"
            response=client.chat.completions.create( 
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
            )
        ai_reply=response.choices[0].message.content
        st.success("复盘完成")
        st.write(ai_reply)
        today=date.today()
        with open("my_sum.md","a",encoding="utf-8") as f:
            f.write(f"{today}\n我的记录\n{user_input}\n{ai_reply}")
        st.info("以自动保存到历史记录！刷新网站左侧即可查看")

    else:
        st.warning("请输入今天的记录")