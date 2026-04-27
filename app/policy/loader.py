"""
Policy loading, validation, and runtime fingerprint generation.
"""

import hashlib

import yaml

from app.core.config import POLICY_FILE
from app.policy.models import LoadedPolicy, PolicyDocument


def load_agent_policy() -> LoadedPolicy:
    """
    Loads the policy document from the configured file path and returns a LoadedPolicy object.
    Returns:
        LoadedPolicy: An object containing the loaded policy document and its SHA256 hash.
    """
    policy_bytes = POLICY_FILE.read_bytes()
    policy_sha256 = hashlib.sha256(policy_bytes).hexdigest()
    data = yaml.safe_load(policy_bytes.decode("utf-8"))

    return LoadedPolicy(
        document=PolicyDocument.model_validate(data),
        policy_sha256=policy_sha256,
    )