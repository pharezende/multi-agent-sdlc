from unittest.mock import MagicMock

from langchain_core.messages import AIMessage, HumanMessage

from multi_agent_sdlc.agents.coder import node as coder_module
from multi_agent_sdlc.agents.coder.models import CoderSummary
from multi_agent_sdlc.agents.coder.node import (
    MAX_CONSECUTIVE_CODER_INVALID_RESPONSES,
)
from multi_agent_sdlc.agents.coder.prompt import (
    CODER_INVALID_RESPONSE_FEEDBACK,
    CODER_SUBMIT_SUMMARY_WITH_OTHER_TOOLS_FEEDBACK,
)
from multi_agent_sdlc.workflow.models import DevelopmentStatus
from multi_agent_sdlc.workflow.state import DevState


def test_coder_node_increments_invalid_response_count(
    dev_state: DevState,
) -> None:
    response = AIMessage(content="I have completed the implementation.")

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = response

    dev_state["coder_messages"] = [
        HumanMessage(content="Implement the application.")
    ]

    result = coder_module.coder_node(dev_state, mock_llm)

    assert result["coder_invalid_response_count"] == 1
    messages = result["coder_messages"]
    assert isinstance(messages, list)
    assert messages[1].content == CODER_INVALID_RESPONSE_FEEDBACK
    mock_llm.invoke.assert_called_once()


def test_coder_node_fails_after_max_invalid_responses(
    dev_state: DevState,
) -> None:
    response = AIMessage(
        content="The implementation is complete.",
    )

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = response

    dev_state["coder_messages"] = [
        HumanMessage(content="Implement the application."),
    ]
    dev_state["development_status"] = DevelopmentStatus.IMPLEMENTING
    dev_state["coder_invalid_response_count"] = (
        MAX_CONSECUTIVE_CODER_INVALID_RESPONSES - 1
    )

    result = coder_module.coder_node(dev_state, mock_llm)

    assert (
        result["coder_invalid_response_count"]
        == MAX_CONSECUTIVE_CODER_INVALID_RESPONSES
    )
    assert result["development_status"] == DevelopmentStatus.FAILED

    mock_llm.invoke.assert_called_once()


def test_coder_node_accepts_summary_called_alone(
    dev_state: DevState,
    coder_summary: CoderSummary,
) -> None:
    response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "submit_coder_summary",
                "args": {
                    "summary": coder_summary.model_dump(),
                },
                "id": "call-1",
                "type": "tool_call",
            }
        ],
    )

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = response

    dev_state["coder_messages"] = [
        HumanMessage(content="Implement the application."),
    ]
    dev_state["development_status"] = DevelopmentStatus.IMPLEMENTING
    dev_state["coder_invalid_response_count"] = 1

    result = coder_module.coder_node(dev_state, mock_llm)

    assert result["development_status"] == DevelopmentStatus.COMPLETED
    assert result["current_coder_summary"] == coder_summary
    assert result["coder_invalid_response_count"] == 0
    assert result["coder_messages"] == [response]

    mock_llm.invoke.assert_called_once()


def test_coder_node_accepts_multiple_operational_tool_calls(
    dev_state: DevState,
) -> None:
    response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "coder_write_file",
                "args": {
                    "path": "src/main.py",
                    "content": "print('hello')",
                },
                "id": "call-1",
                "type": "tool_call",
            },
            {
                "name": "coder_write_file",
                "args": {
                    "path": "src/config.py",
                    "content": "DEBUG = False",
                },
                "id": "call-2",
                "type": "tool_call",
            },
        ],
    )

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = response

    dev_state["coder_messages"] = [
        HumanMessage(content="Implement the application."),
    ]
    dev_state["coder_invalid_response_count"] = 1

    result = coder_module.coder_node(dev_state, mock_llm)

    assert result["coder_messages"] == [response]
    assert result["coder_invalid_response_count"] == 0


def test_coder_node_rejects_summary_with_other_tool_call(
    dev_state: DevState,
    coder_summary: CoderSummary,
) -> None:
    response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "submit_coder_summary",
                "args": {
                    "summary": coder_summary.model_dump(),
                },
                "id": "call-1",
                "type": "tool_call",
            },
            {
                "name": "coder_write_file",
                "args": {
                    "path": "src/main.py",
                    "content": "print('hello')",
                },
                "id": "call-2",
                "type": "tool_call",
            },
        ],
    )

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = response

    dev_state["coder_messages"] = [
        HumanMessage(content="Implement the application."),
    ]

    result = coder_module.coder_node(dev_state, mock_llm)

    assert result["coder_invalid_response_count"] == 1

    messages = result["coder_messages"]
    assert isinstance(messages, list)
    assert messages[0] == response
    assert messages[1].content == CODER_SUBMIT_SUMMARY_WITH_OTHER_TOOLS_FEEDBACK
