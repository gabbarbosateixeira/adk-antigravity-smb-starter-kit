variable "project_id" {
  description = "Google Cloud Project ID for the SMB Agent Platform deployment."
  type        = string
}

variable "region" {
  description = "Primary GCP region for Cloud Run and Vertex AI Agent Engine."
  type        = string
  default     = "us-central1"
}

variable "container_image" {
  description = "Artifact Registry container image URI for the ADK 2.0 agent service."
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}

output "agent_service_account_email" {
  description = "Least-privilege Service Account email used by the deployed SMB agents."
  value       = google_service_account.smb_agent_runtime_sa.email
}

output "frontdesk_cloud_run_uri" {
  description = "Private Cloud Run URI for the 24/7 Front-Desk Triage Agent (/run_sse)."
  value       = google_cloud_run_v2_service.frontdesk_triage_service.uri
}
