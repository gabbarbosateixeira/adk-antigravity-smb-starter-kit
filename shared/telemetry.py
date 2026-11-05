"""OpenTelemetry Tracing & Observability setup for the 'Optimize' Pillar.

Exports agent spans, tool latencies, and token telemetry to Google Cloud Trace
when `ENABLE_CLOUD_TRACE=TRUE`, or provides clean structured console telemetry locally.
"""

from __future__ import annotations

import logging
from typing import Any

from shared.config import get_config

logger = logging.getLogger("smb_agent_telemetry")


def configure_telemetry(service_name: str) -> dict[str, Any]:
    """Configures OpenTelemetry tracing for ADK 2.0 agents."""
    cfg = get_config()
    if not cfg.enable_cloud_trace:
        return {
            "service_name": service_name,
            "exporter": "local_console",
            "cloud_trace_enabled": False,
        }

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        exporter = CloudTraceSpanExporter(project_id=cfg.project_id)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        logger.info("Initialized Google Cloud Trace exporter for %s", service_name)
        return {
            "service_name": service_name,
            "exporter": "google_cloud_trace",
            "project_id": cfg.project_id,
            "cloud_trace_enabled": True,
        }
    except Exception as exc:  # pragma: no cover - graceful fallback if credentials absent
        logger.warning("Falling back to local telemetry (%s)", exc)
        return {
            "service_name": service_name,
            "exporter": "local_fallback",
            "cloud_trace_enabled": False,
        }
