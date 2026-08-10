from multi_agent_sdlc.tools.shared.models import ProcessResult
import subprocess
from pathlib import Path
import os
import signal


from multi_agent_sdlc.runtime.environment import build_sandbox_environment


def normalise_process_output(
    output: str | bytes | None,
) -> str:
    """Convert subprocess output to a clean string."""
    if output is None:
        return ""

    if isinstance(output, bytes):
        return output.decode(
            "utf-8",
            errors="replace",
        ).strip()

    return output.strip()


def _start_process(
    command: list[str],
    project_directory: Path,
    stdin_text: str | None,
) -> subprocess.Popen[str]:
    """Start a process in an isolated process group."""

    return subprocess.Popen(
        command,
        cwd=project_directory,
        env=build_sandbox_environment(),
        stdin=subprocess.PIPE if stdin_text is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=False,
        start_new_session=True,
    )


def _terminate_process_group(
    process: subprocess.Popen[str],
    grace_period_seconds: int = 5,
) -> tuple[str, str]:
    """Terminate the process group and collect remaining output."""

    os.killpg(
        os.getpgid(process.pid),
        signal.SIGTERM,
    )

    try:
        return process.communicate(
            timeout=grace_period_seconds,
        )
    except subprocess.TimeoutExpired:
        os.killpg(
            os.getpgid(process.pid),
            signal.SIGKILL,
        )

        return process.communicate()


def execute_process(
    command: list[str],
    project_directory: Path,
    timeout_seconds: int,
    stdin_text: str | None = None,
) -> ProcessResult:
    """Execute an internally constructed command inside the project."""

    process = _start_process(
        command=command,
        project_directory=project_directory,
        stdin_text=stdin_text,
    )

    try:
        stdout, stderr = process.communicate(
            input=stdin_text,
            timeout=timeout_seconds,
        )

    except subprocess.TimeoutExpired as error:
        stdout, stderr = _terminate_process_group(process)

        return {
            "command": command,
            "exit_code": None,
            "stdout": normalise_process_output(stdout or error.stdout),
            "stderr": normalise_process_output(stderr or error.stderr),
            "timed_out": True,
            "message": (
                f"Command exceeded the {timeout_seconds}-second timeout. "
                "The process group was terminated."
            ),
        }

    return {
        "command": command,
        "exit_code": process.returncode,
        "stdout": stdout.strip(),
        "stderr": stderr.strip(),
        "timed_out": False,
    }
