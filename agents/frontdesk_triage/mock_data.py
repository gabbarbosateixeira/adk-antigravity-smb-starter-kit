"""Pre-seeded Inventory, Consultation Slots, and Store Policies for Agent 2 (Front-Desk Triage).

Used when `DATA_BACKEND="mock"`. When `DATA_BACKEND="gcp"`, tools query Cloud Firestore.
"""

from __future__ import annotations

INVENTORY_STOCK = {
    "AURA-SERUM-01": {
        "sku": "AURA-SERUM-01",
        "name": "Nordic Berry Barrier Repair Serum",
        "in_stock": True,
        "available_units": 42,
        "price_usd": 48.00,
        "pickup_locations": ["Austin Flagship Studio", "Online Warehouse (2-Day Shipping)"],
    },
    "AURA-MIST-02": {
        "sku": "AURA-MIST-02",
        "name": "Hinoki & Magnesium Sleep Mist",
        "in_stock": True,
        "available_units": 19,
        "price_usd": 34.00,
        "pickup_locations": ["Austin Flagship Studio", "Online Warehouse (2-Day Shipping)"],
    },
    "AURA-BUNDLE-03": {
        "sku": "AURA-BUNDLE-03",
        "name": "The Evening Reset Ritual Bundle",
        "in_stock": True,
        "available_units": 11,
        "price_usd": 72.00,
        "pickup_locations": ["Online Warehouse (2-Day Shipping)"],
    },
}

AVAILABLE_APPOINTMENT_SLOTS = [
    {
        "slot_id": "SLOT-FRI-1400",
        "service_type": "Custom Skin Barrier Consultation (30 min)",
        "date": "Friday",
        "time": "14:00 CST",
        "specialist": "Elena Vance, Lead Esthetician",
        "available": True,
    },
    {
        "slot_id": "SLOT-FRI-1600",
        "service_type": "B2B Wholesale & Spa Partner Onboarding (45 min)",
        "date": "Friday",
        "time": "16:00 CST",
        "specialist": "Marcus Chen, Account Director",
        "available": True,
    },
    {
        "slot_id": "SLOT-SAT-1030",
        "service_type": "Custom Skin Barrier Consultation (30 min)",
        "date": "Saturday",
        "time": "10:30 CST",
        "specialist": "Elena Vance, Lead Esthetician",
        "available": True,
    },
]

BOOKED_RESERVATIONS: list[dict[str, str]] = []
