"""Tools for Agent 3: 'Retention Radar' Customer Churn & Win-Back Multi-Agent Pipeline.

Modeled on Codelab 2 (`create-low-code-agent-with-ADK-visual-builder`) & ADK 2.0 Graph Workflows:
- Sub-Agent 1 (`ChurnRiskDetector`) calls `fetch_at_risk_customers`.
- Sub-Agent 2 (`RootCauseDiagnosisAgent`) calls `diagnose_customer_churn_drivers`.
- Sub-Agent 3 (`WinBackActionAgent`) calls `issue_winback_offer` (protected by HITL & discount guardrails).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from agents.churn_retention_radar.mock_data import (
    CUSTOMER_CHURN_TELEMETRY,
    CUSTOMER_INTERACTION_HISTORY,
    RETENTION_POLICY_PLAYBOOK,
)
from shared.config import get_config
from shared.guardrails import enforce_discount_guardrail


def fetch_at_risk_customers(min_risk_tier: str = "HIGH") -> dict[str, Any]:
    """Queries BigQuery / CRM telemetry for accounts exhibiting high or critical churn risk.

    Args:
        min_risk_tier: Minimum risk tier to return ('CRITICAL', 'HIGH', or 'ALL').

    Returns:
        Dictionary of customer accounts sorted by churn probability and annual contract value.
    """
    cfg = get_config()
    tier = min_risk_tier.upper()
    if tier == "CRITICAL":
        allowed = {"CRITICAL"}
    elif tier == "HIGH":
        allowed = {"CRITICAL", "HIGH"}
    else:
        allowed = {"CRITICAL", "HIGH", "LOW"}

    accounts = [
        acct for acct in CUSTOMER_CHURN_TELEMETRY.values() if acct["risk_tier"] in allowed
    ]
    accounts.sort(key=lambda x: x["churn_probability_score"], reverse=True)

    return {
        "source": f"bigquery.{cfg.bigquery_dataset}" if not cfg.is_mock else "mock_bigquery_telemetry",
        "at_risk_count": len(accounts),
        "accounts": accounts,
    }


def diagnose_customer_churn_drivers(customer_id: str) -> dict[str, Any]:
    """Retrieves support tickets, billing actions, and policy playbooks to diagnose churn root cause.

    Args:
        customer_id: Account identifier (e.g., 'CUST-1042' or 'CUST-2089').

    Returns:
        Structured root-cause diagnosis and matching company retention policy playbook.
    """
    telemetry = CUSTOMER_CHURN_TELEMETRY.get(customer_id)
    if not telemetry:
        return {"status": "NOT_FOUND", "message": f"Unknown customer_id '{customer_id}'."}

    interactions = CUSTOMER_INTERACTION_HISTORY.get(customer_id, [])
    primary_driver = (
        interactions[0]["primary_churn_driver"] if interactions else "PRICE_SENSITIVITY"
    )
    policy = RETENTION_POLICY_PLAYBOOK.get(
        primary_driver, RETENTION_POLICY_PLAYBOOK["PRICE_SENSITIVITY"]
    )

    return {
        "customer_id": customer_id,
        "account_name": telemetry["account_name"],
        "risk_tier": telemetry["risk_tier"],
        "annual_contract_value_usd": telemetry["annual_contract_value_usd"],
        "recent_interactions": interactions,
        "diagnosed_primary_driver": primary_driver,
        "policy_playbook": policy,
    }


def issue_winback_offer(
    customer_id: str,
    discount_pct: float,
    added_perks: list[str],
    personalized_message: str,
    manager_approved: bool = False,
) -> dict[str, Any]:
    """Issues a personalized customer retention / win-back offer and logs a task in Gemini Enterprise.

    Protected by `enforce_discount_guardrail`: any discount above `MAX_AUTONOMOUS_DISCOUNT_PCT` (20%)
    without `manager_approved=True` is deterministically blocked and routed for Human-in-the-Loop sign-off.

    Args:
        customer_id: Target customer identifier (e.g., 'CUST-1042').
        discount_pct: Proposed retention discount percentage (e.g., 15.0).
        added_perks: Non-discount value-adds (e.g., ['Complimentary Expedited 2-Day Air']).
        personalized_message: Tailored outreach email or account manager script.
        manager_approved: True only when a human manager has explicitly approved a >20% exception.

    Returns:
        Execution receipt or HITL approval request payload.
    """
    guardrail_result = enforce_discount_guardrail(
        tool_name="issue_winback_offer",
        tool_args={"discount_pct": discount_pct, "manager_approved": manager_approved},
    )
    if guardrail_result is not None:
        return guardrail_result

    telemetry = CUSTOMER_CHURN_TELEMETRY.get(customer_id, {"account_name": customer_id})
    return {
        "status": "WINBACK_OFFER_DISPATCHED",
        "offer_id": f"RET-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{customer_id[-4:]}",
        "customer_id": customer_id,
        "account_name": telemetry["account_name"],
        "approved_discount_pct": discount_pct,
        "added_perks": added_perks,
        "personalized_message": personalized_message,
        "human_in_the_loop_verified": manager_approved or discount_pct <= 20.0,
    }
