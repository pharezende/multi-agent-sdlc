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


def prepare_initial_coder_cycle_node(
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
        "current_coder_summary": None,
    }


# def prepare_tester_cycle(state: DevState) -> dict[str, object]:
#     coder_summary = state["current_coder_summary"]

#     if coder_summary is None:
#         raise ValueError("Cannot initialize testing without a Coder summary.")

#     if state["coder_status"] not in {
#         CoderStatus.COMPLETED,
#     }:
#         raise ValueError(
#             "Cannot initialize testing unless the Coder completed its cycle."
#         )

#     tester_context = build_tester_context(state)

#     return {
#         "tester_status": TesterStatus.TESTING_PENDING,
#         "tester_messages": [
#             HumanMessage(
#                 content=TESTER_HUMAN_PROMPT.format(
#                     tester_execution_input=json.dumps(
#                         tester_context,
#                         indent=2,
#                         ensure_ascii=False,
#                     )
#                 )
#             )
#         ],
#         "current_tester_summary": None,
#         "current_project_verification_result": None,
#     }


# def prepare_coder_repair(state: DevState) -> dict[str, object]:
#     tester_summary = state["current_tester_summary"]

#     if tester_summary is None:
#         raise ValueError("Cannot initialize a repair cycle without a Tester summary.")

#     if tester_summary.overall_status != "failed":
#         raise ValueError("Coder repair requires a failed Tester summary.")

#     if not tester_summary.coder_repair_requests:
#         raise ValueError("Failed Tester summary contains no Coder repair requests.")

#     repair_count = state.get("coder_repair_count", 0) + 1

#     if repair_count > state["maximum_coder_repairs"]:
#         raise RepairLimitExceededError("Maximum Coder repair cycles exceeded.")

#     repair_context = build_coder_repair_context(state)

#     return {
#         "coder_status": CoderStatus.REPAIRING,
#         "tester_status": TesterStatus.REPAIR_REQUIRED,
#         "coder_repair_count": repair_count,
#         "coder_messages": [
#             HumanMessage(
#                 content=CODER_REPAIR_PROMPT.format(
#                     coder_repair_input=json.dumps(
#                         repair_context,
#                         indent=2,
#                         ensure_ascii=False,
#                     )
#                 )
#             )
#         ],
#     }


def create_prepare_retest_node(
    state: DevState,
) -> dict[str, object]:
    return {
        "current_tester_summary": None,
        "current_coder_summary": None,
        "coder_mode": CoderMode.REPAIR,
    }
