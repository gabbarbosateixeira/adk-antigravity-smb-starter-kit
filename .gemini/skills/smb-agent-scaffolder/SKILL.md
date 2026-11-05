---
name: smb-agent-scaffolder
description: Interactive Antigravity skill for customizing, evaluating, and deploying the 3 SMB Starter Agents (Marketing Copilot, 24/7 Front-Desk Triage, and Churn Retention Radar) using ADK 2.0 and agents-cli.
---

# SMB Agent Scaffolder & Customization Skill (`agents-cli` + ADK 2.0)

Use this skill when a user wants to adapt one of the 3 reference SMB agents to their specific industry (e.g., Dental Clinic, HVAC Services, E-Commerce, B2B SaaS, Law Firm, Fitness Studio), run evaluations, or deploy to Google Cloud.

## Step 1: Requirements Discovery (`/grill-me` Pattern)
Before modifying code, ask 3 concise questions to lock down the SMB customization:
1. **Vertical & Brand Tone:** What is the business name, industry, and desired brand voice?
2. **Data Source Mode:** Are we starting in instant local demo mode (`DATA_BACKEND=mock`) or wiring directly to a live GCP resource (Firestore collection, BigQuery table, or Vertex AI Search Data Store)?
3. **Target Surface & Guardrails:** Will this agent be registered in **Gemini Enterprise** (on **Agent Runtime**) or embedded in an external customer portal (on **Cloud Run** via `/run_sse`)? What numeric or policy guardrails (e.g., max discount `%`, booking hours) must be enforced via `before_tool_callback`?

## Step 2: Customize the Selected Template
- **Template 1 (`agents/01_marketing_copilot`)**:
  - Update brand guidelines and product catalog in `mock_data.py` or point `VERTEX_SEARCH_DATA_STORE_ID` to the customer's Drive/GCS data store.
  - Ensure `gemini-3.1-pro-preview` is used for campaign strategy and `gemini-3.1-flash-image` is configured for visual asset prompts.
- **Template 2 (`agents/02_frontdesk_triage`)**:
  - Update service slots / inventory items in `mock_data.py` or Firestore collection names in `tools.py`.
  - Keep `gemini-3-flash-preview` as the primary model for sub-second streaming triage over `/run_sse`.
- **Template 3 (`agents/03_churn_retention_radar`)**:
  - Update churn risk thresholds, customer telemetry fields, and retention discount tiers in `tools.py` and `guardrails.py`.
  - Verify `enforce_retention_policy_guardrail` blocks autonomous discounts above `MAX_AUTONOMOUS_DISCOUNT_PCT` and triggers Human-in-the-Loop confirmation.

## Step 3: Local Verification & Evaluation
Always run the unit & smoke test suite and the LLM-as-a-Judge evaluation before deploying:
```bash
# 1. Run deterministic unit and guardrail tests
pytest tests/

# 2. Launch ADK Visual Builder or CLI Playground for interactive inspection
adk web agents/
# OR via agents-cli:
agents-cli playground

# 3. Run Golden Dataset Evaluation
agents-cli eval run --config agents/<template_dir>/eval/eval_config.yaml --dataset agents/<template_dir>/eval/golden_dataset.json
```

## Step 4: Deployment (Two-Stage Maturity Model)
- **Stage 1 (Fast Day-1 PoC via Script):**
  ```bash
  ./deployment/scripts/deploy_cloud_run.sh <agent_folder>
  # OR for Gemini Enterprise via Agent Runtime:
  ./deployment/scripts/deploy_agent_engine.sh <agent_folder>
  ```
- **Stage 2 (Production IaC via Terraform):**
  ```bash
  cd deployment/terraform
  terraform init
  terraform plan -var="project_id=$GOOGLE_CLOUD_PROJECT"
  ```
