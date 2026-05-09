from __future__ import annotations

import json
from datetime import datetime, timezone

from .data_analyst import DataAnalystAgent
from .guardrail import GuardrailAgent
from .llm_client import DeepSeekClient
from .router import RouterAgent


class ChatOrchestrator:
    def __init__(
        self,
        router: RouterAgent,
        analyst: DataAnalystAgent,
        guardrail: GuardrailAgent,
        llm_client: DeepSeekClient,
        max_history: int = 8,
    ):
        self.router = router
        self.analyst = analyst
        self.guardrail = guardrail
        self.llm_client = llm_client
        self.max_history = max_history

    def ask(self, question: str, history: list[dict[str, str]], session) -> dict:
        reject = self.guardrail.precheck(question)
        if reject:
            return {
                "answer": reject,
                "intent": "guardrail_reject",
                "rewritten_question": question.strip(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "route_reason": "question_invalid",
            }

        route = self.router.route(question.strip(), history)
        context = self.analyst.build_context(session)
        evidence = self.analyst.build_evidence(route.intent, context)

        messages = self._build_messages(
            rewritten_question=route.rewritten_question,
            history=history,
            context=context,
            intent=route.intent,
            evidence=evidence,
        )
        llm_answer, llm_error = self.llm_client.complete(messages)
        if llm_error:
            answer = self.guardrail.fallback_on_llm_error(route.intent, context, llm_error)
            return {
                "answer": answer,
                "intent": route.intent,
                "rewritten_question": route.rewritten_question,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "route_reason": route.reason,
                "guardrail_fallback": True,
                "model_error": llm_error,
            }

        safe_answer = self.guardrail.postprocess(llm_answer or "", route.intent, context)
        return {
            "answer": safe_answer,
            "intent": route.intent,
            "rewritten_question": route.rewritten_question,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "route_reason": route.reason,
            "guardrail_fallback": False,
        }

    def _build_messages(
        self,
        rewritten_question: str,
        history: list[dict[str, str]],
        context: dict,
        intent: str,
        evidence: list[str],
    ) -> list[dict]:
        context_json = json.dumps(context, ensure_ascii=False, default=str)
        system_prompt = (
            "你是网络流量监控看板助手。"
            "你要基于实时上下文回答，不允许编造。"
            "如果上下文没有该信息，要明确说“当前数据没有该项”。"
            "回答简洁、专业、可执行，优先中文。"
            f"\n当前路由意图: {intent}"
            f"\n关键证据:\n- " + "\n- ".join(evidence) +
            f"\n\n实时上下文(JSON):\n{context_json}"
        )

        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        trimmed = [x for x in history if x.get("role") in {"user", "assistant"}][-self.max_history :]
        for msg in trimmed:
            messages.append({"role": msg["role"], "content": msg.get("content", "")})
        messages.append({"role": "user", "content": rewritten_question})
        return messages

