---
title: Multi Agent Sdlc
emoji: 🏢
colorFrom: green
colorTo: red
sdk: static
pinned: false
short_description: Multi-Agent AI application for automating the Software Dev
---

# Multi-Agent SDLC

A sandboxed multi-agent software development workflow built with LangGraph.

The project explores how specialized AI agents can collaborate across the software development lifecycle with deterministic graph-based orchestration, explicit role boundaries, controlled tools, persistent state, automated verification, bounded repair loops, and human approval.

> **Status:** Work in progress. Planner, Coder, Tester, workflow transitions, persistence, and plan review are implemented. Reviewer and Deployer are planned.

## Workflow
![Multi-Agent SDLC Workflow](assets/multi_agent_sdlc_workflow.png)

### Node Categories

**Agent Nodes** — LLM-driven nodes that do the core work
`planner`, `coder`, `tester`, `reviewer` *(WIP)*, `deployer` *(WIP)*

**Preparation Nodes** — assemble context for the following agent node
`prepare_coder_implementation`, `prepare_coder_repair`,
`prepare_tester_run`, `prepare_planner_replan`, `prepare_human_plan_review`

**Human Review** — interrupt nodes that pause execution for external input
`human_plan_review`


| Preparation Node | Feeds |
|---|---|
| `prepare_plan_review` | `human` |
| `prepare_coder_implementation` | `coder` |
| `prepare_coder_repair` | `coder` |
| `prepare_tester` | `tester` |
| `prepare_planner_revision` | `planner` |


### Planner

Creates a structured development plan containing tasks, ownership, dependencies, target files, assumptions, and acceptance criteria.

### Plan Review

The workflow pauses for human approval before implementation.

The plan can be approved, returned for revision, or rejected.

Plan approval can optionally be automated through the CLI.

### Coder

Implements Coder-owned tasks using a restricted tool set.

The Coder can create and modify project files, install allowed dependencies, run development checks, and repair defects reported by the Tester.

Repeated invalid Coder responses are bounded to prevent uncontrolled loops.

### Tester

Independently verifies the implementation against the approved plan.

The Tester can create and run tests, perform linting and type checking, verify builds and entry points, and request Coder repair when production-code defects are found.

## Persistence

The project uses two SQLite databases:

```text
.data/
├── checkpoints.sqlite
└── workflow_runs.sqlite
```

`checkpoints.sqlite` stores LangGraph checkpoints and workflow state.

`workflow_runs.sqlite` stores application-level run metadata such as thread ID, status, request, project directory, and timestamps.

Persisted workflows can be resumed using their thread ID.

## Running

Install dependencies:

```bash
uv sync
```

Start a new workflow:

```bash
uv run multi-agent-sdlc
```

Resume a workflow:

```bash
uv run multi-agent-sdlc --resume <thread-id>
```

Automatically approve plan review:

```bash
uv run multi-agent-sdlc --auto-approve-plan
```

Show CLI options:

```bash
uv run multi-agent-sdlc --help
```
## Implemented

* Planner, Coder, and Tester agents
* Human plan review
* Optional automatic plan approval
* Coder–Tester repair loop
* Restricted tool execution
* Sandboxed project directories
* Persistent LangGraph checkpoints
* Persistent workflow metadata
* Thread-ID-based workflow resume
* Bounded Coder invalid-response handling

## Planned

* Reviewer agent
* Deployer agent
* Additional failure-recovery policies

