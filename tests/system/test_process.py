import signal
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch
from unittest.mock import call


from multi_agent_sdlc.system.process import (
    _start_process,
    _terminate_process_group,
    execute_process,
    normalise_process_output,
)


def test_normalise_process_output_none() -> None:
    assert normalise_process_output(None) == ""


def test_normalise_process_output_string() -> None:
    assert normalise_process_output("  output\n") == "output"


def test_normalise_process_output_bytes() -> None:
    assert normalise_process_output(b"  output\n") == "output"


def test_normalise_process_output_replaces_invalid_utf8() -> None:
    assert normalise_process_output(b"a\xffb") == "a\ufffdb"


def test_start_process(
    tmp_path: Path,
) -> None:
    command = ["python", "-c", "print('hello')"]
    environment = {"PATH": "/sandbox/bin"}

    process = Mock()

    with (
        patch(
            "multi_agent_sdlc.system.process.build_sandbox_environment",
            return_value=environment,
        ) as build_environment,
        patch(
            "multi_agent_sdlc.system.process.subprocess.Popen",
            return_value=process,
        ) as popen,
    ):
        result = _start_process(
            command=command,
            project_directory=tmp_path,
            stdin_text=None,
        )

    assert result is process

    build_environment.assert_called_once_with()

    popen.assert_called_once_with(
        command,
        cwd=tmp_path,
        env=environment,
        stdin=None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=False,
        start_new_session=True,
    )


def test_start_process_enables_stdin_when_provided(
    tmp_path: Path,
) -> None:
    with (
        patch(
            "multi_agent_sdlc.system.process.build_sandbox_environment",
            return_value={},
        ),
        patch(
            "multi_agent_sdlc.system.process.subprocess.Popen",
        ) as popen,
    ):
        _start_process(
            command=["python"],
            project_directory=tmp_path,
            stdin_text="input",
        )

    assert popen.call_args.kwargs["stdin"] == subprocess.PIPE


def test_terminate_process_group_gracefully() -> None:
    process = Mock()
    process.pid = 1234
    process.communicate.return_value = ("stdout", "stderr")

    with (
        patch(
            "multi_agent_sdlc.system.process.os.getpgid",
            return_value=5678,
        ) as getpgid,
        patch(
            "multi_agent_sdlc.system.process.os.killpg",
        ) as killpg,
    ):
        result = _terminate_process_group(
            process,
            grace_period_seconds=3,
        )

    assert result == ("stdout", "stderr")

    getpgid.assert_called_once_with(1234)
    killpg.assert_called_once_with(
        5678,
        signal.SIGTERM,
    )
    process.communicate.assert_called_once_with(
        timeout=3,
    )


def test_terminate_process_group_force_kills_after_grace_period() -> None:
    process = Mock()
    process.pid = 1234

    process.communicate.side_effect = [
        subprocess.TimeoutExpired(
            cmd=["python"],
            timeout=5,
        ),
        ("stdout", "stderr"),
    ]

    with (
        patch(
            "multi_agent_sdlc.system.process.os.getpgid",
            return_value=5678,
        ),
        patch(
            "multi_agent_sdlc.system.process.os.killpg",
        ) as killpg,
    ):
        result = _terminate_process_group(
            process,
            grace_period_seconds=5,
        )

    assert result == ("stdout", "stderr")

    assert killpg.call_args_list == [
        call(5678, signal.SIGTERM),
        call(5678, signal.SIGKILL),
    ]

    assert process.communicate.call_count == 2


def test_execute_process_success(
    tmp_path: Path,
) -> None:
    process = Mock()
    process.returncode = 0
    process.communicate.return_value = (
        "  hello\n",
        "  warning\n",
    )

    with patch(
        "multi_agent_sdlc.system.process._start_process",
        return_value=process,
    ) as start_process:
        result = execute_process(
            command=["python", "script.py"],
            project_directory=tmp_path,
            timeout_seconds=10,
        )

    start_process.assert_called_once_with(
        command=["python", "script.py"],
        project_directory=tmp_path,
        stdin_text=None,
    )

    process.communicate.assert_called_once_with(
        input=None,
        timeout=10,
    )

    assert result == {
        "command": ["python", "script.py"],
        "exit_code": 0,
        "stdout": "hello",
        "stderr": "warning",
        "timed_out": False,
    }


def test_execute_process_passes_stdin(
    tmp_path: Path,
) -> None:
    process = Mock()
    process.returncode = 0
    process.communicate.return_value = ("output", "")

    with patch(
        "multi_agent_sdlc.system.process._start_process",
        return_value=process,
    ):
        execute_process(
            command=["python", "script.py"],
            project_directory=tmp_path,
            timeout_seconds=10,
            stdin_text="hello",
        )

    process.communicate.assert_called_once_with(
        input="hello",
        timeout=10,
    )


def test_execute_process_returns_nonzero_exit_code(
    tmp_path: Path,
) -> None:
    process = Mock()
    process.returncode = 2
    process.communicate.return_value = (
        "",
        "Invalid argument",
    )

    with patch(
        "multi_agent_sdlc.system.process._start_process",
        return_value=process,
    ):
        result = execute_process(
            command=["tool", "--invalid"],
            project_directory=tmp_path,
            timeout_seconds=10,
        )

    assert result["exit_code"] == 2
    assert result["stderr"] == "Invalid argument"
    assert result["timed_out"] is False


def test_execute_process_timeout(
    tmp_path: Path,
) -> None:
    process = Mock()

    timeout_error = subprocess.TimeoutExpired(
        cmd=["python", "script.py"],
        timeout=10,
        output="partial stdout",
        stderr="partial stderr",
    )

    process.communicate.side_effect = timeout_error

    with (
        patch(
            "multi_agent_sdlc.system.process._start_process",
            return_value=process,
        ),
        patch(
            "multi_agent_sdlc.system.process._terminate_process_group",
            return_value=("final stdout", "final stderr"),
        ) as terminate,
    ):
        result = execute_process(
            command=["python", "script.py"],
            project_directory=tmp_path,
            timeout_seconds=10,
        )

    terminate.assert_called_once_with(process)

    assert result == {
        "command": ["python", "script.py"],
        "exit_code": None,
        "stdout": "final stdout",
        "stderr": "final stderr",
        "timed_out": True,
        "message": (
            "Command exceeded the 10-second timeout. "
            "The process group was terminated."
        ),
    }


def test_execute_process_timeout_uses_partial_output(
    tmp_path: Path,
) -> None:
    process = Mock()

    process.communicate.side_effect = subprocess.TimeoutExpired(
        cmd=["python"],
        timeout=10,
        output="partial stdout",
        stderr="partial stderr",
    )

    with (
        patch(
            "multi_agent_sdlc.system.process._start_process",
            return_value=process,
        ),
        patch(
            "multi_agent_sdlc.system.process._terminate_process_group",
            return_value=("", ""),
        ),
    ):
        result = execute_process(
            command=["python"],
            project_directory=tmp_path,
            timeout_seconds=10,
        )

    assert result["stdout"] == "partial stdout"
    assert result["stderr"] == "partial stderr"
