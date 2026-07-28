# tools/commands.py

from multi_agent_sdlc.state import DevState
from langgraph.prebuilt import ToolRuntime
import shlex
import subprocess
from pathlib import Path

from langchain_core.tools import tool


ALLOWED_COMMANDS = {
    "python",
    "pytest",
    "ruff",
    "mypy",
    "uv",
}


def validate_command(command: list[str]) -> None:
    if not command:
        raise ValueError("Command cannot be empty.")

    executable = Path(command[0]).name

    if executable not in ALLOWED_COMMANDS:
        raise ValueError(f"Executable is not allowed: {executable}")

    for argument in command[1:]:
        argument_path = Path(argument)

        if argument_path.is_absolute():
            raise ValueError(f"Absolute path arguments are not allowed: {argument}")

        if ".." in argument_path.parts:
            raise ValueError(f"Parent-directory traversal is not allowed: {argument}")


@tool
def run_command(
    command: list[str],
    runtime: ToolRuntime[DevState],
    timeout_seconds: int = 60,
) -> str:
    """Run an approved command inside the current project directory."""

    project_directory = Path(runtime.state["project_directory"]).resolve()

    validate_command(command)

    result = subprocess.run(
        command,
        cwd=project_directory,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        shell=False,
        check=False,
    )

    return (
        f"Exit code: {result.returncode}\n\n"
        f"Standard output:\n{result.stdout.strip()}\n\n"
        f"Standard error:\n{result.stderr.strip()}"
    )
