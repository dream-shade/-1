import json
import pandas as pd
from pathlib import Path

# 找路径 (复用你之前的逻辑)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" if (BASE_DIR / "data").exists() else BASE_DIR.parent / "data"
notes_path = DATA_DIR / "math_notes.json"

if notes_path.exists():
    # 1. 读取 JSON 数据
    notes = json.loads(notes_path.read_text(encoding="utf-8"))
    
    # 2. 把列表转成 Pandas 的 DataFrame (数据表格)
    df = pd.DataFrame(notes)
    
    # 3. 核心体验：查看数据
    print("=== 错题本数据概览 ===")
    print(df.head()) # 打印前几行
    print(f"\n总错题数: {len(df)} 道")
    df['题目字数'] = df['question'].apply(len)
    # 4. 统计每道题的文本长度
    df['答案字数'] = df['answer'].apply(len)
    print(f"\n最长的一道题有 {df['题目字数'].max()} 个字。")
    
    # 5. 保存为 Excel 表格！
    excel_path = DATA_DIR / "math_notes.xlsx"
    df.to_excel(excel_path, index=False)
    print(f"\n✅ 已成功导出 Excel 文件: {excel_path}")
else:
    print("❌ 找不到错题本文件")
    # 1. 找出字数最长的那道题（也就是 OCR 识别最痛苦，或者题干最长的那道）
    # 按字数降序排列，并取前 1 名
    # 1. 找出字数最长的那道题（也就是 OCR 识别最痛苦，或者题干最长的那道）
    # 按字数降序排列，并取前 1 名
hardest_question = df.sort_values(by='题目字数', ascending=False).iloc[0]
print("\n=== 最长的一道题 ===")
print(f"题目内容：{hardest_question['question']}")
print(f"字数：{hardest_question['题目字数']}")
    
    # 2. 数据筛选：只挑出题目里包含 "导数" 或 "lim" 的题
filtered_df = df[df['question'].str.contains('导数|lim', na=False, regex=True)]
print(f"\n=== 包含'导数'或'lim'的题有 {len(filtered_df)} 道 ===")
print(filtered_df[['question']]) # 只打印题目这一列，答案太长就不打印了