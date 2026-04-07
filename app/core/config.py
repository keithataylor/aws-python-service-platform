from pathlib import Path

SERVICE_NAME = "AWS Python Service Platform"

APP_VERSION = "0.1.0"

BASE_DIR = Path(__file__).resolve().parents[2]
POLICY_FILE = BASE_DIR / "app" / "policies" / "agent_policy.yaml"