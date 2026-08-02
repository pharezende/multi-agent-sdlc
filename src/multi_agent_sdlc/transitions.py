from multi_agent_sdlc.models import CoderMode
from multi_agent_sdlc.state import DevState


def create_prepare_retest_node(
    state: DevState,
) -> dict[str, object]:
    return {
        "current_tester_summary": None,
        "current_coder_summary": None,
        "coder_mode": CoderMode.REPAIR,
    }
