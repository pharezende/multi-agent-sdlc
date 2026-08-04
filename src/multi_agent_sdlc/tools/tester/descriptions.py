WRITE_TEST_FILE_DESCRIPTION = """
Create or replace a Tester-owned file inside the current project.

Permitted files include:
- automated tests;
- test fixtures, mocks, helpers, and test data;
- verification configuration for Pytest, Ruff, Mypy, and coverage;
- development-tool configuration required by Tester-owned tasks.

Path rules:
- `path` must be relative to the current project root.
- Do not include `sandbox/`, the project name, or an absolute path.
- Do not use `..`.

Correct examples:
- tests/test_calculator.py
- tests/conftest.py
- tests/fixtures/expressions.json
- pytest.ini
- ruff.toml
- mypy.ini
- .coveragerc

Incorrect examples:
- sandbox/terminal-calculator/tests/test_calculator.py
- /absolute/path/test_calculator.py
- ../other-project/test_calculator.py
- src/calculator/main.py

When writing a test file, provide valid UTF-8 source content with actual
newline characters. Do not emit escaped newline text, flattened source code,
or stringified file contents.

Production boundary:
- Do not create or modify production source files.
- Do not change application behaviour to make verification pass.
- Do not modify runtime dependencies, build configuration, or application entry
  points unless the approved plan explicitly assigns that work to the Tester.
- `pyproject.toml` may be modified only for Tester-owned development
  dependencies or verification-tool configuration.
- Production implementation and repair belong to the Coder.
- Do not retry rejected production work using another path, tool, or mechanism.

Python project requirements:
- Use `pyproject.toml` or an established project-specific configuration file for
  verification tooling.
- Generated verification instructions must use `uv`.
- Do not generate `pip install`, `python -m pip`, manual virtual-environment
  activation, or direct tool execution outside `uv run`.
""".strip()


CREATE_TEST_DIRECTORY_DESCRIPTION = """
Create a Tester-owned directory inside the current project.

Use this tool for test suites, fixtures, mocks, test data, and other
verification assets.

Path rules:
- `path` must be relative to the current project root.
- Do not include `sandbox/`, the project name, or an absolute path.
- Do not use `..`.

Correct examples:
- tests
- tests/unit
- tests/integration
- tests/fixtures
- specs

Incorrect examples:
- sandbox/terminal-calculator/tests
- /absolute/path/tests
- ../other-project/tests
- src
- src/calculator
- config

Production boundary:
- Do not create production source, package, runtime-configuration, deployment,
  or application-data directories.
- Directory creation must support Tester-owned verification work.
- Production directory creation belongs to the Coder.

This tool uses Python filesystem operations directly. It does not run `mkdir`,
shell commands, Python snippets, or project-management commands.
""".strip()


RUN_APPLICATION_DESCRIPTION = """
Run a declared project application entry point inside the project's uv-managed
environment for smoke or acceptance verification.

The tool internally executes:

    uv run <entry_point> [arguments]

The Tester provides only:
- an entry-point name declared in `[project.scripts]` in `pyproject.toml`;
- optional application arguments.

Correct examples:
- entry_point="calc", arguments=[]
- entry_point="calc", arguments=["2 + 3"]
- entry_point="odd-even", arguments=["7"]
- entry_point="my-app", arguments=["--help"]

Important uv rules:
- Do not include `uv run` in `entry_point`.
- Do not activate `.venv` manually.
- Do not use `python`, `pip`, `uv pip`, shell commands, or absolute paths.
- The tool runs from the current project root, so `uv` discovers
  `pyproject.toml` and uses the project's managed environment.
- Use this tool instead of requesting a generic shell command.

Verification boundary:
- Use this tool to verify declared application behaviour, command-line
  interfaces, argument handling, exit status, and focused acceptance criteria.
- Record the observed output and exit status without assuming success.
- Do not use this tool to execute Pytest, Ruff, Mypy, coverage, build tools, or
  shell scripts when a dedicated verification tool is available.
- Do not perform destructive, deployment, publishing, or irreversible
  operations.
- If valid execution exposes a production defect, report it instead of
  modifying production files.
""".strip()


