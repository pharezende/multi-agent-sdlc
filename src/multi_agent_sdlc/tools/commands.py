from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Annotated, Any
from multi_agent_sdlc.state import DevState

from langgraph.prebuilt import ToolRuntime
from langchain_core.tools import tool
from pydantic import Field


# ============================================================
# POLICY CONSTANTS
# ============================================================

TEST_DIRECTORY_NAMES = {
    "test",
    "tests",
    "__tests__",
    "spec",
    "specs",
}

PROHIBITED_ENTRY_POINTS = {
    "pytest",
    "ruff",
    "mypy",
    "flake8",
    "coverage",
    "coverage3",
    "pip",
    "pip3",
    "bash",
    "sh",
    "zsh",
    "fish",
    "powershell",
    "pwsh",
}

PROHIBITED_PYTHON_MODULES = {
    "pytest",
    "unittest",
    "coverage",
    "pip",
    "ensurepip",
    "venv",
    "subprocess",
}

PROHIBITED_RUNTIME_PACKAGES = {
    "pytest",
    "pytest-cov",
    "coverage",
    "ruff",
    "mypy",
    "flake8",
    "tox",
    "nox",
}

ENTRY_POINT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

MODULE_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$")

DEPENDENCY_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]*"
    r"(?:\[[A-Za-z0-9._,-]+\])?"
    r"(?:(?:===|==|~=|!=|<=|>=|<|>)[A-Za-z0-9.*+!_-]+)?$"
)

REMOTE_DEPENDENCY_PREFIXES = (
    "http://",
    "https://",
    "git+",
    "ssh://",
    "file:",
)


# ============================================================
# TOOL DESCRIPTIONS
# ============================================================

LIST_FILES_DESCRIPTION = """
List files and directories inside the current generated project.

Path rules:
- `path` must be relative to the current project root.
- Use `.` to list the project root.
- Do not include `sandbox/`, the project name, or an absolute path.
- Do not use `..`.

Correct examples:
- .
- src
- src/calculator

Incorrect examples:
- sandbox/terminal-calculator
- /home/user/project
- ../other-project

This tool only inspects the filesystem. It does not execute shell commands.
""".strip()


READ_FILE_DESCRIPTION = """
Read a UTF-8 text file inside the current generated project.

Path rules:
- `path` must be relative to the current project root.
- Do not include `sandbox/`, the project name, or an absolute path.
- Do not use `..`.

Correct examples:
- pyproject.toml
- README.md
- src/calculator/main.py

Incorrect examples:
- sandbox/terminal-calculator/pyproject.toml
- /home/user/project/main.py
- ../other-project/main.py

Use this tool to inspect existing project files before modifying them.
""".strip()


WRITE_FILE_DESCRIPTION = """
Create or replace a production file inside the current generated project.

Path rules:
- `path` must be relative to the current project root.
- Do not include `sandbox/`, the project name, or an absolute path.
- Do not use `..`.

Correct examples:
- pyproject.toml
- README.md
- src/calculator/__init__.py
- src/calculator/main.py

Incorrect examples:
- sandbox/terminal-calculator/src/calculator/main.py
- /absolute/path/main.py
- ../other-project/main.py
- tests/test_calculator.py

Testing boundary:
- This tool is restricted to production files.
- Do not create or modify files inside `test`, `tests`, `__tests__`, `spec`,
  or `specs`.
- Test implementation belongs exclusively to the Tester agent.
- Do not retry rejected test work using another path, tool, or mechanism.

Python project requirements:
- Use `pyproject.toml` for project metadata and dependency declarations.
- Generated setup and execution instructions must use `uv`.
- Do not document or generate `pip install`, `python -m pip`, virtual
  environment activation, or direct dependency installation instructions.
- Application execution instructions should use `uv run`.
""".strip()


CREATE_DIRECTORY_DESCRIPTION = """
Create a production directory inside the current generated project.

Path rules:
- `path` must be relative to the current project root.
- Do not include `sandbox/`, the project name, or an absolute path.
- Do not use `..`.

Correct examples:
- src
- src/calculator
- config

Incorrect examples:
- sandbox/terminal-calculator/src
- /absolute/path
- ../other-project
- tests
- src/tests

Testing boundary:
- Do not create `test`, `tests`, `__tests__`, `spec`, or `specs` directories.
- Test directory creation belongs exclusively to the Tester agent.

This tool only creates directories. It does not run `mkdir`, shell commands,
Python snippets, or project-management commands.
""".strip()


