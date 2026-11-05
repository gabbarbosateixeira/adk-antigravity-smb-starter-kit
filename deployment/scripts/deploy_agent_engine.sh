#!/usr/bin/env bash
# ============================================================================
# Stage 1 (Day-1 Fast PoC): Deploy to Vertex AI Agent Engine & Register in Gemini Enterprise
# ============================================================================
set -euo pipefail

AGENT_FOLDER="${1:-agents/marketing_copilot}"
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?Please set GOOGLE_CLOUD_PROJECT in your environment or .env}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
GEMINI_APP_ID="${GEMINI_ENTERPRISE_APP_ID:-}"

echo "============================================================================"
echo "1. Deploying '${AGENT_FOLDER}' to Vertex AI Agent Engine (Agent Runtime)..."
echo "============================================================================"

if command -v agents-cli >/dev/null 2>&1; then
  agents-cli deploy \
    --target agent-engine \
    --agent-path "${AGENT_FOLDER}" \
    --project "${PROJECT_ID}" \
    --region "${REGION}"
else
  adk deploy agent_engine \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    "${AGENT_FOLDER}"
fi

if [[ -n "${GEMINI_APP_ID}" ]]; then
  echo "============================================================================"
  echo "2. Registering Agent Engine Resource with Gemini Enterprise App (${GEMINI_APP_ID})..."
  echo "============================================================================"
  echo "POST https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/global/collections/default_collection/engines/${GEMINI_APP_ID}/assistants/default_assistant/agents"
fi
