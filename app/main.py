
from fastapi import FastAPI
from fastmcp import FastMCP
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context
from fastmcp.utilities.lifespan import combine_lifespans
from fastapi.concurrency import asynccontextmanager

from app.api.routes import router, api_v1_router
from app.core.config import SERVICE_NAME
from app.policy.loader import load_agent_policy
from app.proxy.wrapper import proxy_process_tool_invocation


@asynccontextmanager
async def lifespan(app: FastAPI):
  app.state.agent_policy = load_agent_policy()
  yield
   
mcp = FastMCP(name="MCP Service")
mcp_app = mcp.http_app(path="/", json_response=True)

app = FastAPI(title=SERVICE_NAME, lifespan=combine_lifespans(mcp_app.lifespan, lifespan))

app.mount("/mcp", mcp_app)

app.state.agent_policy = load_agent_policy()

app.include_router(router)  
app.include_router(api_v1_router)

def resolve_agent_id(ctx: Context) -> str:
  if ctx.request_context.meta:
    return ctx.request_context.meta.get("agent_id", "unknown-agent")
  return "unknown-agent"

@mcp.tool(name="list_documents")
async def list_documents(query: str, ctx: Context = CurrentContext()) -> dict:
  """List all document titles and summaries matching the query."""

  proxy_response = proxy_process_tool_invocation(
    agent_id=resolve_agent_id(ctx),
    tool_name="list_documents",
    tool_arguments={"query": query},
    policy=app.state.agent_policy
  )

  return proxy_response


@mcp.tool(name="docs_tool")
async def docs_tool(document_id: str, ctx: Context = CurrentContext() ) -> dict:
  """Example tool implementation that normalizes the incoming MCP request and simulates a response."""
   
  proxy_response = proxy_process_tool_invocation(
    agent_id=resolve_agent_id(ctx),
    tool_name="docs_tool",
    tool_arguments={"document_id": document_id},
    policy=app.state.agent_policy
  )    

  return proxy_response
  
