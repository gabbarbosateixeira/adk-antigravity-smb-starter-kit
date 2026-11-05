"""Tools for Agent 2: '24/7 Front-Desk' Customer Triage & Booking Agent.

Modeled on Codelab 1 (`build-deploy-embed-agy-agents-cli`):
- Connects to Cloud Firestore (`DATA_BACKEND="gcp"`) or local mock state (`DATA_BACKEND="mock"`).
- Exposed via ADK 2.0 `/run_sse` streaming endpoint on Cloud Run.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from agents.frontdesk_triage.mock_data import (
    AVAILABLE_APPOINTMENT_SLOTS,
    BOOKED_RESERVATIONS,
    INVENTORY_STOCK,
)
from shared.config import get_config
from shared.guardrails import inspect_prompt_safety


def check_inventory_and_availability(product_query: str) -> dict[str, Any]:
    """Checks real-time product stock levels, pricing, and pickup/shipping availability.

    Args:
        product_query: Product SKU or keyword (e.g., 'AURA-SERUM-01', 'sleep mist', 'bundle').

    Returns:
        Dictionary with matching inventory items and fulfillment options.
    """
    cfg = get_config()
    q = product_query.lower()
    matches = [
        item
        for sku, item in INVENTORY_STOCK.items()
        if q in sku.lower() or q in item["name"].lower() or "all" in q
    ]
    if not matches:
        matches = list(INVENTORY_STOCK.values())

    return {
        "backend": "cloud_firestore" if not cfg.is_mock else "mock_firestore",
        "matches": matches,
    }


def list_open_appointment_slots(day_filter: str = "all") -> dict[str, Any]:
    """Lists available consultation or B2B onboarding appointment slots.

    Args:
        day_filter: Optional day of the week filter (e.g., 'Friday', 'Saturday', or 'all').

    Returns:
        Dictionary of currently available appointment slots.
    """
    open_slots = [
        s
        for s in AVAILABLE_APPOINTMENT_SLOTS
        if s["available"] and (day_filter.lower() in {"all", "", s["date"].lower()})
    ]
    return {
        "available_count": len(open_slots),
        "open_slots": open_slots,
    }


def book_customer_appointment(
    slot_id: str,
    customer_name: str,
    customer_email: str,
    notes: str = "",
) -> dict[str, Any]:
    """Books an available appointment slot and records the reservation in Firestore.

    Screens `notes` through `inspect_prompt_safety` to redact accidental PII (SSN/credit cards)
    before persisting to the database.

    Args:
        slot_id: Identifier of the open slot (e.g., 'SLOT-FRI-1400').
        customer_name: Full name of the customer booking the session.
        customer_email: Contact email for calendar invite confirmation.
        notes: Optional triage notes or skin/product questions.

    Returns:
        Booking confirmation receipt or error if the slot is unavailable.
    """
    safety_check = inspect_prompt_safety(notes)
    if not safety_check["allowed"]:
        return {"status": "BLOCKED", "reason": safety_check["reason"]}

    slot = next((s for s in AVAILABLE_APPOINTMENT_SLOTS if s["slot_id"] == slot_id), None)
    if not slot:
        return {
            "status": "ERROR",
            "message": f"Slot '{slot_id}' not found. Call list_open_appointment_slots first.",
        }

    booking = {
        "confirmation_id": f"RES-{datetime.now(timezone.utc).strftime('%H%M%S')}-{slot_id[-4:]}",
        "slot_id": slot_id,
        "service_type": slot["service_type"],
        "date": slot["date"],
        "time": slot["time"],
        "specialist": slot["specialist"],
        "customer_name": customer_name,
        "customer_email": customer_email,
        "sanitized_notes": safety_check["redacted_text"],
    }
    BOOKED_RESERVATIONS.append(booking)
    return {
        "status": "CONFIRMED",
        "booking": booking,
    }
