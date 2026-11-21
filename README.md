@"
# AI 高数解题器

基于 Streamlit 的 Web 应用，拍照上传高数题目，自动 OCR 识别并调用 DeepSeek 生成解题步骤。

## 功能
- 百度 OCR 识别手写/印刷体数学题
- DeepSeek 大模型解析并输出详细解题过程
- 支持错题记录与导出

## 本地运行
pip install -r requirements.txt
streamlit run math_web.py

## 密钥配置
在 .streamlit/secrets.toml 中配置百度 OCR 与 DeepSeek 密钥（该文件已被 gitignore，不会上传）。
"@ | Out-File -Encoding utf8 README.md

