LIST_FILES_DESCRIPTION = """
List files and directories inside the current project.

Path rules:

* `path` must be relative to the current project root.
* Use `.` to list the project root.
* Do not include `sandbox/`, the project name, or an absolute path.
* Do not use `..`.

Correct examples:

* .
* src
* src/calculator
* config

Incorrect examples:

* sandbox/terminal-calculator
* /home/user/project
* ../other-project

Use this tool to inspect the project structure before implementation, repair,
configuration, or preliminary quality verification.

This tool only inspects the filesystem. It does not execute shell commands or
modify files.
""".strip()

READ_FILE_DESCRIPTION = """
Read a UTF-8 text file inside the current project.

Path rules:

* `path` must be relative to the current project root.
* Do not include `sandbox/`, the project name, or an absolute path.
* Do not use `..`.

Correct examples:

* pyproject.toml
* README.md
* src/calculator/main.py
* ruff.toml
* mypy.ini
* .coveragerc

Incorrect examples:

* sandbox/terminal-calculator/pyproject.toml
* /home/user/project/main.py
* ../other-project/main.py

Use this tool to inspect:

* existing production files;
* project metadata and packaging configuration;
* application entry points;
* existing quality-tool configuration;
* relevant existing tests when needed to understand a reported failure.

Reading a test file does not authorise the Coder to modify it.

This tool only reads files. It does not modify project contents.
""".strip()

WRITE_FILE_DESCRIPTION = """
Create or replace a Coder-owned file inside the current project.

Permitted files include:

* production source code;
* production configuration;
* project metadata and packaging configuration;
* application entry points;
* documentation;
* Coder-owned linting, formatting, static-type-checking, coverage, build, and
  packaging configuration.

Path rules:

* `path` must be relative to the current project root.
* Do not include `sandbox/`, the project name, or an absolute path.
* Do not use `..`.

Correct examples:

* pyproject.toml
* README.md
* src/calculator/**init**.py
* src/calculator/main.py
* ruff.toml
* mypy.ini
* .coveragerc

Incorrect examples:

* sandbox/terminal-calculator/src/calculator/main.py
* /absolute/path/main.py
* ../other-project/main.py
* tests/test_calculator.py
* tests/conftest.py

Test ownership boundary:

* Do not create, modify, rename, or delete automated tests.
* Do not create or modify fixtures, mocks, test data, test helpers, or other
  Tester-owned assets.
* Do not modify files under `test`, `tests`, `__tests__`, `spec`, or `specs`.
* Existing tests may be inspected, but test implementation belongs exclusively
  to the Tester.
* Do not modify valid tests to make production code appear correct.
* Do not retry rejected test work using another path, tool, or mechanism.

Quality-configuration boundary:

* Preserve existing quality configuration whenever possible.
* Add or modify quality-tool configuration only when necessary for preliminary
  Coder-side verification or an approved production task.
* Do not broadly disable linting or type-checking rules.
* Do not add unjustified ignores, exclusions, or type suppressions.
* Do not reduce coverage thresholds merely to obtain a successful result.
* Do not weaken approved acceptance criteria.

Python project requirements:

* Use `pyproject.toml` for project metadata and dependency declarations.
* Preserve established project-specific configuration files when they exist.
* Generated setup, quality-check, and application-execution instructions must
  use `uv`.
* Do not document or generate `pip install`, `python -m pip`, `uv pip`, manual
  virtual-environment activation, or direct modification of `.venv`.
* Application execution instructions should use `uv run`.
  """.strip()

CREATE_DIRECTORY_DESCRIPTION = """
Create a Coder-owned directory inside the current project.

Permitted directories include:

* production source packages;
* production configuration;
* application resources;
* documentation;
* directories required by Coder-owned build, packaging, or quality-tool
  configuration.

Path rules:

* `path` must be relative to the current project root.
* Do not include `sandbox/`, the project name, or an absolute path.
* Do not use `..`.

Correct examples:

* src
* src/calculator
* config
* docs

Incorrect examples:

* sandbox/terminal-calculator/src
* /absolute/path
* ../other-project
* tests
* src/tests
* tests/fixtures

Test ownership boundary:

* Do not create `test`, `tests`, `__tests__`, `spec`, or `specs` directories.
* Do not create fixture, mock, test-data, or Tester-owned verification
  directories.
* Test-directory creation belongs exclusively to the Tester.

This tool uses Python filesystem operations directly. It does not run `mkdir`,
shell commands, Python snippets, or project-management commands.
""".strip()

