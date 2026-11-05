#!/usr/bin/env bash
# ============================================================================
# Stage 1 (Day-1 Fast PoC): 1-Command Cloud Run Deployment via agents-cli / adk
# Follows GCP Well-Architected Security: --no-allow-unauthenticated by default
# ============================================================================
set -euo pipefail

AGENT_FOLDER="${1:-agents/frontdesk_triage}"
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?Please set GOOGLE_CLOUD_PROJECT in your environment or .env}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
SERVICE_NAME="smb-$(basename "${AGENT_FOLDER}" | tr '_' '-')"

echo "============================================================================"
echo "Deploying ADK 2.0 Agent '${AGENT_FOLDER}' to Cloud Run (${SERVICE_NAME})"
echo "Project: ${PROJECT_ID} | Region: ${REGION}"
echo "============================================================================"

if command -v agents-cli >/dev/null 2>&1; then
  agents-cli deploy \
    --agent-path "${AGENT_FOLDER}" \
    --project "${PROJECT_ID}" \
    --region "${REGION}" \
    --service-name "${SERVICE_NAME}" \
    --no-allow-unauthenticated
else
  adk deploy cloud_run \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --service_name="${SERVICE_NAME}" \
    --with_ui=false \
    "${AGENT_FOLDER}"
fi

echo "Deployment complete. Expose externally ONLY via the BFF with OIDC or Identity-Aware Proxy (IAP)."
