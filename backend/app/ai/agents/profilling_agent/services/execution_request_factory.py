from uuid import uuid4

from app.ai.agents.profilling_agent.schema.execution_request import (
    AgentType,
    ExpectedOutputType,
    ExecutionContext,
    ExecutionRequest,
    ExecutionRequestDraft,
)


class ExecutionRequestFactory:
    """
    Creates controlled ExecutionRequest objects from
    AI-generated ExecutionRequestDraft objects.

    The AI decides:
    - agent_type
    - input

    Python controls:
    - request_id
    - expected_output
    - execution_context
    """

    @staticmethod
    def create(
        draft: ExecutionRequestDraft,
        run_id: str,
        mode: str | None,
    ) -> ExecutionRequest:

        request_id = str(
            uuid4()
        )

        expected_output = (
            ExecutionRequestFactory
            ._resolve_expected_output(
                agent_type=draft.agent_type,
            )
        )

        execution_context = ExecutionContext(
            run_id=run_id,
            mode=mode,
        )

        return ExecutionRequest(
            execution_request_draft=draft,
            request_id=request_id,
            expected_output=expected_output,
            execution_context=execution_context,
        )

    @staticmethod
    def _resolve_expected_output(
        agent_type: AgentType,
    ) -> ExpectedOutputType:

        if agent_type == AgentType.SOURCE_AGENT:
            return (
                ExpectedOutputType
                .PARSED_SOURCE_RESULT
            )

        if agent_type == AgentType.EVIDENCE_AGENT:
            return (
                ExpectedOutputType
                .EVIDENCE_RESULT
            )

        if agent_type == AgentType.PROFILE_AGENT:
            return (
                ExpectedOutputType
                .PROFILE_RESULT
            )

        raise ValueError(
            f"Unsupported agent type: {agent_type}"
        )