RUN_APPLICATION_DESCRIPTION = """
Run a declared project application entry point inside the current project's
uv-managed environment.

The tool internally executes:

```
uv run <entry_point> [arguments]
```

The Coder provides only:

* an entry-point name declared in `[project.scripts]` in `pyproject.toml`;
* optional application arguments.

Correct examples:

* entry_point="calc", arguments=[]
* entry_point="calc", arguments=["2 + 3"]
* entry_point="odd-even", arguments=["7"]
* entry_point="my-app", arguments=["--help"]

Important uv rules:

* Do not include `uv run` in `entry_point`.
* Do not activate `.venv` manually.
* Do not use `python`, `pytest`, `pip`, `uv pip`, shell commands, or absolute
  paths.
* The tool runs from the current project root, allowing `uv` to discover
  `pyproject.toml` and use the project's managed environment.
* Use this tool instead of requesting a generic shell command.

Permitted use:

* direct application execution;
* focused smoke checks;
* command-line-interface checks;
* argument-handling checks;
* preliminary application-behaviour checks;
* reproduction of a Tester-reported application failure.

Boundaries:

* Do not use this tool to execute Pytest or another test runner.
* Do not use it to execute Ruff, Mypy, Coverage, build tools, packaging tools,
  shell scripts, or arbitrary executables.
* Do not simulate interactive input through temporary subprocess scripts.
* Record the observed output and exit status.
* Repair failures only when they originate from Coder-owned production
  artefacts.
* Do not treat successful Coder-side execution as independent acceptance.
* The Tester must independently verify applicable behaviour and acceptance
  criteria.
  """.strip()

RUN_PYTHON_MODULE_DESCRIPTION = """
Run an importable application module inside the current project's uv-managed
environment.

The tool internally executes:

```
uv run python -m <module> [arguments]
```

The Coder provides only:

* an importable application module name;
* optional application arguments.

Correct examples:

* module="calculator"
* module="calculator.cli"
* module="odd_even"
* module="customer_support.main"

Incorrect examples:

* module="src/calculator/main.py"
* module="python -m calculator"
* module="pytest"
* module="unittest"
* module="coverage"
* module="ruff"
* module="mypy"
* module="pip"
* module="-c"

Important uv rules:

* Do not include `uv run python -m` in `module`.
* Do not provide a file path or Python source code.
* Do not activate `.venv` manually.
* Do not use direct `python`, `pytest`, `pip`, `uv pip`, or shell commands.
* `uv` executes the module inside the current project's managed environment.

Permitted use:

* execute importable application modules;
* perform focused application smoke checks;
* reproduce application-module failures reported by the Tester.

Boundaries:

* This tool cannot execute testing, linting, formatting, type-checking,
  coverage, build, packaging, or environment-management modules.
* Do not use it to execute Pytest, unittest, Coverage, Ruff, Mypy, or another
  verification framework.
* Do not use it to create or execute temporary verification scripts.
* Record observed failures accurately.
* Repair failures only when they originate from Coder-owned artefacts.
* Successful execution remains preliminary and must not be represented as
  independent Tester verification.
  """.strip()

INSTALL_RUNTIME_DEPENDENCIES_DESCRIPTION = """
Add required production runtime dependencies to the current project using `uv`.

The tool internally executes:

```
uv add <package> [<package> ...]
```

`uv add`:

* records dependencies in `project.dependencies` in `pyproject.toml`;
* updates `uv.lock`;
* synchronises the project's uv-managed environment.

Provide only runtime dependency specifications.

Correct examples:

* ["click"]
* ["requests>=2.32"]
* ["pydantic>=2"]
* ["fastapi", "uvicorn"]

Incorrect examples:

* ["uv", "add", "click"]
* ["pip install click"]
* ["--dev", "ruff"]
* ["pytest"]
* ["ruff"]
* ["mypy"]
* ["coverage"]
* ["git+https://example.com/repository.git"]
* ["package @ https://example.com/package.whl"]

Important rules:

* Do not use `pip`, `python -m pip`, or `uv pip install`.
* Do not manually edit or activate `.venv`.
* Use this tool only when the production application genuinely requires an
  external runtime dependency.
* Do not add packages already provided by the Python standard library.
* Do not add direct URL, Version Control System, SSH, or local-file
  dependencies.
* Do not add linting, formatting, type-checking, coverage, testing, build, or
  other development dependencies with this tool.
* Record every runtime dependency actually added or changed.
  """.strip()

