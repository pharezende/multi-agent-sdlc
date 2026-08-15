from multi_agent_sdlc.agents.tester.model import TesterSummary
from multi_agent_sdlc.workflow.models import VerificationBlockDecision
from multi_agent_sdlc.workflow.models import VerificationBlockReview
from unittest.mock import MagicMock
from pathlib import Path
from multi_agent_sdlc.workflow.transitions import prepare_coder_repair_node
from multi_agent_sdlc.agents.tester import model as tester_model
from multi_agent_sdlc.agents.tester.prompt import TESTER_SYSTEM_RULES
from multi_agent_sdlc.workflow.transitions import prepare_tester_node
from multi_agent_sdlc.agents.coder.models import CoderSummary
from langchain_core.messages import SystemMessage
from multi_agent_sdlc.workflow.models import VerificationStatus
from multi_agent_sdlc.workflow.models import PlanReviewDecisionValue
from multi_agent_sdlc.workflow.transitions import prepare_coder_implementation_node
from multi_agent_sdlc.presentation.plan_formatter import format_plan
from multi_agent_sdlc.agents.coder.prompt import CODER_SYSTEM_RULES
from multi_agent_sdlc.workflow.models import DevelopmentStatus
from langchain_core.messages import HumanMessage
from langgraph.graph.state import RunnableConfig
from multi_agent_sdlc.workflow.transitions import prepare_planner_revision_node
from multi_agent_sdlc.workflow.models import PlanReviewDecision
from multi_agent_sdlc.agents.planner.models import RiskLevel, Task
from multi_agent_sdlc.agents.planner.models import DevelopmentPlan
from multi_agent_sdlc.workflow.models import PlanReviewStatus
from multi_agent_sdlc.workflow.transitions import prepare_plan_review_node
from multi_agent_sdlc.workflow.state import DevState
from multi_agent_sdlc.workflow.state import build_initial_state
import pytest
from unittest.mock import patch
import multi_agent_sdlc.workflow.transitions as transitions_module


@pytest.fixture
def development_plan() -> DevelopmentPlan:
    return DevelopmentPlan(
        project_id="test-project",
        goal="Build a small test application.",
        tasks=[
            Task(
                id="T1",
                title="Implement application",
                owner="coder",
                description="Implement the application.",
                acceptance_criteria=[
                    "The application runs successfully.",
                ],
                depends_on=[],
                target_files=[
                    "src/main.py",
                ],
                risk=RiskLevel.LOW,
            ),
            Task(
                id="T2",
                title="Verify application",
                owner="tester",
                description="Verify the implemented application.",
                acceptance_criteria=[
                    "Automated verification passes.",
                ],
                depends_on=[
                    "T1",
                ],
                target_files=[
                    "tests/test_main.py",
                ],
                risk=RiskLevel.LOW,
            ),
        ],
        execution_order=[
            "T1",
            "T2",
        ],
        assumptions=[
            "Python is available.",
        ],
        out_of_scope=[],
    )


@pytest.fixture
def dev_state() -> DevState:
    return build_initial_state("test request")


@pytest.fixture
def runnable_config() -> RunnableConfig:
    return {
        "configurable": {
            "thread_id": "test-thread",
        }
    }


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


