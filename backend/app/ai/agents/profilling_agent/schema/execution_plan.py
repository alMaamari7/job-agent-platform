from pydantic import BaseModel, Field

from app.ai.agents.profilling_agent.schema.execution_request import ExecutionRequest


class ExecutionPlan(BaseModel):
    execution_requests: list[ExecutionRequest] = Field(
        ...,
        description=(
            "Execution requests created by the manager. "
            "Each request represents exactly one agent execution."
        ),
    )