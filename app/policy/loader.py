"""Policy loading utilities."""
import yaml

from app.core.config import POLICY_FILE
from app.policy.models import AgentPolicyDocument


def load_agent_policy() -> AgentPolicyDocument:
    with POLICY_FILE.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return AgentPolicyDocument.model_validate(data)

