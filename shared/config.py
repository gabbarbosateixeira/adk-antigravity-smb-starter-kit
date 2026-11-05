"""Centralized configuration for Google Models, GCP projects, and Governance Guardrails.

Aligned with https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class PlatformConfig:
    """Immutable configuration following the GCP Well-Architected Framework."""

    project_id: str = field(
        default_factory=lambda: os.getenv("GOOGLE_CLOUD_PROJECT", "demo-smb-launchpad")
    )
    location: str = field(
        default_factory=lambda: os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    )
    use_vertexai: bool = field(
        default_factory=lambda: os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "TRUE").upper() == "TRUE"
    )
    data_backend: str = field(
        default_factory=lambda: os.getenv("DATA_BACKEND", "mock").lower()
    )

    # Google Models Lineup (Gemini Enterprise Agent Platform)
    pro_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_PRO_MODEL", "gemini-3.1-pro-preview")
    )
    flash_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_FLASH_MODEL", "gemini-3-flash-preview")
    )
    flash_lite_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_FLASH_LITE_MODEL", "gemini-3.1-flash-lite")
    )
    image_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")
    )

    # Data Store & Database Identifiers
    vertex_search_data_store_id: str = field(
        default_factory=lambda: os.getenv(
            "VERTEX_SEARCH_DATA_STORE_ID", "aura-brand-and-catalog-store"
        )
    )
    firestore_database: str = field(
        default_factory=lambda: os.getenv("FIRESTORE_DATABASE", "(default)")
    )
    bigquery_dataset: str = field(
        default_factory=lambda: os.getenv("BIGQUERY_DATASET", "smb_customer_analytics")
    )

    # Governance & Guardrails
    max_autonomous_discount_pct: float = field(
        default_factory=lambda: float(os.getenv("MAX_AUTONOMOUS_DISCOUNT_PCT", "20.0"))
    )
    model_armor_template_id: str = field(
        default_factory=lambda: os.getenv(
            "MODEL_ARMOR_TEMPLATE_ID",
            "projects/demo-smb-launchpad/locations/us-central1/templates/smb-default-armor",
        )
    )
    enable_cloud_trace: bool = field(
        default_factory=lambda: os.getenv("ENABLE_CLOUD_TRACE", "FALSE").upper() == "TRUE"
    )

    @property
    def is_mock(self) -> bool:
        """Returns True when running in zero-config local mock data mode."""
        return self.data_backend != "gcp"


def get_config() -> PlatformConfig:
    """Returns the current platform configuration from environment variables."""
    return PlatformConfig()
