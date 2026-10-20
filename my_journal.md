

## 2026-10-15

今日成果：  
1. 放弃 python-dotenv，改用 key.txt + open().read().strip() 安全读取密钥，配置 .gitignore 成功屏蔽 key.txt 和 ai_chat.py，避免密钥泄露风险。  
2. 跑通“第二大脑”日记脚本 journal.py，接入 DeepSeek API，实现将今日记录发送给 AI 获取复盘总结并追加写入 Markdown。  
3. 蓝桥杯算法备战：掌握 collections.Counter，一行代码完成字母频率统计（O(N)），理解字典 in 判断与 +=1 计数，向输出“最大频率字母及次数”目标推进。

## 2026-10-16

今日完成Day 6三项任务：journal.py通过while循环+EOF结束符实现多行输入并用"\n".join拼接，解决了昨日回车即执行的痛点；counter.py补充最大频率查找与并列取字母序最小的逻辑，通关蓝桥杯"单词分析"；重构counter.py将逻辑封装为analyze_word函数并置于__main__保护下，新建test_counter.py用pytest完成单元测试（2 passed）。最后Git提交三文件与学习日志，记录EOF多行写法、assert与pytest作用及函数封装原因。

## 2026-10-17

Day 7 总结：成功用 Streamlit 将 AI 第二大脑从 CLI 升级为 Web 应用，跑出真正的浏览器网页，完成大一第七天的里程碑式突破。掌握 Streamlit 基础布局（Title、TextArea、Button、Spinner）与组件化思维，手握一个可现场演示的"Demo 级"黑客松产品。收尾三步：①安全检查（Ctrl+C 停服务，确认 .gitignore 含 key.txt、__pycache__/、.pytest_cache/）；②git add . 并 commit 提交里程碑；③顺手清理 aichat.py / ai_chat.py 等重复与测试文件。明日待办：加 Sidebar 历史记录功能、着手生成黑客松 PPT。

## 2026-10-18

今日完成Day 8任务：升级app.py为网页添加侧边栏历史记录与Markdown本地持久化（AI复盘自动保存），完成蓝桥杯多条件排序题（成绩降序+姓名字典序），撰写README项目简介与运行说明，配置.gitignore保护隐私文件并完成Git提交。

## 2026-10-19

今日成果总结：

1. **AI周报功能**：在app.py侧边栏新增“生成近期周报”按钮，读取my_journal.md最后3000字符历史记录，调用DeepSeek API生成周报并显示在主界面，实现RAG雏形。
2. **黑客松PPT骨架**：完成4页结构（痛点/解决方案/技术架构/核心亮点），准备10月22日提交。
3. **蓝桥杯练习**：新建palindrome.py，用双指针法实现回文串判断（忽略大小写和标点）。
4. **Git提交**：确认.gitignore包含my_journal.md，提交app.py和palindrome.py，commit信息为"feat: 实现 AI 全局周报功能(RAG雏形)，新增蓝桥杯回文串算法"。



