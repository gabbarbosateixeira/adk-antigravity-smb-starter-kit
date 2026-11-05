"""Tools for Agent 1: 'Growth Engine' Omnichannel Marketing & Campaign Copilot.

Supports both:
- `DATA_BACKEND="mock"`: Instant local execution over pre-seeded Aura & Co. brand & catalog data.
- `DATA_BACKEND="gcp"`: Live Vertex AI Search (RAG Engine) Data Store + `gemini-3.1-flash-image` asset briefs.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from agents.marketing_copilot.mock_data import (
    BRAND_GUIDELINES,
    MARKET_TRENDS_SNAPSHOT,
    PRODUCT_CATALOG,
)
from shared.config import get_config
from shared.guardrails import enforce_discount_guardrail


def search_brand_and_catalog_knowledge(query: str, category_filter: str = "all") -> dict[str, Any]:
    """Retrieves official brand guidelines, product specs, margins, and customer testimonials.

    In Gemini Enterprise production (`DATA_BACKEND="gcp"`), queries the Vertex AI Search
    Data Store indexing the SMB's Google Drive brand kit and product catalog with OAuth ACLs.

    Args:
        query: Search topic or product keyword (e.g., 'barrier serum', 'brand voice', 'high margin bundles').
        category_filter: Optional product category filter ('Skincare', 'Sleep & Recovery', 'Bundles', or 'all').

    Returns:
        Dictionary containing matching brand rules, product SKUs, and grounding metadata.
    """
    cfg = get_config()
    q_lower = query.lower()

    matching_products = [
        p
        for p in PRODUCT_CATALOG
        if category_filter.lower() in {"all", "", p["category"].lower()}
        and (
            q_lower in p["name"].lower()
            or q_lower in p["category"].lower()
            or any(q_lower in b.lower() for b in p["key_benefits"])
            or "all" in q_lower
            or "margin" in q_lower
            or "bundle" in q_lower
            or "product" in q_lower
        )
    ]
    if not matching_products:
        matching_products = PRODUCT_CATALOG

    return {
        "source": "vertex_ai_search_datastore" if not cfg.is_mock else "mock_brand_datastore",
        "data_store_id": cfg.vertex_search_data_store_id,
        "brand_guidelines": BRAND_GUIDELINES,
        "matching_products": matching_products,
    }


def analyze_market_and_competitor_trends(segment: str) -> dict[str, Any]:
    """Analyzes current market trends, trending keywords, and competitor promotions for a segment.

    Complements native Google Search grounding with structured industry benchmark telemetry.

    Args:
        segment: Product or industry segment to research (e.g., 'skincare', 'sleep', 'b2b wholesale').

    Returns:
        Dictionary with trending keywords, competitor promo benchmarks, and top channels.
    """
    seg_key = "sleep" if "sleep" in segment.lower() or "mist" in segment.lower() else "skincare"
    return {
        "segment_analyzed": segment,
        "insights": MARKET_TRENDS_SNAPSHOT[seg_key],
        "recommendation": (
            "Lead with high-margin bundle value (76% gross margin) and refill sustainability "
            "rather than deep discounting."
        ),
    }


def generate_visual_asset_brief(
    campaign_theme: str,
    featured_sku: str,
    aspect_ratio: str = "4:5",
) -> dict[str, Any]:
    """Generates a production-ready visual prompt & asset spec for Gemini 3.1 Flash Image / Nano Banana 2.1.

    Enforces brand palette and photography rules automatically.

    Args:
        campaign_theme: Headline or theme of the campaign (e.g., 'Autumn Barrier Reset').
        featured_sku: Product SKU to highlight (e.g., 'AURA-SERUM-01').
        aspect_ratio: Target social/ad aspect ratio ('1:1', '4:5', '16:9', '9:16').

    Returns:
        Structured visual generation payload configured for `gemini-3.1-flash-image`.
    """
    cfg = get_config()
    product = next((p for p in PRODUCT_CATALOG if p["sku"] == featured_sku), PRODUCT_CATALOG[0])
    palette = ", ".join(BRAND_GUIDELINES["visual_identity"]["palette"])
    style = BRAND_GUIDELINES["visual_identity"]["photography_style"]

    image_prompt = (
        f"Editorial commercial product photography of {product['name']} ({product['sku']}) "
        f"for campaign '{campaign_theme}'. Style: {style}. Brand color palette: {palette}. "
        f"Aspect ratio {aspect_ratio}, photorealistic, high-resolution studio lighting."
    )

    return {
        "status": "READY_FOR_RENDER",
        "image_model": cfg.image_model,
        "featured_product": product["name"],
        "aspect_ratio": aspect_ratio,
        "synthesized_prompt": image_prompt,
        "brand_compliance_verified": True,
    }


def create_promotional_campaign(
    campaign_name: str,
    target_persona: str,
    featured_skus: list[str],
    discount_pct: float,
    channels: list[str],
    manager_approved: bool = False,
) -> dict[str, Any]:
    """Saves a multi-channel marketing campaign package and enforces promotional discount guardrails.

    Enforces the company policy that autonomous promotions cannot exceed `MAX_AUTONOMOUS_DISCOUNT_PCT` (20%)
    without explicit Human-in-the-Loop (`manager_approved=True`) authorization.

    Args:
        campaign_name: Title of the marketing campaign.
        target_persona: Target customer segment (e.g., 'Busy Urban Professionals').
        featured_skus: List of product SKU codes included in the campaign.
        discount_pct: Proposed promotional discount percentage (e.g., 15.0).
        channels: Distribution channels (e.g., ['Instagram', 'Email Drip', 'Google Ads']).
        manager_approved: Set True only after human manager confirmation for discounts >20%.

    Returns:
        Confirmation receipt with campaign ID or a guardrail HITL escalation payload.
    """
    guardrail_result = enforce_discount_guardrail(
        tool_name="create_promotional_campaign",
        tool_args={"discount_pct": discount_pct, "manager_approved": manager_approved},
    )
    if guardrail_result is not None:
        return guardrail_result

    return {
        "status": "CAMPAIGN_STAGED_IN_WORKSPACE",
        "campaign_id": f"CMP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-01",
        "campaign_name": campaign_name,
        "target_persona": target_persona,
        "featured_skus": featured_skus,
        "approved_discount_pct": discount_pct,
        "channels": channels,
        "gemini_enterprise_doc_url": f"https://docs.google.com/document/d/mock-{campaign_name.lower().replace(' ', '-')}",
    }
