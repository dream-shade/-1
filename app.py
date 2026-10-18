import streamlit as st
from openai import OpenAI
st.title("我的ai第二大脑")
with open("key.txt","r",encoding="utf-8") as f:
    my_key=f.read().strip()
client=OpenAI(
     api_key=my_key,
    base_url="https://api.deepseek.com"
)
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
    else:
        st.warning("请输入今天的记录")