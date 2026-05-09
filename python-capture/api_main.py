from __future__ import annotations

import os

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text

from capture_backend.db import init_db
from capture_backend.forecast import forecast_traffic_with_lstm
from chat_agents.data_analyst import DataAnalystAgent
from chat_agents.env_utils import load_dotenv_if_present
from chat_agents.guardrail import GuardrailAgent
from chat_agents.llm_client import DeepSeekClient, DeepSeekConfig
from chat_agents.router import RouterAgent
from chat_agents.service import ChatOrchestrator


load_dotenv_if_present()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "mysql+pymysql://root:123456@127.0.0.1:3306/nettraffic_ai"
)
ACTIVE_WINDOW_MINUTES = int(os.getenv("ACTIVE_WINDOW_MINUTES", "5"))

DEEPSEEK_CONFIG = DeepSeekConfig(
    api_key=os.getenv("DEEPSEEK_API_KEY", "").strip(),
    api_url=os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions").strip(),
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip(),
    timeout_sec=float(os.getenv("DEEPSEEK_TIMEOUT_SEC", "20")),
)
DEEPSEEK_MAX_HISTORY = int(os.getenv("DEEPSEEK_MAX_HISTORY", "8"))

_, SESSION_FACTORY = init_db(DATABASE_URL)

CHAT_ORCHESTRATOR = ChatOrchestrator(
    router=RouterAgent(),
    analyst=DataAnalystAgent(active_window_minutes=ACTIVE_WINDOW_MINUTES),
    guardrail=GuardrailAgent(),
    llm_client=DeepSeekClient(DEEPSEEK_CONFIG),
    max_history=DEEPSEEK_MAX_HISTORY,
)

app = FastAPI(
    title="NetTraffic AI Capture API",
    description="Capture statistics API for dashboard and chatbot",
    version="1.2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_session():
    session = SESSION_FACTORY()
    try:
        yield session
    finally:
        session.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/dashboard/overview")
def dashboard_overview(session=Depends(get_session)):
    active_host_count = session.execute(
        text("SELECT COUNT(*) FROM active_hosts"),
    ).scalar_one()
    active_ip_count = session.execute(
        text("SELECT COUNT(*) FROM active_ips"),
    ).scalar_one()
    active_alert_count = session.execute(
        text("SELECT COUNT(*) FROM alert_records WHERE status='ACTIVE'"),
    ).scalar_one()

    return {
        "active_window_minutes": ACTIVE_WINDOW_MINUTES,
        "active_host_count": active_host_count,
        "active_ip_count": active_ip_count,
        "realtime_alert_count": active_alert_count,
    }


@app.get("/api/dashboard/active-hosts")
def active_hosts(limit: int = Query(20, ge=1, le=200), session=Depends(get_session)):
    rows = session.execute(
        text(
            """
            SELECT mac_address, last_seen, packet_count, byte_count
            FROM active_hosts
            ORDER BY last_seen DESC
            LIMIT :limit
            """
        ),
        {"limit": limit},
    ).mappings()
    return [
        {
            "mac_address": r["mac_address"],
            "last_seen": r["last_seen"],
            "packet_count": r["packet_count"],
            "byte_count": r["byte_count"],
        }
        for r in rows
    ]


@app.get("/api/dashboard/active-ips")
def active_ips(limit: int = Query(20, ge=1, le=200), session=Depends(get_session)):
    rows = session.execute(
        text(
            """
            SELECT ip_address, last_seen, packet_count, byte_count
            FROM active_ips
            ORDER BY last_seen DESC
            LIMIT :limit
            """
        ),
        {"limit": limit},
    ).mappings()
    return [
        {
            "ip_address": r["ip_address"],
            "last_seen": r["last_seen"],
            "packet_count": r["packet_count"],
            "byte_count": r["byte_count"],
        }
        for r in rows
    ]


@app.get("/api/dashboard/high-traffic-ips")
def high_traffic_ips(limit: int = Query(20, ge=1, le=200), session=Depends(get_session)):
    rows = session.execute(
        text(
            """
            SELECT ip_address, byte_count, packet_count, last_seen
            FROM active_ips
            ORDER BY byte_count DESC
            LIMIT :limit
            """
        ),
        {"limit": limit},
    ).mappings()
    return [
        {
            "ip_address": r["ip_address"],
            "byte_count": r["byte_count"],
            "packet_count": r["packet_count"],
            "last_seen": r["last_seen"],
        }
        for r in rows
    ]


@app.get("/api/dashboard/traffic-forecast")
def traffic_forecast(
    history_minutes: int = Query(180, ge=30, le=24 * 60),
    forecast_steps: int = Query(12, ge=3, le=120),
    interval_minutes: int = Query(1, ge=1, le=10),
    window_size: int = Query(12, ge=4, le=60),
    epochs: int = Query(30, ge=5, le=200),
    session=Depends(get_session),
):
    try:
        result = forecast_traffic_with_lstm(
            session,
            history_minutes=history_minutes,
            forecast_steps=forecast_steps,
            interval_minutes=interval_minutes,
            window_size=window_size,
            epochs=epochs,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {
        "interval_minutes": interval_minutes,
        "history": [
            {"time": ts, "traffic_mb": value}
            for ts, value in result.history_points
        ],
        "forecast": [
            {"time": ts, "traffic_mb": value}
            for ts, value in result.forecast_points
        ],
        "model": {
            "name": result.model_name,
            "fallback_used": result.fallback_used,
            "train_samples": result.train_samples,
            "window_size": window_size,
            "epochs": epochs,
        },
    }


def _protocol_distribution(layer: str, session):
    rows = list(
        session.execute(
            text(
                """
                SELECT protocol_name, packet_count, byte_count
                FROM protocol_metrics
                WHERE protocol_layer = :layer
                ORDER BY byte_count DESC
                """
            ),
            {"layer": layer},
        ).mappings()
    )
    total_bytes = sum(r["byte_count"] for r in rows) or 1
    return [
        {
            "protocol": r["protocol_name"],
            "packet_count": r["packet_count"],
            "byte_count": r["byte_count"],
            "ratio": round(r["byte_count"] / total_bytes, 4),
        }
        for r in rows
    ]


@app.get("/api/dashboard/protocols/transport")
def transport_protocols(session=Depends(get_session)):
    return _protocol_distribution("L4", session)


@app.get("/api/dashboard/protocols/application")
def application_protocols(session=Depends(get_session)):
    return _protocol_distribution("L7", session)


@app.get("/api/dashboard/alerts/recent")
def recent_alerts(limit: int = Query(20, ge=1, le=200), session=Depends(get_session)):
    rows = session.execute(
        text(
            """
            SELECT id, alert_type, severity, target_value, message, packet_count, byte_count, first_seen, last_seen, status
            FROM alert_records
            ORDER BY last_seen DESC
            LIMIT :limit
            """
        ),
        {"limit": limit},
    ).mappings()
    return [dict(r) for r in rows]


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str = Field(min_length=1, max_length=2000)


class ChatAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    history: list[ChatMessage] = Field(default_factory=list)


@app.post("/api/chat/ask")
def chat_ask(payload: ChatAskRequest, session=Depends(get_session)):
    history = [{"role": msg.role, "content": msg.content} for msg in payload.history]
    result = CHAT_ORCHESTRATOR.ask(
        question=payload.question,
        history=history,
        session=session,
    )
    result["model"] = DEEPSEEK_CONFIG.model
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=False)
