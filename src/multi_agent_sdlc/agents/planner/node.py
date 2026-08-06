from multi_agent_sdlc.agents.planner.prompt import PLANNER_INITIAL_HUMAN_PROMPT_TEMPLATE
from langchain_core.messages import BaseMessage
from multi_agent_sdlc.agents.planner.prompt import (
    PLANNER_REVISION_HUMAN_PROMPT_TEMPLATE,
)
from multi_agent_sdlc.models import PlanReviewStatus
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from multi_agent_sdlc.models import DevelopmentPlan
from pathlib import Path
from re import fullmatch

from langchain_core.messages import HumanMessage, SystemMessage

from multi_agent_sdlc.agents.planner.exporter import export_plan_to_pdf
from multi_agent_sdlc.agents.planner.formatter import format_plan
from multi_agent_sdlc.agents.planner.model import planner_llm
from multi_agent_sdlc.agents.planner.prompt import PLANNER_SYSTEM_RULES
from multi_agent_sdlc.config import SANDBOX_ROOT
from multi_agent_sdlc.state import DevState


def create_project_directory(project_id: str) -> Path:
    "Create project folder inside 'sandbox', e.g: terminal-calculator"

    if not fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", project_id):
        raise ValueError("project_id must use lowercase kebab-case.")

    project_directory = Path(SANDBOX_ROOT) / project_id
    project_directory.mkdir(parents=True, exist_ok=True)

    return project_directory


def _generate_initial_plan(
    state: DevState,
) -> dict[str, object]:
    user_request = state["request"].strip()

    if not user_request:
        raise ValueError("User request cannot be empty.")

    initial_planner_messages: list[BaseMessage] = [
        SystemMessage(content=PLANNER_SYSTEM_RULES),
        HumanMessage(
            content=PLANNER_INITIAL_HUMAN_PROMPT_TEMPLATE.format(
                user_request=user_request,
            )
        ),
    ]

    plan = planner_llm.invoke(initial_planner_messages)

    if not isinstance(plan, DevelopmentPlan):
        raise TypeError(
            "Planner did not return a DevelopmentPlan. "
            f"Received {type(plan).__name__}."
        )

    return {
        "plan": plan,
        "planner_messages": [
            *initial_planner_messages,
            AIMessage(
                content=plan.model_dump_json(indent=2),
            ),
        ],
    }


def planner_node(state: DevState) -> dict[str, object]:
    """Generate the initial plan or revise the existing plan."""

    plan_review_status = state["plan_review_status"]

    if plan_review_status == PlanReviewStatus.REVISION_REQUIRED:
        planner_messages = state["planner_messages"]
        plan = planner_llm.invoke(planner_messages)

        if not isinstance(plan, DevelopmentPlan):
            raise TypeError(
                "Planner did not return a DevelopmentPlan. "
                f"Received {type(plan).__name__}."
            )

        return {
            "plan": plan,
            "planner_messages": [
                AIMessage(
                    content=plan.model_dump_json(indent=2),
                ),
            ],
        }

    return _generate_initial_plan(state)