@pytest.fixture
def tester_summary() -> tester_model.TesterSummary:
    return tester_model.TesterSummary(
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


def build_plan_review_decision(
    decision: PlanReviewDecisionValue = "approved",
    feedback: str | None = None,
) -> PlanReviewDecision:
    return PlanReviewDecision(
        decision=decision,
        feedback=feedback,
    )


def test_prepare_plan_review_node_sets_state(
    dev_state: DevState,
    development_plan: DevelopmentPlan,
) -> None:
    dev_state["plan"] = development_plan

    result = prepare_plan_review_node(dev_state)

    assert result["plan_review_status"] == PlanReviewStatus.AWAITING_REVIEW
    assert result["plan_review_decision"] is None


def test_prepare_planner_revision_sets_planner_messages(
    dev_state: DevState,
) -> None:
    dev_state["plan_review_decision"] = build_plan_review_decision(
        decision="revision_required",
        feedback="Add more verification tasks.",
    )
    result = prepare_planner_revision_node(dev_state)

    messages = result["planner_messages"]

    assert isinstance(messages, list)
    assert len(messages) == 1
    assert isinstance(messages[0], HumanMessage)
    assert "Add more verification tasks." in messages[0].content


def test_prepare_coder_implementation_sets_state(
    dev_state: DevState,
    development_plan: DevelopmentPlan,
    runnable_config: RunnableConfig,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dev_state["plan"] = development_plan
    dev_state["plan_review_content"] = format_plan(dev_state["plan"])

    tmp_path = Path("/tmp/")
    project_directory = tmp_path / development_plan.project_id
    create_project_directory_mock = MagicMock(return_value=project_directory)

    monkeypatch.setattr(
        transitions_module,
        "create_project_directory",
        create_project_directory_mock,
    )

    with patch(
        "multi_agent_sdlc.workflow.transitions.update_workflow_project_directory"
    ) as mock_update_project_directory:
        result = prepare_coder_implementation_node(dev_state, runnable_config)

    messages = result["coder_messages"]

    assert result["development_status"] == DevelopmentStatus.IMPLEMENTING
    assert result["coder_invalid_response_count"] == 0

    assert isinstance(messages, list)
    assert len(messages) == 2
    assert isinstance(messages[0], SystemMessage)
    assert messages[0].content == CODER_SYSTEM_RULES
    assert isinstance(messages[1], HumanMessage)
    assert "test request" in messages[1].content
    assert "test-project" in messages[1].content
    assert '"id": "T1"' in messages[1].content
    assert '"owner": "coder"' in messages[1].content

    mock_update_project_directory.assert_called_once_with(
        "test-thread", str(project_directory)
    )


def test_prepare_tester_retest_sets_state(
    dev_state: DevState, coder_summary: CoderSummary, tester_summary: TesterSummary
) -> None:
    dev_state["current_coder_summary"] = coder_summary
    dev_state["current_tester_summary"] = tester_summary
    dev_state["tester_messages"] = [
        SystemMessage(content=TESTER_SYSTEM_RULES),
        HumanMessage(content="Previous verification."),
    ]
    dev_state["verification_block_review"] = None

    result = prepare_tester_node(dev_state)

    messages = result["tester_messages"]

    assert result["verification_status"] == VerificationStatus.VERIFYING
    assert result["current_project_verification_result"] is None

    assert isinstance(messages, list)
    assert len(messages) == 1
    assert isinstance(messages[0], HumanMessage)


def test_prepare_tester_verification_retry_sets_state(
    dev_state: DevState,
    tester_summary: TesterSummary,
) -> None:
    dev_state["current_tester_summary"] = tester_summary
    dev_state["verification_block_review"] = VerificationBlockReview(
        decision=VerificationBlockDecision.RETRY,
        reason="Retry verification using the corrected verification context.",
    )

    result = prepare_tester_node(dev_state)

    messages = result["tester_messages"]

    assert result["verification_status"] == VerificationStatus.VERIFYING
    assert result["current_project_verification_result"] is None

    assert isinstance(messages, list)
    assert len(messages) == 1

    message = messages[0]

    assert isinstance(message, HumanMessage)
    assert isinstance(message.content, str)
    assert (
        "Retry verification using the corrected verification context."
        in message.content
    )


def test_prepare_coder_repair_node_sets_state(
    development_plan: DevelopmentPlan,
    dev_state: DevState,
    tester_summary: tester_model.TesterSummary,
):
    dev_state["plan"] = development_plan
    dev_state["current_tester_summary"] = tester_summary

    result = prepare_coder_repair_node(dev_state)
    messages = result["coder_messages"]

    assert result["development_status"] == DevelopmentStatus.REPAIRING
    assert result["current_coder_summary"] is None

    assert isinstance(messages, list)
    assert len(messages) == 1
    assert isinstance(messages[0], HumanMessage)
