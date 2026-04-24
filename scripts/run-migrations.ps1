Get-Content migrations/001_create_documents_table.sql | docker compose exec -T postgres psql -U app_user -d app_db
Get-Content migrations/002_seed_documents.sql | docker compose exec -T postgres psql -U app_user -d app_db
Get-Content migrations/003_create_pdp_audit_table.sql | docker compose exec -T postgres psql -U app_user -d app_db
Get-Content migrations/004_add_policy_sha256_to_pdp_audit.sql | docker compose exec -T postgres psql -U app_user -d app_db
Get-Content migrations/005_change_pdp_audit_resource_to_text_array.sql | docker compose exec -T postgres psql -U app_user -d app_db
Get-Content migrations/006_revert_pdp_audit_resource_to_text.sql | docker compose exec -T postgres psql -U app_user -d app_db