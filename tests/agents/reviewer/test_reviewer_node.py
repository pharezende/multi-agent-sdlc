from unittest.mock import Mock, patch

import pytest
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from multi_agent_sdlc.agents.reviewer.models import ReviewerSummary, ReviewFinding
from multi_agent_sdlc.agents.reviewer.node import reviewer_node
from multi_agent_sdlc.agents.reviewer.prompt import (
    REVIEWER_INVALID_RESPONSE_MESSAGE,
    REVIEWER_SUMMARY_MUST_BE_ALONE_MESSAGE,
)
from multi_agent_sdlc.workflow.models import ReviewCycle, ReviewStatus
from multi_agent_sdlc.workflow.state import DevState


@pytest.fixture
def reviewer_messages() -> list[BaseMessage]:
    return [
        SystemMessage(content="You are the code reviewer."),
        HumanMessage(
            content=(
                "Review the current implementation against the approved plan "
                "and verification context."
            )
        ),
    ]


@pytest.fixture
def reviewer_passed_summary() -> ReviewerSummary:
    return ReviewerSummary(
        overall_status="passed",
        summary="The implementation is acceptable and no material issues remain.",
        findings=[],
    )


@pytest.fixture
def reviewer_repair_summary() -> ReviewerSummary:
    return ReviewerSummary(
        overall_status="repair-required",
        summary="The implementation contains a material maintainability issue.",
        findings=[
            ReviewFinding(
                file="app/storage.py",
                description="Validation and persistence logic are tightly coupled.",
                rationale=(
                    "This reduces separation of concerns and makes the code "
                    "harder to maintain and test."
                ),
                required_change=(
                    "Separate validation logic from persistence responsibilities."
                ),
            )
        ],
    )


@pytest.fixture
def reviewer_blocked_summary() -> ReviewerSummary:
    return ReviewerSummary(
        overall_status="blocked",
        summary=(
            "The review could not be completed because required repository "
            "evidence was unavailable."
        ),
        findings=[],
    )


def test_reviewer_node_raises_when_messages_not_initialized(
    dev_state: DevState,
) -> None:
    dev_state["reviewer_messages"] = []

    response = AIMessage(
        content="",
    )

    reviewer_llm = Mock()
    reviewer_llm.invoke.return_value = response

    with pytest.raises(
        ValueError,
        match="Reviewer conversation was not initialized",
    ):
        reviewer_node(dev_state, reviewer_llm)


def test_reviewer_node_returns_operational_tool_call(
    dev_state: DevState,
    reviewer_messages: list[BaseMessage],
) -> None:
    dev_state["reviewer_messages"] = reviewer_messages

    response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "read_file",
                "args": {"path": "app/storage.py"},
                "id": "tool-call-1",
                "type": "tool_call",
            }
        ],
    )

    reviewer_llm = Mock()
    reviewer_llm.invoke.return_value = response

    result = reviewer_node(dev_state, reviewer_llm)

    assert result == {
        "reviewer_messages": [response],
    }

    reviewer_llm.invoke.assert_called_once_with(reviewer_messages)


def test_reviewer_node_rejects_response_without_tool_call(
    dev_state: DevState,
    reviewer_messages: list[BaseMessage],
) -> None:
    dev_state["reviewer_messages"] = reviewer_messages

    response = AIMessage(content="The implementation looks good.")

    reviewer_llm = Mock()
    reviewer_llm.invoke.return_value = response

    result = reviewer_node(dev_state, reviewer_llm)

    messages = result["reviewer_messages"]
    assert isinstance(messages, list)

    assert messages[0] == response
    assert isinstance(messages[1], HumanMessage)
    assert messages[1].content == REVIEWER_INVALID_RESPONSE_MESSAGE


def test_reviewer_node_rejects_multiple_summary_calls(
    dev_state: DevState,
    reviewer_messages: list[BaseMessage],
    reviewer_passed_summary: ReviewerSummary,
) -> None:
    dev_state["reviewer_messages"] = reviewer_messages

    response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "submit_reviewer_summary",
                "args": {"summary": reviewer_passed_summary.model_dump()},
                "id": "tool-call-1",
                "type": "tool_call",
            },
            {
                "name": "submit_reviewer_summary",
                "args": {"summary": reviewer_passed_summary.model_dump()},
                "id": "tool-call-2",
                "type": "tool_call",
            },
        ],
    )

    reviewer_llm = Mock()
    reviewer_llm.invoke.return_value = response

    result = reviewer_node(dev_state, reviewer_llm)

    messages = result["reviewer_messages"]
    assert isinstance(messages, list)
    assert messages[0] == response
    assert isinstance(messages[1], HumanMessage)
    assert messages[1].content == REVIEWER_SUMMARY_MUST_BE_ALONE_MESSAGE


@pytest.mark.parametrize(
    ("reviewer_summary_fixture", "expected_review_status"),
    [
        ("reviewer_passed_summary", ReviewStatus.PASSED),
        ("reviewer_repair_summary", ReviewStatus.REPAIR_REQUIRED),
        ("reviewer_blocked_summary", ReviewStatus.BLOCKED),
    ],
)
def test_process_reviewer_summary_call(
    dev_state: DevState,
    reviewer_messages: list[BaseMessage],
    request: pytest.FixtureRequest,
    reviewer_summary_fixture: str,
    expected_review_status: ReviewStatus,
) -> None:
    dev_state["reviewer_messages"] = reviewer_messages

    reviewer_summary: ReviewerSummary = request.getfixturevalue(
        reviewer_summary_fixture
    )

    response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "submit_reviewer_summary",
                "args": {
                    "summary": reviewer_summary.model_dump(),
                },
                "id": "tool-call-1",
                "type": "tool_call",
            }
        ],
    )

    reviewer_llm = Mock()
    reviewer_llm.invoke.return_value = response

    with patch.object(
        ReviewerSummary,
        "model_validate",
        return_value=reviewer_summary,
    ) as model_validate:
        result = reviewer_node(dev_state, reviewer_llm)

    model_validate.assert_called_once_with(response.tool_calls[0]["args"]["summary"])

    messages = result["reviewer_messages"]
    assert isinstance(messages, list)

    assert result["reviewer_messages"] == [response]
    assert result["current_reviewer_summary"] == reviewer_summary
    assert result["review_status"] == expected_review_status
    assert result["reviewer_summary_history"] == [
        ReviewCycle(
            cycle_number=1,
            reviewer_summary=reviewer_summary,
        )
    ]
