param(
    [Parameter(Mandatory = $true)]
    [string]$RawApiKey,
    [string]$DocumentId = "doc1"
)

$ErrorActionPreference = "Stop"

$mcpUrl = "http://aspsp-dev-alb-1213226492.eu-west-2.elb.amazonaws.com/mcp/"

$commonHeaders = @{
    "Content-Type"    = "application/json"
    "Accept"          = "application/json, text/event-stream"
    "X-Agent-Api-Key" = $RawApiKey
}

$initBody = @{
    jsonrpc = "2.0"
    id = 1
    method = "initialize"
    params = @{
        protocolVersion = "2024-11-05"
        capabilities = @{}
        clientInfo = @{
            name = "manual-aws-smoke-test"
            version = "0.1.0"
        }
    }
} | ConvertTo-Json -Compress -Depth 10

$initResponse = Invoke-WebRequest `
    -Method POST `
    -Uri $mcpUrl `
    -Headers $commonHeaders `
    -Body $initBody

$sessionId = [string]$initResponse.Headers["mcp-session-id"]

if ([string]::IsNullOrWhiteSpace($sessionId)) {
    throw "MCP session ID was not returned."
}

Write-Host "MCP session created:"
Write-Host $sessionId

$sessionHeaders = $commonHeaders.Clone()
$sessionHeaders["Mcp-Session-Id"] = $sessionId

$initializedBody = @{
    jsonrpc = "2.0"
    method = "notifications/initialized"
} | ConvertTo-Json -Compress -Depth 5

Invoke-WebRequest `
    -Method POST `
    -Uri $mcpUrl `
    -Headers $sessionHeaders `
    -Body $initializedBody | Out-Null

Write-Host "MCP initialized notification accepted."

$toolBody = @{
    jsonrpc = "2.0"
    id = 4
    method = "tools/call"
    params = @{
        name = "docs_tool"
        arguments = @{
            document_id = $DocumentId
        }
    }
} | ConvertTo-Json -Compress -Depth 10

$toolResponse = Invoke-WebRequest `
    -Method POST `
    -Uri $mcpUrl `
    -Headers $sessionHeaders `
    -Body $toolBody

Write-Host "Tool response status:"
Write-Host $toolResponse.StatusCode

Write-Host "Tool response body:"
Write-Host $toolResponse.Content