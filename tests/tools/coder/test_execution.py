from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, cast
from unittest.mock import patch

import pytest
from langchain.tools import ToolRuntime
from langchain_core.tools import BaseTool, StructuredTool

from multi_agent_sdlc.system.process import ProcessResult
from multi_agent_sdlc.tools.coder.execution import (
    coder_run_application,
    coder_run_python_module,
    coder_run_verification_command,
    coder_sync_project,
)
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
            "command": ["uv", "run", "expense-tracker"],
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


def test_run_application_uses_entry_point(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_run_application)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        result = function(
            entry_point="expense-tracker",
            runtime=tool_runtime,
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "run",
            "expense-tracker",
        ],
        project_directory=project_directory,
        timeout_seconds=15,
        stdin_text=None,
    )

    assert result is process_result


def test_run_application_appends_arguments(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_run_application)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        function(
            entry_point="expense-tracker",
            arguments=[
                "add",
                "--amount",
                "25.50",
            ],
            runtime=tool_runtime,
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "run",
            "expense-tracker",
            "add",
            "--amount",
            "25.50",
        ],
        project_directory=project_directory,
        timeout_seconds=15,
        stdin_text=None,
    )


def test_run_application_passes_stdin(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_run_application)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        function(
            entry_point="expense-tracker",
            runtime=tool_runtime,
            stdin_text="yes\n",
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "run",
            "expense-tracker",
        ],
        project_directory=project_directory,
        timeout_seconds=15,
        stdin_text="yes\n",
    )


def test_run_application_uses_custom_timeout(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_run_application)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        function(
            entry_point="expense-tracker",
            runtime=tool_runtime,
            timeout_seconds=30,
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "run",
            "expense-tracker",
        ],
        project_directory=project_directory,
        timeout_seconds=30,
        stdin_text=None,
    )


def test_run_application_returns_process_result(
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_run_application)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ):
        result = function(
            entry_point="expense-tracker",
            runtime=tool_runtime,
        )

    assert result is process_result


def test_run_python_module_uses_python_module_command(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_run_python_module)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        result = function(
            module="expense_tracker",
            runtime=tool_runtime,
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "run",
            "python",
            "-m",
            "expense_tracker",
        ],
        project_directory=project_directory,
        timeout_seconds=15,
        stdin_text=None,
    )

    assert result is process_result


def test_run_python_module_appends_arguments(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_run_python_module)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        function(
            module="expense_tracker",
            arguments=[
                "list",
                "--category",
                "food",
            ],
            runtime=tool_runtime,
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "run",
            "python",
            "-m",
            "expense_tracker",
            "list",
            "--category",
            "food",
        ],
        project_directory=project_directory,
        timeout_seconds=15,
        stdin_text=None,
    )


def test_run_python_module_passes_stdin(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_run_python_module)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        function(
            module="expense_tracker",
            runtime=tool_runtime,
            stdin_text="input\n",
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "run",
            "python",
            "-m",
            "expense_tracker",
        ],
        project_directory=project_directory,
        timeout_seconds=15,
        stdin_text="input\n",
    )


def test_run_python_module_uses_custom_timeout(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_run_python_module)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        function(
            module="expense_tracker",
            runtime=tool_runtime,
            timeout_seconds=45,
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "run",
            "python",
            "-m",
            "expense_tracker",
        ],
        project_directory=project_directory,
        timeout_seconds=45,
        stdin_text=None,
    )


def test_run_python_module_returns_process_result(
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_run_python_module)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ):
        result = function(
            module="expense_tracker",
            runtime=tool_runtime,
        )

    assert result is process_result


def test_sync_project_runs_uv_sync(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_sync_project)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        result = function(
            runtime=tool_runtime,
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "sync",
        ],
        project_directory=project_directory,
        timeout_seconds=120,
    )

    assert result is process_result


def test_sync_project_uses_custom_timeout(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_sync_project)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        function(
            runtime=tool_runtime,
            timeout_seconds=300,
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "sync",
        ],
        project_directory=project_directory,
        timeout_seconds=300,
    )


def test_sync_project_returns_process_result(
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_sync_project)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ):
        result = function(
            runtime=tool_runtime,
        )

    assert result is process_result


def test_run_verification_command_runs_command(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_run_verification_command)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        result = function(
            command="pytest",
            runtime=tool_runtime,
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "run",
            "pytest",
        ],
        project_directory=project_directory,
        timeout_seconds=120,
    )

    assert result is process_result


def test_run_verification_command_appends_arguments(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_run_verification_command)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        function(
            command="pytest",
            arguments=[
                "tests/test_cli.py",
                "-q",
            ],
            runtime=tool_runtime,
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "run",
            "pytest",
            "tests/test_cli.py",
            "-q",
        ],
        project_directory=project_directory,
        timeout_seconds=120,
    )


def test_run_verification_command_uses_custom_timeout(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_run_verification_command)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        function(
            command="mypy",
            arguments=["app"],
            runtime=tool_runtime,
            timeout_seconds=240,
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "run",
            "mypy",
            "app",
        ],
        project_directory=project_directory,
        timeout_seconds=240,
    )


def test_run_verification_command_returns_process_result(
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_run_verification_command)

    with patch(
        "multi_agent_sdlc.tools.coder.execution.execute_process",
        return_value=process_result,
    ):
        result = function(
            command="ruff",
            arguments=["check", "."],
            runtime=tool_runtime,
        )

    assert result is process_result
