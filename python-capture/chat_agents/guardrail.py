from __future__ import annotations


class GuardrailAgent:
    def precheck(self, question: str) -> str | None:
        text_value = question.strip()
        if not text_value:
            return "请输入问题后再发送。"
        if len(text_value) > 500:
            return "问题过长，请控制在 500 字以内。"
        return None

    def postprocess(self, answer: str, intent: str, context: dict) -> str:
        cleaned = (answer or "").strip()
        if not cleaned:
            return "暂时没有拿到有效回答，请稍后再试。"

        if len(cleaned) > 1600:
            cleaned = cleaned[:1600] + "\n\n(回答已截断)"

        if intent == "top_traffic_ip" and not context.get("top_traffic_ips"):
            return self._ensure_no_data_notice(cleaned)
        if intent == "alert_status" and not context.get("recent_alerts"):
            return self._ensure_no_data_notice(cleaned)
        if intent == "protocol_distribution":
            if not context.get("top_l4_protocols") and not context.get("top_l7_protocols"):
                return self._ensure_no_data_notice(cleaned)

        return cleaned

    def fallback_on_llm_error(self, intent: str, context: dict, err: str) -> str:
        overview = context.get("overview", {})
        if intent == "overview":
            return (
                "当前无法调用大模型，先返回实时概览："
                f"活跃主机 {overview.get('active_host_count', 0)}，"
                f"活跃IP {overview.get('active_ip_count', 0)}，"
                f"实时告警 {overview.get('realtime_alert_count', 0)}。"
            )
        return f"当前无法调用模型服务：{err}"

    @staticmethod
    def _ensure_no_data_notice(answer: str) -> str:
        if "没有" in answer or "暂无" in answer or "no data" in answer.lower():
            return answer
        return answer + "\n\n注：当前实时数据中没有对应记录。"

