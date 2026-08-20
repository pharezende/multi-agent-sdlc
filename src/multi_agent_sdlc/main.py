import logging
from textwrap import dedent

from dotenv import load_dotenv

from multi_agent_sdlc.cli import parse_args
from multi_agent_sdlc.workflow.models import PlanReviewDecision
from multi_agent_sdlc.workflow.runner import resume_workflow, run_new_workflow

load_dotenv(override=True)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


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
            checkpoint_id=args.checkpoint_id,
            configurable=automatic_plan_review_config,
        )
    else:
        request = dedent(
            """
        Build a containerized URL shortener REST API using Python, PostgreSQL, and Docker Compose.
        Provide endpoints to create short URLs, redirect them, retrieve statistics, and check health.
        Validate that submitted URLs use HTTP or HTTPS and return clear errors for invalid input.
        Store short codes, original URLs, creation timestamps, and access counts in PostgreSQL.
        Increment the access count whenever a short URL is successfully resolved.
        Use Docker Compose with separate application and PostgreSQL services.
        Persist PostgreSQL data with a Docker volume and configure a database health check.
        Automate database initialization or migrations without requiring manual SQL execution.
        Provide automated tests for API behavior, persistence, redirects, errors, and health checks.
        The project must pass Ruff, MyPy, pytest, and start with `docker compose up -d --build --wait`.
        """
        ).strip()

        run_new_workflow(
            request=request,
            configurable=automatic_plan_review_config,
        )


if __name__ == "__main__":
    run()
