from workflow.runs import list_workflow_runs
from workflow.checkpointing import get_thread_id
from workflow.runs import WorkflowRunStatus
from workflow.runs import update_workflow_run_status
from workflow.runs import create_workflow_run
from workflow.runs import initialize_workflow_runs_database
from uuid import uuid4
from multi_agent_sdlc.agents.presentation.terminal_plan_review import (
    collect_plan_review_decision,
)
from langchain_core.runnables import RunnableConfig
from multi_agent_sdlc.models import PlanReviewStatus
from langgraph.graph.state import CompiledStateGraph

from multi_agent_sdlc.models import CoderStatus, TesterStatus
from multi_agent_sdlc.state import DevState

from langgraph.types import Command

from .graph import build_graph


def generate_diagram(graph: CompiledStateGraph) -> None:

    png_data = graph.get_graph().draw_mermaid_png()

    with open("multi_agent_sdlc_workflow.png", "wb") as file:
        file.write(png_data)


def run() -> None:
    graph = build_graph()

    request = """ Build a local task-management REST API that lets users create, retrieve, update, delete, and list tasks. Each task must include an ID, title, optional description, priority, status, creation timestamp, optional due date, and tags. Support filtering by status, priority, tag, and due-date range, as well as sorting and pagination.
        Store data locally in SQLite and ensure database initialization happens automatically. Enforce valid task-state transitions, such as preventing a completed task from being moved directly back to in_progress without first reopening it. Validate all inputs and return appropriate HTTP status codes and structured error responses.
        Add an endpoint that returns task statistics, including total tasks, counts by status and priority, overdue tasks, and completion percentage.
        Include automated unit and integration tests using an isolated temporary database. Provide clear handling for invalid IDs, malformed requests, duplicate or invalid data, database errors, and unsupported state transitions.
        Use FastAPI, Pydantic, SQLite, and a uv-managed Python project. Declare an application entry point so the service can be started with uv run <entry-point>. Include a concise README with installation instructions, API examples, expected responses, error behavior, and all commands required to run and verify the application.
        """.strip()
    initial_state: DevState = {
        "request": request,
        # "request": "Build a CLI expense tracker that lets users add expenses, list them, filter by category or date, and display total spending. Store data locally in a JSON file, validate invalid inputs, and provide clear exit codes and error messages. Include a concise README and a uv-managed Python project with a declared command-line entry point.",
        # "request": "Build an app that sum two numbers. The end user interactions happen via the terminal.",
        # "request": "Build a calculator app, all end user interactions happens via the terminal.",
        # "request": "Build an app that enable the user to compute the area of squares and triangles. The end user interactions happen via the terminal.",
        # "request": "Build a Python command-line application named `temperature-converter`. The application must convert temperatures between Celsius and Fahrenheit.",
        # "request": "Build a Python CLI app named password-strength-checker that accepts a password as an argument and reports weak, medium, or strong using only the standard library.",
        "plan": None,
        "project_directory": None,
        "plan_review_status": PlanReviewStatus.NOT_STARTED,
        "plan_review_decision": None,
        "plan_review_content": None,
        "planner_messages": [],
        "coder_messages": [],
        "coder_status": CoderStatus.IDLE,
        "current_coder_summary": None,
        "coder_invalid_response_count": 0,
        "coder_summary_history": [],
        "tester_messages": [],
        "tester_status": TesterStatus.IDLE,
        "current_tester_summary": None,
        "tester_summary_history": [],
        "current_project_verification_result": None,
    }

    # generate_diagram(graph)

    initialize_workflow_runs_database()

    workflow_run = create_workflow_run(request)

    print(list_workflow_runs())

    exit()
    config: RunnableConfig = {
        "configurable": {
            "thread_id": workflow_run.thread_id,
            "plan_review_decision": {
                "decision": "approved",
                "feedback": None,
            },
        }
    }

    result = graph.invoke(
        initial_state,
        config=config,
    )

    interrupts = result.get("__interrupt__", ())

    while interrupts:
        interrupt_value = interrupts[0].value

        update_workflow_run_status(
            get_thread_id(config),
            WorkflowRunStatus.INTERRUPTED,
        )

        if interrupt_value["type"] != "plan_review":
            raise ValueError(f"Unsupported interrupt type: {interrupt_value['type']!r}")

        print()
        print(interrupt_value["content"])
        print("\nGraph paused for plan review.")

        review_response = collect_plan_review_decision()

        result = graph.invoke(
            Command(resume=review_response),
            config=config,
        )

        interrupts = result.get("__interrupt__", ())

    update_workflow_run_status(
        get_thread_id(config),
        WorkflowRunStatus.COMPLETED,
    )

    print("\nGraph completed.")


if __name__ == "__main__":
    run()
