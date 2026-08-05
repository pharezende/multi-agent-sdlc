from multi_agent_sdlc.agents.coder.context import build_coder_repair_context
from multi_agent_sdlc.agents.coder.prompt import CODER_REPAIR_CHAT_PROMPT_TEMPLATE
from multi_agent_sdlc.agents.coder.messages import build_tester_initial_messages
from multi_agent_sdlc.agents.coder.messages import build_tester_retest_messages
from multi_agent_sdlc.models import CoderMode
from multi_agent_sdlc.agents.coder.context import build_coder_context
from multi_agent_sdlc.agents.coder.prompt import CODER_SYSTEM_RULES
from multi_agent_sdlc.agents.coder.prompt import CODER_CHAT_PROMPT_TEMPLATE
from langchain_core.messages import BaseMessage
from multi_agent_sdlc.state import DevState
from langchain_core.messages import HumanMessage
from multi_agent_sdlc.models import TesterStatus
from multi_agent_sdlc.models import CoderStatus
from multi_agent_sdlc.agents.tester.context import build_tester_context
from multi_agent_sdlc.state import DevState
import json


def prepare_coder_implementation_node(
    state: DevState,
) -> dict[str, object]:
    prompt_value = CODER_CHAT_PROMPT_TEMPLATE.invoke(
        {
            "coder_rules": CODER_SYSTEM_RULES,
            "coder_execution_input": json.dumps(
                build_coder_context(state),
                indent=2,
                ensure_ascii=False,
            ),
        }
    )

    return {
        "coder_status": CoderStatus.IMPLEMENTING,
        "coder_messages": prompt_value.to_messages(),
    }


def prepare_tester_node(
    state: DevState,
) -> dict[str, object]:

    coder_summary = state["current_coder_summary"]

    if coder_summary is None:
        raise ValueError("Cannot prepare the Tester without a Coder summary.")

    existing_messages = state.get("tester_messages", [])

    if existing_messages:
        messages = [
            build_tester_retest_messages(state),
        ]
    else:
        messages = build_tester_initial_messages(state)

    return {
        "tester_status": TesterStatus.TESTING,
        "tester_messages": messages,
        "current_project_verification_result": None,
    }


def prepare_coder_repair_node(
    state: DevState,
) -> dict[str, object]:
    prompt_value = CODER_REPAIR_CHAT_PROMPT_TEMPLATE.invoke(
        {
            "coder_repair_input": json.dumps(
                build_coder_repair_context(state),
                indent=2,
                ensure_ascii=False,
            ),
        }
    )

    return {
        "coder_status": CoderStatus.REPAIRING,
        "coder_messages": prompt_value.to_messages(),
        "current_coder_summary": None,
    }
