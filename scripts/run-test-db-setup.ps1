$ErrorActionPreference = "Stop"

$testDbName = "test_db"

$dbExists = docker compose exec -T postgres psql -U app_user -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$testDbName';"

if ($dbExists.Trim() -ne "1") {
    docker compose exec -T postgres psql -U app_user -d postgres -c "CREATE DATABASE $testDbName;"
}

& "$PSScriptRoot\run-test-db-migrations.ps1"