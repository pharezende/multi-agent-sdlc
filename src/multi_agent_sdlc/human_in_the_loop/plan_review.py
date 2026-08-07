from multi_agent_sdlc.models import PlanReviewStatus
from multi_agent_sdlc.models import PlanReviewDecision
from multi_agent_sdlc.state import DevState
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt


def human_plan_review_node(
    state: DevState,
    config: RunnableConfig,
) -> dict[str, object]:
    configurable = config.get("configurable", {})

    predefined_decision = configurable.get("plan_review_decision")

    if predefined_decision is not None:
        response = predefined_decision
    else:
        response = interrupt(
            {
                "type": "plan_review",
                "content": state["plan_review_content"],
            }
        )

    decision = PlanReviewDecision.model_validate(response)

    return {
        "plan_review_decision": decision,
        "plan_review_status": PlanReviewStatus(decision.decision),
    }
