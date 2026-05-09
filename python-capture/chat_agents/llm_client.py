from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass
class DeepSeekConfig:
    api_key: str
    api_url: str
    model: str
    timeout_sec: float = 20


class DeepSeekClient:
    def __init__(self, config: DeepSeekConfig):
        self.config = config

    def complete(self, messages: list[dict]) -> tuple[str | None, str | None]:
        if not self.config.api_key:
            return None, "未检测到 DEEPSEEK_API_KEY，请先在 .env 中配置。"

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": 0.2,
            "stream": False,
        }
        req = urllib.request.Request(
            self.config.api_url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_sec) as resp:
                body = resp.read().decode("utf-8")
            parsed = json.loads(body)
            answer = (
                parsed.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            if not answer:
                return None, "DeepSeek 返回了空内容。"
            return answer, None
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8", errors="ignore")
            return None, f"DeepSeek HTTP {err.code}: {detail[:300]}"
        except Exception as err:
            return None, str(err)

