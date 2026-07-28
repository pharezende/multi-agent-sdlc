from pathlib import Path


def resolve_project_path(
    project_directory: Path,
    relative_path: str,
) -> Path:
    project_root = project_directory.resolve()

    if not project_root.is_dir():
        raise NotADirectoryError(
            f"Project directory does not exist: {project_directory}"
        )

    candidate = Path(relative_path)

    if candidate.is_absolute():
        raise ValueError("Absolute paths are not allowed.")

    resolved_path = (project_root / candidate).resolve()

    if not resolved_path.is_relative_to(project_root):
        raise ValueError(f"Path escapes the project directory: {relative_path}")

    return resolved_path
