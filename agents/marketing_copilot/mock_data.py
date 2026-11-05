"""Pre-seeded SMB Brand Kit, Product Catalog, and Past Campaign Benchmarks for Aura & Co.

Used when `DATA_BACKEND="mock"` so SMB workshops and tests run out-of-the-box with zero config.
When `DATA_BACKEND="gcp"`, tools query the Vertex AI Search / RAG Engine Data Store.
"""

from __future__ import annotations

BRAND_GUIDELINES = {
    "company_name": "Aura & Co. Botanical Wellness",
    "brand_voice": "Warm, science-backed, sustainable, and approachable—never pushy or overly clinical.",
    "target_personas": [
        {
            "name": "Busy Urban Professionals (25-45)",
            "pain_points": ["Stress recovery", "Clean ingredients", "Fast subscription convenience"],
        },
        {
            "name": "Boutique Spa & Studio Owners (B2B Wholesale)",
            "pain_points": ["Reliable bulk restocking", "High retail margins (50%+)", "Co-branded displays"],
        },
    ],
    "prohibited_claims": [
        "Never claim to cure or treat medical conditions (FDA compliance).",
        "Never offer sitewide discounts above 20% without explicit executive approval.",
    ],
    "visual_identity": {
        "palette": ["Sage Green (#6B8E78)", "Warm Terracotta (#D48C70)", "Oatmeal Cream (#F7F4EF)"],
        "photography_style": "Natural morning sunlight, linen textures, minimalist glass apothecary bottles.",
    },
}

PRODUCT_CATALOG = [
    {
        "sku": "AURA-SERUM-01",
        "name": "Nordic Berry Barrier Repair Serum",
        "category": "Skincare",
        "price_usd": 48.00,
        "gross_margin_pct": 74,
        "key_benefits": ["24-hour hydration", "Cold-pressed cloudberry antioxidants", "Refillable glass pod"],
        "top_customer_quote": "Saved my skin during winter flights—my third refill already!",
    },
    {
        "sku": "AURA-MIST-02",
        "name": "Hinoki & Magnesium Sleep Mist",
        "category": "Sleep & Recovery",
        "price_usd": 34.00,
        "gross_margin_pct": 78,
        "key_benefits": ["Japanese Hinoki wood oil", "Topical magnesium blend", "Non-staining pillow & body mist"],
        "top_customer_quote": "Our boutique yoga studio sells out of this every single month.",
    },
    {
        "sku": "AURA-BUNDLE-03",
        "name": "The Evening Reset Ritual Bundle",
        "category": "Bundles",
        "price_usd": 72.00,
        "gross_margin_pct": 76,
        "key_benefits": ["Combines Barrier Serum + Hinoki Sleep Mist", "Includes organic cotton travel pouch"],
        "top_customer_quote": "The best corporate and holiday gift set under $75.",
    },
]

MARKET_TRENDS_SNAPSHOT = {
    "skincare": {
        "trending_keywords": ["skin barrier repair", "refillable beauty", "waterless botanicals"],
        "competitor_promo_benchmark": "Competitors are running 15% off bundles + free shipping at $60.",
        "best_performing_channels": ["Instagram Reels", "SMS VIP Early Access", "LinkedIn Founder Story (B2B)"],
    },
    "sleep": {
        "trending_keywords": ["magnesium sleep routine", "evening cortisol reset", "hinoki aromatherapy"],
        "competitor_promo_benchmark": "Subscription-first brands offering free travel-size mist on 1st order.",
        "best_performing_channels": ["TikTok / Reels routine videos", "Email 3-part educational drip"],
    },
}
