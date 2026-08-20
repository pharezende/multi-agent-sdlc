from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable

from multi_agent_sdlc.agents.reviewer.models import ReviewerSummary
from multi_agent_sdlc.agents.reviewer.prompt import (
    REVIEWER_INVALID_RESPONSE_MESSAGE,
    REVIEWER_SUMMARY_MUST_BE_ALONE_MESSAGE,
)
from multi_agent_sdlc.workflow.models import ReviewCycle, ReviewStatus
from multi_agent_sdlc.workflow.state import DevState


def reviewer_node(state: DevState, reviewer_llm: Runnable) -> dict[str, object]:
    reviewer_messages = state["reviewer_messages"]

    if not reviewer_messages:
        raise ValueError(
            "Reviewer conversation was not initialized before reviewer execution."
        )

    response = reviewer_llm.invoke(reviewer_messages)

    if response.tool_calls:
        first_tool_call = response.tool_calls[0]

        if first_tool_call["name"] == "submit_reviewer_summary":
            if len(response.tool_calls) != 1:
                return {
                    "reviewer_messages": [
                        response,
                        HumanMessage(content=REVIEWER_SUMMARY_MUST_BE_ALONE_MESSAGE),
                    ]
                }

            return _process_reviewer_summary_call(state, response)

        return {
            "reviewer_messages": [response],
        }

    return {
        "reviewer_messages": [
            response,
            HumanMessage(content=REVIEWER_INVALID_RESPONSE_MESSAGE),
        ]
    }


def _process_reviewer_summary_call(
    state: DevState,
    response: AIMessage,
) -> dict[str, object]:
    tool_call = response.tool_calls[0]
    reviewer_summary = ReviewerSummary.model_validate(tool_call["args"]["summary"])

    match reviewer_summary.overall_status:
        case "passed":
            review_status = ReviewStatus.PASSED
        case "repair-required":
            review_status = ReviewStatus.REPAIR_REQUIRED
        case "blocked":
            review_status = ReviewStatus.BLOCKED

    history = state.get("reviewer_summary_history", [])

    review_cycle = ReviewCycle(
        cycle_number=len(history) + 1,
        reviewer_summary=reviewer_summary,
    )

    return {
        "reviewer_messages": [response],
        "current_reviewer_summary": reviewer_summary,
        "review_status": review_status,
        "reviewer_summary_history": [review_cycle],
    }
