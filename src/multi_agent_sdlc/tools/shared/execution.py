from multi_agent_sdlc.tools.shared.models import DockerComposeOperation
from multi_agent_sdlc.tools.shared.description import RUN_DOCKER_COMPOSE_DESCRIPTION
from langchain.tools import ToolRuntime, tool

from multi_agent_sdlc.system.process import execute_process
from multi_agent_sdlc.tools.shared.models import (
    ExecutionTimeout,
    ProcessResult,
)
from multi_agent_sdlc.workflow.state import DevState


@tool(
    "run_docker_compose",
    description=RUN_DOCKER_COMPOSE_DESCRIPTION,
)
def run_docker_compose(
    operation: DockerComposeOperation,
    runtime: ToolRuntime[DevState],
    remove_volumes: bool = False,
    timeout_seconds: ExecutionTimeout = 120,
) -> ProcessResult:
    project_directory = runtime.state["project_directory"]

    command = ["docker", "compose"]

    match operation:
        case DockerComposeOperation.UP:
            command.extend(
                [
                    "up",
                    "-d",
                    "--wait",
                    "--wait-timeout",
                    "60",
                ]
            )

        case DockerComposeOperation.DOWN:
            command.append("down")

            if remove_volumes:
                command.append("-v")

        case DockerComposeOperation.BUILD:
            command.append("build")

        case DockerComposeOperation.CONFIG:
            command.extend(["config", "--quiet"])

        case DockerComposeOperation.PS:
            command.append("ps")

    return execute_process(
        command,
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )
