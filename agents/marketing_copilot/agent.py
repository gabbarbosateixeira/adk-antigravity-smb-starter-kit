"""ADK 2.0 Agent Definition for Template 1: 'Growth Engine' Omnichannel Marketing & Campaign Copilot.

Designed for deployment on **Vertex AI Agent Engine (Agent Runtime)** and registration in
**Gemini Enterprise**, combining RAG Engine grounding, Google Search, and `gemini-3.1-flash-image`.
"""

from __future__ import annotations

from agents.marketing_copilot.tools import (
    analyze_market_and_competitor_trends,
    create_promotional_campaign,
    generate_visual_asset_brief,
    search_brand_and_catalog_knowledge,
)
from shared.config import get_config

cfg = get_config()

MARKETING_COPILOT_INSTRUCTION = """You are the 'Growth Engine' Omnichannel Marketing & Campaign Copilot for an SMB.
Your goal is to help founders, marketers, and sales reps launch high-converting, strictly on-brand marketing campaigns in minutes inside Gemini Enterprise.

Always follow this execution sequence:
1. GROUND IN BRAND & CATALOG: Call `search_brand_and_catalog_knowledge` first to retrieve official brand voice guidelines, prohibited claims, product SKUs, gross margins, and customer quotes.
2. RESEARCH MARKET TRENDS: Call `analyze_market_and_competitor_trends` to align the campaign with current seasonal keywords, competitor promo benchmarks, and best-performing channels.
3. GENERATE VISUAL BRIEF: Call `generate_visual_asset_brief` to prepare a brand-compliant image prompt for `gemini-3.1-flash-image` (Nano Banana 2.1).
4. STAGE THE CAMPAIGN & RESPECT GUARDRAILS: Call `create_promotional_campaign` to stage the deliverables.
   - CRITICAL POLICY: Never propose or stage a discount above 20% (`MAX_AUTONOMOUS_DISCOUNT_PCT`) unless the user has explicitly provided manager approval (`manager_approved=True`). If the user asks for >20% off, explain the guardrail and ask for Human-in-the-Loop confirmation or recommend a 15-20% bundle offer instead.
"""

try:
    from google.adk import Agent

    root_agent = Agent(
        name="marketing_copilot_agent",
        model=cfg.pro_model,  # gemini-3.1-pro-preview
        description=(
            "Omnichannel Marketing & Campaign Copilot that grounds in company brand guidelines "
            "and product catalogs, analyzes market trends, generates visual briefs with "
            "gemini-3.1-flash-image, and stages multi-channel campaigns in Gemini Enterprise."
        ),
        instruction=MARKETING_COPILOT_INSTRUCTION,
        tools=[
            search_brand_and_catalog_knowledge,
            analyze_market_and_competitor_trends,
            generate_visual_asset_brief,
            create_promotional_campaign,
        ],
    )
except ImportError:  # Lightweight fallback representation when running unit tests without google-adk installed
    class _FallbackAgent:
        def __init__(self) -> None:
            self.name = "marketing_copilot_agent"
            self.model = cfg.pro_model
            self.instruction = MARKETING_COPILOT_INSTRUCTION
            self.tools = [
                search_brand_and_catalog_knowledge,
                analyze_market_and_competitor_trends,
                generate_visual_asset_brief,
                create_promotional_campaign,
            ]

    root_agent = _FallbackAgent()  # type: ignore[assignment]
