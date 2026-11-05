import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import sys

from pathlib import Path

# ==========================================
# ⚙️ 配置区：请在这里修改你的专属信息
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
KEY_FILE = BASE_DIR / "key.txt"

try:
    keys = KEY_FILE.read_text(encoding="utf-8").strip().splitlines()
    
    DS_KEY = keys[3].strip()   
    DASHSCOPE_API_KEY =  keys[4].strip()   
except:
    print("无key")
    sys.exit()
    



# 2. 填入你的本地 PDF 文件路径（如果是同目录下，直接写文件名）
PDF_FILE_PATH = "微分中值定理学习资料.pdf" 

# 3. 填入你想问的问题
QUESTION = "这份文档里讲了什么核心内容？请用三点总结。"

# ==========================================
# 🛠️ 核心代码区：无需修改
# ==========================================

print("⏳ 1. 正在初始化模型...")
# 配置环境变量
os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY

# 初始化大语言模型 (使用 DeepSeek，兼容 OpenAI 格式)
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=DS_KEY,
    base_url="https://api.deepseek.com/v1",
    temperature=0.3 # 调低温度，让回答更严谨，减少幻觉
)

# 初始化 Embedding 模型 (使用阿里云 DashScope)
embeddings = DashScopeEmbeddings(model="text-embedding-v2")


print(f"⏳ 2. 正在加载文档: {PDF_FILE_PATH} ...")
if not os.path.exists(PDF_FILE_PATH):
    raise FileNotFoundError(f"找不到文件 {PDF_FILE_PATH}，请确保 PDF 和代码在同一目录下，且名字正确！")

loader = PyPDFLoader(PDF_FILE_PATH)
docs = loader.load()

# 将长文本切分成小块
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
splits = text_splitter.split_documents(docs)
print(f"✅ 文档切分完成，共切分为 {len(splits)} 个文本块。")


print("⏳ 3. 正在进行向量化并存入数据库...")
# 将切分后的文档块向量化并存入 Chroma
# persist_directory 会在当前目录下生成一个 chroma_db 文件夹，保存数据
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="./chroma_db",
)
print(f"✅ 存入成功！当前向量库共有 {vectorstore._collection.count()} 个向量。")


print(f"⏳ 4. 正在检索并生成回答...\n问题: {QUESTION}\n")
# 创建检索器 (每次检索最相关的 4 个文本块)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# 构造 Prompt 模板
prompt_template = ChatPromptTemplate.from_template("""
你是一个知识问答助手。请严格基于以下参考资料回答用户的问题。
要求：
1. 只基于参考资料回答，绝对不要自己编造信息。
2. 如果参考资料中没有相关信息，请明确告知"文档中找不到相关信息"。

参考资料：
{context}

用户问题：{question}
""")

# 辅助函数：将检索到的多个文档块拼接成一个大字符串
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 组装 RAG 链
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt_template
    | llm
    | StrOutputParser()
)

# 执行提问
answer = rag_chain.invoke(QUESTION)

print("================= 最终回答 =================")
print(answer)
print("============================================")