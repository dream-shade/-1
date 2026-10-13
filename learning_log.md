# 学习日志 · 吴政（软件工程 · 大一）

> **用法**：换账号 / 换 AI 时，第一句话把这个文件的内容粘过去，说：
> "这是我的学习日志，请据此给我今天的任务。"
> 每天学完，在「今日记录」最上面补一条。**只写事实（命令、报错原文、结论），不写感想** ——
> AI 需要的是事实，不是心情。
>
> 最后更新：2026-10-13

---

## 1. 我的目标

- **长期方向**：AI 应用开发 / 大模型应用工程。不是训练模型，是"用模型做出能用的产品"。
- **大学目标**：毕业时能独立交付一个 LLM 应用（有界面、有后端、能部署），GitHub 上有 3~5 个能拿出手的仓库。
- **这个月的目标**：把 Python 工程化基础 + Git 工作流 + API 调用练成肌肉记忆。

## 2. 当前环境（事实）

| 项目 | 情况 |
|---|---|
| 系统 | Windows |
| 代码目录 | `D:\mycode` |
| 编辑器 | VS Code |
| Python | 3.11.4（系统装在 `D:\python`），项目内用 `.venv` 虚拟环境 |
| pip 源 | 已永久配置清华源 `https://pypi.tuna.tsinghua.edu.cn/simple` |
| 已装包（`.venv`） | openai 3.29.0（含 httpx2 / pydantic）、python-dotenv（待装） |
| Git | 本地仓库 `D:\mycode`，分支 `master`，**无远程仓库**，4 次提交 |
| 已解决 | PowerShell 执行策略导致 `.venv` 激活脚本无法运行 |

## 3. 技能清单

### Git — 已掌握
`init` / `add` / `commit` / `status` / `log` / `reset` / `checkout -b` / `merge`
`.gitignore` 语法 · `git rm -r --cached`（只移出版本控制，不删硬盘文件）

### Python — 已掌握
变量 / 条件 / 循环 / 函数 / `try-except` · 列表与元组 · `sum` · `sort(key=lambda)`
文件读写 `with open(..., encoding="utf-8")` · `venv` 创建与激活 · `input()` 交互

### 正在学（本阶段重点）
面向对象封装（`class` / `@dataclass`）· 自定义异常 · 异常分类处理
API 调用（openai SDK）· `.env` 管理密钥 · 分支开发流程 `feature/* → merge`

## 4. 踩坑档案（最重要的一节，只增不删）

| 日期 | 坑 | 根本原因 | 现在的做法 |
|---|---|---|---|
| 10-11 | `git add .` 把 `.venv` 里 1400+ 文件加进版本控制 | 没有 `.gitignore` | `add` 之前先 `git status` 自检 |
| 10-11 | PowerShell 不允许运行 `.venv` 激活脚本 | 执行策略限制 | 已解决 |
| 10-12 | `pip install openai` 极慢、卡住 | 默认走 PyPI 官方源 | 已永久配置清华源，秒装 |
| 10-12 | **以为修好了 `.venv` 入库问题，其实 `.gitignore` 是 0 字节空文件，且那次提交正是把 1473 个 `.venv` 文件提交进去的提交** | 文件建了但内容没写进去；`git rm --cached` 后又被 `git add .` 加回来 | 10-13 用脚本写入 `.gitignore` 并逐条验证"被跟踪文件数 = 0" |
| 10-13 | （待你补充） | | |

**结论**：*"我修好了"必须以一条可验证的命令为证据*（比如 `git ls-files | Select-String '^\.venv/'` 输出 0 条），
不能凭"我记得我敲过了"。

## 5. 项目

| 项目 | 状态 | 说明 |
|---|---|---|
| `daily_plan.py` | ✅ 完成 | 输入权重 → 按时长分配 → 写 `plan.txt`；已做函数封装 + `try/except` |
| `singu.py` | 🔶 练习 | 奇偶判断。待改：变量名、异常文案（`print('滚你妈的')` 必须换掉） |
| `ai_chat.py` | 🚧 进行中 | 命令行多轮对话；`.env` 管密钥；自定义异常；面向对象封装 |
| `learning_log.md` | 🚧 持续更新 | 本文件 |

## 6. 今日记录（倒序，最新在最上面）

### 2026-10-13（D1）
- **目标**：跑通 `ai_chat.py` + 学会用 `.env` 安全管理 API 密钥
- **实际完成**：
- **遇到的新报错 + 解决方式**（写原文）：
- **新学到的概念**：
- **明天要做**：

### 2026-10-12（D0）
- 配置清华源；`openai` 装好（3.29.0）

## 7. 待学清单（排队中）

- [ ] `git log -p` / `git diff` 读懂自己每次改动
- [ ] `pytest` 单元测试 + mock 掉 API（不花一分钱 token 测代码）
- [ ] `logging` 模块替代 `print`
- [ ] 清除 Git 历史里的 `.venv`（`git filter-repo` 或 orphan 分支重建）
- [ ] 流式输出 `stream=True`
- [ ] `FastAPI` 最小后端
- [ ] `asyncio` 并发调用
