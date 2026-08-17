from typing import Any
from multi_agent_sdlc.workflow.state import DevState


def build_reviewer_context(state: DevState) -> dict[str, Any]:
    plan = state["plan"]
    coder_summary = state["current_coder_summary"]
    tester_summary = state["current_tester_summary"]
    project_verification_result = state[
        "current_project_verification_result"
    ]  # TODO: Concatenate with tester_summary

    if plan is None:
        raise ValueError("This workflow stage requires an approved plan.")
    if coder_summary is None:
        raise ValueError("This workflow stage requires a coder summary.")
    if tester_summary is None:
        raise ValueError("This workflow stage requires a tester summary.")
    if project_verification_result is None:
        raise ValueError("This workflow stage requires a project verification result.")

    context: dict[str, Any] = {
        "request": state["request"],
        "plan": plan.model_dump(mode="json"),
        "coder_summary": coder_summary.model_dump(mode="json"),
        "tester_summary": tester_summary.model_dump(mode="json"),
        "project_verification_result": project_verification_result,
    }

    reviewer_history = state.get("reviewer_summary_history", [])

    if reviewer_history:
        context["current_reviewer_summary"] = reviewer_history[
            -1
        ].reviewer_summary.model_dump(mode="json")

    return context
