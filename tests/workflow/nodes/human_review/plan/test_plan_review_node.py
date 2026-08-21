from unittest.mock import MagicMock

import pytest
from langchain_core.runnables import RunnableConfig

import multi_agent_sdlc.workflow.nodes.human_review.plan.node as plan_review_module
from multi_agent_sdlc.agents.planner.models import DevelopmentPlan
from multi_agent_sdlc.workflow.models import PlanReviewDecision, PlanReviewStatus
from multi_agent_sdlc.workflow.run_repository import WorkflowRunStatus
from multi_agent_sdlc.workflow.state import DevState


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
    dev_state: DevState,
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
        dev_state,
        workflow_config,
    )

    assert result["plan_review_status"] == expected_status
    assert result["plan_review_decision"] == review_decision

    update_status_mock.assert_called_once_with(
        "test-thread-id",
        WorkflowRunStatus.RUNNING,
    )


def test_human_plan_review_node_automatted_approval_plan(
    dev_state: DevState,
    auto_approve_workflow_config: RunnableConfig,
    development_plan: DevelopmentPlan,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dev_state["plan"] = development_plan

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
        dev_state, auto_approve_workflow_config
    )

    interrupt_mock.assert_not_called()
    update_status_mock.assert_not_called()

    assert result["plan_review_status"] == PlanReviewStatus.APPROVED
