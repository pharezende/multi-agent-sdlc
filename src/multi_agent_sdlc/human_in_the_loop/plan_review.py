from multi_agent_sdlc.models import PlanReviewStatus
from multi_agent_sdlc.models import PlanReviewDecision
from multi_agent_sdlc.state import DevState
from langgraph.types import interrupt


def human_plan_review_node(
    state: DevState,
) -> dict[str, object]:
    plan_review_content = state["plan_review_content"]

    if not plan_review_content:
        raise ValueError("Plan review content cannot be empty.")

    response = interrupt(
        {
            "type": "plan_review",
            "content": plan_review_content,
        }
    )

    decision = PlanReviewDecision.model_validate(response)

    return {
        "plan_review_status": PlanReviewStatus(decision.decision),
        "plan_review_decision": decision,
    }
