

from pydantic import BaseModel, Field, model_validator

from app.ai.agents.profilling_agent.schema.agent_execution_result import (
    ReviewStatus,
)








class ReviewFeedbackItem(BaseModel):
    issue_type: str = Field(
        ...,
        description="Type or category of the identified review issue.",
    )

    description: str = Field(
        ...,
        description="Explanation of what is wrong or insufficient.",
    )

    required_change: str = Field(
        ...,
        description="Concrete change required from the agent.",
    )


class ManagerReview(BaseModel):
    status: ReviewStatus = Field(
        ...,
        description=(
            "Manager decision for this execution, such as "
            "NEEDS_IMPROVEMENT or APPROVED_BY_MANAGER."
        ),
    )

    feedback_items: list[ReviewFeedbackItem] = Field(
        default_factory=list,
        description=(
            "Structured feedback for the executed agent. "
            "Required when status is NEEDS_IMPROVEMENT."
        ),
    )

    @model_validator(mode="after")
    def validate_review_state(self):
        if (
            self.status == ReviewStatus.NEEDS_IMPROVEMENT
            and not self.feedback_items
        ):
            raise ValueError(
                "NEEDS_IMPROVEMENT requires at least one feedback item."
            )

        if (
            self.status == ReviewStatus.APPROVED_BY_MANAGER
            and self.feedback_items
        ):
            raise ValueError(
                "APPROVED_BY_MANAGER must not contain feedback items."
            )

        return self