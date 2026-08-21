import pytest
from langchain_core.messages import HumanMessage, SystemMessage

from multi_agent_sdlc.agents.coder.models import CoderSummary
from multi_agent_sdlc.agents.planner.models import DevelopmentPlan
from multi_agent_sdlc.agents.reviewer.models import ReviewerSummary
from multi_agent_sdlc.agents.reviewer.prompt import REVIEWER_SYSTEM_RULES
from multi_agent_sdlc.agents.tester.model import TesterSummary as _TesterSummary
from multi_agent_sdlc.agents.tester.model import VerificationType
from multi_agent_sdlc.tools.shared.models import ProcessResult
from multi_agent_sdlc.tools.tester.model import ProjectVerificationResult
from multi_agent_sdlc.workflow.models import (
    ReviewCycle,
    ReviewStatus,
    VerificationBlockDecision,
    VerificationBlockReview,
)
from multi_agent_sdlc.workflow.nodes.preparation.reviewer import prepare_reviewer_node
from multi_agent_sdlc.workflow.state import DevState


@pytest.fixture
def project_verification_result_passed() -> ProjectVerificationResult:
    return ProjectVerificationResult(
        verification_type=VerificationType.COMPLETE_PROJECT_VERIFICATION,
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
def project_verification_result_blocked() -> ProjectVerificationResult:
    return {
        "verification_type": VerificationType.COMPLETE_PROJECT_VERIFICATION,
        "passed": False,
        "overall_exit_code": 1,
        "checks": [
            {
                "command": ["uv", "run", "ruff", "check", "."],
                "exit_code": 0,
                "stdout": "All checks passed!",
                "stderr": "",
                "timed_out": False,
            },
            {
                "command": ["uv", "run", "ruff", "format", "--check", "."],
                "exit_code": 0,
                "stdout": "Files already formatted.",
                "stderr": "",
                "timed_out": False,
            },
            {
                "command": ["uv", "run", "mypy", "src"],
                "exit_code": None,
                "stdout": "",
                "stderr": "",
                "timed_out": True,
            },
            {
                "command": ["uv", "run", "pytest"],
                "exit_code": 0,
                "stdout": "10 passed",
                "stderr": "",
                "timed_out": False,
            },
        ],
    }


@pytest.fixture
def review_cycle() -> ReviewCycle:
    return ReviewCycle(
        cycle_number=1,
        reviewer_summary=ReviewerSummary(
            overall_status="passed",
            summary="The implementation is acceptable and no material issues remain.",
            findings=[],
        ),
    )


def test_prepare_reviewer_initial_review_sets_state(
    development_plan: DevelopmentPlan,
    coder_summary: CoderSummary,
    tester_summary: _TesterSummary,
    project_verification_result_passed: ProjectVerificationResult,
    dev_state: DevState,
) -> None:
    dev_state["plan"] = development_plan
    dev_state["current_coder_summary"] = coder_summary
    dev_state["current_tester_summary"] = tester_summary
    dev_state["current_project_verification_result"] = (
        project_verification_result_passed
    )

    result = prepare_reviewer_node(dev_state)

    messages = result["reviewer_messages"]

    assert result["current_reviewer_summary"] is None

    assert isinstance(messages, list)
    assert len(messages) == 2

    system_message, human_message = messages

    assert isinstance(system_message, SystemMessage)
    assert system_message.content == REVIEWER_SYSTEM_RULES

    assert isinstance(human_message, HumanMessage)
    assert isinstance(human_message.content, str)


def test_prepare_reviewer_rereview_sets_state(
    development_plan: DevelopmentPlan,
    coder_summary: CoderSummary,
    tester_summary: _TesterSummary,
    project_verification_result_passed: ProjectVerificationResult,
    dev_state: DevState,
    review_cycle: ReviewCycle,
) -> None:
    dev_state["plan"] = development_plan
    dev_state["current_coder_summary"] = coder_summary
    dev_state["current_tester_summary"] = tester_summary
    dev_state["current_project_verification_result"] = (
        project_verification_result_passed
    )
    dev_state["reviewer_summary_history"] = [review_cycle]
    dev_state["verification_block_review"] = None

    result = prepare_reviewer_node(dev_state)

    messages = result["reviewer_messages"]

    assert result["current_reviewer_summary"] is None

    assert isinstance(messages, list)
    assert len(messages) == 1
    assert isinstance(messages[0], HumanMessage)
    assert isinstance(messages[0].content, str)


def test_prepare_reviewer_initial_override_sets_state(
    development_plan: DevelopmentPlan,
    coder_summary: CoderSummary,
    tester_summary: _TesterSummary,
    project_verification_result_blocked: ProjectVerificationResult,
    dev_state: DevState,
) -> None:
    dev_state["plan"] = development_plan
    dev_state["current_coder_summary"] = coder_summary
    dev_state["current_tester_summary"] = tester_summary
    dev_state["current_project_verification_result"] = (
        project_verification_result_blocked
    )
    dev_state["reviewer_messages"] = []
    dev_state["reviewer_summary_history"] = []
    dev_state["verification_block_review"] = VerificationBlockReview(
        decision=VerificationBlockDecision.PROCEED_WITH_OVERRIDE,
        reason="The verification blocker is environmental and is accepted.",
    )

    result = prepare_reviewer_node(dev_state)

    messages = result["reviewer_messages"]

    assert result["review_status"] == ReviewStatus.REVIEWING
    assert result["current_reviewer_summary"] is None

    assert isinstance(messages, list)
    assert len(messages) == 2

    system_message, human_message = messages

    assert isinstance(system_message, SystemMessage)
    assert system_message.content == REVIEWER_SYSTEM_RULES

    assert isinstance(human_message, HumanMessage)
    assert isinstance(human_message.content, str)
    assert "environmental and is accepted" in human_message.content
    assert "override" in human_message.content.lower()
    assert "blocked" in human_message.content.lower()


def test_prepare_reviewer_rereview_override_sets_state(
    development_plan: DevelopmentPlan,
    coder_summary: CoderSummary,
    tester_summary: _TesterSummary,
    project_verification_result_blocked: ProjectVerificationResult,
    dev_state: DevState,
    review_cycle: ReviewCycle,
) -> None:
    dev_state["plan"] = development_plan
    dev_state["current_coder_summary"] = coder_summary
    dev_state["current_tester_summary"] = tester_summary
    dev_state["current_project_verification_result"] = (
        project_verification_result_blocked
    )
    dev_state["reviewer_messages"] = [
        SystemMessage(content=REVIEWER_SYSTEM_RULES),
        HumanMessage(content="Previous review context."),
    ]
    dev_state["reviewer_summary_history"] = [review_cycle]
    dev_state["verification_block_review"] = VerificationBlockReview(
        decision=VerificationBlockDecision.PROCEED_WITH_OVERRIDE,
        reason="Proceed despite the unresolved verification blocker.",
    )

    result = prepare_reviewer_node(dev_state)

    messages = result["reviewer_messages"]

    assert result["review_status"] == ReviewStatus.REVIEWING
    assert result["current_reviewer_summary"] is None

    assert isinstance(messages, list)
    assert len(messages) == 3

    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)

    override_message = messages[2]

    assert isinstance(override_message, HumanMessage)
    assert isinstance(override_message.content, str)
    assert "Proceed despite the unresolved verification blocker." in (
        override_message.content
    )
    assert "override" in override_message.content.lower()
    assert "blocked" in override_message.content.lower()
    assert review_cycle.reviewer_summary.summary in override_message.content
