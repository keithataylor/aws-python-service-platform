"""Policy loading utilities."""
import hashlib

import yaml

from app.core.config import POLICY_FILE
from app.policy.models import LoadedPolicy, PolicyDocument


# def load_agent_policy() -> PolicyDocument:
#     with POLICY_FILE.open("r", encoding="utf-8") as file:
#         data = yaml.safe_load(file)
#     return PolicyDocument.model_validate(data)


def load_agent_policy() -> LoadedPolicy:
    policy_bytes = POLICY_FILE.read_bytes()
    policy_sha256 = hashlib.sha256(policy_bytes).hexdigest()
    data = yaml.safe_load(policy_bytes.decode("utf-8"))

    return LoadedPolicy(
        document=PolicyDocument.model_validate(data),
        policy_sha256=policy_sha256,
    )