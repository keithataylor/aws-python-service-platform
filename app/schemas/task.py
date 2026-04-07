""" Task-related API schemas. """

from pydantic import BaseModel, Field
from typing import Literal

TaskStatus = Literal["submitted", "running", "completed", "failed"]

class TaskSubmitRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class TaskSubmitResponse(BaseModel):
    task_id: str
    status: TaskStatus


class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus