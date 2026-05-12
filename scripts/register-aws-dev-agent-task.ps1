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
            command = @("python", "scripts/register_aws_dev_agent.py")
        }
    )
} | ConvertTo-Json -Compress -Depth 5

$taskArn = aws ecs run-task `
    --cluster $cluster `
    --launch-type FARGATE `
    --task-definition $taskDefinition `
    --network-configuration $networkConfiguration `
    --overrides $overrides `
    --query "tasks[0].taskArn" `
    --output text

if ($LASTEXITCODE -ne 0) {
    throw "aws ecs run-task failed."
}

if ([string]::IsNullOrWhiteSpace($taskArn) -or $taskArn -eq "None") {
    throw "aws ecs run-task did not return a task ARN."
}

Write-Host "Started ECS registration task:"
Write-Host $taskArn