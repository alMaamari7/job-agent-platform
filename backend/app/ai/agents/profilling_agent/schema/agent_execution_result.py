from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ReviewStatus(str, Enum):
    """
    Describes the review lifecycle of a ParsedSourceResult
    between worker execution and manager approval.
    """

    NEEDS_MANAGER_REVIEW = "NEEDS_MANAGER_REVIEW"
    NEEDS_IMPROVEMENT = "NEEDS_IMPROVEMENT"
    APPROVED_BY_MANAGER = "APPROVED_BY_MANAGER"
    EXECUTION_FAILED = "EXECUTION_FAILED"


class AgentExecutionResult(BaseModel):
    """
    Controlled result of one concrete profiling-agent execution.

    The agent produces only its domain-specific result.

    Python infrastructure adds execution identity,
    lifecycle state, attempt information, and lineage.
    """

    agent_id: str = Field(
        ...,
        description="Identifier of the concrete agent instance.",
    )

    execution_id: str = Field(
        ...,
        description="Identifier of this concrete execution.",
    )

    request_id: str = Field(
        ...,
        description=(
            "Identifier of the ExecutionRequest that triggered "
            "this execution."
        ),
    )

    attempt: int = Field(
        ...,
        ge=1,
        description="Execution attempt number.",
    )

    previous_execution_id: str | None = Field(
        default=None,
        description=(
            "Identifier of the previous execution in the same "
            "rework chain, if one exists."
        ),
    )

    execution_status: ReviewStatus = Field(
        ...,
        description=(
            "Infrastructure-controlled lifecycle status "
            "of this execution result."
        ),
    )

    result: Any = Field(
        ...,
        description=(
            "Domain-specific result produced by the executed agent."
        ),
    )