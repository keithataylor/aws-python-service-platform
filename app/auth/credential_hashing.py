import hashlib
import hmac


def hash_agent_api_key(api_key: str, secret: str) -> str:
    return hmac.new(
        key=secret.encode("utf-8"),
        msg=api_key.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


