# ============================================================================
# Stage 2 (Day-2 Production IaC): Google Cloud Well-Architected Terraform
# Provisions Least-Privilege Service Accounts, Artifact Registry, Cloud Run,
# and Discovery Engine / Vertex AI APIs for the 3 SMB Starter Agents.
# ============================================================================

terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.12"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  required_apis = [
    "aiplatform.googleapis.com",
    "discoveryengine.googleapis.com",
    "run.googleapis.com",
    "firestore.googleapis.com",
    "bigquery.googleapis.com",
    "cloudtrace.googleapis.com",
    "modelarmor.googleapis.com",
  ]
}

resource "google_project_service" "agent_platform_apis" {
  for_each           = toset(local.required_apis)
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# Dedicated Least-Privilege Runtime Identity (supplementing SPIFFE Agent Identity)
resource "google_service_account" "smb_agent_runtime_sa" {
  account_id   = "smb-agent-runtime-sa"
  display_name = "SMB Agent Platform Least-Privilege Runtime SA"
}

resource "google_project_iam_member" "agent_least_privilege_roles" {
  for_each = toset([
    "roles/aiplatform.user",
    "roles/discoveryengine.viewer",
    "roles/datastore.user",
    "roles/bigquery.dataViewer",
    "roles/cloudtrace.agent",
  ])
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.smb_agent_runtime_sa.email}"
}

# Private Cloud Run Service for External Portal Front-Desk Agent (/run_sse)
resource "google_cloud_run_v2_service" "frontdesk_triage_service" {
  name     = "smb-frontdesk-triage-agent"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    service_account = google_service_account.smb_agent_runtime_sa.email
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
    containers {
      image = var.container_image
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.region
      }
      env {
        name  = "GEMINI_PRO_MODEL"
        value = "gemini-3.1-pro-preview"
      }
      env {
        name  = "GEMINI_FLASH_MODEL"
        value = "gemini-3-flash-preview"
      }
      env {
        name  = "DATA_BACKEND"
        value = "gcp"
      }
    }
  }
  depends_on = [google_project_service.agent_platform_apis]
}
