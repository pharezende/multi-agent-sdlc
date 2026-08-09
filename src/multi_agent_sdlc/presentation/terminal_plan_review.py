from multi_agent_sdlc.workflow.models import PlanReviewDecision


def collect_plan_review_decision() -> PlanReviewDecision:

    decisions = {
        "1": "approved",
        "2": "revision_required",
        "3": "rejected",
    }

    while True:
        option = input(
            "Select: [1] Approve, [2] Request revision, [3] Reject: "
        ).strip()

        decision = decisions.get(option)
        if decision is not None:
            break

        print("Invalid option. Enter 1, 2, or 3.")

    feedback: str | None = None

    if decision in {"revision_required", "rejected"}:
        while True:
            feedback = input("Feedback: ").strip()

            if feedback:
                break

            print("Feedback is required.")

    return PlanReviewDecision.model_validate(
        {
            "decision": decision,
            "feedback": feedback,
        }
    )
