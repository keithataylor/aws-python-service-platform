import pytest

from app.proxy.tool_registry import get_tool_spec


def test_tool_registry():
    tool_spec = get_tool_spec("list_documents")
    assert tool_spec is not None
    assert tool_spec.tool_name == "list_documents"
    assert tool_spec.invocation_action == "document.search"
    assert tool_spec.resource == "document"

    tool_spec = get_tool_spec("docs_tool")
    assert tool_spec is not None
    assert tool_spec.tool_name == "docs_tool"
    assert tool_spec.invocation_action == "document.read"
    assert tool_spec.resource == "document"


def test_tool_registry_invalid_tool():
    with pytest.raises(ValueError, match="Tool spec not found"):
        get_tool_spec("unknown_tool")

                                                                                                                                                     
