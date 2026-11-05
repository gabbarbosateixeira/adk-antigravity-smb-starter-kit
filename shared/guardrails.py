"""Deterministic Governance, Security, and Guardrail Callbacks for ADK 2.0 Agents.

Implements the 'Govern' pillar of the Gemini Enterprise Agent Platform:
- Prompt Injection & PII Sanitization (Local fallback + Model Armor hook)
- Deterministic Tool Policy Enforcement (`before_tool_callback`)
- Agent Identity & End-User OAuth Context Verification
"""

from __future__ import annotations

import logging
import re
from typing import Any

from shared.config import get_config

logger = logging.getLogger(__name__)

# Basic patterns for demonstration of defense-in-depth alongside Model Armor
_SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"system\s+override\s+grant\s+admin", re.IGNORECASE),
    re.compile(r"bypass\s+discount\s+limit", re.IGNORECASE),
]


def inspect_prompt_safety(user_text: str) -> dict[str, Any]:
    """Screens incoming user input for prompt injection and raw PII before tool execution.

    In production on Gemini Enterprise Agent Platform, this works in tandem with
    **Model Armor** and **Agent Gateway** at the ingress/egress boundary.
    """
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(user_text):
            logger.warning("Blocked adversarial prompt injection attempt.")
            return {
                "allowed": False,
                "reason": "Blocked by security guardrail: Potential prompt injection or policy bypass detected.",
                "redacted_text": "[REDACTED_INJECTION_ATTEMPT]",
            }

    redacted = _SSN_PATTERN.sub("[REDACTED_SSN]", user_text)
    redacted = _CREDIT_CARD_PATTERN.sub("[REDACTED_PAN]", redacted)
    return {
        "allowed": True,
        "reason": "passed",
        "redacted_text": redacted,
        "pii_detected": redacted != user_text,
    }


def enforce_discount_guardrail(
    tool_name: str,
    tool_args: dict[str, Any],
    max_discount_pct: float | None = None,
) -> dict[str, Any] | None:
    """Deterministic `before_tool_callback` guardrail for retention & promo tools.

    Blocks any autonomous discount offer that exceeds `MAX_AUTONOMOUS_DISCOUNT_PCT` (default 20%)
    unless `manager_approved=True` is explicitly provided via Human-in-the-Loop (HITL) confirmation.

    Returns:
        `None` if the tool execution is permitted to proceed, or a `dict` payload
        intercepting the tool call with a policy violation / HITL escalation response.
    """
    cfg = get_config()
    limit = max_discount_pct if max_discount_pct is not None else cfg.max_autonomous_discount_pct

    if tool_name in {"issue_winback_offer", "create_promotional_campaign"}:
        requested_discount = float(tool_args.get("discount_pct", 0.0))
        manager_approved = bool(tool_args.get("manager_approved", False))

        if requested_discount > limit and not manager_approved:
            logger.warning(
                "Guardrail intercepted %s: requested discount %.1f%% exceeds autonomous limit %.1f%%",
                tool_name,
                requested_discount,
                limit,
            )
            return {
                "status": "HITL_APPROVAL_REQUIRED",
                "guardrail_triggered": True,
                "PolicyRule": f"Autonomous discounts cannot exceed {limit:.0f}%.",
                "requested_discount_pct": requested_discount,
                "max_autonomous_discount_pct": limit,
                "action_required": (
                    f"Request Human-in-the-Loop manager approval in Gemini Enterprise or re-submit "
                    f"with discount_pct <= {limit:.0f}%."
                ),
            }
    return None