RUN_PYTHON_MODULE_DESCRIPTION = """
Run an application module inside the project's uv-managed environment for
focused smoke or acceptance verification.

The tool internally executes:

    uv run python -m <module> [arguments]

The Tester provides only:
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
- module="coverage"
- module="pip"
- module="-c"

Important uv rules:
- Do not include `uv run python -m` in `module`.
- Do not provide a file path or Python source code.
- Do not activate `.venv` manually.
- Do not use direct `python`, `pip`, `uv pip`, or shell commands.
- `uv` executes the module inside the current project's managed environment.

Verification boundary:
- Use this tool only to verify importable application modules.
- Use dedicated tools for tests, linting, type checking, coverage, build, and
  packaging verification.
- Do not use this tool to create or execute temporary verification scripts.
- If execution exposes a valid production failure, preserve the evidence and
  report it without modifying production code.
""".strip()


INSTALL_VERIFICATION_DEPENDENCIES_DESCRIPTION = """
Add required development and verification dependencies to the current project
using `uv`.

The tool internally executes:

    uv add --dev <package> [<package> ...]

`uv add --dev`:
- records dependencies as development dependencies in `pyproject.toml`;
- updates `uv.lock`;
- synchronises the project's uv-managed environment.

Provide only dependencies required for Tester-owned verification work.

Correct examples:
- ["pytest"]
- ["pytest", "pytest-cov"]
- ["ruff"]
- ["mypy"]
- ["hypothesis>=6"]
- ["coverage[toml]>=7"]

Incorrect examples:
- ["uv", "add", "--dev", "pytest"]
- ["pip install pytest"]
- ["--dev", "pytest"]
- ["requests"]
- ["fastapi"]
- ["git+https://example.com/repository.git"]
- ["package @ https://example.com/package.whl"]

Important uv rules:
- Do not use `pip`, `python -m pip`, or `uv pip install`.
- Do not manually edit or activate `.venv`.
- Use this tool only when an approved Tester-owned task genuinely requires an
  external development or verification dependency.
- Do not add packages already provided by the Python standard library.
- Do not add direct URL, Version Control System, SSH, or local-file
  dependencies.

Production boundary:
- Do not add or change production runtime dependencies.
- Do not use this tool to repair missing application dependencies.
- If verification reveals a missing runtime dependency, report it as a
  Coder-owned implementation issue.
""".strip()


SYNC_PROJECT_DESCRIPTION = """
Synchronise the Python project and verify that its declared environment can be
created using uv.

The tool internally executes:

    uv sync

Use this tool after:
- adding or changing development dependencies;
- modifying Tester-owned verification configuration;
- repairing a development-dependency synchronization failure;
- receiving a project from the Coder before executing verification;
- an earlier `uv sync` operation failed.

Do not provide a command, path, package name, or application argument.
This tool requires no project-specific input other than the optional timeout.

A successful result confirms that:
- `pyproject.toml` can be parsed;
- declared dependencies can be resolved;
- the project can be installed into its uv-managed environment;
- the declared package structure is compatible with the build configuration.

A successful result does not confirm that:
- application behaviour is correct;
- acceptance criteria pass;
- tests pass;
- linting or type checking passes;
- coverage requirements are satisfied;
- packaging or application entry points work correctly.

Failure handling:
- If synchronization fails because of a Tester-owned development dependency or
  verification configuration, repair that Tester-owned issue and run the tool
  again.
- If synchronization fails because of production dependencies, package
  structure, build configuration, or other Coder-owned files, preserve the
  failure evidence and report it without modifying production files.

Do not use this tool to:
- add dependencies;
- run tests, linting, type checking, or coverage;
- execute the application;
- modify production configuration;
- claim that acceptance verification succeeded.
""".strip()


