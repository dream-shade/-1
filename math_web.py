import streamlit as st
from pathlib import Path
from openai import OpenAI
from aip import AipOcr
import json

st.title("🧠 AI 高数解题器")
st.markdown("支持拍照批量解析与文字直接输入，公式自动渲染。")

# ================= 1. 密钥与初始化 =================
BASE_DIR = Path(__file__).resolve().parent
KEY_FILE = BASE_DIR / "key.txt" if (BASE_DIR / "key.txt").exists() else BASE_DIR.parent / "key.txt"

# 确保 data 文件夹存在，并定义错题本路径
DATA_DIR = BASE_DIR.parent / "data" if (BASE_DIR.parent / "data").exists() else BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
notes_path = DATA_DIR / "math_notes.json"

try:
    keys = KEY_FILE.read_text(encoding="utf-8").strip().splitlines()
    APP_ID = keys[0].strip()       
    API_KEY = keys[1].strip()      
    SECRET_KEY = keys[2].strip()   
    DS_KEY = keys[3].strip()   
except Exception as e:
    st.error(f"❌ 读取 key.txt 失败: {e}")
    st.stop()

ocr_client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
ds_client = OpenAI(api_key=DS_KEY, base_url="https://api.deepseek.com")


# ================= 2. 核心函数区 =================
def ask_ai(prompt_text):
    """公共的大模型调用函数"""
    try:
        response = ds_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt_text}]
        )
        reply = response.choices[0].message.content
        # 强制替换 LaTeX 语法，确保 Streamlit 能渲染公式
        reply = reply.replace(r"\[", "$$").replace(r"\]", "$$")
        reply = reply.replace(r"\(", "$").replace(r"\)", "$")
        return reply, None
    except Exception as e:
        return None, f"调用 AI 失败: {e}"

def process_image(file_obj):
    """处理图片:OCR + 大模型解题"""
    file_obj.seek(0) # 核心修复：把指针拨回开头
    image_bytes = file_obj.read()
    
    result = ocr_client.basicGeneral(image_bytes)
    if 'words_result' not in result:
        return None, f"OCR 识别失败: {result}"
    
    text = "\n".join([item['words'] for item in result['words_result']])
    
    prompt = f"""
    请详细解答这道题。题目由ocr识别，请自行甄别字符。
    要求：所有的数学公式和变量，请全部使用 $$ 包裹（例如：$$x^2$$），以便网页渲染。
    题目如下：
    {text}
    """
    reply, error = ask_ai(prompt)
    if error:
        return text, error
    return text, reply

def save_to_file(question, answer):
    """将题目和解析保存到 JSON 错题本"""
    if notes_path.exists():
        try:
            notes = json.loads(notes_path.read_text(encoding="utf-8"))
        except Exception as e:
            st.error(f"读取历史记录报错: {e}")
            notes = []
    else:
        notes = []
        
    notes.append({"question": question, "answer": answer})
    notes_path.write_text(json.dumps(notes, ensure_ascii=False, indent=4), encoding="utf-8")


# ================= 3. 前端 UI 渲染 =================
# --- 侧边栏：历史错题本 ---
st.sidebar.title("📚 历史错题本")
if notes_path.exists():
    try:
        notes_data = json.loads(notes_path.read_text(encoding="utf-8"))
        for i, note in enumerate(reversed(notes_data)):
            with st.sidebar.expander(f"历史题 {len(notes_data) - i}"):
                st.write(note['question'])
                st.markdown(note['answer'])
    except Exception as e:
        st.sidebar.error("读取历史记录失败")
else:
    st.sidebar.info("暂无历史错题")

# --- 主界面：Tabs ---
tab1, tab2 = st.tabs(["📷 拍照批量解析", "⌨️ 文字直接输入"])

# 标签页 1：拍照解析
with tab1:
    uploaded_files = st.file_uploader(
        "请选择多张图片（可多选）", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"成功接收 {len(uploaded_files)} 张图片！")
        for idx, file in enumerate(uploaded_files, start=1):
            st.subheader(f"第 {idx} 题：{file.name}")
            st.image(file, width=250)
            
            with st.spinner("AI 正在思考中..."):
                text, reply = process_image(file)
                
            if reply and not reply.startswith("OCR") and not reply.startswith("调用 AI"):
                with st.expander("查看 OCR 识别文字"):
                    st.write(text)
                st.markdown("### 📝 解析结果")
                st.markdown(reply)
                
                # 核心：保存到错题本
                save_to_file(text, reply)
            else:
                st.error(reply)
            st.divider()

# 标签页 2：文字输入
with tab2:
    user_text = st.text_area("请输入题目内容（支持直接复制粘贴文字）：", height=150)
    
    if st.button("解析文字题目", type="primary"):
        if user_text:
            with st.spinner("AI 正在思考中..."):
                prompt = f"""
                请详细解答这道题。
                要求：所有的数学公式和变量，请全部使用 $$ 包裹（例如：$$x^2$$），以便网页渲染。
                题目如下：
                {user_text}
                """
                reply, error = ask_ai(prompt)
                
                if error:
                    st.error(error)
                else:
                    st.markdown("### 📝 解析结果")
                    st.markdown(reply)
                    
                    # 核心：保存到错题本
                    save_to_file(user_text, reply)
        else:
            st.warning("请先输入题目内容！")

    # 核心：新增的追问功能
    st.divider()
    st.subheader("💬 对解析有疑问？继续追问 AI 老师")
    follow_up = st.chat_input("例如：请把第一步再详细解释一下...")
    if follow_up:
        with st.spinner("AI 导师正在回答你的追问..."):
            reply, error = ask_ai(follow_up)
            if error:
                st.error(error)
            else:
                st.info("👨‍🏫 AI 导师回复：")
                st.markdown(reply)