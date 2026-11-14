from app.ai.agents.profilling_agent.schema.agent_execution_result import ReviewStatus
from app.ai.agents.profilling_agent.schema.manager_feedback import ManagerReview
from app.ai.agents.profilling_agent.services.execution_coordinator import ExecutionCoordinator
from smolagents import Tool












class SubmitManagerReviewTool(Tool):

    name = "submit_manager_review"

    description = (
        "Submit exactly one structured manager review for one "
        "AgentExecutionResult. The review is validated before "
        "it is applied to the execution."
    )

    inputs = {
        "execution_id": {
            "type": "string",
            "description": (
                "The execution_id of the AgentExecutionResult "
                "being reviewed."
            ),
        },
        "review": {
            "type": "object",
            "description": (
                "Structured ManagerReview containing the review "
                "status and optional feedback_items."
            ),
        },
    }

    output_type = "object"

    def __init__(
        self,
        execution_coordinator: ExecutionCoordinator,
    ):
        self.execution_coordinator = execution_coordinator

        super().__init__()

    def forward(
        self,
        execution_id: str,
        review: dict,
    ) -> dict:

        # ---------------------------------------------
        # Validate AI-produced review
        # ---------------------------------------------

        manager_review = ManagerReview.model_validate(
            review
        )

        # ---------------------------------------------
        # Apply review to exact execution
        # ---------------------------------------------

        result = self.execution_coordinator.apply_manager_review(
            execution_id=execution_id,
            review=manager_review,
        )

        # ---------------------------------------------
        # Approved: no new execution
        # ---------------------------------------------

        if result is None:
            return {
                "reviewed_execution_id": execution_id,
                "review_status": manager_review.status.value,
                "next_execution": None,
            }

        # ---------------------------------------------
        # Rework produced a new execution
        # ---------------------------------------------

        return {
            "reviewed_execution_id": execution_id,
            "review_status": manager_review.status.value,
            "next_execution": result.model_dump(),
        }