RUN_APPLICATION_DESCRIPTION = """
Run a project application entry point inside the generated project's uv-managed
environment.

The tool internally executes:

    uv run <entry_point> [arguments]

The Coder provides only:
- the entry-point name declared in `[project.scripts]` in `pyproject.toml`;
- optional application arguments.

Correct examples:
- entry_point="calc", args=[]
- entry_point="calc", args=["2 + 3"]
- entry_point="odd-even", args=["7"]
- entry_point="my-app", args=["--help"]

Important uv rules:
- Do not include `uv run` in `entry_point`.
- Do not activate `.venv` manually.
- Do not use `python`, `pip`, `uv pip`, shell commands, or absolute paths.
- The tool runs from the current project root, so `uv` automatically discovers
  `pyproject.toml` and uses or creates `<project_root>/.venv`.
- Use this tool instead of requesting a generic shell command.

Testing boundary:
- Use this tool only for direct application execution and simple smoke checks.
- Do not use Pytest, Ruff, Mypy, coverage, shell scripts, or test entry points.
- Do not simulate interactive input through subprocess scripts.
- Interactive and end-to-end verification belongs to the Tester agent.
""".strip()


RUN_PYTHON_MODULE_DESCRIPTION = """
Run an application module inside the generated project's uv-managed environment.

The tool internally executes:

    uv run python -m <module> [arguments]

The Coder provides only:
- an importable application module name;
- optional application arguments.

Correct examples:
- module="calculator"
- module="calculator.cli"
- module="odd_even"
- module="customer_support.main"

Incorrect examples:
- module="src/calculator/main.py"
- module="python -m calculator"
- module="pytest"
- module="unittest"
- module="pip"
- module="-c"

Important uv rules:
- Do not include `uv run python -m` in `module`.
- Do not provide a file path or Python source code.
- Do not activate `.venv` manually.
- Do not use direct `python`, `pip`, `uv pip`, or shell commands.
- `uv` automatically executes the module inside the current project's `.venv`.

Testing boundary:
- This tool may run application modules only.
- It cannot execute testing, linting, coverage, packaging, or environment
  management modules.
- Do not use it to create temporary verification scripts.
""".strip()


INSTALL_RUNTIME_DEPENDENCIES_DESCRIPTION = """
Add required runtime dependencies to the current generated project using `uv`.

The tool internally executes:

    uv add <package> [<package> ...]

`uv add`:
- records dependencies in `pyproject.toml`;
- updates `uv.lock`;
- synchronises the generated project's `.venv`.

Provide only runtime dependency specifications.

Correct examples:
- ["click"]
- ["requests>=2.32"]
- ["pydantic>=2"]
- ["fastapi", "uvicorn"]

Incorrect examples:
- ["uv", "add", "click"]
- ["pip install click"]
- ["--dev", "pytest"]
- ["pytest"]
- ["ruff"]
- ["git+https://example.com/repository.git"]
- ["package @ https://example.com/package.whl"]

Important uv rules:
- Do not use `pip`, `python -m pip`, or `uv pip install`.
- Do not manually edit or activate `.venv`.
- Use this tool only when the production application genuinely requires an
  external runtime dependency.
- Do not install packages already provided by the Python standard library.

Testing boundary:
- Do not add Pytest, Ruff, Mypy, coverage, Tox, Nox, or other testing and
  development dependencies.
- Development and testing dependencies belong to the Tester or Verifier stage.
""".strip()


# ============================================================
# PROJECT AND PATH HELPERS
# ============================================================


def get_project_directory(
    runtime: ToolRuntime[DevState],
) -> Path:
    """Return the absolute project root stored in the graph state."""
    project_directory = runtime.state.get("project_directory")

    if not project_directory:
        raise RuntimeError("`project_directory` is missing from the graph state.")

    root = Path(project_directory).expanduser().resolve()

    if not root.exists():
        raise FileNotFoundError(f"Project directory does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Project path is not a directory: {root}")

    return root


