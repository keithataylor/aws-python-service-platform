""" Task service functions. """

from app.schemas.task import TaskStatusResponse, TaskSubmitResponse
from uuid import uuid4

def submit_task(name: str) -> TaskSubmitResponse:
    return TaskSubmitResponse(task_id=str(uuid4()), status="submitted")

def get_task_status(task_id: str) -> TaskStatusResponse:
    return TaskStatusResponse(task_id=task_id, status="submitted")