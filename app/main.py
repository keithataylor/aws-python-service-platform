
"""
Application assembly for the FastAPI service and mounted FastMCP runtime.
"""

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastmcp import FastMCP
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context
from fastmcp.server.dependencies import CurrentRequest
from fastmcp.utilities.lifespan import combine_lifespans
from starlette.requests import Request

from app.api.deps import get_loaded_policy
from app.api.routes import api_v1_router, router
from app.core.config import SERVICE_NAME
from app.policy.loader import load_agent_policy
from app.proxy.identity import resolve_agent_identity_from_mcp_meta
from app.proxy.wrapper import proxy_process_tool_invocation


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.loaded_policy = load_agent_policy()
    yield
   
mcp = FastMCP(name="MCP Service")
mcp_app = mcp.http_app(path="/", json_response=True)

app = FastAPI(title=SERVICE_NAME, lifespan=combine_lifespans(mcp_app.lifespan, lifespan))

app.mount("/mcp", mcp_app)

loaded_policy = load_agent_policy()
app.state.loaded_policy = loaded_policy
mcp_app.state.loaded_policy = loaded_policy

app.include_router(router)  
app.include_router(api_v1_router)


@mcp.tool(name="list_documents")
async def list_documents(query: str, 
                         ctx: Context = CurrentContext(),
                         request: Request = CurrentRequest()
) -> dict:
    """List all document titles and summaries matching the query."""

    agent_identity = resolve_agent_identity_from_mcp_meta(ctx.request_context.meta)

    proxy_response = proxy_process_tool_invocation(
        agent_id = agent_identity.agent_id,
        tool_name = "list_documents",
        tool_arguments = {"query": query},
        loaded_policy = get_loaded_policy(request)
    )

    return proxy_response


@mcp.tool(name="docs_tool")
async def docs_tool(document_id: str, 
                    ctx: Context = CurrentContext(), 
                    request: Request = CurrentRequest()
) -> dict:
    """
    Example tool implementation that normalizes 
    the incoming MCP request and simulates a response.
    """
    agent_identity = resolve_agent_identity_from_mcp_meta(ctx.request_context.meta)

    proxy_response = proxy_process_tool_invocation(
        agent_id = agent_identity.agent_id,
        tool_name = "docs_tool",
        tool_arguments = {"document_id": document_id},
        loaded_policy = get_loaded_policy(request)
    )    

    return proxy_response
  
