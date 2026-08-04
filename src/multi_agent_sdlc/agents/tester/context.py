from multi_agent_sdlc.state import DevState


def build_tester_context(state: DevState) -> dict[str, object]:
    plan = state["plan"]

    return {
        "project_directory": state["project_directory"],
        "plan": plan.model_dump(mode="json"),
        "coder_summary": state["current_coder_summary"].model_dump(mode="json"),
    }
