from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Defines which registered agent type should execute the request."""

    SOURCE_AGENT = "SOURCE_AGENT"
    EVIDENCE_AGENT = "EVIDENCE_AGENT"
    PROFILE_AGENT = "PROFILE_AGENT"


class ExpectedOutputType(str, Enum):
    """Defines the output type expected from the requested agent execution."""

    PARSED_SOURCE_RESULT = "ParsedSourceResult"
    EVIDENCE_RESULT = "EvidenceResult"
    PROFILE_RESULT = "ProfileResult"


class ExecutionContext(BaseModel):
    """Contains execution-level context shared with the requested agent."""

    run_id: str = Field(
        ...,
        description=(
            "Unique identifier of the profiling run to which this "
            "agent execution belongs."
        ),
    )

    mode: str | None = Field(
        default=None,
        description=(
            "Optional workflow or execution mode relevant to this request, "
            "for example INITIAL_PROFILE_BUILD or UPDATE_EXISTING_PROFILE."
        ),
    )






class ExecutionRequestDraft(BaseModel):
    """
    Represents the execution decision made by an AI manager.

    It contains only the information the AI manager is
    responsible for deciding.

    Technical execution metadata such as request_id,
    run_id, execution_id, attempt number, and expected
    output are controlled by Python infrastructure.
    """

    agent_type: AgentType = Field(
        ...,
        description=(
            "Type of profiling agent that should execute "
            "the requested work."
        ),
    )

    input: dict[str, Any] = Field(
        ...,
        description=(
            "Agent-specific task input. "
            "For a SourceAgent this contains the authorized "
            "source_id to process."
        ),
    )








class ExecutionRequest(BaseModel):
    """
    Represents one controlled request to execute a registered agent.

    The request describes what agent should be executed, which input it
    should receive, what output is expected, and the execution context
    in which the task belongs.
    """


    execution_request_draft: ExecutionRequestDraft = Field(
        ...,
        description=(
            "The execution request draft containing the agent type, "
            "input, and other information decided by the AI manager."
        ),
    )

    request_id: str = Field(
        ...,
        description=(
            "Unique identifier of this specific agent execution request."
        ),
    )



    expected_output: ExpectedOutputType = Field(
        ...,
        description=(
            "Type of result that the execution is expected to return."
        ),
    )

    execution_context: ExecutionContext = Field(
        ...,
        description=(
            "Contextual information associated with the execution, "
            "such as the parent profiling run and execution mode."
        ),
    )