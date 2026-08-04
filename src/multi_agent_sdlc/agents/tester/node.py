from multi_agent_sdlc.tools.tester.validation import ProjectVerificationResult
from langchain_core.messages import HumanMessage
from multi_agent_sdlc.models import TesterStatus
from multi_agent_sdlc.models import CoderStatus
from multi_agent_sdlc.models import VerificationCycle
from multi_agent_sdlc.models import TesterSummary
from multi_agent_sdlc.agents.tester.model import tester_llm
from multi_agent_sdlc.agents.tester.context import build_tester_context
from multi_agent_sdlc.agents.tester.prompt import (
    TESTER_CHAT_PROMPT_TEMPLATE,
    TESTER_SYSTEM_RULES,
)
from langchain_core.messages import AIMessage
from multi_agent_sdlc.state import DevState
import json


def tester_node(state: DevState) -> dict:

    tester_messages = state.get("tester_messages", [])
    tester_status = state["tester_status"]
    current_coder_summary = state["current_coder_summary"]

    if not tester_messages:
        return _initialize_tester_conversation(
            state
        )  # Summary is sent from here. (Need to fix for the second iteration with the tester)

    if tester_status is TesterStatus.TESTING_PENDING:
        tester_messages.append(
            HumanMessage(
                content=(
                    "The Coder has completed a production implementation or repair "
                    "cycle. Independently verify the current project state and "
                    "confirm whether the reported changes resolve the relevant "
                    "requirements or previously reported defects.\n\n"
                    "Do not treat the Coder's results as authoritative evidence. "
                    "Inspect the affected files and rerun the applicable Tester-owned "
                    "verification.\n\n"
                    "Latest Coder handoff:\n"
                    f"{current_coder_summary.model_dump_json(indent=2)}"
                )
            )
        )

    response = tester_llm.invoke(tester_messages)

    if response.tool_calls:
        if response.tool_calls[0]["name"] == "submit_tester_summary":
            if len(response.tool_calls) != 1:
                raise ValueError("`submit_tester_summary` must be called alone.")
            return _process_tester_summary_call(state, response)
        return {
            "tester_messages": [response],
        }

    return {
        "tester_messages": [
            response,
            HumanMessage(
                content=(
                    "Invalid response."
                    "Call exactly one approved Tester tool, or call "
                    "`submit_tester_summary` alone."
                )
            ),
        ],
    }


def _initialize_tester_conversation(
    state: DevState,
) -> dict[str, object]:
    current_coder_summary = state.get("current_coder_summary")

    tester_context = build_tester_context(state)
    tester_context["current_coder_summary"] = current_coder_summary.model_dump(
        mode="json"
    )

    prompt_value = TESTER_CHAT_PROMPT_TEMPLATE.invoke(
        {
            "tester_rules": TESTER_SYSTEM_RULES,
            "tester_context": json.dumps(
                tester_context,
                indent=2,
                ensure_ascii=False,
            ),
        }
    )

    initial_messages = prompt_value.to_messages()
    response = tester_llm.invoke(initial_messages)

    return {
        "tester_messages": [
            *initial_messages,
            response,
        ],
        "tester_status": TesterStatus.TESTING,
    }


def _process_tester_summary_call(
    state: DevState,
    response: AIMessage,
) -> dict[str, object]:
    if len(response.tool_calls) != 1:
        raise ValueError("`submit_tester_summary` must be called alone.")

    tool_call = response.tool_calls[0]

    tester_summary = TesterSummary.model_validate(tool_call["args"]["summary"])

    latest_project_verification = state.get("current_project_verification_result")

    if tester_summary.overall_status == "passed":
        if latest_project_verification is None or not project_verification_passed(
            latest_project_verification
        ):
            return {
                "tester_messages": [
                    response,
                    HumanMessage(
                        content=(
                            "The Tester summary cannot report `passed`. "
                            "Run `tester_run_project_verification` and ensure "
                            "the complete Ruff, Mypy, and Pytest checks all "
                            "finish successfully before submitting the "
                            "summary again."
                        )
                    ),
                ],
            }

    verification_history = state.get(
        "verification_history",
        [],
    )

    verification_cycle = VerificationCycle(
        cycle_number=(
            verification_history[-1].cycle_number + 1 if verification_history else 1
        ),
        tester_summary=tester_summary,
    )

    if tester_summary.overall_status == "failed":
        tester_status = TesterStatus.REPAIR_REQUIRED
    elif tester_summary.overall_status == "blocked":
        tester_status = TesterStatus.BLOCKED
    elif tester_summary.overall_status == "passed":
        tester_status = TesterStatus.PASSED
    else:
        raise ValueError(
            f"Unsupported Tester status: " f"{tester_summary.overall_status!r}"
        )

    update: dict[str, object] = {
        "tester_messages": [response],
        "current_tester_summary": tester_summary,
        "verification_history": [verification_cycle],
        "tester_status": tester_status,
    }

    if tester_status == TesterStatus.REPAIR_REQUIRED:
        update["coder_status"] = CoderStatus.REPAIRING

    return update


def project_verification_passed(
    result: ProjectVerificationResult,
) -> bool:
    return (
        result["verification_type"] == "complete_project_verification"
        and result["passed"]
        and result["overall_exit_code"] == 0
        and all(
            not check["timed_out"] and check["exit_code"] == 0
            for check in result["checks"]
        )
    )
