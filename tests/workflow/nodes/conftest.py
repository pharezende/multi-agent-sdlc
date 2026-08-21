import pytest

from multi_agent_sdlc.agents.tester.model import TesterSummary as _TesterSummary


@pytest.fixture
def tester_summary() -> _TesterSummary:
    return _TesterSummary(
        addressed_task_ids=["T2"],
        passed_task_ids=[],
        related_task_ids=["T1"],
        files_created_or_modified=[],
        development_dependencies_added=[],
        verification_results=[],
        acceptance_criteria_results=[],
        tester_repairs=[],
        implementation_failures=[],
        unresolved_issues=[],
        overall_status="blocked",
        coder_repair_requests=[],
    )
