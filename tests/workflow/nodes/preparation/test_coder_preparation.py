from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph.state import RunnableConfig

import multi_agent_sdlc.workflow.nodes.preparation.coder as coder_preparation_module
from multi_agent_sdlc.agents.coder.prompt import CODER_SYSTEM_RULES
from multi_agent_sdlc.agents.planner.models import DevelopmentPlan
from multi_agent_sdlc.agents.tester.model import TesterSummary as _TesterSummary
from multi_agent_sdlc.presentation.plan_text import format_plan
from multi_agent_sdlc.workflow.models import DevelopmentStatus
from multi_agent_sdlc.workflow.nodes.preparation import (
    prepare_coder_implementation_node,
    prepare_coder_repair_node,
)
from multi_agent_sdlc.workflow.state import DevState


@pytest.fixture
def runnable_config() -> RunnableConfig:
    return {
        "configurable": {
            "thread_id": "test-thread",
        }
    }


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
        coder_preparation_module,
        "create_project_directory",
        create_project_directory_mock,
    )

    with patch(
        "multi_agent_sdlc.workflow.nodes.preparation.coder."
        "update_workflow_project_directory"
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


def test_prepare_coder_repair_node_sets_state(
    development_plan: DevelopmentPlan,
    dev_state: DevState,
    tester_summary: _TesterSummary,
) -> None:
    dev_state["plan"] = development_plan
    dev_state["current_tester_summary"] = tester_summary

    result = prepare_coder_repair_node(dev_state)
    messages = result["coder_messages"]

    assert result["development_status"] == DevelopmentStatus.REPAIRING
    assert result["current_coder_summary"] is None

    assert isinstance(messages, list)
    assert len(messages) == 1
    assert isinstance(messages[0], HumanMessage)
