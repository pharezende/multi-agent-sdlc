from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver

import multi_agent_sdlc.tools.tester.execution as tester_execution_module
import multi_agent_sdlc.workflow.graph as graph_module
from multi_agent_sdlc.agents.coder.models import CoderSummary
from multi_agent_sdlc.agents.planner.models import DevelopmentPlan
from multi_agent_sdlc.agents.reviewer.models import ReviewerSummary, ReviewFinding
from multi_agent_sdlc.agents.tester.model import TesterSummary as _TesterSummary
from multi_agent_sdlc.deployment.models import (
    ApplicationVerificationResult,
    DeploymentResult,
)
from multi_agent_sdlc.tools.shared.models import ProcessResult
from multi_agent_sdlc.workflow.models import (
    DevelopmentStatus,
    PlanReviewDecision,
    ReviewStatus,
    VerificationStatus,
)
from multi_agent_sdlc.workflow.state import build_initial_state


def test_workflow_repairs_implementation_after_reviewer_request(
    development_plan: DevelopmentPlan,
    coder_summary: CoderSummary,
    tester_summary_passed: _TesterSummary,
    reviewer_summary_passed: ReviewerSummary,
    deployment_result: DeploymentResult,
    deployment_verification: ApplicationVerificationResult,
    project_verification_commands: list[list[str]],
    passed_process_results: list[ProcessResult],
    prepared_project: tuple[Path, MagicMock],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reviewer_summary_repair_required = ReviewerSummary(
        overall_status="repair-required",
        summary="A material input-validation issue must be corrected.",
        findings=[
            ReviewFinding(
                file="src/main.py",
                description="User input is accepted without validation.",
                rationale="Invalid input can produce incorrect application behavior.",
                required_change="Validate input before processing it.",
            )
        ],
    )
    repaired_coder_summary = CoderSummary(
        implementation_summary="Added the required input validation.",
        completed_task_ids=["T1"],
        modified_files=["src/main.py"],
        runtime_dependencies=[],
        entry_points=[],
        executed_operations=["Added validation and ran a focused check."],
        unresolved_issues=[],
        tester_notes=["Retest valid and invalid input handling."],
    )

    planner_llm = MagicMock()
    planner_llm.invoke.return_value = development_plan

    coder_responses: Iterator[AIMessage] = iter(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "submit_coder_summary",
                        "args": {"summary": coder_summary.model_dump()},
                        "id": "initial-coder-summary",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "submit_coder_summary",
                        "args": {"summary": repaired_coder_summary.model_dump()},
                        "id": "repaired-coder-summary",
                        "type": "tool_call",
                    }
                ],
            ),
        ]
    )
    coder_llm = MagicMock()
    coder_llm.invoke.side_effect = coder_responses

    tester_responses: Iterator[AIMessage] = iter(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "tester_run_project_verification",
                        "args": {},
                        "id": "initial-project-verification",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "submit_tester_summary",
                        "args": {"summary": tester_summary_passed.model_dump()},
                        "id": "initial-tester-summary",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "tester_run_project_verification",
                        "args": {},
                        "id": "retest-project-verification",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "submit_tester_summary",
                        "args": {"summary": tester_summary_passed.model_dump()},
                        "id": "retest-summary",
                        "type": "tool_call",
                    }
                ],
            ),
        ]
    )
    tester_llm = MagicMock()
    tester_llm.invoke.side_effect = tester_responses

    reviewer_responses: Iterator[AIMessage] = iter(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "submit_reviewer_summary",
                        "args": {"summary": reviewer_summary_repair_required.model_dump()},
                        "id": "repair-required-review",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "submit_reviewer_summary",
                        "args": {"summary": reviewer_summary_passed.model_dump()},
                        "id": "passed-rereview",
                        "type": "tool_call",
                    }
                ],
            ),
        ]
    )
    reviewer_llm = MagicMock()
    reviewer_llm.invoke.side_effect = reviewer_responses

    monkeypatch.setattr(
        graph_module,
        "create_planner_llm",
        MagicMock(return_value=planner_llm),
    )
    monkeypatch.setattr(
        graph_module,
        "create_coder_llm",
        MagicMock(return_value=coder_llm),
    )
    monkeypatch.setattr(
        graph_module,
        "create_tester_llm",
        MagicMock(return_value=tester_llm),
    )
    monkeypatch.setattr(
        graph_module,
        "create_reviewer_llm",
        MagicMock(return_value=reviewer_llm),
    )

    project_directory, update_workflow_project_directory_mock = prepared_project
    execute_process = MagicMock(
        side_effect=[
            *passed_process_results,
            *passed_process_results,
        ]
    )
    monkeypatch.setattr(
        tester_execution_module,
        "execute_process",
        execute_process,
    )

    deployer = MagicMock(
        return_value={
            "deployment_result": deployment_result,
            "deployment_verification": deployment_verification,
        }
    )
    monkeypatch.setattr(graph_module, "deployer_node", deployer)

    graph = graph_module.build_graph(InMemorySaver())
    config: RunnableConfig = {
        "configurable": {
            "thread_id": "reviewer-repair",
            "plan_review_decision": PlanReviewDecision(decision="approved"),
        }
    }

    updates = list(
        graph.stream(
            build_initial_state("Build a small test application."),
            config,
            stream_mode="updates",
        )
    )
    executed_nodes = [node for update in updates for node in update]
    final_state = graph.get_state(config).values

    assert executed_nodes == [
        "planner",
        "prepare_plan_review",
        "human_plan_review",
        "prepare_coder_implementation",
        "coder",
        "prepare_tester",
        "tester",
        "tester_tools",
        "tester",
        "prepare_reviewer",
        "reviewer",
        "prepare_coder_repair",
        "coder",
        "prepare_tester",
        "tester",
        "tester_tools",
        "tester",
        "prepare_reviewer",
        "reviewer",
        "deployer",
    ]
    assert final_state["development_status"] == DevelopmentStatus.COMPLETED
    assert final_state["verification_status"] == VerificationStatus.PASSED
    assert final_state["review_status"] == ReviewStatus.PASSED
    assert final_state["current_coder_summary"] == repaired_coder_summary
    assert final_state["current_tester_summary"] == tester_summary_passed
    assert final_state["current_reviewer_summary"] == reviewer_summary_passed
    assert [cycle.coder_summary for cycle in final_state["coder_summary_history"]] == [
        coder_summary,
        repaired_coder_summary,
    ]
    assert [cycle.tester_summary for cycle in final_state["tester_summary_history"]] == [
        tester_summary_passed,
        tester_summary_passed,
    ]
    assert [cycle.reviewer_summary for cycle in final_state["reviewer_summary_history"]] == [
        reviewer_summary_repair_required,
        reviewer_summary_passed,
    ]
    assert final_state["deployment_result"] == deployment_result
    assert final_state["deployment_verification"] == deployment_verification
    assert execute_process.call_count == 8
    assert [call.kwargs["command"] for call in execute_process.call_args_list] == [
        *project_verification_commands,
        *project_verification_commands,
    ]
    deployer.assert_called_once()
    assert deployer.call_args.args[0]["review_status"] == ReviewStatus.PASSED
    update_workflow_project_directory_mock.assert_called_once_with(
        "reviewer-repair",
        str(project_directory),
    )
