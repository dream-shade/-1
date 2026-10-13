"""
mock_server.py — 一个假的"OpenAI 兼容接口"，用来在还没拿到密钥时先验证代码能跑通。

为什么值得写它：真实 API 会花钱、会限流、会网络抖动。一个假服务器能让你把
"我的代码有 bug" 和 "网络/额度有问题" 这两件事分开。这是工程上的基本手段。

用法（两个终端）：
  终端 1:  python mock_server.py
  终端 2:  $env:AI_API_KEY="test-key"
           $env:AI_BASE_URL="http://127.0.0.1:8000/v1"
           $env:AI_MODEL="mock"
           python ai_chat.py
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class MockHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            body = {}

        messages = body.get("messages", [])
        last_user = next(
            (m.get("content", "") for m in reversed(messages) if m.get("role") == "user"),
            "",
        )

        payload = {
            "id": "chatcmpl-mock-0001",
            "object": "chat.completion",
            "created": 0,
            "model": body.get("model", "mock"),
            "choices": [
                {
                    "index": 0,
                    "finish_reason": "stop",
                    "message": {
                        "role": "assistant",
                        "content": (
                            f"[假回答] 服务器收到 {len(messages)} 条消息，"
                            f"你最后说的是：「{last_user}」"
                        ),
                    },
                }
            ],
            "usage": {"prompt_tokens": 12, "completion_tokens": 18, "total_tokens": 30},
        }

        data = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args) -> None:  # 关掉默认的嘈杂日志
        pass


if __name__ == "__main__":
    print(f"假接口已启动：http://127.0.0.1:{PORT}/v1  （Ctrl+C 停止）")
    HTTPServer(("127.0.0.1", PORT), MockHandler).serve_forever()
