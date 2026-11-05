"""Pre-seeded Customer Telemetry, Support Tickets, and Retention Policy Rules for Agent 3.

Used when `DATA_BACKEND="mock"`. When `DATA_BACKEND="gcp"`, tools query BigQuery & Firestore.
"""

from __future__ import annotations

CUSTOMER_CHURN_TELEMETRY = {
    "CUST-1042": {
        "customer_id": "CUST-1042",
        "account_name": "Solstice Yoga & Wellness Collective",
        "segment": "B2B Wholesale Partner",
        "annual_contract_value_usd": 14400.00,
        "days_since_last_order": 58,
        "normal_order_cadence_days": 21,
        "order_velocity_change_pct": -64.0,
        "csat_score": 2.5,
        "churn_probability_score": 0.87,
        "risk_tier": "CRITICAL",
    },
    "CUST-2089": {
        "customer_id": "CUST-2089",
        "account_name": "Liam O'Connor",
        "segment": "VIP DTC Subscriber",
        "annual_contract_value_usd": 680.00,
        "days_since_last_order": 41,
        "normal_order_cadence_days": 30,
        "order_velocity_change_pct": -32.0,
        "csat_score": 3.8,
        "churn_probability_score": 0.62,
        "risk_tier": "HIGH",
    },
    "CUST-3015": {
        "customer_id": "CUST-3015",
        "account_name": "Verdant Apothecary",
        "segment": "B2B Wholesale Partner",
        "annual_contract_value_usd": 9200.00,
        "days_since_last_order": 14,
        "normal_order_cadence_days": 21,
        "order_velocity_change_pct": +12.0,
        "csat_score": 4.9,
        "churn_probability_score": 0.08,
        "risk_tier": "LOW",
    },
}

CUSTOMER_INTERACTION_HISTORY = {
    "CUST-1042": [
        {
            "ticket_id": "TCK-881",
            "date": "12 days ago",
            "channel": "Email Support",
            "sentiment": "Negative",
            "summary": (
                "Complained that their last two wholesale shipments of Hinoki Sleep Mist arrived "
                "4 days late, causing them to miss a weekend studio retreat."
            ),
            "primary_churn_driver": "FULFILLMENT_DELAY_AND_STOCKOUT",
        },
        {
            "ticket_id": "TCK-894",
            "date": "3 days ago",
            "channel": "Billing Portal",
            "sentiment": "Neutral/Risk",
            "summary": "Downloaded historical invoices and paused auto-replenishment schedule.",
            "primary_churn_driver": "COMPETITOR_EVALUATION",
        },
    ],
    "CUST-2089": [
        {
            "ticket_id": "TCK-902",
            "date": "6 days ago",
            "channel": "Subscription Portal",
            "sentiment": "Price Sensitive",
            "summary": "Clicked 'Cancel Subscription' survey step, selecting 'Too expensive right now'.",
            "primary_churn_driver": "PRICE_SENSITIVITY",
        }
    ],
    "CUST-3015": [],
}

RETENTION_POLICY_PLAYBOOK = {
    "FULFILLMENT_DELAY_AND_STOCKOUT": {
        "recommended_discount_pct": 15.0,
        "max_autonomous_discount_pct": 20.0,
        "perks": ["Complimentary Expedited 2-Day Air on next 3 orders", "Dedicated safety stock allocation"],
    },
    "PRICE_SENSITIVITY": {
        "recommended_discount_pct": 15.0,
        "max_autonomous_discount_pct": 20.0,
        "perks": ["Switch to bi-monthly refill pod cadence", "Free travel-size mist on next renewal"],
    },
}
