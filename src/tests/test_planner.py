from langchain_core.messages import BaseMessage
from multi_agent_sdlc.workflow.models import PlanReviewStatus
from multi_agent_sdlc.agents.planner.prompt import PLANNER_SYSTEM_RULES
from multi_agent_sdlc.agents.coder.prompt import CODER_SYSTEM_RULES
from langchain_core.messages import AIMessage, SystemMessage
from multi_agent_sdlc.agents.planner.models import Task
from multi_agent_sdlc.agents.planner.models import RiskLevel
from multi_agent_sdlc.workflow.state import build_initial_state
from langchain_core.messages import HumanMessage
from multi_agent_sdlc.agents.planner.models import DevelopmentPlan
from unittest.mock import MagicMock

import pytest

from multi_agent_sdlc.agents.planner import node as planner_module
from multi_agent_sdlc.workflow.state import DevState


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


def test_planner_node_processes_development_plan(
    initial_dev_state: DevState,
    development_plan: DevelopmentPlan,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = development_plan

    # Set whatever initial planner message your node requires.
    initial_dev_state["planner_messages"] = [
        HumanMessage(content="Build a test application."),
    ]

    result = planner_module.planner_node(initial_dev_state, mock_llm)
    messages = result["planner_messages"]
    assert isinstance(messages, list)
    assert len(messages) == 3
    assert isinstance(messages[0], SystemMessage)
    assert messages[0].content == PLANNER_SYSTEM_RULES
    assert isinstance(messages[1], HumanMessage)
    assert isinstance(messages[2], AIMessage)
    assert "test-project" in messages[2].content
    assert '"id": "T1"' in messages[2].content
    assert '"owner": "coder"' in messages[2].content
    assert result["plan"] == development_plan
    mock_llm.invoke.assert_called_once()


def test_planner_node_processes_plan_revision(
    initial_dev_state: DevState,
    development_plan: DevelopmentPlan,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    revised_plan = development_plan.model_copy(
        update={
            "goal": "Build the revised test application.",
        }
    )

    planner_messages: list[BaseMessage] = [
        HumanMessage(content="Build a test application."),
        HumanMessage(content="Revise the plan to include additional verification."),
    ]

    initial_dev_state["plan"] = development_plan
    initial_dev_state["planner_messages"] = planner_messages
    initial_dev_state["plan_review_status"] = PlanReviewStatus.REVISION_REQUIRED

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = revised_plan

    result = planner_module.planner_node(initial_dev_state, mock_llm)
    messages = result["planner_messages"]
    assert isinstance(messages, list)
    assert len(messages) == 1  # Direct node calls return only the
    # fields explicitly updated by the node, not the existing DevState values.
    assert '"goal": "Build the revised test application."' in messages[0].content
    assert "test-project" in messages[0].content
    assert '"id": "T1"' in messages[0].content
    assert '"owner": "coder"' in messages[0].content
    assert result["plan"] == revised_plan

    mock_llm.invoke.assert_called_once_with(planner_messages)
