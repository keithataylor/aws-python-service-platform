"""Policy loading utilities."""
import yaml

from app.core.config import POLICY_FILE
from app.policy.models import PolicyDocument


def load_agent_policy() -> PolicyDocument:
    with POLICY_FILE.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return PolicyDocument.model_validate(data)

