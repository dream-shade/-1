"""
ai_chat.py — 命令行 AI 对话客户端（Day 1 工程化版本）

和 daily_plan.py 的区别，就是"作业"和"工程"的区别：
  1. 配置与逻辑分离 —— Settings 只管读配置+校验，AIClient 只管发请求。
  2. 密钥永不硬编码 —— 从 .env 读，.env 在 .gitignore 里。
  3. 异常分类处理 —— 401/404/429/超时分别给不同的人话提示，而不是一句"出错了"。
  4. 自定义异常 —— ConfigError（你的问题，重试没用）/ ChatError（网络问题，可以重试）。
  5. 路径不靠 cwd —— 用 Path(__file__) 定位 .env，在哪个目录运行都能找到。

运行：python ai_chat.py
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

# ---------------------------------------------------------------- 常量区
# 用"脚本所在目录"而不是"当前工作目录"，避免"换个文件夹运行就读不到 .env"
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 阿里云百炼
DEFAULT_MODEL = "qwen-turbo"
DEFAULT_SYSTEM_PROMPT = "你是一名耐心的计算机导师，回答简洁，给可执行的步骤。"


# ---------------------------------------------------------------- 自定义异常
class ConfigError(Exception):
    """配置问题（.env 没建 / 密钥是占位符）。这是"人要去改"的错误，重试 100 次也没用。"""


class ChatError(Exception):
    """API 调用失败，但已经被翻译成人话，上层可以直接打印给用户看。"""


# ---------------------------------------------------------------- 配置
@dataclass
class Settings:
    """一次 API 调用需要的全部配置。用 dataclass 是为了让字段有名字、有默认值。"""

    api_key: str
    base_url: str
    model: str
    timeout: float = 30.0
    system_prompt: str = DEFAULT_SYSTEM_PROMPT

    @classmethod
    def from_env(cls, env_file: Path = ENV_FILE) -> "Settings":
        """从 .env 读配置 + 启动前自检。

        关键点：坏配置要在"发请求之前"就报出来，而不是等 API 返回一个看不懂的错。
        """
        load_dotenv(env_file)  # 文件不存在时不会报错，只是什么都读不到

        api_key = (os.getenv("AI_API_KEY") or "").strip()
        if not api_key:
            raise ConfigError(
                f"没读到 AI_API_KEY。\n"
                f"    期望的 .env 路径：{env_file}\n"
                f"    检查：① 文件真的叫 .env（不是 .env.txt）"
                f" ② 是 UTF-8 编码（用 VS Code 保存，别用 PowerShell 的 > 重定向）"
                f" ③ 变量名没拼错"
            )
        if "你的" in api_key or "粘贴" in api_key:
            raise ConfigError("AI_API_KEY 还是模板里的占位符，把真实密钥填进去。")

        base_url = (os.getenv("AI_BASE_URL") or DEFAULT_BASE_URL).strip().rstrip("/")
        if not base_url.startswith("http"):
            raise ConfigError(f"AI_BASE_URL 不像一个网址：{base_url!r}")

        return cls(
            api_key=api_key,
            base_url=base_url,
            model=(os.getenv("AI_MODEL") or DEFAULT_MODEL).strip(),
            timeout=float(os.getenv("AI_TIMEOUT") or 30),
        )

    def masked_key(self) -> str:
        """打印用：密钥只露头尾。日志、截图、提问里永远不要出现完整密钥。"""
        if len(self.api_key) <= 10:
            return "***"
        return f"{self.api_key[:5]}****{self.api_key[-4:]}"


# ---------------------------------------------------------------- 客户端
class AIClient:
    """把 openai SDK 包一层。对外只暴露 ask()，以后换供应商/换模型不用改业务代码。"""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
            timeout=settings.timeout,
        )
        # 对话历史就是这个列表。system 消息固定在第 0 条，永不删除。
        self.history: list[dict[str, str]] = [
            {"role": "system", "content": settings.system_prompt}
        ]

    # -- 对外接口 ------------------------------------------------
    def ask(self, question: str, retries: int = 2) -> str:
        """问一句，返回答案。失败时抛 ChatError（已翻译成人话）。"""
        self.history.append({"role": "user", "content": question})

        for attempt in range(1, retries + 2):  # 1 次首发 + retries 次重试
            try:
                response = self._client.chat.completions.create(
                    model=self.settings.model,
                    messages=self.history,
                )
            except (
                AuthenticationError,
                RateLimitError,
                APITimeoutError,
                APIConnectionError,
                APIStatusError,
            ) as exc:
                if self._should_retry(exc) and attempt <= retries:
                    wait = 2**attempt  # 指数退避：1s、2s、4s……别把对方打挂
                    print(f"  [重试 {attempt}/{retries}] {self._reason(exc).rstrip('。')}，{wait}s 后重试……")
                    time.sleep(wait)
                    continue
                self._rollback()  # 失败的提问不要留在历史里
                raise ChatError(self._reason(exc)) from exc

            answer = response.choices[0].message.content or "(模型返回了空内容)"
            self.history.append({"role": "assistant", "content": answer})
            return answer

        raise ChatError("重试次数用完了，还是没成功。")  # 理论上到不了这里

    def reset(self) -> None:
        """清空上下文，只保留 system 提示。"""
        self.history = self.history[:1]

    @property
    def turns(self) -> int:
        """已经聊了几轮（user 消息条数）。"""
        return sum(1 for m in self.history if m["role"] == "user")

    # -- 内部工具 ------------------------------------------------
    def _rollback(self) -> None:
        """把刚才那条失败的 user 消息撤掉，否则下一轮会把坏上下文一起发出去。"""
        if self.history and self.history[-1]["role"] == "user":
            self.history.pop()

    @staticmethod
    def _should_retry(exc: Exception) -> bool:
        """只有"等一下可能就好了"的错误才值得重试；401/404 重试是浪费时间。"""
        if isinstance(exc, (RateLimitError, APITimeoutError, APIConnectionError)):
            return True
        if isinstance(exc, APIStatusError):
            return exc.status_code >= 500
        return False

    @staticmethod
    def _reason(exc: Exception) -> str:
        """把 SDK 的异常翻译成"人话 + 下一步动作"。这就是工程里的错误处理。"""
        if isinstance(exc, AuthenticationError):
            return "密钥无效（401）：检查 .env 里的 AI_API_KEY 是否复制完整、有没有多余空格/引号。"
        if isinstance(exc, RateLimitError):
            return "被限流或额度用完（429）：等一下再试，或去控制台看剩余免费额度。"
        if isinstance(exc, APITimeoutError):
            return "请求超时：网络慢或服务端忙，重试一次通常就好。"
        if isinstance(exc, APIConnectionError):
            return "连不上服务器：检查网络/代理，以及 AI_BASE_URL 是否写对（结尾不要自己加 /chat/completions）。"
        if isinstance(exc, APIStatusError):
            if exc.status_code == 404:
                return "404：多半是 AI_MODEL 名字写错，或 AI_BASE_URL 少了结尾的 /v1。"
            if exc.status_code == 400:
                return "400：请求被拒绝，通常是模型 ID 不存在，去控制台文档核对模型名。"
            return f"服务端返回 {exc.status_code}，原始信息：{exc.message if hasattr(exc, 'message') else exc}"
        return f"未知错误：{exc!r}"


# ---------------------------------------------------------------- 主程序
HELP_TEXT = "命令：/reset 清空上下文  /help 帮助  /exit 退出"


def _configure_stdio() -> None:
    """Windows 上把标准输入/输出统一成 UTF-8 —— 这是被真实事故逼出来的四行代码。

    不这么做的两种翻车现场：
      1. 中文通过管道/重定向送进来时，Python 按 GBK 解码 → 直接抛
         UnicodeEncodeError: 'utf-8' codec can't encode character '\\udca5': surrogates not allowed
      2. Python 的中文输出到管道时被编成 GBK，别的程序读出来是乱码。
    errors="replace" 的作用：读不懂的字节变成 "?"，而不是让程序崩掉。
    """
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass  # 特殊环境下改不了，忽略，程序照常跑


def main() -> int:
    _configure_stdio()
    print("=" * 52)
    print("  ai_chat.py — 你的第一个 AI 应用")
    print("=" * 52)

    try:
        settings = Settings.from_env()
    except ConfigError as exc:
        print(f"\n[配置错误] {exc}")
        return 2

    print(f"模型  : {settings.model}")
    print(f"接口  : {settings.base_url}")
    print(f"密钥  : {settings.masked_key()}（只显示首尾，任何截图都别露全）")
    print(HELP_TEXT)

    client = AIClient(settings)

    while True:
        try:
            question = input(f"\n你[{client.turns}轮] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            return 0

        if not question:
            continue
        if question in {"/exit", "/quit", "exit", "quit"}:
            print("再见！")
            return 0
        if question == "/reset":
            client.reset()
            print("上下文已清空（system 提示保留）。")
            continue
        if question == "/help":
            print(HELP_TEXT)
            continue

        try:
            answer = client.ask(question)
        except ChatError as exc:
            print(f"\n[调用失败] {exc}")
            continue

        print(f"\nAI > {answer}")


if __name__ == "__main__":  # 有这个保护，别的文件 import 它时才不会自动跑起来
    sys.exit(main())
