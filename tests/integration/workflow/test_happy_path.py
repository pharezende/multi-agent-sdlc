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
from multi_agent_sdlc.agents.tester.model import TesterSummary as _TesterSummary
from multi_agent_sdlc.deployment.models import (
    ApplicationVerificationResult,
    DeploymentResult,
)
from multi_agent_sdlc.tools.shared.models import ProcessResult
from multi_agent_sdlc.workflow.models import (
    DevelopmentStatus,
    PlanReviewDecision,
    PlanReviewStatus,
    ReviewStatus,
    VerificationStatus,
)
from multi_agent_sdlc.workflow.state import build_initial_state


def test_workflow_completes_approved_happy_path(
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
    planner_llm = MagicMock()
    planner_llm.invoke.return_value = development_plan

    coder_llm = MagicMock()
    coder_llm.invoke.return_value = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "submit_coder_summary",
                "args": {"summary": coder_summary.model_dump()},
                "id": "coder-summary",
                "type": "tool_call",
            }
        ],
    )

    tester_responses: Iterator[AIMessage] = iter(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "tester_run_project_verification",
                        "args": {},
                        "id": "project-verification",
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
                        "id": "tester-summary",
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

    execute_process = MagicMock(side_effect=passed_process_results)
    monkeypatch.setattr(tester_execution_module, "execute_process", execute_process)

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
            "thread_id": "happy-path",
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
        "deployer",
    ]
    assert final_state["plan"] == development_plan
    assert final_state["plan_review_status"] == PlanReviewStatus.APPROVED
    assert final_state["current_coder_summary"] == coder_summary
    assert final_state["development_status"] == DevelopmentStatus.COMPLETED
    assert final_state["current_tester_summary"] == tester_summary_passed
    assert final_state["verification_status"] == VerificationStatus.PASSED
    assert final_state["current_reviewer_summary"] == reviewer_summary_passed
    assert final_state["review_status"] == ReviewStatus.PASSED
    assert final_state["deployment_result"] == deployment_result
    assert final_state["deployment_verification"] == deployment_verification
    assert execute_process.call_count == 4
    assert [call.kwargs["command"] for call in execute_process.call_args_list] == project_verification_commands
    deployer.assert_called_once()
    assert deployer.call_args.args[0]["review_status"] == ReviewStatus.PASSED
    update_workflow_project_directory_mock.assert_called_once_with(
        "happy-path",
        str(project_directory),
    )
    assert (project_directory / "development_plan.md").is_file()
