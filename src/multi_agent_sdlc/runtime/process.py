from multi_agent_sdlc.tools.tester.validation import ProcessResult
import subprocess
from pathlib import Path

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


def execute_process(
    command: list[str],
    project_directory: Path,
    timeout_seconds: int,
    stdin_text: str | None = None,
) -> ProcessResult:
    """Execute an internally constructed command inside the project."""
    try:
        result = subprocess.run(
            command,
            cwd=project_directory,
            env=build_sandbox_environment(),
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            shell=False,
            check=False,
        )

    except subprocess.TimeoutExpired as error:
        return {
            "command": command,
            "exit_code": None,
            "stdout": normalise_process_output(error.stdout),
            "stderr": normalise_process_output(error.stderr),
            "timed_out": True,
            "message": (
                f"Command exceeded the {timeout_seconds}-second timeout. "
                "The process was stopped."
            ),
        }

    return ProcessResult(
        command=command,
        exit_code=result.returncode,
        stdout=result.stdout.strip(),
        stderr=result.stderr.strip(),
        timed_out=False,
    )
