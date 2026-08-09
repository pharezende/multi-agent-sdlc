from enum import StrEnum

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4


WORKFLOW_RUNS_DATABASE_PATH = Path(".data/workflow_runs.sqlite")


class WorkflowRunStatus(StrEnum):
    RUNNING = "running"
    INTERRUPTED = "interrupted"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class WorkflowRun:
    thread_id: str
    status: str
    request: str
    project_directory: str | None
    created_at: str
    updated_at: str
    completed_at: str | None


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _connect() -> sqlite3.Connection:
    WORKFLOW_RUNS_DATABASE_PATH.parent.mkdir(
        exist_ok=True,
    )

    connection = sqlite3.connect(WORKFLOW_RUNS_DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_workflow_runs_database() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS workflow_runs (
                thread_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                request TEXT NOT NULL,
                project_directory TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT
            )
            """
        )


def create_workflow_run(
    request: str,
    status: str = "running",
) -> WorkflowRun:
    thread_id = str(uuid4())
    now = _utc_now()

    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO workflow_runs (
                thread_id,
                status,
                request,
                project_directory,
                created_at,
                updated_at,
                completed_at
            )
            VALUES (?, ?, ?, NULL, ?, ?, NULL)
            """,
            (
                thread_id,
                status,
                request,
                now,
                now,
            ),
        )

    return WorkflowRun(
        thread_id=thread_id,
        status=status,
        request=request,
        project_directory=None,
        created_at=now,
        updated_at=now,
        completed_at=None,
    )


def get_workflow_run(
    thread_id: str,
) -> WorkflowRun | None:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT
                thread_id,
                status,
                request,
                project_directory,
                created_at,
                updated_at,
                completed_at
            FROM workflow_runs
            WHERE thread_id = ?
            """,
            (thread_id,),
        ).fetchone()

    if row is None:
        return None

    return _row_to_workflow_run(row)


def list_workflow_runs() -> list[WorkflowRun]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT
                thread_id,
                status,
                request,
                project_directory,
                created_at,
                updated_at,
                completed_at
            FROM workflow_runs
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [_row_to_workflow_run(row) for row in rows]


def update_workflow_run_status(
    thread_id: str,
    status: str,
    *,
    completed: bool = False,
) -> None:
    now = _utc_now()
    completed_at = now if completed else None

    with _connect() as connection:
        cursor = connection.execute(
            """
            UPDATE workflow_runs
            SET
                status = ?,
                updated_at = ?,
                completed_at = ?
            WHERE thread_id = ?
            """,
            (
                status,
                now,
                completed_at,
                thread_id,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError(f"Workflow run not found: {thread_id}")


def update_workflow_project_directory(
    thread_id: str,
    project_directory: str,
) -> None:
    now = _utc_now()

    with _connect() as connection:
        cursor = connection.execute(
            """
            UPDATE workflow_runs
            SET
                project_directory = ?,
                updated_at = ?
            WHERE thread_id = ?
            """,
            (
                project_directory,
                now,
                thread_id,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError(f"Workflow run not found: {thread_id}")


def _row_to_workflow_run(
    row: sqlite3.Row,
) -> WorkflowRun:
    return WorkflowRun(
        thread_id=row["thread_id"],
        status=row["status"],
        request=row["request"],
        project_directory=row["project_directory"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        completed_at=row["completed_at"],
    )


def get_resumable_workflow_run(
    thread_id: str,
) -> WorkflowRun:
    workflow_run = get_workflow_run(thread_id)

    if workflow_run is None:
        raise ValueError(f"Workflow run not found: {thread_id}")

    if workflow_run.status is WorkflowRunStatus.COMPLETED:
        raise ValueError(
            f"Workflow run {thread_id} cannot be resumed because its "
            "completed already."
        )

    return workflow_run
