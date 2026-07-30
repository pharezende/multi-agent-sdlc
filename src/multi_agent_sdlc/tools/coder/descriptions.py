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


RUN_SYNC_PROJECT = """
Synchronise the generated Python project and validate its production
environment using uv.

The tool internally executes:

    uv sync

Use this tool after:
- creating or modifying `pyproject.toml`;
- adding or changing runtime dependencies;
- changing the package structure;
- changing build-system or packaging configuration;
- repairing an earlier `uv sync` failure.

Correct usage examples:
- After creating a new `pyproject.toml`.
- After adding `click` to `[project.dependencies]`.
- After changing the package path from `src/app` to `src/my_app`.
- After adding or modifying an entry under `[project.scripts]`.
- After correcting Hatchling build configuration.

Do not provide a command, path, package name, or application argument.
This tool requires no project-specific input other than the optional timeout.

A successful result confirms that:
- the `pyproject.toml` file can be parsed;
- production dependencies can be resolved;
- the project can be built and installed into its uv-managed environment;
- the declared package structure is compatible with the build configuration.

A successful result does not confirm that:
- application behaviour is correct;
- command-line arguments work as intended;
- unit or integration tests pass;
- linting, type checking, coverage, or acceptance criteria pass.

If synchronisation fails because of production code, dependency, build, or
packaging configuration, inspect the returned error, repair the relevant
Coder-owned files, and call this tool again.

Do not use this tool to:
- install development or testing dependencies;
- run Pytest, Ruff, Mypy, coverage, or other verification tools;
- execute the application;
- perform Tester-owned verification.
""".strip()
