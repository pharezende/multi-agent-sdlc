from pathlib import Path
from typing import cast

import pytest
from langchain.tools import ToolRuntime

from multi_agent_sdlc.system.process import ProcessResult
from multi_agent_sdlc.workflow.state import DevState, build_initial_state


@pytest.fixture
def project_directory(tmp_path: Path) -> Path:
    project_directory = tmp_path / "sandbox" / "terminal-calculator"
    project_directory.mkdir(parents=True)
    return project_directory


@pytest.fixture
def tool_runtime(
    project_directory: Path,
) -> ToolRuntime[DevState]:
    state = build_initial_state("test request")
    state["project_directory"] = project_directory

    return cast(
        ToolRuntime[DevState],
        ToolRuntime(
            state=state,
            context=None,
            config={},
            stream_writer=lambda _: None,
            tool_call_id=None,
            store=None,
        ),
    )


@pytest.fixture
def process_result() -> ProcessResult:
    return ProcessResult(
        command=["test-command"],
        exit_code=0,
        stdout="success",
        stderr="",
        timed_out=False,
    )
