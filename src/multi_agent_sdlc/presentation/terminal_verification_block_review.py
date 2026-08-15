from multi_agent_sdlc.workflow.models import VerificationBlockReview


def collect_verification_block_review() -> VerificationBlockReview:
    decisions = {
        "1": "retry",
        "2": "coder-repair",
        "3": "proceed-with-override",
        "4": "abort",
    }

    while True:
        option = input(
            "Select: [1] Retry verification, "
            "[2] Send to coder for repair, "
            "[3] Proceed with override, "
            "[4] Abort: "
        ).strip()

        decision = decisions.get(option)

        if decision is not None:
            break

        print("Invalid option. Enter 1, 2, 3, or 4.")

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
