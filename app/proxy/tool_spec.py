from dataclasses import dataclass
from typing import Any, Callable

PrePDPHandler = Callable[[dict[str, Any]], dict[str, Any]]
#PostAllowHandler = Callable[[dict[str, Any]], dict[str, Any]]
PostAllowHandler = Callable[ [dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class ToolSpec:
    tool_name: str
    invocation_action: str
    resource: str
    pre_pdp: PrePDPHandler | None
    post_allow: PostAllowHandler

