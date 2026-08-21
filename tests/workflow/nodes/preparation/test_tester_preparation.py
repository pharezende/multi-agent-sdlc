from langchain_core.messages import HumanMessage, SystemMessage

from multi_agent_sdlc.agents.coder.models import CoderSummary
from multi_agent_sdlc.agents.tester.model import TesterSummary as _TesterSummary
from multi_agent_sdlc.agents.tester.prompt import TESTER_SYSTEM_RULES
from multi_agent_sdlc.workflow.models import (
    VerificationBlockDecision,
    VerificationBlockReview,
    VerificationStatus,
)
from multi_agent_sdlc.workflow.nodes.preparation import prepare_tester_node
from multi_agent_sdlc.workflow.state import DevState


def test_prepare_tester_retest_sets_state(
    dev_state: DevState,
    coder_summary: CoderSummary,
    tester_summary: _TesterSummary,
) -> None:
    dev_state["current_coder_summary"] = coder_summary
    dev_state["current_tester_summary"] = tester_summary
    dev_state["tester_messages"] = [
        SystemMessage(content=TESTER_SYSTEM_RULES),
        HumanMessage(content="Previous verification."),
    ]
    dev_state["verification_block_review"] = None

    result = prepare_tester_node(dev_state)

    messages = result["tester_messages"]

    assert result["verification_status"] == VerificationStatus.VERIFYING
    assert result["current_project_verification_result"] is None

    assert isinstance(messages, list)
    assert len(messages) == 1
    assert isinstance(messages[0], HumanMessage)


def test_prepare_tester_verification_retry_sets_state(
    dev_state: DevState,
    tester_summary: _TesterSummary,
) -> None:
    dev_state["current_tester_summary"] = tester_summary
    dev_state["verification_block_review"] = VerificationBlockReview(
        decision=VerificationBlockDecision.RETRY,
        reason="Retry verification using the corrected verification context.",
    )

    result = prepare_tester_node(dev_state)

    messages = result["tester_messages"]

    assert result["verification_status"] == VerificationStatus.VERIFYING
    assert result["current_project_verification_result"] is None

    assert isinstance(messages, list)
    assert len(messages) == 1

    message = messages[0]

    assert isinstance(message, HumanMessage)
    assert isinstance(message.content, str)
    assert (
        "Retry verification using the corrected verification context."
        in message.content
    )
