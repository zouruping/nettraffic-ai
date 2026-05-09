from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RouteDecision:
    intent: str
    rewritten_question: str
    reason: str


class RouterAgent:
    _AMBIGUOUS_MARKERS = [
        "这个",
        "这个ip",
        "这个主机",
        "上面那个",
        "那个",
        "它",
        "this",
        "that",
        "it",
    ]

    _INTENT_RULES = {
        "overview": ["概览", "总览", "overview", "当前情况", "整体情况", "现状"],
        "top_traffic_ip": ["最高流量", "流量最高", "top ip", "topip", "最耗流量"],
        "alert_status": ["告警", "报警", "alert", "异常", "风险"],
        "protocol_distribution": ["协议", "protocol", "l4", "l7", "http", "dns", "tcp", "udp"],
    }

    def route(self, question: str, history: list[dict[str, str]]) -> RouteDecision:
        rewritten = self._rewrite_if_needed(question, history)
        lowered = rewritten.lower()
        for intent, keywords in self._INTENT_RULES.items():
            if any(k in lowered for k in keywords):
                return RouteDecision(intent=intent, rewritten_question=rewritten, reason=f"matched:{intent}")
        return RouteDecision(intent="general_analysis", rewritten_question=rewritten, reason="fallback")

    def _rewrite_if_needed(self, question: str, history: list[dict[str, str]]) -> str:
        if not self._contains_ambiguous_reference(question):
            return question
        for turn in reversed(history):
            if turn.get("role") != "user":
                continue
            content = (turn.get("content") or "").strip()
            if not content or self._contains_ambiguous_reference(content):
                continue
            return f"{content}。补充问题：{question}"
        return question

    def _contains_ambiguous_reference(self, text_value: str) -> bool:
        lowered = text_value.strip().lower()
        return any(marker in lowered for marker in self._AMBIGUOUS_MARKERS)

