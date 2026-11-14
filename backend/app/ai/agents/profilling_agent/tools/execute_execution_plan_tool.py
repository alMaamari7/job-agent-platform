from smolagents import Tool

from app.ai.agents.profilling_agent.schema.execution_plan import (
    ExecutionPlan,
)
from app.ai.agents.profilling_agent.schema.execution_request import (
    ExecutionRequestDraft,
)
from app.ai.agents.profilling_agent.services.execution_coordinator import (
    ExecutionCoordinator,
)
from app.ai.agents.profilling_agent.services.execution_request_factory import (
    ExecutionRequestFactory,
)


class ExecuteExecutionPlanTool(Tool):
    name = "execute_execution_plan"

    description = (
        "Execute one or more profiling-agent execution drafts. "
        "The AI manager provides only ExecutionRequestDraft objects. "
        "Python infrastructure creates controlled ExecutionRequest objects "
        "and the final ExecutionPlan."
    )

    inputs = {
        "execution_request_drafts": {
            "type": "array",
            "description": (
                "ExecutionRequestDraft objects. "
                "Each draft may contain only agent_type and input."
            ),
        },
    }

    output_type = "array"

    def __init__(
        self,
        execution_coordinator: ExecutionCoordinator,
    ):
        self.execution_coordinator = execution_coordinator

        self.run_id: str | None = None
        self.mode: str | None = None

        super().__init__()

    def set_execution_context(
        self,
        run_id: str,
        mode: str | None,
    ) -> None:
        """
        Set the execution context from trusted Python code.

        These values are not provided by the AI manager.
        """

        self.run_id = run_id
        self.mode = mode

    def forward(
        self,
        execution_request_drafts: list[dict],
    ):
        if self.run_id is None:
            raise RuntimeError(
                "Execution context has not been configured."
            )

        drafts = [
            ExecutionRequestDraft.model_validate(
                draft
            )
            for draft in execution_request_drafts
        ]

        requests = [
            ExecutionRequestFactory.create(
                draft=draft,
                run_id=self.run_id,
                mode=self.mode,
            )
            for draft in drafts
        ]

        execution_plan = ExecutionPlan(
            execution_requests=requests,
        )

        results = self.execution_coordinator.execute(
            execution_plan=execution_plan,
        )

        return [
            result.model_dump()
            for result in results
        ]