from multi_agent_sdlc.workflow.state import DevState


def build_tester_context(state: DevState) -> dict[str, object]:
    plan = state["plan"]
    if plan is None:
        raise ValueError("This workflow stage requires an approved plan.")

    current_coder_summary = state["current_coder_summary"]
    if current_coder_summary is None:
        raise ValueError("This workflow stage requires an approved plan.")

    return {
        "plan": plan.model_dump(mode="json"),
        "coder_summary": current_coder_summary.model_dump(mode="json"),
    }


def build_tester_retest_context(
    state: DevState,
) -> dict[str, object]:
    coder_summary = state["current_coder_summary"]
    tester_summary = state["current_tester_summary"]

    if coder_summary is None:
        raise ValueError("Tester retest context requires the previous Tester summary.")

    if tester_summary is None:
        raise ValueError("Tester retest context requires the previous Tester summary.")

    return {
        "latest_coder_summary": coder_summary.model_dump(mode="json"),
        "previous_implementation_failures": [
            failure.model_dump(mode="json")
            for failure in tester_summary.implementation_failures
        ],
        "previous_coder_repair_requests": [
            request.model_dump(mode="json")
            for request in tester_summary.coder_repair_requests
        ],
        "previous_failed_verification_results": [
            result.model_dump(mode="json")
            for result in tester_summary.verification_results
            if result.status == "failed"
        ],
        "previous_unresolved_issues": [
            issue.model_dump(mode="json") for issue in tester_summary.unresolved_issues
        ],
    }
