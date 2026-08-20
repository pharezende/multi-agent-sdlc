from typing import Any, Callable

import pytest
from langchain_core.tools import BaseTool, StructuredTool

from multi_agent_sdlc.agents.coder.models import CoderSummary
from multi_agent_sdlc.tools.coder.finalization import submit_coder_summary


@pytest.fixture
def coder_summary() -> CoderSummary:
    return CoderSummary(
        implementation_summary=(
            "Implemented the Issue Tracker project scaffolding and application."
        ),
        completed_task_ids=["T1"],
        modified_files=[
            "issues_app/__init__.py",
            "issues_app/cli.py",
            "pyproject.toml",
        ],
        runtime_dependencies=[
            "flask",
        ],
        entry_points=[
            "issue-tracker",
        ],
        executed_operations=[
            "Created and updated the planned production files.",
            "Ran uv sync successfully.",
        ],
        unresolved_issues=[],
        tester_notes=[
            "Verify application startup and the configured issue-tracker entry point.",
        ],
    )


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