INSTALL_DEVELOPMENT_DEPENDENCIES_DESCRIPTION = """
Add required Coder-side quality and development dependencies to the current
project using `uv`.

The tool internally executes:

```
uv add --dev <package> [<package> ...]
```

`uv add --dev`:

* records dependencies as development dependencies in `pyproject.toml`;
* updates `uv.lock`;
* synchronises the project's uv-managed environment.

Use this tool only for dependencies required to perform approved preliminary
Coder-side operations such as:

* linting and formatting with Ruff;
* static type checking with Mypy;
* coverage reporting or analysis;
* build and packaging validation when supported by an approved Coder tool.

Correct examples:

* ["ruff"]
* ["mypy"]
* ["coverage[toml]>=7"]
* ["build"]

Incorrect examples:

* ["uv", "add", "--dev", "ruff"]
* ["pip install ruff"]
* ["--dev", "mypy"]
* ["pytest"]
* ["pytest-cov"]
* ["requests"]
* ["fastapi"]
* ["git+https://example.com/repository.git"]
* ["package @ https://example.com/package.whl"]

Important rules:

* Pytest and other test runners are not Coder-owned dependencies.
* Do not add Pytest, pytest-cov, Hypothesis, Tox, Nox, or other Tester-owned
  testing dependencies.
* Do not use `pip`, `python -m pip`, or `uv pip install`.
* Do not manually edit or activate `.venv`.
* Reuse existing development dependencies whenever possible.
* Add only dependencies genuinely required for approved Coder-side quality
  operations.
* Do not add direct URL, Version Control System, SSH, or local-file
  dependencies.
* Do not add a production requirement as a development dependency.
* Record every development dependency added and explain why it was necessary.

Coder-side quality results remain preliminary. The Tester must independently
execute the applicable checks before the workflow proceeds to review.
""".strip()

RUN_SYNC_PROJECT = """
Synchronise the current Python project and validate its declared environment
using uv.

The tool internally executes:

```
uv sync
```

Use this tool after:

* creating or materially modifying `pyproject.toml`;
* adding or changing runtime dependencies;
* adding or changing approved development dependencies;
* changing the package structure;
* changing build-system or packaging configuration;
* changing application entry points;
* changing quality-tool configuration that affects synchronisation;
* repairing an earlier `uv sync` failure.

Correct usage examples:

* After creating a new `pyproject.toml`.
* After adding `click` to `[project.dependencies]`.
* After adding Ruff or Mypy as an approved development dependency.
* After changing the package path from `src/app` to `src/my_app`.
* After adding or modifying an entry under `[project.scripts]`.
* After correcting Hatchling build configuration.

Do not provide a command, path, package name, or application argument.
This tool requires no project-specific input other than the optional timeout.

A successful result confirms that:

* `pyproject.toml` can be parsed;
* declared runtime and development dependencies can be resolved;
* the project can be built and installed into its uv-managed environment;
* the declared package structure is compatible with the build configuration.

A successful result does not confirm that:

* application behaviour is correct;
* command-line arguments work as intended;
* tests pass;
* linting or formatting passes;
* static type checking passes;
* coverage requirements are satisfied;
* acceptance criteria pass;
* independent Tester verification has succeeded.

If synchronisation fails because of Coder-owned source, dependencies, package
structure, build configuration, entry points, or quality-tool configuration,
inspect the returned error, repair the relevant Coder-owned files, and run this
tool again.

Do not use this tool to:

* add dependencies;
* execute Pytest or another test runner;
* execute Ruff, Mypy, Coverage, or other quality tools;
* execute the application;
* claim that independent verification succeeded.
  """.strip()

