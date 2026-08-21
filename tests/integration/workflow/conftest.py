from pathlib import Path
from unittest.mock import MagicMock

import pytest

import multi_agent_sdlc.workflow.nodes.preparation.coder as coder_preparation_module
from multi_agent_sdlc.agents.planner.models import DevelopmentPlan
from multi_agent_sdlc.agents.reviewer.models import ReviewerSummary
from multi_agent_sdlc.agents.tester.model import TesterSummary as _TesterSummary
from multi_agent_sdlc.deployment.models import (
    ApplicationVerificationResult,
    DeploymentResult,
)
from multi_agent_sdlc.tools.shared.models import ProcessResult


@pytest.fixture(autouse=True)
def disable_langsmith_tracing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")


@pytest.fixture
def tester_summary_passed() -> _TesterSummary:
    return _TesterSummary(
        addressed_task_ids=["T2"],
        passed_task_ids=["T2"],
        related_task_ids=["T1"],
        files_created_or_modified=["tests/test_main.py"],
        development_dependencies_added=[],
        verification_results=[],
        acceptance_criteria_results=[],
        tester_repairs=[],
        implementation_failures=[],
        unresolved_issues=[],
        overall_status="passed",
        coder_repair_requests=[],
    )


@pytest.fixture
def reviewer_summary_passed() -> ReviewerSummary:
    return ReviewerSummary(
        overall_status="passed",
        summary="The implementation satisfies the approved plan.",
        findings=[],
    )


@pytest.fixture
def deployment_result() -> DeploymentResult:
    return DeploymentResult(
        instance_id="i-test",
        command_id="deploy-command",
        exit_code=0,
        stdout="Deployment completed.",
        stderr="",
    )


@pytest.fixture
def deployment_verification() -> ApplicationVerificationResult:
    return ApplicationVerificationResult(
        instance_id="i-test",
        command_id="verification-command",
        passed=True,
        exit_code=0,
        stdout="Application is healthy.",
        stderr="",
    )


@pytest.fixture
def project_verification_commands() -> list[list[str]]:
    return [
        ["uv", "run", "ruff", "check", "."],
        ["uv", "run", "ruff", "format", "--check", "."],
        ["uv", "run", "mypy", "."],
        ["uv", "run", "pytest"],
    ]


@pytest.fixture
def passed_process_results(
    project_verification_commands: list[list[str]],
) -> list[ProcessResult]:
    return [
        ProcessResult(
            command=command,
            exit_code=0,
            stdout="success",
            stderr="",
            timed_out=False,
        )
        for command in project_verification_commands
    ]


@pytest.fixture
def prepared_project(
    development_plan: DevelopmentPlan,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Path, MagicMock]:
    project_directory = tmp_path / development_plan.project_id
    project_directory.mkdir()

    monkeypatch.setattr(
        coder_preparation_module,
        "create_project_directory",
        MagicMock(return_value=project_directory),
    )
    update_workflow_project_directory_mock = MagicMock()
    monkeypatch.setattr(
        coder_preparation_module,
        "update_workflow_project_directory",
        update_workflow_project_directory_mock,
    )

    return project_directory, update_workflow_project_directory_mock