def normalise_relative_path(path: str) -> PurePosixPath:
    """Normalise and validate a project-relative path."""
    if not isinstance(path, str):
        raise TypeError("Path must be a string.")

    cleaned = path.strip().replace("\\", "/")

    if not cleaned:
        raise ValueError("Path cannot be empty.")

    candidate = PurePosixPath(cleaned)

    if candidate.is_absolute():
        raise PermissionError(f"Absolute paths are not allowed: {path}")

    if ".." in candidate.parts:
        raise PermissionError(f"Parent-directory traversal is not allowed: {path}")

    return candidate


def is_test_related_path(path: str) -> bool:
    """Return True when a path includes a blocked test directory."""
    candidate = normalise_relative_path(path)

    return any(part.lower() in TEST_DIRECTORY_NAMES for part in candidate.parts)


def reject_coder_test_path(path: str) -> None:
    """Prevent the Coder from writing into test-related directories."""
    if is_test_related_path(path):
        raise PermissionError(
            "The Coder cannot create or modify files or directories "
            f"inside test-related paths: {path}. "
            "Test implementation belongs to the Tester. "
            "Do not retry this operation using another tool or path."
        )


def reject_repeated_project_prefix(
    project_directory: Path,
    path: str,
) -> None:
    """Reject paths such as sandbox/project-name/src/file.py."""
    candidate = normalise_relative_path(path)
    parts = candidate.parts
    project_name = project_directory.name

    if len(parts) >= 2 and parts[0].lower() == "sandbox" and parts[1] == project_name:
        remaining_parts = parts[2:]

        suggested_path = (
            PurePosixPath(*remaining_parts).as_posix() if remaining_parts else "."
        )

        raise PermissionError(
            "Do not include the sandbox or project-directory prefix. "
            f"Use `{suggested_path}` instead of `{path}`."
        )


def resolve_project_path(
    project_directory: Path,
    path: str,
) -> Path:
    """Resolve a relative path and ensure it remains inside the project."""
    candidate = normalise_relative_path(path)

    reject_repeated_project_prefix(
        project_directory,
        path,
    )

    root = project_directory.resolve()
    resolved = (root / Path(*candidate.parts)).resolve()

    if not resolved.is_relative_to(root):
        raise PermissionError(f"Path escapes the project directory: {path}")

    return resolved


# ============================================================
# SUBPROCESS HELPERS
# ============================================================