SUBMIT_TESTER_SUMMARY_DESCRIPTION = """
Submit the final structured handoff summary for the Tester stage.

Call this tool only when:
- all safe Tester-owned tasks and verification operations are complete; or
- no further safe verification work can continue because of a genuine blocker.

This is a terminal Tester action. Call it alone. After calling it, do not
request additional filesystem, dependency, synchronization, test, analysis,
build, packaging, or application-execution operations.

Populate the summary only with evidence from:
- Tester-owned tasks and acceptance criteria in the approved DevelopmentPlan;
- repository inspection;
- the Coder handoff;
- Tester-owned files actually created or modified;
- development-dependency operations;
- synchronization, test, linting, type-checking, coverage, build, packaging,
  smoke, and acceptance-verification results;
- observed failures and blockers.

The summary must:
- identify completed Tester-owned task IDs;
- list project-relative Tester-owned files created or modified;
- list development dependencies actually added or changed;
- record only verification operations that were actually executed;
- distinguish passed, failed, blocked, and not-executed verification;
- identify acceptance criteria that were independently verified;
- report valid production failures without claiming they were repaired;
- identify Tester-owned repairs and their subsequent verification results;
- identify unresolved failures, blockers, and verification limitations;
- provide concise handoff notes for the Reviewer.

Do not:
- call this tool while more safe Tester-owned work remains;
- call it together with another tool;
- include production implementation as completed Tester work;
- modify or conceal production failures;
- claim that unexecuted verification succeeded;
- claim that review, approval, merge, deployment, or release succeeded;
- invent files, dependencies, commands, task completion, acceptance results, or
  successful outcomes;
- return the final summary as ordinary text or Markdown instead of calling this
  tool.
""".strip()


TESTER_RUN_VERIFICATION_COMMAND_DESCRIPTION = """
Run an approved Tester verification command inside the current project's
uv-managed environment.

The tool internally executes:

```
uv run <command> [arguments]
```

Approved commands:

* `pytest` for executing tests;
* `ruff` for linting and formatting checks;
* `mypy` for static type checking;
* `coverage` for test coverage operations.

Examples:

* command="pytest", arguments=["-q"]
* command="ruff", arguments=["check", "."]
* command="ruff", arguments=["format", "--check", "."]
* command="mypy", arguments=["src"]
* command="coverage", arguments=["run", "-m", "pytest"]
* command="coverage", arguments=["report", "--show-missing"]

Rules:

* Use only an approved command.
* Do not include `uv run` in the command or arguments.
* Do not execute Python, shell commands, arbitrary executables, application
  entry points, or temporary scripts.
* Ruff may only perform non-mutating checks. Do not use `--fix`,
  `--unsafe-fixes`, or `ruff format` without `--check`.
* Coverage may execute only Pytest through `coverage run -m pytest`.
* Do not install dependencies or modify the environment.
* Do not weaken tests, assertions, linting rules, type-checking rules, or
  coverage thresholds to obtain a passing result.
* Repair failures only when they originate from Tester-owned files or
  verification configuration.
* Report valid production failures as focused Coder repair requests.
* Record the command, arguments, exit status, output, and observed result.
* Treat returned results as authoritative Tester-stage verification evidence.
  """.strip()

TESTER_RUN_PROJECT_VERIFICATION_DESCRIPTION = """
Run the complete mandatory project verification suite inside the current
project's uv-managed environment.

The tool executes these fixed checks:

    uv run ruff check .
    uv run ruff format --check .
    uv run mypy src
    uv run pytest

All checks are attempted, even when an earlier check fails. The result includes
the command, exit code, timeout status, standard output, and standard error for
each check, together with an overall pass or fail result.

Use this tool as the authoritative final verification gate before submitting a
Tester summary with `overall_status="passed"`.

Rules:
- Run this tool after implementing or repairing Tester-owned tests and
  verification configuration.
- Run it again after any change that could affect verification results.
- A successful targeted test or individual verification command does not
  replace this complete project verification.
- Do not report `passed` unless the latest complete project verification
  finished without timeouts and every mandatory check returned exit code 0.
- When a check fails, inspect its full result to determine whether the failure
  originates from production code, Tester-owned files, verification
  configuration, dependencies, or the execution environment.
- Repair failures only when they originate from Tester-owned tests or
  verification configuration.
- Report valid production-code failures through focused Coder repair requests.
- Report an external or unresolvable verification obstacle as `blocked`.
- Do not weaken tests, assertions, linting rules, formatting rules,
  type-checking rules, or project configuration merely to obtain a passing
  result.
- Do not install dependencies, modify the environment, or execute arbitrary
  commands through this tool.
""".strip()
