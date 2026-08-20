from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, cast
from unittest.mock import patch

import pytest
from langchain.tools import ToolRuntime
from langchain_core.tools import BaseTool, StructuredTool

from multi_agent_sdlc.system.process import ProcessResult
from multi_agent_sdlc.tools.shared.execution import run_docker_compose
from multi_agent_sdlc.tools.shared.models import DockerComposeOperation
from multi_agent_sdlc.workflow.state import DevState


@pytest.fixture
def project_directory(tmp_path: Path) -> Path:
    project_directory = tmp_path / "sandbox" / "terminal-calculator"
    project_directory.mkdir(parents=True)
    return project_directory


@pytest.fixture
def tool_runtime(
    project_directory: Path,
) -> ToolRuntime[DevState]:
    state = cast(
        DevState,
        {
            "project_directory": project_directory,
        },
    )

    return cast(
        ToolRuntime[DevState],
        SimpleNamespace(state=state),
    )


@pytest.fixture
def process_result() -> ProcessResult:
    return cast(
        ProcessResult,
        {
            "command": ["test-command"],
            "exit_code": 0,
            "stdout": "success",
            "stderr": "",
            "timed_out": False,
        },
    )


def get_tool_function(
    tool: BaseTool,
) -> Callable[..., Any]:
    if not isinstance(tool, StructuredTool):
        raise TypeError(f"Expected StructuredTool, got {type(tool).__name__}")

    if tool.func is None:
        raise TypeError(f"Tool {tool.name} does not have a synchronous function")

    return tool.func


@pytest.mark.parametrize(
    ("operation", "expected_command"),
    [
        (
            DockerComposeOperation.UP,
            [
                "docker",
                "compose",
                "up",
                "-d",
                "--wait",
                "--wait-timeout",
                "60",
            ],
        ),
        (
            DockerComposeOperation.DOWN,
            [
                "docker",
                "compose",
                "down",
            ],
        ),
        (
            DockerComposeOperation.BUILD,
            [
                "docker",
                "compose",
                "build",
            ],
        ),
        (
            DockerComposeOperation.CONFIG,
            [
                "docker",
                "compose",
                "config",
                "--quiet",
            ],
        ),
        (
            DockerComposeOperation.PS,
            [
                "docker",
                "compose",
                "ps",
            ],
        ),
    ],
)
def test_run_docker_compose_executes_expected_command(
    operation: DockerComposeOperation,
    expected_command: list[str],
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(run_docker_compose)

    with patch(
        "multi_agent_sdlc.tools.shared.execution.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        result = function(
            operation=operation,
            runtime=tool_runtime,
        )

    assert result is process_result

    execute_process_mock.assert_called_once_with(
        expected_command,
        project_directory=tool_runtime.state["project_directory"],
        timeout_seconds=120,
    )


def test_run_docker_compose_uses_custom_timeout(
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(run_docker_compose)

    with patch(
        "multi_agent_sdlc.tools.shared.execution.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        result = function(
            operation=DockerComposeOperation.BUILD,
            runtime=tool_runtime,
            timeout_seconds=300,
        )

    assert result is process_result

    execute_process_mock.assert_called_once_with(
        [
            "docker",
            "compose",
            "build",
        ],
        project_directory=tool_runtime.state["project_directory"],
        timeout_seconds=300,
    )
