from openai import OpenAI
from aip import AipOcr
from pathlib import Path
import sys
import json 
import argparse
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
KEY_FILE = BASE_DIR.parent / "key.txt"

# 1. 读取密钥
try:
    keys = KEY_FILE.read_text(encoding="utf-8").strip().splitlines()
    APP_ID = keys[0].strip()       
    API_KEY = keys[1].strip()      
    SECRET_KEY = keys[2].strip()   
    DS_KEY = keys[3].strip()   
except Exception as e:
    print(f"读取key错误: {e}")
    sys.exit(1)
st.title("ai高数解题器")
st.markdown("上传图片或文字，立即解析")




# 2. 核心功能
def solve_math(image_path):
    # 在写入之前加这一行

    ds_client = OpenAI(api_key=DS_KEY, base_url="https://api.deepseek.com")
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    
    # 读图
    try:
        with open(image_path, 'rb') as f:
            image = f.read()
        result = client.basicGeneral(image)
    except Exception as e:
        print(f"读图或OCR失败：{type(e).__name__}: {e}")
        return  # 读图失败，直接结束函数，不要用 sys.exit(1) 卡死整个程序
        
    # 提取文字
    text = ""
    if 'words_result' in result:
         text = "\n".join([item['words'] for item in result['words_result']])
    else:
        print(f"识别失败: {result}")
        return 
        
    print(f"--- OCR 提取出的题目 ---\n{text}")
    
    # 调 AI
    prompt = f"请详细解答这道题，题目由ocr识别，请自行按照数学逻辑甄别字符，题目如下{text}"
    try:
        response = ds_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content
        print("\n=== AI 解析 ===")
        print(reply)
    except Exception as e:
        print(f"调用 AI 失败: {e}")
        return

    # 组装 JSON 数据并保存
    notes_path = BASE_DIR.parent /"data"/ "math_notes.json"
    # 在写入之前加这一行
    notes_path.parent.mkdir(parents=True, exist_ok=True)
    # 组装新的字典（你之前漏了这步）
    new_note = {
        "question": text,
        "answer": reply
    }
    
    if notes_path.exists():
        try:
            notes = json.loads(notes_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            notes = [] 
    else:
        notes = []
        
    notes.append(new_note)
    
    notes_path.write_text(
        json.dumps(notes, ensure_ascii=False, indent=4), 
        encoding="utf-8"
    )
    print(f"\n✅ 错题已结构化保存至 {notes_path.name}")

# 3. 程序入口
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI 高数错题机")
    parser.add_argument("--img", default="math.png", help="图片文件的路径")
    args = parser.parse_args()
    
    solve_math(args.img)  