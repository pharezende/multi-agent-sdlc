from workflow.models import PlanReviewDecision
from multi_agent_sdlc.cli import parse_args
from workflow.runner import resume_workflow
from workflow.runner import run_new_workflow
from workflow.run_repository import initialize_workflow_runs_database


def run() -> None:
    args = parse_args()

    automatic_plan_review_decision = PlanReviewDecision(
        decision="approved"
    ).model_dump()

    if args.resume:
        resume_workflow(
            thread_id=args.resume,
            plan_review_decision=automatic_plan_review_decision,
        )
    else:
        request = """
        Build a local task-management REST API that lets users create, retrieve,
        update, delete, and list tasks. Each task must include an ID, title,
        optional description, priority, status, creation timestamp, optional due
        date, and tags. Support filtering by status, priority, tag, and due-date
        range, as well as sorting and pagination.

        Store data locally in SQLite and ensure database initialization happens
        automatically. Enforce valid task-state transitions, such as preventing
        a completed task from being moved directly back to in_progress without
        first reopening it. Validate all inputs and return appropriate HTTP
        status codes and structured error responses.

        Add an endpoint that returns task statistics, including total tasks,
        counts by status and priority, overdue tasks, and completion percentage.

        Include automated unit and integration tests using an isolated temporary
        database. Provide clear handling for invalid IDs, malformed requests,
        duplicate or invalid data, database errors, and unsupported state
        transitions.

        Use FastAPI, Pydantic, SQLite, and a uv-managed Python project. Declare
        an application entry point so the service can be started with
        uv run <entry-point>. Include a concise README with installation
        instructions, API examples, expected responses, error behavior, and all
        commands required to run and verify the application.
        """.strip()

        run_new_workflow(
            request=request, plan_review_decision=automatic_plan_review_decision
        )


if __name__ == "__main__":
    run()
