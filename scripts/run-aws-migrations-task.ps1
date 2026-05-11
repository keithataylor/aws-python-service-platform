$ErrorActionPreference = "Stop"

Push-Location "$PSScriptRoot\..\infra\terraform"

$cluster = terraform output -raw ecs_cluster_name
$taskDefinition = terraform output -raw ecs_task_definition_family
$appSecurityGroupId = terraform output -raw app_security_group_id
$publicSubnetIds = terraform output -json public_subnet_ids | ConvertFrom-Json

Pop-Location

$subnetList = $publicSubnetIds -join ","

$networkConfiguration = "awsvpcConfiguration={subnets=[$subnetList],securityGroups=[$appSecurityGroupId],assignPublicIp=ENABLED}"

$overrides = @{
    containerOverrides = @(
        @{
            name    = "app"
            command = @("python", "scripts/run_aws_migrations.py")
        }
    )
} | ConvertTo-Json -Compress -Depth 5

aws ecs run-task `
    --cluster $cluster `
    --launch-type FARGATE `
    --task-definition $taskDefinition `
    --network-configuration $networkConfiguration `
    --overrides $overrides `
    --query "tasks[0].taskArn" `
    --output text