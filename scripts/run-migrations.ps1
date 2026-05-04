Get-Content migrations/001_create_documents_table.sql | docker compose exec -T postgres psql -U app_user -d app_db
Get-Content migrations/002_seed_documents.sql | docker compose exec -T postgres psql -U app_user -d app_db
Get-Content migrations/003_create_pdp_audit_table.sql | docker compose exec -T postgres psql -U app_user -d app_db
Get-Content migrations/004_create_registered_agent_credentials.sql | docker compose exec -T postgres psql -U app_user -d app_db