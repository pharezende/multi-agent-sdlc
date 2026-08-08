from langchain_core.messages import AIMessage, HumanMessage

from multi_agent_sdlc.agents.tester.model import tester_llm
from multi_agent_sdlc.models import (
    TesterCycle,
    TesterStatus,
    TesterSummary,
    VerificationType,
)
from multi_agent_sdlc.state import DevState
from multi_agent_sdlc.tools.tester.validation import ProjectVerificationResult


def tester_node(state: DevState) -> dict[str, object]:
    tester_messages = state["tester_messages"]

    if not tester_messages:
        raise ValueError("Tester conversation has not been prepared.")

    response = tester_llm.invoke(tester_messages)

    if response.tool_calls:  # Also change for planner.
        submit_calls = [
            tool_call
            for tool_call in response.tool_calls
            if tool_call["name"] == "submit_tester_summary"
        ]

        if submit_calls:
            if len(response.tool_calls) != 1:
                return {
                    "tester_messages": [
                        response,
                        HumanMessage(
                            content=(
                                "`submit_tester_summary` must be called alone. "
                                "Do not combine it with operational tool calls. "
                                "Correct the response and call "
                                "`submit_tester_summary` again."
                            )
                        ),
                    ],
                }

            return _process_tester_summary_call(
                state,
                response,
            )

        return {
            "tester_messages": [response],
        }

    return {
        "tester_messages": [
            response,
            HumanMessage(
                content=(
                    "Invalid response. Return no explanatory text. "
                    "Call one or more approved Tester operational tools, "
                    "or call `submit_tester_summary` alone."
                )
            ),
        ],
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
                    content=(
                        "The Tester summary cannot report `passed`. "
                        "Run `tester_run_project_verification` and ensure "
                        "all mandatory Ruff, Mypy, and Pytest checks complete "
                        "successfully before submitting the summary again."
                    )
                ),
            ],
        }

    match tester_summary.overall_status:
        case "passed":
            tester_status = TesterStatus.PASSED
        case "repair-required":
            tester_status = TesterStatus.REPAIR_REQUIRED
        case "blocked":
            tester_status = TesterStatus.BLOCKED

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
        "tester_status": tester_status,
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
