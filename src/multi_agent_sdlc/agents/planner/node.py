
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from multi_agent_sdlc.agents.planner.llm import planner_llm
from multi_agent_sdlc.agents.planner.models import DevelopmentPlan
from multi_agent_sdlc.agents.planner.prompt import (
    PLANNER_INITIAL_HUMAN_PROMPT_TEMPLATE,
    PLANNER_SYSTEM_RULES,
)
from multi_agent_sdlc.workflow.models import PlanReviewStatus
from multi_agent_sdlc.workflow.state import DevState


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
