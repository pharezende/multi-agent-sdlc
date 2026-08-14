from multi_agent_sdlc.workflow.models import VerificationBlockReview


def collect_verification_block_review() -> VerificationBlockReview:

    decisions = {
        "1": "retry",
        "2": "coder-repair",
        "3": "plan-revision",
        "4": "proceed-with-override",
        "5": "abort",
    }

    while True:
        option = input(
            "Select: [1] Retry verification, "
            "[2] Send to coder for repair, "
            "[3] Request plan revision, "
            "[4] Proceed with override, "
            "[5] Abort: "
        ).strip()

        decision = decisions.get(option)
        if decision is not None:
            break

        print("Invalid option. Enter 1, 2, 3, 4, or 5.")

    reason: str | None = None

    if decision != "retry":
        while True:
            reason = input("Reason: ").strip()

            if reason:
                break

            print("Reason is required.")

    return VerificationBlockReview.model_validate(
        {
            "decision": decision,
            "reason": reason,
        }
    )
