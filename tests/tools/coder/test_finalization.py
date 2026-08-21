from typing import Any, Callable

from langchain_core.tools import BaseTool, StructuredTool

from multi_agent_sdlc.agents.coder.models import CoderSummary
from multi_agent_sdlc.tools.coder.finalization import submit_coder_summary


def get_tool_function(
    tool: BaseTool,
) -> Callable[..., Any]:
    if not isinstance(tool, StructuredTool):
        raise TypeError(f"Expected StructuredTool, got {type(tool).__name__}")

    if tool.func is None:
        raise TypeError(f"Tool {tool.name} does not have a synchronous function")

    return tool.func


def test_submit_coder_summary_accepts_summary(
    coder_summary: CoderSummary,
) -> None:
    function = get_tool_function(submit_coder_summary)

    result = function(
        summary=coder_summary,
    )

    assert result == "Coder summary accepted."


def test_submit_coder_summary_has_expected_tool_name() -> None:
    assert submit_coder_summary.name == "submit_coder_summary"


def test_submit_coder_summary_has_description() -> None:
    assert submit_coder_summary.description


def test_submit_coder_summary_exposes_summary_argument() -> None:
    assert "summary" in submit_coder_summary.args
