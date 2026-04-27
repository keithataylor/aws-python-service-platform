"""
API route definitions.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_agent_policy
from app.core.config import APP_VERSION, SERVICE_NAME
from app.db.connection import check_database_health
from app.policy.evaluator import pdp_evaluate_agent_action
from app.policy.models import PolicyDocument
from app.schemas.invocation import InvocationDecisionRequest, InvocationDecisionResponse
from app.schemas.system import HealthResponse, ServiceInfoResponse

router = APIRouter()

api_v1_router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=HealthResponse, status_code=200)
async def health_check() -> HealthResponse:
    """ Return service health status. """
    # Check database connectivity.
    if not check_database_health():
        raise HTTPException(status_code=503, detail="database connection failed")
    return HealthResponse(status="ok")


@api_v1_router.get("/service-info", response_model=ServiceInfoResponse, status_code=200)
async def service_info() -> ServiceInfoResponse:  
    """ Return basic service metadata. """
    return ServiceInfoResponse(service=SERVICE_NAME, version=APP_VERSION)


@api_v1_router.post(
        "/agent-actions/evaluate",
        response_model=InvocationDecisionResponse,
        status_code=200,
)
async def evaluate_agent_action_endpoint(
    payload: InvocationDecisionRequest,
    policy: Annotated[PolicyDocument, Depends(get_agent_policy)],
) -> InvocationDecisionResponse:
    """Evaluate an agent action request."""
    return pdp_evaluate_agent_action(payload, policy)