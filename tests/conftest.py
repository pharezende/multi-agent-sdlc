import pytest

from multi_agent_sdlc.agents.coder.models import CoderSummary
from multi_agent_sdlc.agents.planner.models import DevelopmentPlan, RiskLevel, Task
from multi_agent_sdlc.workflow.state import DevState, build_initial_state


@pytest.fixture
def dev_state() -> DevState:
    return build_initial_state("test request")


@pytest.fixture
def development_plan() -> DevelopmentPlan:
    return DevelopmentPlan(
        project_id="test-project",
        goal="Build a small test application.",
        tasks=[
            Task(
                id="T1",
                title="Implement application",
                owner="coder",
                description="Implement the application.",
                acceptance_criteria=[
                    "The application runs successfully.",
                ],
                depends_on=[],
                target_files=[
                    "src/main.py",
                ],
                risk=RiskLevel.LOW,
            ),
            Task(
                id="T2",
                title="Verify application",
                owner="tester",
                description="Verify the implemented application.",
                acceptance_criteria=[
                    "Automated verification passes.",
                ],
                depends_on=[
                    "T1",
                ],
                target_files=[
                    "tests/test_main.py",
                ],
                risk=RiskLevel.LOW,
            ),
        ],
        execution_order=[
            "T1",
            "T2",
        ],
        assumptions=[
            "Python is available.",
        ],
        out_of_scope=[],
    )


@pytest.fixture
def coder_summary() -> CoderSummary:
    return CoderSummary(
        implementation_summary=(
            "Implemented the Issue Tracker project scaffolding and application."
        ),
        completed_task_ids=["T1"],
        modified_files=[
            "issues_app/__init__.py",
            "issues_app/cli.py",
            "pyproject.toml",
        ],
        runtime_dependencies=[
            "flask",
        ],
        entry_points=[
            "issue-tracker",
        ],
        executed_operations=[
            "Created and updated the planned production files.",
            "Ran uv sync successfully.",
        ],
        unresolved_issues=[],
        tester_notes=[
            "Verify application startup and the configured issue-tracker entry point.",
        ],
    )
