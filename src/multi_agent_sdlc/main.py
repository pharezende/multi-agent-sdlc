from textwrap import dedent
from multi_agent_sdlc.cli import parse_args
from multi_agent_sdlc.workflow.models import PlanReviewDecision
from multi_agent_sdlc.workflow.runner import resume_workflow, run_new_workflow


def run() -> None:
    args = parse_args()

    automatic_plan_review_config = (
        {"plan_review_decision": (PlanReviewDecision(decision="approved").model_dump())}
        if args.auto_approve_plan
        else {}
    )

    if args.resume:
        resume_workflow(
            thread_id=args.resume,
            plan_review_decision=automatic_plan_review_config,
        )
    else:
        request = dedent(
            """
        Build a local web-based issue-tracking application that lets users create,
        retrieve, update, delete, and list issues through a browser interface. Each
        issue must include an ID, title, optional description, priority, status,
        assignee, creation timestamp, update timestamp, optional due date, and labels.

        Provide pages for viewing issues, creating and editing issues, viewing issue
        details, and changing issue status. Support filtering by status, priority,
        assignee, label, and due-date range, as well as sorting and pagination. Enforce
        valid transitions between open, in_progress, resolved, and closed.

        Provide a dashboard with counts by status and priority, overdue issue count,
        and average resolution time. Persist data locally using SQLite, validate user
        input on the server side, display clear error messages, and include automated
        tests covering the required functionality and relevant edge cases.
        """
        ).strip()

        run_new_workflow(
            request=request,
            plan_review_decision=automatic_plan_review_config,
        )


if __name__ == "__main__":
    run()
