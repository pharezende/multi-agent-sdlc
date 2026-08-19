from multi_agent_sdlc.agents.tester.prompt import (
    TESTER_EMPTY_UNRESOLVED_ISSUE_VERIFICATION_CALLS_FEEDBACK,
)
from multi_agent_sdlc.agents.tester.prompt import (
    TESTER_MULTIPLE_PROJECT_VERIFICATION_CALLS_FEEDBACK,
)
from multi_agent_sdlc.agents.tester.prompt import TESTER_INVALID_RESPONSE_FEEDBACK
from multi_agent_sdlc.agents.tester.prompt import (
    TESTER_SUBMIT_SUMMARY_WITH_OTHER_TOOLS_FEEDBACK,
)
from multi_agent_sdlc.agents.tester.prompt import (
    TESTER_PASSED_SUMMARY_WITHOUT_SUCCESSFUL_VERIFICATION_FEEDBACK,
)
from multi_agent_sdlc.tools.shared.models import ProcessResult
from multi_agent_sdlc.tools.tester.model import ProjectVerificationResult
from multi_agent_sdlc.workflow.state import build_initial_state
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from multi_agent_sdlc.agents.tester import node as tester_module
from multi_agent_sdlc.agents.tester.model import (
    TesterSummary as _TesterSummary,
    UnresolvedIssue,
)
from multi_agent_sdlc.workflow.state import DevState, VerificationStatus


@pytest.fixture
def initial_dev_state() -> DevState:
    return build_initial_state("test request")


@pytest.fixture
def tester_summary_blocked() -> _TesterSummary:
    return _TesterSummary(
        addressed_task_ids=["T2"],
        passed_task_ids=[],
        related_task_ids=["T1"],
        files_created_or_modified=[],
        development_dependencies_added=[],
        verification_results=[],
        acceptance_criteria_results=[],
        tester_repairs=[],
        implementation_failures=[],
        unresolved_issues=[
            UnresolvedIssue(
                owner="environment",
                description="PostgreSQL is not available at the configured local address,"
                "preventing database-backed tests from running.",
                related_task_ids=["T7", "T8"],
                evidence=(
                    "uv run pytest -q failed because connections to 127.0.0.1:5432 "
                    "were refused."
                ),
            )
        ],
        overall_status="blocked",
        coder_repair_requests=[],
    )


@pytest.fixture
def tester_summary_blocked_with_empty_unresolved_issues() -> _TesterSummary:
    return _TesterSummary(
        addressed_task_ids=["T2"],
        passed_task_ids=[],
        related_task_ids=["T1"],
        files_created_or_modified=[],
        development_dependencies_added=[],
        verification_results=[],
        acceptance_criteria_results=[],
        tester_repairs=[],
        implementation_failures=[],
        unresolved_issues=[],
        overall_status="blocked",
        coder_repair_requests=[],
    )


@pytest.fixture
def tester_summary_passed() -> _TesterSummary:
    return _TesterSummary(
        addressed_task_ids=["T2"],
        passed_task_ids=["T2"],
        related_task_ids=["T1"],
        files_created_or_modified=["tests/test_main.py"],
        development_dependencies_added=[],
        verification_results=[
            # ...
        ],
        acceptance_criteria_results=[
            # ...
        ],
        tester_repairs=[],
        implementation_failures=[],
        unresolved_issues=[],
        overall_status="passed",
        coder_repair_requests=[],
    )


@pytest.fixture
def tester_summary_repair_required() -> _TesterSummary:
    return _TesterSummary(
        addressed_task_ids=["T2"],
        passed_task_ids=[],
        related_task_ids=["T1"],
        files_created_or_modified=["tests/test_main.py"],
        development_dependencies_added=[],
        verification_results=[
            # ...
        ],
        acceptance_criteria_results=[
            # ...
        ],
        tester_repairs=[],
        implementation_failures=[
            # ...
        ],
        unresolved_issues=[],
        overall_status="repair-required",
        coder_repair_requests=[
            # ...
        ],
    )


