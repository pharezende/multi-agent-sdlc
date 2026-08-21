from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from multi_agent_sdlc.agents.planner import node as planner_module
from multi_agent_sdlc.agents.planner.models import DevelopmentPlan
from multi_agent_sdlc.agents.planner.prompt import PLANNER_SYSTEM_RULES
from multi_agent_sdlc.workflow.models import PlanReviewStatus
from multi_agent_sdlc.workflow.state import DevState


def test_planner_node_processes_development_plan(
    dev_state: DevState,
    development_plan: DevelopmentPlan,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = development_plan

    # Set whatever initial planner message your node requires.
    dev_state["planner_messages"] = [
        HumanMessage(content="Build a test application."),
    ]

    result = planner_module.planner_node(dev_state, mock_llm)
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
    dev_state: DevState,
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

    dev_state["plan"] = development_plan
    dev_state["planner_messages"] = planner_messages
    dev_state["plan_review_status"] = PlanReviewStatus.REVISION_REQUIRED

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = revised_plan

    result = planner_module.planner_node(dev_state, mock_llm)
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