def build_sandbox_environment() -> dict[str, str]:
    """Create an environment isolated from the orchestrator's Python setup."""
    environment = os.environ.copy()

    # Do not expose the orchestrator's active virtual environment to uv.
    environment.pop("VIRTUAL_ENV", None)

    # Do not leak custom Python import/runtime configuration.
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)

    # Prevent imports from the user's global site-packages directory.
    environment["PYTHONNOUSERSITE"] = "1"

    return environment


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
    *,
    project_directory: Path,
    timeout_seconds: int,
) -> dict[str, object]:
    """Execute an internally constructed command inside the project."""
    try:
        result = subprocess.run(
            command,
            cwd=project_directory,
            env=build_sandbox_environment(),
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

    return {
        "command": command,
        "exit_code": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "timed_out": False,
    }


# ============================================================
# EXECUTION VALIDATORS
# ============================================================


def validate_timeout(
    timeout_seconds: int,
    *,
    maximum: int,
) -> None:
    """Validate a tool-specific timeout range."""
    if not isinstance(timeout_seconds, int):
        raise TypeError("timeout_seconds must be an integer.")

    if not 1 <= timeout_seconds <= maximum:
        raise ValueError(f"timeout_seconds must be between 1 and {maximum}.")


def validate_entry_point(entry_point: str) -> str:
    """Validate and return a project entry-point name."""
    if not isinstance(entry_point, str):
        raise TypeError("Entry point must be a string.")

    cleaned = entry_point.strip()

    if not cleaned:
        raise ValueError("Entry point cannot be empty.")

    if cleaned.lower() in PROHIBITED_ENTRY_POINTS:
        raise PermissionError(f"The Coder cannot execute `{cleaned}`.")

    if not ENTRY_POINT_PATTERN.fullmatch(cleaned):
        raise ValueError(f"Invalid application entry point: {cleaned}")

    return cleaned


def validate_module_name(module: str) -> str:
    """Validate and return an application module name."""
    if not isinstance(module, str):
        raise TypeError("Module must be a string.")

    cleaned = module.strip()

    if not cleaned:
        raise ValueError("Module cannot be empty.")

    if not MODULE_PATTERN.fullmatch(cleaned):
        raise ValueError(f"Invalid Python module name: {cleaned}")

    root_module = cleaned.split(".", maxsplit=1)[0].lower()

    if root_module in PROHIBITED_PYTHON_MODULES:
        raise PermissionError(f"The Coder cannot execute Python module `{cleaned}`.")

    return cleaned


def validate_application_arguments(
    arguments: list[str],
) -> list[str]:
    """Validate arguments passed to an application or module."""
    if not isinstance(arguments, list):
        raise TypeError("Application arguments must be provided as a list of strings.")

    validated: list[str] = []

    for argument in arguments:
        if not isinstance(argument, str):
            raise TypeError("Every application argument must be a string.")

        if "\n" in argument or "\r" in argument:
            raise PermissionError("Multiline application arguments are not allowed.")

        if "\x00" in argument:
            raise PermissionError(
                "Null bytes are not allowed in application arguments."
            )

        validated.append(argument)

    return validated


def normalise_dependency_name(specification: str) -> str:
    """Extract the normalised package name from a dependency specification."""
    match = re.match(
        r"^[A-Za-z0-9][A-Za-z0-9._-]*",
        specification,
    )

    if match is None:
        return ""

    return match.group(0).lower().replace("_", "-")


def validate_runtime_dependency(package: str) -> str:
    """Validate and return a runtime dependency specification."""
    if not isinstance(package, str):
        raise TypeError("Dependency specifications must be strings.")

    cleaned = package.strip()

    if not cleaned:
        raise ValueError("Dependency specification cannot be empty.")

    lowered = cleaned.lower()

    if lowered.startswith(REMOTE_DEPENDENCY_PREFIXES):
        raise PermissionError(
            "Git, URL, SSH, and local-file dependencies are not allowed: " f"{cleaned}"
        )

    if cleaned.startswith("-"):
        raise PermissionError(
            f"Dependency command-line options are not allowed: {cleaned}"
        )

    if "@" in cleaned:
        raise PermissionError(
            f"Direct-reference dependencies are not allowed: {cleaned}"
        )

    if not DEPENDENCY_PATTERN.fullmatch(cleaned):
        raise ValueError(f"Invalid runtime dependency specification: {cleaned}")

    dependency_name = normalise_dependency_name(cleaned)

    if dependency_name in PROHIBITED_RUNTIME_PACKAGES:
        raise PermissionError(
            f"`{cleaned}` is a testing or development dependency. "
            "The Coder may add runtime dependencies only."
        )

    return cleaned


# ============================================================
# CODER FILESYSTEM TOOLS
# ============================================================


@tool(
    "list_files",
    description=LIST_FILES_DESCRIPTION,
)
def coder_list_files(
    path: str,
    runtime: ToolRuntime[DevState],
) -> str:
    project_directory = get_project_directory(runtime)
    target = resolve_project_path(project_directory, path)

    if not target.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    if target.is_file():
        return target.relative_to(
            project_directory,
        ).as_posix()

    entries: list[str] = []

    for item in sorted(
        target.iterdir(),
        key=lambda value: (
            not value.is_dir(),
            value.name.lower(),
        ),
    ):
        relative = item.relative_to(
            project_directory,
        ).as_posix()

        suffix = "/" if item.is_dir() else ""
        entries.append(f"{relative}{suffix}")

    return "\n".join(entries) or "(empty directory)"


@tool(
    "read_file",
    description=READ_FILE_DESCRIPTION,
)
def coder_read_file(
    path: str,
    runtime: ToolRuntime[DevState],
) -> str:
    project_directory = get_project_directory(runtime)
    file_path = resolve_project_path(project_directory, path)

    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    if not file_path.is_file():
        raise IsADirectoryError(f"Path is not a file: {path}")

    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"File is not valid UTF-8 text: {path}") from error


