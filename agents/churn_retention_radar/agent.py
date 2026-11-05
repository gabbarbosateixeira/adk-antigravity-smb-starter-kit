"""ADK 2.0 Multi-Agent Workflow Definition for Template 3: 'Retention Radar' Churn & Win-Back Agent.

Modeled on Codelab 2 (`create-low-code-agent-with-ADK-visual-builder`) and ADK 2.0 Graph Workflows:
Composes three specialized agents deterministically:
1. `churn_risk_detector_agent` (`gemini-3-flash-preview`)
2. `root_cause_diagnosis_agent` (`gemini-3.1-pro-preview`)
3. `winback_action_agent` (`gemini-3.1-pro-preview` + HITL / `before_tool_callback` guardrails)
"""

from __future__ import annotations

from agents.churn_retention_radar.tools import (
    diagnose_customer_churn_drivers,
    fetch_at_risk_customers,
    issue_winback_offer,
)
from shared.config import get_config

cfg = get_config()

DETECTOR_INSTRUCTION = """You are Step 1 (Churn Risk Detector) of the Retention Radar pipeline.
Call `fetch_at_risk_customers` to identify CRITICAL and HIGH churn risk accounts from BigQuery/CRM telemetry,
and pass their `customer_id`, `account_name`, `annual_contract_value_usd`, and `churn_probability_score` to the next stage.
"""

DIAGNOSIS_INSTRUCTION = """You are Step 2 (Root Cause Diagnosis Agent) of the Retention Radar pipeline.
For each at-risk customer identified in Step 1, call `diagnose_customer_churn_drivers` to inspect recent support tickets,
shipping delays, or cancellation survey responses, and match them to the company's `RETENTION_POLICY_PLAYBOOK`.
"""

WINBACK_INSTRUCTION = """You are Step 3 (Win-Back Action Agent) of the Retention Radar pipeline.
Using the diagnosis and policy playbook from Step 2, craft a personalized win-back offer and execute `issue_winback_offer`.
CRITICAL POLICY GUARDRAIL:
- Autonomous discounts CANNOT exceed 20% (`MAX_AUTONOMOUS_DISCOUNT_PCT=20.0`).
- Always lead with non-discount operational perks (like expedited 2-day air shipping or cadence adjustments) plus a 15%-20% discount.
- If a user explicitly requests a discount >20% without `manager_approved=True`, `issue_winback_offer` will trigger `HITL_APPROVAL_REQUIRED`. Report the guardrail status clearly and request manager sign-off.
"""

try:
    from google.adk import Agent
    from google.adk.agents import SequentialAgent

    churn_risk_detector_agent = Agent(
        name="churn_risk_detector_agent",
        model=cfg.flash_model,  # gemini-3-flash-preview
        description="Detects high and critical churn risk accounts from usage and order velocity telemetry.",
        instruction=DETECTOR_INSTRUCTION,
        tools=[fetch_at_risk_customers],
    )

    root_cause_diagnosis_agent = Agent(
        name="root_cause_diagnosis_agent",
        model=cfg.pro_model,  # gemini-3.1-pro-preview
        description="Diagnoses the primary churn driver from support tickets and billing interactions.",
        instruction=DIAGNOSIS_INSTRUCTION,
        tools=[diagnose_customer_churn_drivers],
    )

    winback_action_agent = Agent(
        name="winback_action_agent",
        model=cfg.pro_model,  # gemini-3.1-pro-preview
        description="Executes policy-compliant customer win-back offers with HITL discount guardrails.",
        instruction=WINBACK_INSTRUCTION,
        tools=[issue_winback_offer],
    )

    root_agent = SequentialAgent(
        name="churn_retention_radar_workflow",
        description=(
            "ADK 2.0 Multi-Agent Sequential Workflow that detects at-risk customers, diagnoses "
            "churn root causes, and dispatches policy-guarded win-back offers in Gemini Enterprise."
        ),
        sub_agents=[
            churn_risk_detector_agent,
            root_cause_diagnosis_agent,
            winback_action_agent,
        ],
    )
except ImportError:
    class _FallbackSequentialWorkflow:
        def __init__(self) -> None:
            self.name = "churn_retention_radar_workflow"
            self.model = cfg.pro_model
            self.sub_agents = [
                "churn_risk_detector_agent",
                "root_cause_diagnosis_agent",
                "winback_action_agent",
            ]
            self.tools = [
                fetch_at_risk_customers,
                diagnose_customer_churn_drivers,
                issue_winback_offer,
            ]

    root_agent = _FallbackSequentialWorkflow()  # type: ignore[assignment]
