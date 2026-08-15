from multi_agent_sdlc.workflow.state import DevState


def build_coder_implementation_context(state: DevState) -> dict[str, object]:

    plan = state.get("plan")
    if plan is None:
        raise ValueError("This workflow stage requires an approved plan.")
    coder_tasks = [
        task.model_dump(mode="json") for task in plan.tasks if task.owner == "coder"
    ]

    if not coder_tasks:
        raise ValueError("The approved plan contains no Coder-owned tasks.")

    return {
        "request": state["request"],
        "project_id": plan.project_id,
        "goal": plan.goal,
        "assumptions": plan.assumptions,
        "out_of_scope": plan.out_of_scope,
        "tasks": coder_tasks,
    }


def build_coder_repair_context(
    state: DevState,
) -> dict[str, object]:
    plan = state["plan"]

    if plan is None:
        raise ValueError("This workflow stage requires an approved plan.")

    tester_summary = state["current_tester_summary"]

    if tester_summary is None:
        raise ValueError("This workflow stage requires a tester summary.")

    reviewer_summary = state.get("current_reviewer_summary")
    verification_block_review = state.get("verification_block_review")

    coder_tasks = [
        task.model_dump(mode="json") for task in plan.tasks if task.owner == "coder"
    ]

    return {
        "coder_tasks": coder_tasks,
        "tester_summary": tester_summary.model_dump(mode="json"),
        "reviewer_summary": (
            reviewer_summary.model_dump(mode="json")
            if reviewer_summary is not None
            else None
        ),
        "verification_block_review": (
            verification_block_review.model_dump(mode="json")
            if verification_block_review is not None
            else None
        ),
    }
