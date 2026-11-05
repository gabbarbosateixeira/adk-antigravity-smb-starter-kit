"""ADK 2.0 Agent Definition for Template 2: '24/7 Front-Desk' Customer Triage & Booking Agent.

Modeled on Codelab 1 (`build-deploy-embed-agy-agents-cli`):
- Uses `gemini-3-flash-preview` for low-latency streaming responses.
- Designed to be deployed to **Cloud Run** (`--no-allow-unauthenticated`) and embedded into an
  SMB web portal via the `/run_sse` streaming endpoint.
"""

from __future__ import annotations

from agents.frontdesk_triage.tools import (
    book_customer_appointment,
    check_inventory_and_availability,
    list_open_appointment_slots,
)
from shared.config import get_config

cfg = get_config()

FRONTDESK_INSTRUCTION = """You are the '24/7 Front-Desk' Customer Triage & Booking Concierge for Aura & Co.
You assist website visitors with real-time product inventory questions and booking consultations or B2B onboarding sessions.

Rules of Engagement:
1. ALWAYS verify live stock using `check_inventory_and_availability` before quoting prices or availability.
2. ALWAYS check open times using `list_open_appointment_slots` before offering or confirming an appointment.
3. When booking an appointment via `book_customer_appointment`, confirm the `slot_id`, `customer_name`, and `customer_email` clearly and return the `confirmation_id`.
4. Never ask customers for credit card numbers or Social Security Numbers in chat.
"""

try:
    from google.adk import Agent

    root_agent = Agent(
        name="frontdesk_triage_agent",
        model=cfg.flash_model,  # gemini-3-flash-preview
        description=(
            "Low-latency 24/7 Front-Desk Customer Triage & Booking Agent for SMB web portals, "
            "backed by Cloud Firestore and streaming over /run_sse on Cloud Run."
        ),
        instruction=FRONTDESK_INSTRUCTION,
        tools=[
            check_inventory_and_availability,
            list_open_appointment_slots,
            book_customer_appointment,
        ],
    )
except ImportError:
    class _FallbackAgent:
        def __init__(self) -> None:
            self.name = "frontdesk_triage_agent"
            self.model = cfg.flash_model
            self.instruction = FRONTDESK_INSTRUCTION
            self.tools = [
                check_inventory_and_availability,
                list_open_appointment_slots,
                book_customer_appointment,
            ]

    root_agent = _FallbackAgent()  # type: ignore[assignment]
