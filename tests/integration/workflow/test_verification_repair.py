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
from multi_agent_sdlc.agents.reviewer.models import ReviewerSummary
from multi_agent_sdlc.agents.tester.model import (
    AcceptanceCriterionResult,
    CoderRepairRequest,
    ImplementationFailure,
    VerificationResult,
    VerificationType,
)
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


def test_workflow_repairs_implementation_after_failed_verification(
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
    tester_summary_repair_required = _TesterSummary(
        addressed_task_ids=["T2"],
        passed_task_ids=[],
        related_task_ids=["T1"],
        files_created_or_modified=["tests/test_main.py"],
        development_dependencies_added=[],
        verification_results=[
            VerificationResult(
                verification_type=VerificationType.COMPLETE_PROJECT_VERIFICATION,
                status="failed",
                exit_code=1,
                summary="The application test failed.",
                verified_task_ids=["T1"],
            )
        ],
        acceptance_criteria_results=[
            AcceptanceCriterionResult(
                task_id="T1",
                criterion="The application runs successfully.",
                status="failed",
                evidence="The application test exited with status 1.",
            )
        ],
        tester_repairs=[],
        implementation_failures=[
            ImplementationFailure(
                description="The application returns the wrong result.",
                related_task_ids=["T1"],
                evidence="The application test exited with status 1.",
            )
        ],
        unresolved_issues=[],
        overall_status="repair-required",
        coder_repair_requests=[
            CoderRepairRequest(
                related_task_ids=["T1"],
                affected_files=["src/main.py"],
                failed_criteria=["The application runs successfully."],
                observed_behavior="The application returns the wrong result.",
                expected_behavior="The application returns the expected result.",
                evidence="The application test exited with status 1.",
            )
        ],
    )
    repaired_coder_summary = CoderSummary(
        implementation_summary="Corrected the application result.",
        completed_task_ids=["T1"],
        modified_files=["src/main.py"],
        runtime_dependencies=[],
        entry_points=[],
        executed_operations=["Corrected the application and ran a focused check."],
        unresolved_issues=[],
        tester_notes=["Retest the previously failing application behavior."],
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
                        "id": "failed-project-verification",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "submit_tester_summary",
                        "args": {"summary": tester_summary_repair_required.model_dump()},
                        "id": "repair-required-summary",
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
                        "id": "passed-project-verification",
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
                        "id": "passed-tester-summary",
                        "type": "tool_call",
                    }
                ],
            ),
        ]
    )
    tester_llm = MagicMock()
    tester_llm.invoke.side_effect = tester_responses

    reviewer_llm = MagicMock()
    reviewer_llm.invoke.return_value = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "submit_reviewer_summary",
                "args": {"summary": reviewer_summary_passed.model_dump()},
                "id": "reviewer-summary",
                "type": "tool_call",
            }
        ],
    )

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
    failed_process_result = ProcessResult(
        command=project_verification_commands[-1],
        exit_code=1,
        stdout="",
        stderr="application test failed",
        timed_out=False,
    )
    execute_process = MagicMock(
        side_effect=[
            *passed_process_results[:3],
            failed_process_result,
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
            "thread_id": "verification-repair",
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
        tester_summary_repair_required,
        tester_summary_passed,
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
        "verification-repair",
        str(project_directory),
    )