@pytest.fixture
def project_verification_result_passed() -> ProjectVerificationResult:
    return ProjectVerificationResult(
        verification_type="complete_project_verification",
        passed=True,
        overall_exit_code=0,
        checks=[
            ProcessResult(
                command=["uv", "run", "ruff", "check", "."],
                exit_code=0,
                stdout="All checks passed!",
                stderr="",
                timed_out=False,
            ),
            ProcessResult(
                command=["uv", "run", "mypy", "."],
                exit_code=0,
                stdout="Success: no issues found",
                stderr="",
                timed_out=False,
            ),
            ProcessResult(
                command=["uv", "run", "pytest"],
                exit_code=0,
                stdout="3 passed",
                stderr="",
                timed_out=False,
            ),
        ],
    )


@pytest.fixture
def project_verification_result_non_passed() -> ProjectVerificationResult:
    return ProjectVerificationResult(
        verification_type="complete_project_verification",
        passed=False,
        overall_exit_code=0,
        checks=[],
    )


def test_tester_node_accepts_tool_call(
    initial_dev_state: DevState,
) -> None:
    response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "tester_run_project_verification",
                "args": {},
                "id": "call-1",
                "type": "tool_call",
            },
        ],
    )

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = response

    initial_dev_state["tester_messages"] = [
        HumanMessage(content="Verify the implementation."),
    ]
    initial_dev_state["verification_status"] = VerificationStatus.VERIFYING

    result = tester_module.tester_node(initial_dev_state, mock_llm)

    assert result["tester_messages"] == [response]

    mock_llm.invoke.assert_called_once()


def test_tester_node_processes_empty_unresolved_issues_non_passed_summary(
    tester_summary_blocked_empty_unresolved_issues: _TesterSummary,
    initial_dev_state: DevState,
) -> None:

    llm_response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "submit_tester_summary",
                "args": {
                    "summary": tester_summary_blocked_empty_unresolved_issues.model_dump(),
                },
                "id": "call-1",
                "type": "tool_call",
            },
        ],
    )

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = llm_response

    initial_dev_state["tester_messages"] = [
        HumanMessage(content="Verify the implementation."),
    ]
    initial_dev_state["verification_status"] = VerificationStatus.VERIFYING

    result = tester_module.tester_node(initial_dev_state, mock_llm)

    assert result["tester_messages"] == [
        llm_response,
        HumanMessage(content=TESTER_EMPTY_UNRESOLVED_ISSUE_VERIFICATION_CALLS_FEEDBACK),
    ]


@pytest.mark.parametrize(
    ("summary_fixture", "expected_status"),
    [
        ("tester_summary_blocked", VerificationStatus.BLOCKED),
        (
            "tester_summary_repair_required",
            VerificationStatus.REPAIR_REQUIRED,
        ),
    ],
)
def test_tester_node_processes_non_passed_summary(
    summary_fixture: str,
    expected_status: VerificationStatus,
    request: pytest.FixtureRequest,
    initial_dev_state: DevState,
) -> None:
    tester_summary = request.getfixturevalue(summary_fixture)
    assert isinstance(tester_summary, _TesterSummary)

    response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "submit_tester_summary",
                "args": {
                    "summary": tester_summary.model_dump(),
                },
                "id": "call-1",
                "type": "tool_call",
            },
        ],
    )

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = response

    initial_dev_state["tester_messages"] = [
        HumanMessage(content="Verify the implementation."),
    ]
    initial_dev_state["verification_status"] = VerificationStatus.VERIFYING

    result = tester_module.tester_node(initial_dev_state, mock_llm)

    assert result["verification_status"] == expected_status
    assert result["current_tester_summary"] == tester_summary
    assert result["tester_messages"] == [response]


def test_tester_node_processes_passed_summary(
    initial_dev_state: DevState,
    tester_summary_passed: _TesterSummary,
    project_verification_result_passed: ProjectVerificationResult,
) -> None:
    response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "submit_tester_summary",
                "args": {
                    "summary": tester_summary_passed.model_dump(),
                },
                "id": "call-1",
                "type": "tool_call",
            },
        ],
    )

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = response

    initial_dev_state["tester_messages"] = [
        HumanMessage(content="Verify the implementation."),
    ]
    initial_dev_state["current_project_verification_result"] = (
        project_verification_result_passed
    )

    result = tester_module.tester_node(initial_dev_state, mock_llm)

    assert result["verification_status"] == VerificationStatus.PASSED
    assert result["current_tester_summary"] == tester_summary_passed
    assert result["tester_messages"] == [response]


