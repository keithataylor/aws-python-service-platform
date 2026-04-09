
class InvocationDecisionRequest(BaseModel):
    request_id: str
    agent_id: str
    server_name: str
    tool_name: str
    action: str
    resource: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)