RUN_VERIFICATION_COMMAND_DESCRIPTION = """
Run an approved Coder-side quality command inside the current project's
uv-managed environment.

The tool internally executes:

```
uv run <command> [arguments]
```

Approved commands:

* `ruff` for linting, formatting checks, safe automatic fixes, and formatting;
* `mypy` for static type checking;
* `coverage` for coverage reporting and analysis.

The Coder may use this tool during initial implementation and repair cycles to
detect and address problems in Coder-owned production code, production
configuration, dependency declarations, packaging metadata, or application
entry points.

Ruff permissions:

* `ruff check` is permitted.
* `ruff check --fix` is permitted for safe automatic fixes.
* `ruff check --diff` is permitted.
* `ruff format` is permitted.
* `ruff format --check` is permitted.
* `--unsafe-fixes` is prohibited.
* Automatic fixes and formatting must target only Coder-owned files.
* Do not run automatic fixes against test directories or Tester-owned files.
* After applying fixes or formatting, rerun the relevant Ruff check.
* Rerun Mypy or applicable application smoke checks when Ruff changes could
  affect application behaviour or interfaces.

Mypy permissions:

* Run Mypy only against Coder-owned production modules or approved production
  paths.
* Fix valid type errors in production artefacts.
* Preserve existing type-checking configuration.
* Do not suppress valid errors through blanket ignores, broad exclusions, or
  unjustified annotations.
* Do not run Mypy against Tester-owned files for the purpose of modifying them.

Coverage permissions:

* Coverage may be used for reporting, combining, inspecting, exporting, or
  analysing existing coverage data.
* Coverage may execute an approved application module only when needed to
  measure production application execution.
* Do not use Coverage to invoke Pytest, unittest, another test runner, an
  arbitrary Python file, inline Python, or a temporary verification script.
* Do not lower coverage thresholds.
* Do not omit production modules merely to improve the reported percentage.
* Do not create or modify tests to increase coverage.
* When additional tests are required, report the gap to the Tester.

Prohibited commands:

* `pytest`;
* `python`;
* `python3`;
* `unittest`;
* `tox`;
* `nox`;
* shell interpreters;
* arbitrary executables.

Command boundaries:

* Pytest cannot be used through this tool.
* Direct Python execution cannot be used through this tool.
* Existing tests and authoritative test execution belong exclusively to the
  Tester.
* Application entry points must be executed with `run_application`.
* Importable application modules must normally be executed with
  `run_python_module`.
* Do not use an approved command as a wrapper for a prohibited command.
* Do not use `coverage run` to bypass the prohibition against Pytest, arbitrary
  Python scripts, or inline Python.
* Do not include `uv run` in `command`.

General rules:

* Use only an approved command.
* Do not execute shell commands, arbitrary executables, external scripts,
  temporary scripts, or inline Python.
* Do not create, modify, rename, or delete valid tests or Tester-owned files.
* Do not weaken linting rules, type-checking rules, coverage thresholds, or
  approved acceptance criteria merely to obtain a successful result.
* Fix valid findings when they originate from Coder-owned production artefacts.
* Record the exact command, arguments, exit status, and observed result.
* Treat successful results as preliminary Coder-side quality evidence.
* The Tester must independently rerun the applicable checks before the
  workflow proceeds to review.
  """.strip()

SUBMIT_CODER_SUMMARY_DESCRIPTION = """
Submit the final structured handoff summary for the current Coder implementation
or repair cycle.

Call this tool only when:

* all safe Coder-owned implementation and preliminary quality work for the
  current cycle is complete; or
* no further safe work can continue because of a genuine blocker.

This is a terminal Coder action. Call it alone.

After calling it, do not request additional:

* filesystem operations;
* dependency operations;
* project synchronisation;
* application or module execution;
* Ruff, Mypy, Coverage, build, or packaging operations.

Populate the summary only with evidence from:

* Coder-owned tasks in the approved DevelopmentPlan;
* the current Tester repair requests when operating in repair mode;
* successful filesystem operations;
* runtime and approved development-dependency operations;
* project-synchronisation results;
* application or module execution results;
* Coder-executed Ruff, Mypy, Coverage, build, or packaging operations;
* observed failures and blockers.

The summary must:

* identify completed Coder-owned task IDs;
* list project-relative Coder-owned files created or modified;
* list runtime dependencies actually added or changed;
* list approved development dependencies actually added or changed;
* list command-line entry points actually configured;
* record only operations that were actually executed;
* record the observed outcome of every reported operation;
* distinguish successful Coder-side quality checks from independent Tester
  verification;
* identify unresolved failures, blockers, uncertainties, and incomplete work;
* identify Tester repair requests addressed during a repair cycle;
* provide concise `tester_notes` describing checks, coverage gaps, behaviours,
  and acceptance criteria requiring independent verification or
  re-verification.

Do not:

* call this tool while more safe Coder-owned work remains;
* call it together with another tool;
* include test files or Tester-owned work as completed Coder work;
* claim that Pytest or another Tester-owned test runner was executed;
* claim that automated tests passed during the Coder stage;
* claim that independent Tester verification, review, human approval, merge,
  deployment, publishing, or release succeeded;
* claim that an operation succeeded without a supporting tool result;
* invent files, dependencies, commands, task completion, verification results,
  or successful outcomes;
* return the final summary as ordinary text, JSON, or Markdown instead of
  calling this tool.
  """.strip()