def test_tester_node_processes_passed_summary_non_passed_project_verification(
    initial_dev_state: DevState,
    tester_summary_passed: _TesterSummary,
    project_verification_result_non_passed: ProjectVerificationResult,
) -> None:
    response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "submit_tester_summary",
                "args": {
                    "summary": tester_summary_passed.model_dump(),
                },
                "id": "call-1",
                "type": "tool_call",
            },
        ],
    )

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = response

    initial_dev_state["tester_messages"] = [
        HumanMessage(content="Verify the implementation."),
    ]
    initial_dev_state["current_project_verification_result"] = (
        project_verification_result_non_passed
    )

    result = tester_module.tester_node(initial_dev_state, mock_llm)
    messages = result["tester_messages"]
    assert isinstance(messages, list)
    assert not hasattr(result, "verification_status")
    assert not hasattr(result, "current_tester_summary")
    assert (
        messages[1].content
        == TESTER_PASSED_SUMMARY_WITHOUT_SUCCESSFUL_VERIFICATION_FEEDBACK
    )


def test_tester_node_accepts_multiple_operational_tool_calls(
    initial_dev_state: DevState,
) -> None:
    response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "tester_write_file",
                "args": {
                    "path": "tests/test_main.py",
                    "content": "def test_main(): pass",
                },
                "id": "call-1",
                "type": "tool_call",
            },
            {
                "name": "tester_run_project_verification",
                "args": {},
                "id": "call-2",
                "type": "tool_call",
            },
        ],
    )

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = response

    initial_dev_state["tester_messages"] = [
        HumanMessage(content="Verify the implementation."),
    ]
    initial_dev_state["verification_status"] = VerificationStatus.VERIFYING

    result = tester_module.tester_node(initial_dev_state, mock_llm)

    assert result["tester_messages"] == [response]


def test_tester_node_rejects_multiple_tool_calls_with_summary(
    initial_dev_state: DevState,
    tester_summary_blocked: _TesterSummary,
) -> None:
    response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "submit_tester_summary",
                "args": {
                    "summary": tester_summary_blocked.model_dump(),
                },
                "id": "call-1",
                "type": "tool_call",
            },
            {
                "name": "tester_run_project_verification",
                "args": {},
                "id": "call-2",
                "type": "tool_call",
            },
        ],
    )

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = response

    initial_dev_state["tester_messages"] = [
        HumanMessage(content="Verify the implementation."),
    ]
    initial_dev_state["verification_status"] = VerificationStatus.VERIFYING

    result = tester_module.tester_node(initial_dev_state, mock_llm)

    messages = result["tester_messages"]

    assert isinstance(messages, list)
    assert messages[0] == response
    assert messages[1].content == TESTER_SUBMIT_SUMMARY_WITH_OTHER_TOOLS_FEEDBACK

    assert result.get("current_tester_summary") is None


def test_tester_node_handles_response_without_tool_calls(
    initial_dev_state: DevState,
) -> None:
    response = AIMessage(
        content="The verification is complete.",
    )

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = response

    initial_dev_state["tester_messages"] = [
        HumanMessage(content="Verify the implementation."),
    ]

    result = tester_module.tester_node(initial_dev_state, mock_llm)

    messages = result["tester_messages"]

    assert isinstance(messages, list)
    assert messages[0] == response
    assert messages[1].content == TESTER_INVALID_RESPONSE_FEEDBACK


def test_tester_node_rejects_multiple_project_verification_calls(
    initial_dev_state: DevState,
) -> None:
    response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "tester_run_project_verification",
                "args": {},
                "id": "call-1",
                "type": "tool_call",
            },
            {
                "name": "tester_run_project_verification",
                "args": {},
                "id": "call-2",
                "type": "tool_call",
            },
        ],
    )

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = response

    initial_dev_state["tester_messages"] = [
        HumanMessage(content="Verify the implementation."),
    ]

    result = tester_module.tester_node(initial_dev_state, mock_llm)

    assert result["tester_messages"] == [
        response,
        HumanMessage(content=TESTER_MULTIPLE_PROJECT_VERIFICATION_CALLS_FEEDBACK),
    ]
