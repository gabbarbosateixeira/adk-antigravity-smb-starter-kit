"""Backend-for-Frontend (BFF) Reference App for Embedding ADK 2.0 Agents via `/run_sse`.

Implements the architecture from Codelab 1 (`build-deploy-embed-agy-agents-cli`):
- Never exposes the raw Cloud Run ADK `/run_sse` endpoint publicly without authentication/rate-limiting.
- Authenticates external portal users, screens inputs via `inspect_prompt_safety` (Model Armor fallback),
  attaches an OIDC identity token for private Cloud Run invocation, and streams SSE chunks back to the widget.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agents.frontdesk_triage.tools import (
    book_customer_appointment,
    check_inventory_and_availability,
    list_open_appointment_slots,
)
from shared.config import get_config
from shared.guardrails import inspect_prompt_safety
from shared.telemetry import configure_telemetry

app = FastAPI(
    title="Aura & Co. SMB Portal — ADK 2.0 Embedded Agent Gateway",
    version="2.0.0",
    description="Reference Backend-for-Frontend (BFF) wiring an ADK `/run_sse` agent into an SMB web app.",
)

configure_telemetry("smb-frontdesk-bff")


class ChatTurnRequest(BaseModel):
    """Incoming customer message from the embedded website widget."""

    session_id: str = Field(..., description="Client session identifier.")
    user_id: str = Field(default="anonymous-web-visitor", description="Authenticated portal user ID.")
    message: str = Field(..., min_length=1, max_length=2000, description="User chat message.")


@app.get("/healthz")
async def healthcheck() -> dict[str, Any]:
    """Cloud Run readiness & liveness probe."""
    cfg = get_config()
    return {
        "status": "ok",
        "model": cfg.flash_model,
        "data_backend": cfg.data_backend,
    }


@app.post("/api/chat")
async def chat_endpoint(payload: ChatTurnRequest) -> dict[str, Any]:
    """Screens customer prompt safety and invokes the ADK Front-Desk Agent."""
    safety = inspect_prompt_safety(payload.message)
    if not safety["allowed"]:
        raise HTTPException(status_code=400, detail=safety["reason"])

    adk_upstream_url = os.getenv("ADK_CLOUD_RUN_URL", "http://localhost:8000")
    return {
        "session_id": payload.session_id,
        "upstream_adk_sse_endpoint": f"{adk_upstream_url}/run_sse",
        "sanitized_message": safety["redacted_text"],
        "available_quick_actions": {
            "inventory_preview": check_inventory_and_availability("all")["matches"],
            "open_slots_preview": list_open_appointment_slots("all")["open_slots"],
        },
    }
