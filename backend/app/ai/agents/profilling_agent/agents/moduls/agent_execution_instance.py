from dataclasses import dataclass
from typing import Any

from app.ai.agents.profilling_agent.schema.execution_request import (
    ExecutionRequest,
)
from app.ai.agents.profilling_agent.schema.manager_feedback import ManagerReview


@dataclass
class AgentExecutionInstance:
    """
    Represents one concrete runtime execution of an agent
    inside the Candidate Profiling workflow.

    The class is generic and may represent executions of:

    - SourceAgent
    - EvidenceAgent
    - ProfileAgent
    - future profiling worker agents

    It connects:

    - the concrete agent instance;
    - the ExecutionRequest that triggered it;
    - the concrete execution attempt;
    - an optional previous execution;
    - the produced result.
    """



    # -------------------------------------------------
    # Execution identity
    # -------------------------------------------------

    execution_id: str

    # -------------------------------------------------
    # Request
    # -------------------------------------------------

    request: ExecutionRequest



    # -------------------------------------------------
    # Attempt information
    # -------------------------------------------------

    attempt: int = 1

    previous_execution_id: str | None = None

    # -------------------------------------------------
    # Execution result
    # -------------------------------------------------

    result: Any | None = None



    # -------------------------------------------------
    # Manager review
    # -------------------------------------------------

    manager_review: ManagerReview | None = None




    input_snapshot: Any | None = None

    # -------------------------------------------------
    # Convenience properties
    # -------------------------------------------------
    @property
    def request_id(self) -> str:
        return self.request.request_id

    @property
    def agent_type(self):
        return self.request.execution_request_draft.agent_type

    @property
    def execution_context(self):
        return self.request.execution_context

    @property
    def input(self) -> dict[str, Any]:
        return self.request.execution_request_draft.input