from typing import Annotated
from fastapi import APIRouter, Depends
from app.policy.models import PolicyDocument
from app.schemas.system import HealthResponse, ServiceInfoResponse
from app.schemas.echo import EchoRequest, EchoResponse
from app.schemas.task import TaskSubmitRequest, TaskSubmitResponse, TaskStatusResponse
from app.schemas.invocation import InvocationDecisionRequest, InvocationDecisionResponse
from app.services.task_service import get_task_status, submit_task
from app.policy.evaluator import evaluate_agent_action
from app.api.deps import get_agent_policy

from app.core.config import APP_VERSION, SERVICE_NAME


router = APIRouter()

api_v1_router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=HealthResponse, status_code=200)
async def health_check() -> HealthResponse:
    """ Return service health status. """
    return HealthResponse(status="ok")


@api_v1_router.get("/service-info", response_model=ServiceInfoResponse, status_code=200)
async def service_info() -> ServiceInfoResponse:  
    """ Return basic service metadata. """
    return ServiceInfoResponse(service=SERVICE_NAME, version=APP_VERSION)


@api_v1_router.post("/echo", response_model=EchoResponse, status_code=200)
async def echo(payload: EchoRequest) -> EchoResponse:
    """Return the submitted text."""
    return EchoResponse(text=payload.text)


@api_v1_router.post("/tasks", response_model=TaskSubmitResponse, status_code=202)
async def submit_task_endpoint(payload: TaskSubmitRequest) -> TaskSubmitResponse:
    """Accept a task submission."""
    return submit_task(payload.name)


@api_v1_router.get("/tasks/{task_id}", response_model=TaskStatusResponse, status_code=200)
async def get_task_status_endpoint(task_id: str) -> TaskStatusResponse:
    """Return task status."""
    return get_task_status(task_id)


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
    return evaluate_agent_action(payload, policy)