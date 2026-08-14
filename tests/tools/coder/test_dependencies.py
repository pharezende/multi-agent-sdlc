from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, cast
from unittest.mock import patch

import pytest
from langchain.tools import ToolRuntime
from langchain_core.tools import BaseTool, StructuredTool

from multi_agent_sdlc.system.process import ProcessResult
from multi_agent_sdlc.tools.coder.dependencies import (
    coder_install_package_dependencies,
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
            "command": ["uv", "add", "requests"],
            "exit_code": 0,
            "stdout": "Installed requests",
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


def test_install_package_dependencies_installs_single_dependency(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_install_package_dependencies)

    with patch(
        "multi_agent_sdlc.tools.coder.dependencies.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        result = function(
            dependencies=["requests"],
            runtime=tool_runtime,
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "add",
            "requests",
        ],
        project_directory=project_directory,
        timeout_seconds=120,
    )

    assert result is process_result


def test_install_package_dependencies_installs_multiple_dependencies(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_install_package_dependencies)

    with patch(
        "multi_agent_sdlc.tools.coder.dependencies.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        result = function(
            dependencies=[
                "requests",
                "pydantic",
                "pytest",
            ],
            runtime=tool_runtime,
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "add",
            "requests",
            "pydantic",
            "pytest",
        ],
        project_directory=project_directory,
        timeout_seconds=120,
    )

    assert result is process_result


def test_install_package_dependencies_preserves_dependency_specifiers(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_install_package_dependencies)

    with patch(
        "multi_agent_sdlc.tools.coder.dependencies.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        function(
            dependencies=[
                "requests>=2.32",
                "pydantic==2.11.7",
            ],
            runtime=tool_runtime,
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "add",
            "requests>=2.32",
            "pydantic==2.11.7",
        ],
        project_directory=project_directory,
        timeout_seconds=120,
    )


def test_install_package_dependencies_uses_custom_timeout(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    process_result: ProcessResult,
) -> None:
    function = get_tool_function(coder_install_package_dependencies)

    with patch(
        "multi_agent_sdlc.tools.coder.dependencies.execute_process",
        return_value=process_result,
    ) as execute_process_mock:
        function(
            dependencies=["requests"],
            runtime=tool_runtime,
            timeout_seconds=300,
        )

    execute_process_mock.assert_called_once_with(
        [
            "uv",
            "add",
            "requests",
        ],
        project_directory=project_directory,
        timeout_seconds=300,
    )


def test_install_package_dependencies_returns_failed_process_result(
    tool_runtime: ToolRuntime[DevState],
) -> None:
    failed_result = cast(
        ProcessResult,
        {
            "command": ["uv", "add", "missing-package"],
            "exit_code": 1,
            "stdout": "",
            "stderr": "Dependency resolution failed",
            "timed_out": False,
        },
    )

    function = get_tool_function(coder_install_package_dependencies)

    with patch(
        "multi_agent_sdlc.tools.coder.dependencies.execute_process",
        return_value=failed_result,
    ):
        result = function(
            dependencies=["missing-package"],
            runtime=tool_runtime,
        )

    assert result is failed_result


def test_install_package_dependencies_returns_timeout_result(
    tool_runtime: ToolRuntime[DevState],
) -> None:
    timeout_result = cast(
        ProcessResult,
        {
            "command": ["uv", "add", "requests"],
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "timed_out": True,
            "message": ("Command exceeded timeout and process group terminated."),
        },
    )

    function = get_tool_function(coder_install_package_dependencies)

    with patch(
        "multi_agent_sdlc.tools.coder.dependencies.execute_process",
        return_value=timeout_result,
    ):
        result = function(
            dependencies=["requests"],
            runtime=tool_runtime,
        )

    assert result is timeout_result
