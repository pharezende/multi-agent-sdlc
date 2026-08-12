from langchain_core.runnables import Runnable
from multi_agent_sdlc.agents.tester.prompt import (
    TESTER_MULTIPLE_PROJECT_VERIFICATION_CALLS_FEEDBACK,
)
from multi_agent_sdlc.agents.tester.prompt import TESTER_INVALID_RESPONSE_FEEDBACK
from multi_agent_sdlc.agents.tester.prompt import (
    TESTER_SUBMIT_SUMMARY_WITH_OTHER_TOOLS_FEEDBACK,
)
from multi_agent_sdlc.agents.tester.prompt import (
    TESTER_PASSED_SUMMARY_WITHOUT_SUCCESSFUL_VERIFICATION_FEEDBACK,
)
from langchain_core.messages import AIMessage, HumanMessage

from multi_agent_sdlc.agents.tester.model import (
    TesterCycle,
    TesterSummary,
    VerificationType,
)
from multi_agent_sdlc.tools.tester.model import ProjectVerificationResult
from multi_agent_sdlc.workflow.models import VerificationStatus
from multi_agent_sdlc.workflow.state import DevState


def tester_node(state: DevState, tester_llm: Runnable) -> dict[str, object]:
    tester_messages = state["tester_messages"]

    if not tester_messages:
        raise ValueError("Tester conversation has not been prepared.")

    response = tester_llm.invoke(tester_messages)

    if not response.tool_calls:
        return {
            "tester_messages": [
                response,
                HumanMessage(content=TESTER_INVALID_RESPONSE_FEEDBACK),
            ],
        }

    has_submit_call = any(
        tool_call["name"] == "submit_tester_summary"
        for tool_call in response.tool_calls
    )

    if has_submit_call:
        if len(response.tool_calls) > 1:
            return {
                "tester_messages": [
                    response,
                    HumanMessage(
                        content=TESTER_SUBMIT_SUMMARY_WITH_OTHER_TOOLS_FEEDBACK
                    ),
                ],
            }

        return _process_tester_summary_call(
            state,
            response,
        )

    if _has_multiple_project_verification_calls(response):
        return {
            "tester_messages": [
                response,
                HumanMessage(
                    content=TESTER_MULTIPLE_PROJECT_VERIFICATION_CALLS_FEEDBACK
                ),
            ],
        }

    return {
        "tester_messages": [response],
    }


def _process_tester_summary_call(
    state: DevState,
    response: AIMessage,
) -> dict[str, object]:

    tool_call = response.tool_calls[0]
    tester_summary = TesterSummary.model_validate(tool_call["args"]["summary"])

    latest_project_verification = state["current_project_verification_result"]

    if tester_summary.overall_status == "passed" and not project_verification_passed(
        latest_project_verification
    ):
        return {
            "tester_messages": [
                response,
                HumanMessage(
                    content=TESTER_PASSED_SUMMARY_WITHOUT_SUCCESSFUL_VERIFICATION_FEEDBACK
                ),
            ],
        }

    match tester_summary.overall_status:
        case "passed":
            verification_status = VerificationStatus.PASSED
        case "repair-required":
            verification_status = VerificationStatus.REPAIR_REQUIRED
        case "blocked":
            verification_status = VerificationStatus.BLOCKED

    tester_summary_history = state["tester_summary_history"]

    tester_cycle = TesterCycle(
        cycle_number=(
            tester_summary_history[-1].cycle_number + 1 if tester_summary_history else 1
        ),
        tester_summary=tester_summary,
    )

    return {
        "tester_messages": [response],
        "current_tester_summary": tester_summary,
        "tester_summary_history": [tester_cycle],
        "verification_status": verification_status,
    }


def project_verification_passed(
    result: ProjectVerificationResult | None,
) -> bool:
    if result is None:
        return False

    return (
        result["verification_type"] == VerificationType.COMPLETE_PROJECT_VERIFICATION
        and result["passed"]
        and result["overall_exit_code"] == 0
        and bool(result["checks"])
        and all(
            not check["timed_out"] and check["exit_code"] == 0
            for check in result["checks"]
        )
    )


def _has_multiple_project_verification_calls(response: AIMessage) -> bool:
    return (
        sum(
            tool_call["name"] == "tester_run_project_verification"
            for tool_call in response.tool_calls
        )
        > 1
    )
