

from uuid import uuid4

from app.ai.agents.profilling_agent.schema.execution_plan import (
    ExecutionPlan,
)
from app.ai.agents.profilling_agent.schema.execution_request import (
    AgentType,
    ExecutionRequest,
)
from app.ai.agents.profilling_agent.services.candidate_source_service import (
    CandidateSourceService,
)
from app.ai.agents.profilling_agent.agents.source_ai.source_agent.source_agent import (
    SourceAgent,
)
from app.ai.agents.profilling_agent.agents.source_ai.schema.parsed_source_result import (
    ParsedSourceResult,
)
from app.ai.agents.profilling_agent.agents.moduls.agent_instance import (
    AgentInstance,
)
from app.ai.agents.profilling_agent.agents.moduls.agent_execution_instance import (
    AgentExecutionInstance,
)
from app.ai.agents.profilling_agent.schema.agent_execution_result import (
    AgentExecutionResult,
    ReviewStatus,
)
from app.ai.agents.profilling_agent.schema.manager_feedback import ManagerReview
from app.ai.agents.profilling_agent.services.execution_request_factory import ExecutionRequestFactory


class ExecutionCoordinator:

    MAX_EXECUTION_ATTEMPTS = 3


    def __init__(
        self,
        candidate_source_service: CandidateSourceService,
        source_agent: SourceAgent,
    ):
        self.candidate_source_service = candidate_source_service

        self.source_agent = source_agent

        # -------------------------------------------------
        # Persistent agent registry
        # -------------------------------------------------

        self.agents: dict[str, AgentInstance] = {}

        # -------------------------------------------------
        # Execution registry
        # -------------------------------------------------

        self.executions: dict[
            str,
            AgentExecutionInstance,
        ] = {}

    def execute(
        self,
        execution_plan: ExecutionPlan,
    ) -> list[AgentExecutionResult]:

        results: list[AgentExecutionResult] = []

        for request in execution_plan.execution_requests:

            # ---------------------------------------------
            # Resolve persistent agent instance
            # ---------------------------------------------

            agent_instance = self._resolve_agent_instance(
                request=request,
            )

            # ---------------------------------------------
            # Create one concrete execution
            # ---------------------------------------------

            execution = self._create_execution_instance(
                request=request,
                agent_instance=agent_instance,
            )

            try:

                # -----------------------------------------
                # Execute actual agent
                # -----------------------------------------

                agent_run_output = self._execute_request(
                    request=request,
                    agent_instance=agent_instance,
                )

                # -----------------------------------------
                # Store domain result in execution
                # -----------------------------------------

                execution.input_snapshot = agent_run_output.input_snapshot
                execution.result = agent_run_output.result

                # -----------------------------------------
                # Build controlled external result
                # -----------------------------------------

                execution_result = self._build_agent_execution_result(
                    agent_instance=agent_instance,
                    execution=execution,
                    result=agent_run_output.result,
                )

            except Exception as error:

                execution_result = (
                    self._build_execution_failed_result(
                        agent_instance=agent_instance,
                        execution=execution,
                        error=error,
                    )
                )

            results.append(
                execution_result
            )

        return results

    # =====================================================
    # Agent resolution
    # =====================================================

    def _resolve_agent_instance(
        self,
        request: ExecutionRequest,
    ) -> AgentInstance:
        """
        Resolve or create the persistent AgentInstance
        responsible for this request.
        """

        agent_type = (
            request
            .execution_request_draft
            .agent_type
        )

        if agent_type == AgentType.SOURCE_AGENT:

            return self._get_or_create_agent_instance(
                agent=self.source_agent,
            )

        raise ValueError(
            f"Unsupported agent type: {agent_type}"
        )

    def _get_or_create_agent_instance(
        self,
        agent,
    ) -> AgentInstance:
        """
        Return an existing persistent AgentInstance for
        the runtime agent object, or create one.
        """

        for agent_instance in self.agents.values():

            if agent_instance.agent is agent:
                return agent_instance

        agent_id = str(
            uuid4()
        )

        agent_instance = AgentInstance(
            agent_id=agent_id,
            agent=agent,
        )

        self.agents[
            agent_id
        ] = agent_instance

        return agent_instance

    # =====================================================
    # Execution creation
    # =====================================================

    def _create_execution_instance(
        self,
        request: ExecutionRequest,
        agent_instance: AgentInstance,
        attempt: int = 1,
        previous_execution_id: str | None = None,
    ) -> AgentExecutionInstance:
        """
        Create one concrete execution belonging to
        the persistent AgentInstance.
        """

        execution_id = str(
            uuid4()
        )

        execution = AgentExecutionInstance(
            execution_id=execution_id,
            request=request,
            attempt=attempt,
            previous_execution_id=previous_execution_id,
        )

        # Global execution lookup
        self.executions[
            execution_id
        ] = execution

        # Agent-specific execution history
        agent_instance.executions.append(
            execution
        )

        return execution

    # =====================================================
    # Agent execution
    # =====================================================

    def _execute_request(
        self,
        request: ExecutionRequest,
        agent_instance: AgentInstance,
    ) -> ParsedSourceResult:

        agent_type = (
            request
            .execution_request_draft
            .agent_type
        )

        if agent_type == AgentType.SOURCE_AGENT:

            return self._execute_source_agent(
                request=request,
                agent=agent_instance.agent,
            )

        raise ValueError(
            f"Unsupported agent type: {agent_type}"
        )

    def _execute_source_agent(
        self,
        request: ExecutionRequest,
        agent: SourceAgent,
    ) -> ParsedSourceResult:

        source_id = (
            request
            .execution_request_draft
            .input
            .get("source_id")
        )

        if source_id is None:
            raise ValueError(
                "SOURCE_AGENT execution requires source_id."
            )

        source = (
            self.candidate_source_service
            .get_source_by_id(
                source_id=source_id,
            )
        )

        if source is None:
            raise ValueError(
                f"CandidateSource not found: {source_id}"
            )

        return agent.run(
            source=source,
        )

    # =====================================================
    # Successful execution result
    # =====================================================

    def _build_agent_execution_result(
        self,
        agent_instance: AgentInstance,
        execution: AgentExecutionInstance,
        result,
    ) -> AgentExecutionResult:

        return AgentExecutionResult(
            agent_id=agent_instance.agent_id,
            execution_id=execution.execution_id,
            request_id=execution.request_id,
            attempt=execution.attempt,
            previous_execution_id=(
                execution.previous_execution_id
            ),
            execution_status=(
                ReviewStatus.NEEDS_MANAGER_REVIEW
            ),
            result=result,
        )

    # =====================================================
    # Failed execution result
    # =====================================================

    def _build_execution_failed_result(
        self,
        agent_instance: AgentInstance,
        execution: AgentExecutionInstance,
        error: Exception,
    ) -> AgentExecutionResult:

        failure_result = {
            "error_type": type(error).__name__,
            "error_message": str(error),
        }

        execution.result = failure_result

        return AgentExecutionResult(
            agent_id=agent_instance.agent_id,
            execution_id=execution.execution_id,
            request_id=execution.request_id,
            attempt=execution.attempt,
            previous_execution_id=(
                execution.previous_execution_id
            ),
            execution_status=(
                ReviewStatus.EXECUTION_FAILED
            ),
            result=failure_result,
        )

    # =====================================================
    # Lookup
    # =====================================================

    def get_execution(
        self,
        execution_id: str,
    ) -> AgentExecutionInstance | None:

        return self.executions.get(
            execution_id
        )

    def get_agent(
        self,
        agent_id: str,
    ) -> AgentInstance | None:

        return self.agents.get(
            agent_id
        )




    def apply_manager_review(
    self,
    execution_id: str,
    review: ManagerReview,
) -> AgentExecutionResult | None:

        execution = self.get_execution(
            execution_id=execution_id,
        )

        if execution is None:
            raise ValueError(
                f"Execution not found: {execution_id}"
            )


        if execution.manager_review is not None:
            raise ValueError(
                f"Execution {execution_id} has already been reviewed."
            )

        # ---------------------------------------------
        # Store manager review
        # ---------------------------------------------

        execution.manager_review = review

        # ---------------------------------------------
        # Approved
        # ---------------------------------------------

        if review.status == ReviewStatus.APPROVED_BY_MANAGER:
            return None

        # ---------------------------------------------
        # Improvement required
        # ---------------------------------------------

        if review.status == ReviewStatus.NEEDS_IMPROVEMENT:

            if not review.feedback_items:
                raise ValueError(
                    "NEEDS_IMPROVEMENT requires feedback_items."
                )

            return self._execute_rework(
                previous_execution=execution,
            )

        raise ValueError(
            f"Unsupported manager review status: {review.status}"
        )




    def _find_agent_instance_for_execution(
    self,
    execution_id: str,
) -> AgentInstance:

        for agent_instance in self.agents.values():

            for execution in agent_instance.executions:

                if execution.execution_id == execution_id:
                    return agent_instance

        raise ValueError(
            f"AgentInstance for execution "
            f"{execution_id} not found."
        )


    def _execute_rework(
    self,
    previous_execution: AgentExecutionInstance,
) -> AgentExecutionResult:



        previous_snapshot = previous_execution.input_snapshot


        if previous_execution.attempt >= self.MAX_EXECUTION_ATTEMPTS:
            raise ValueError(
                "Maximum execution attempts reached."
            )

        if previous_execution.result is None:
            raise ValueError(
                "Cannot rework an execution without a result."
            )

        if previous_execution.manager_review is None:
            raise ValueError(
                "Cannot rework an execution without manager review."
            )

        agent_instance = (
            self._find_agent_instance_for_execution(
                execution_id=previous_execution.execution_id,
            )
        )

        previous_result = previous_execution.result

        review = previous_execution.manager_review

        previous_draft = (
            previous_execution
            .request
            .execution_request_draft
        )

        new_request = ExecutionRequestFactory.create(
            draft=previous_draft,
            run_id=(
                previous_execution
                .execution_context
                .run_id
            ),
            mode=(
                previous_execution
                .execution_context
                .mode
            ),
        )

        new_execution = self._create_execution_instance(
            request=new_request,
            agent_instance=agent_instance,
            attempt=previous_execution.attempt + 1,
            previous_execution_id=(
                previous_execution.execution_id
            ),
        )

        try:

            agent_result = self._execute_rework_request(
                execution=new_execution,
                agent_instance=agent_instance,
                previous_result=previous_result,
                previous_snapshot=previous_snapshot,
                review=review,
            )

            new_execution.input_snapshot = previous_snapshot
            new_execution.result = agent_result

            return self._build_agent_execution_result(
                agent_instance=agent_instance,
                execution=new_execution,
                result=agent_result,
            )

        except Exception as error:

            return self._build_execution_failed_result(
                agent_instance=agent_instance,
                execution=new_execution,
                error=error,
            )



    def _execute_rework_request(
    self,
    execution: AgentExecutionInstance,
    agent_instance: AgentInstance,
    previous_result,
    previous_snapshot: str | None,
    review: ManagerReview,
):

        if execution.agent_type == AgentType.SOURCE_AGENT:

            if previous_snapshot is None:
                raise ValueError(
                    "SOURCE_AGENT rework requires an input snapshot."
                )

            return agent_instance.agent.run(
                input_snapshot=previous_snapshot,
                previous_result=previous_result,
                review_feedback=review.feedback_items,
            )

        raise ValueError(
            f"Unsupported agent type: "
            f"{execution.agent_type}"
        )