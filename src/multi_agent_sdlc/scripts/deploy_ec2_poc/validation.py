from multi_agent_sdlc.scripts.deploy_ec2_poc.models import ValidatedProject
from pydantic import ConfigDict
from pydantic import BaseModel
from multi_agent_sdlc.system.process import execute_process
from pathlib import Path


COMPOSE_FILE_NAMES = (
    "compose.yaml",
    "compose.yml",
    "docker-compose.yaml",
    "docker-compose.yml",
)


def validate_project(
    project_directory: Path,
) -> ValidatedProject:
    project_directory = project_directory.resolve()

    if not project_directory.exists():
        raise ValueError(f"Project directory does not exist: {project_directory}")

    if not project_directory.is_dir():
        raise ValueError(f"Project path is not a directory: {project_directory}")

    dockerfile = project_directory / "Dockerfile"

    if not dockerfile.is_file():
        raise ValueError(f"Dockerfile was not found in {project_directory}")

    compose_file = _find_compose_file(project_directory)

    result = execute_process(
        [
            "docker",
            "compose",
            "-f",
            compose_file.name,
            "config",
            "--quiet",
        ],
        project_directory=project_directory,
        timeout_seconds=30,
    )

    if result["timed_out"]:
        raise RuntimeError("Docker Compose configuration validation timed out.")

    if result["exit_code"] != 0:
        error = result["stderr"] or result["stdout"]

        raise ValueError(
            "Docker Compose configuration validation failed"
            + (f": {error}" if error else ".")
        )

    return ValidatedProject(
        project_directory=project_directory,
        dockerfile=dockerfile,
        compose_file=compose_file,
    )


def _find_compose_file(
    project_directory: Path,
) -> Path:
    for filename in COMPOSE_FILE_NAMES:
        compose_file = project_directory / filename

        if compose_file.is_file():
            return compose_file

    expected_files = ", ".join(COMPOSE_FILE_NAMES)

    raise ValueError(
        "Docker Compose configuration was not found. "
        f"Expected one of: {expected_files}."
    )
