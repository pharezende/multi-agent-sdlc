import tomllib
from pathlib import Path


def _build_mypy_command(
    project_directory: Path,
) -> list[str]:
    pyproject_path = project_directory / "pyproject.toml"

    if pyproject_path.exists():
        with pyproject_path.open("rb") as file:
            pyproject = tomllib.load(file)

        mypy_config = pyproject.get("tool", {}).get("mypy", {})

        if any(key in mypy_config for key in ("files", "packages", "modules")):
            return ["uv", "run", "mypy"]

    if (project_directory / "src").is_dir():
        return ["uv", "run", "mypy", "src"]

    if (project_directory / "app").is_dir():
        return ["uv", "run", "mypy", "app"]

    return ["uv", "run", "mypy", "."]
