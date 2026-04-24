from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PDPAuditEvent(BaseModel):
    request_id: str
    agent_id: str
    server_name: str
    tool_name: str
    invocation_action: str
    resource: str
    decision: str
    rationale: list[str]
    policy_version: str
    policy_sha256: str = None
    created_at: datetime

    model_config = ConfigDict(extra="forbid")