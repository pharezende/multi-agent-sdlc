from unittest.mock import MagicMock

import pytest
from langchain_core.runnables import RunnableConfig

import multi_agent_sdlc.human_in_the_loop.plan_review as plan_review_module
from multi_agent_sdlc.agents.planner.models import DevelopmentPlan, RiskLevel, Task
from multi_agent_sdlc.workflow.models import PlanReviewDecision, PlanReviewStatus
from multi_agent_sdlc.workflow.run_repository import WorkflowRunStatus
from multi_agent_sdlc.workflow.state import DevState, build_initial_state


@pytest.fixture
def initial_dev_state() -> DevState:
    return build_initial_state("test request")


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
def workflow_config() -> RunnableConfig:
    return {
        "configurable": {
            "thread_id": "test-thread-id",
        }
    }


@pytest.fixture
def auto_approve_workflow_config() -> RunnableConfig:
    return {
        "configurable": {
            "thread_id": "test-thread-id",
            "plan_review_decision": PlanReviewDecision(decision="approved"),
        }
    }


@pytest.mark.parametrize(
    ("review_decision", "expected_status"),
    [
        (
            PlanReviewDecision(
                decision="approved",
                feedback=None,
            ),
            PlanReviewStatus.APPROVED,
        ),
        (
            PlanReviewDecision(
                decision="revision_required",
                feedback="Add more tests",
            ),
            PlanReviewStatus.REVISION_REQUIRED,
        ),
        (
            PlanReviewDecision(
                decision="rejected",
                feedback="Reject the plan.",
            ),
            PlanReviewStatus.REJECTED,
        ),
    ],
)
def test_human_plan_review_node_processes_review_decision(
    review_decision: PlanReviewDecision,
    expected_status: PlanReviewStatus,
    initial_dev_state: DevState,
    workflow_config: RunnableConfig,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    interrupt_mock = MagicMock(
        return_value=review_decision.model_dump(),
    )
    update_status_mock = MagicMock()

    monkeypatch.setattr(
        plan_review_module,
        "interrupt",
        interrupt_mock,
    )
    monkeypatch.setattr(
        plan_review_module,
        "update_workflow_run_status",
        update_status_mock,
    )

    result = plan_review_module.human_plan_review_node(
        initial_dev_state,
        workflow_config,
    )

    assert result["plan_review_status"] == expected_status
    assert result["plan_review_decision"] == review_decision

    update_status_mock.assert_called_once_with(
        "test-thread-id",
        WorkflowRunStatus.RUNNING,
    )


def test_human_plan_review_node_automatted_approval_plan(
    initial_dev_state: DevState,
    auto_approve_workflow_config: RunnableConfig,
    development_plan: DevelopmentPlan,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    initial_dev_state["plan"] = development_plan

    interrupt_mock = MagicMock(
        return_value={
            "decision": "approved",
            "feedback": None,
        }
    )

    monkeypatch.setattr(
        plan_review_module,
        "interrupt",
        interrupt_mock,
    )

    update_status_mock = MagicMock()

    monkeypatch.setattr(
        plan_review_module,
        "update_workflow_run_status",
        update_status_mock,
    )

    result = plan_review_module.human_plan_review_node(
        initial_dev_state, auto_approve_workflow_config
    )

    interrupt_mock.assert_not_called()
    update_status_mock.assert_not_called()

    assert result["plan_review_status"] == PlanReviewStatus.APPROVED