@tool(
    "write_file",
    description=WRITE_FILE_DESCRIPTION,
)
def coder_write_file(
    path: str,
    content: str,
    runtime: ToolRuntime[DevState],
) -> str:
    reject_coder_test_path(path)

    project_directory = get_project_directory(runtime)
    file_path = resolve_project_path(project_directory, path)

    if file_path.exists() and file_path.is_dir():
        raise IsADirectoryError(f"Cannot replace a directory with a file: {path}")

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    return f"Written production file: {path}"


@tool(
    "create_directory",
    description=CREATE_DIRECTORY_DESCRIPTION,
)
def coder_create_directory(
    path: str,
    runtime: ToolRuntime[DevState],
) -> str:
    reject_coder_test_path(path)

    project_directory = get_project_directory(runtime)
    directory_path = resolve_project_path(
        project_directory,
        path,
    )

    if directory_path.exists() and not directory_path.is_dir():
        raise FileExistsError(f"A file already exists at this path: {path}")

    directory_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return f"Created production directory: {path}"


# ============================================================
# CODER UV TOOLS
# ============================================================


from pydantic import BaseModel, Field


class RunApplicationInput(BaseModel):
    entry_point: str = Field(
        description=(
            "Application entry point declared in [project.scripts] "
            "in pyproject.toml, such as `area-calculator`."
        ),
    )

    arguments: list[str] = Field(
        default_factory=list,
        description=(
            "Individual arguments passed to the application. "
            "Do not include `uv run` or shell syntax."
        ),
    )

    timeout_seconds: int = Field(
        default=15,
        ge=1,
        le=60,
        description="Maximum execution time in seconds.",
    )


@tool(
    "run_application",
    args_schema=RunApplicationInput,
    description=RUN_APPLICATION_DESCRIPTION,
)
def coder_run_application(
    entry_point: str,
    arguments: list[str],
    timeout_seconds: int,
    runtime: ToolRuntime,
) -> dict[str, object]:
    validated_entry_point = validate_entry_point(entry_point)
    validated_arguments = validate_application_arguments(arguments)

    project_directory = get_project_directory(runtime)

    return execute_process(
        [
            "uv",
            "run",
            validated_entry_point,
            *validated_arguments,
        ],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )


@tool(
    "run_python_module",
    description=RUN_PYTHON_MODULE_DESCRIPTION,
)
def coder_run_python_module(
    module: str,
    runtime: ToolRuntime[DevState],
    args: list[str] | None = None,
    timeout_seconds: Annotated[
        int,
        Field(
            ge=1,
            le=60,
            description=("Maximum module execution time in seconds."),
        ),
    ] = 15,
) -> dict[str, object]:
    validated_module = validate_module_name(module)
    validated_arguments = validate_application_arguments(args or [])

    validate_timeout(
        timeout_seconds,
        maximum=60,
    )

    project_directory = get_project_directory(runtime)

    return execute_process(
        [
            "uv",
            "run",
            "python",
            "-m",
            validated_module,
            *validated_arguments,
        ],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )


@tool(
    "install_runtime_dependencies",
    description=INSTALL_RUNTIME_DEPENDENCIES_DESCRIPTION,
)
def coder_install_runtime_dependencies(
    packages: list[str],
    runtime: ToolRuntime[DevState],
    timeout_seconds: Annotated[
        int,
        Field(
            ge=1,
            le=180,
            description=("Maximum dependency installation time in seconds."),
        ),
    ] = 120,
) -> dict[str, object]:
    if not packages:
        raise ValueError("At least one runtime dependency is required.")

    validated_packages = [validate_runtime_dependency(package) for package in packages]

    validate_timeout(
        timeout_seconds,
        maximum=180,
    )

    project_directory = get_project_directory(runtime)

    return execute_process(
        [
            "uv",
            "add",
            *validated_packages,
        ],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )


# ============================================================
# CODER TOOL REGISTRATION
# ============================================================

CODER_TOOLS = [
    coder_list_files,
    coder_read_file,
    coder_write_file,
    coder_create_directory,
    coder_run_application,
    coder_run_python_module,
    coder_install_runtime_dependencies,
]
