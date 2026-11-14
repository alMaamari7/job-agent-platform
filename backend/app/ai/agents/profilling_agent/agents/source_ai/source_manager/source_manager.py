from pathlib import Path

from smolagents import ToolCallingAgent

from app.ai.agents.profilling_agent.schema.candidate_source import (
    CandidateSource,
)
from app.ai.agents.profilling_agent.services.execution_coordinator import (
    ExecutionCoordinator,
)
from app.ai.agents.profilling_agent.services.spec_loader import (
    AgentSpecLoader,
)
from app.ai.agents.profilling_agent.tools.execute_execution_plan_tool import (
    ExecuteExecutionPlanTool,
)
from app.ai.agents.profilling_agent.tools.submit_manager_review_tool import (
    SubmitManagerReviewTool,
)
from app.ai.providers.huggingface import get_huggingface_model


class SourceManager:
    """
    AI manager responsible for the Source Processing phase.

    The SourceManager:

    - determines which Candidate Sources require processing;
    - creates ExecutionRequestDraft objects;
    - requests controlled SourceAgent executions;
    - reviews returned AgentExecutionResult objects;
    - submits structured ManagerReview decisions;
    - coordinates improvement cycles when required.

    Technical execution metadata and agent execution are
    controlled by Python infrastructure.
    """

    def __init__(
        self,
        candidate_sources: list[CandidateSource],
        execution_coordinator: ExecutionCoordinator,
    ):
        self.candidate_sources = candidate_sources
        self.execution_coordinator = execution_coordinator

        # -------------------------------------------------
        # Load SourceManager specifications
        # -------------------------------------------------

        specs_dir = Path(__file__).resolve().parent

        spec_loader = AgentSpecLoader(
            agent_dir=specs_dir,
        )

        instructions = spec_loader.load_all()

        # -------------------------------------------------
        # Execution tool
        # -------------------------------------------------

        self.execute_execution_plan_tool = (
            ExecuteExecutionPlanTool(
                execution_coordinator=self.execution_coordinator,
            )
        )

        # -------------------------------------------------
        # Manager review tool
        # -------------------------------------------------

        self.submit_manager_review_tool = (
            SubmitManagerReviewTool(
                execution_coordinator=self.execution_coordinator,
            )
        )

        # -------------------------------------------------
        # SourceManager AI
        # -------------------------------------------------

        self.agent = ToolCallingAgent(
            model=get_huggingface_model(),

            tools=[
                self.execute_execution_plan_tool,
                self.submit_manager_review_tool,
            ],

            managed_agents=[],

            instructions=instructions,

            name="source_manager",

            description=(
                "AI manager responsible for planning, "
                "reviewing, and coordinating the Source "
                "Processing phase. It determines which "
                "SourceAgent executions are required and "
                "reviews their controlled execution results."
            ),

            max_steps=12,

            provide_run_summary=True,
        )

    def _prepare_sources(
        self,
    ) -> str:
        """
        Prepare the authorized CandidateSource scope
        for the SourceManager prompt.
        """

        prepared_sources: list[str] = []

        for source in self.candidate_sources:

            fields = [
                f"source_id={source.source_id}",
                f"source_type={source.source_type.value}",
            ]

            if source.original_filename:
                fields.append(
                    f"original_filename={source.original_filename}"
                )

            if source.file_path:
                fields.append(
                    f"file_path={source.file_path}"
                )

            if source.source_url:
                fields.append(
                    f"source_url={source.source_url}"
                )

            prepared_sources.append(
                "- " + ", ".join(fields)
            )

        return "\n".join(
            prepared_sources
        )




    def run(
    self,
    execution_mode: str,
    run_id: str,
):
        """
        Execute and review the Source Processing phase.

        The SourceManager decides which source executions are required,
        reviews every returned AgentExecutionResult, and submits exactly
        one structured ManagerReview for every execution that requires
        manager review.

        Python infrastructure controls execution metadata, execution
        identity, agent identity, lifecycle state, execution history,
        rework execution, and retry limits.
        """

        sources = self._prepare_sources()

        # -------------------------------------------------
        # Trusted Python-controlled execution context
        # -------------------------------------------------

        self.execute_execution_plan_tool.set_execution_context(
            run_id=run_id,
            mode=execution_mode,
        )

        task = f"""
    Execute the Source Processing phase.

    EXECUTION MODE

    {execution_mode}

    AUTHORIZED CANDIDATE SOURCES

    {sources}

    RESPONSIBILITY

    You are the SourceManager.

    You are responsible for:

    - deciding which authorized Candidate Sources require processing;
    - requesting the required SourceAgent executions;
    - reviewing every returned AgentExecutionResult;
    - creating structured ManagerReview decisions;
    - submitting every review through the controlled
    submit_manager_review tool.

    You do NOT control technical execution metadata.

    ==================================================
    EXECUTION PLANNING
    ==================================================

    For every authorized Candidate Source that requires processing:

    1. Create exactly one ExecutionRequestDraft.

    2. An ExecutionRequestDraft may contain only:

    - agent_type
    - input

    3. For SourceAgent execution:

    - agent_type must be SOURCE_AGENT;
    - input must contain exactly the authorized source_id
        required for that execution.

    4. Do NOT generate, choose, modify, or invent:

    - request_id
    - run_id
    - execution mode
    - expected_output
    - execution_id
    - agent_id
    - attempt number
    - previous_execution_id
    - execution lifecycle status

    These values are controlled by Python infrastructure.

    5. Submit the required ExecutionRequestDraft objects
    through the execute_execution_plan tool.

    Do not claim that an execution occurred unless the
    execute_execution_plan tool actually returned an
    AgentExecutionResult for it.

    ==================================================
    EXECUTION RESULTS
    ==================================================

    The execute_execution_plan tool returns
    AgentExecutionResult objects.

    Each AgentExecutionResult contains Python-controlled
    execution information including:

    - agent_id
    - execution_id
    - request_id
    - attempt
    - previous_execution_id
    - execution_status

    The agent-produced domain result is stored under:

    - result

    For SOURCE_AGENT executions:

    result = ParsedSourceResult

    The ParsedSourceResult contains the source-processing
    result produced by the SourceAgent.

    The SourceAgent does NOT approve its own result.

    ==================================================
    MANAGER REVIEW
    ==================================================

    For every returned AgentExecutionResult whose:

    execution_status = NEEDS_MANAGER_REVIEW

    you MUST perform exactly one manager review.

    Review the contained ParsedSourceResult.

    Evaluate whether:

    - the result corresponds to the assigned Candidate Source;
    - the source identity is coherent;
    - facts are supported by the source;
    - unsupported claims were avoided;
    - candidate contribution was not inflated;
    - repository ownership was not treated as proof of sole
    authorship, ownership, leadership, or creation;
    - uncertainty was preserved where the source does not
    justify a definitive conclusion;
    - the semantic processing status is coherent with the
    actual result;
    - facts preserve relevant context and provenance;
    - the result is sufficiently complete and reliable for
    downstream Evidence Processing.

    After reviewing the execution, choose exactly one:

    - APPROVED_BY_MANAGER
    - NEEDS_IMPROVEMENT

    ==================================================
    APPROVED_BY_MANAGER
    ==================================================

    Choose APPROVED_BY_MANAGER only when the result is
    sufficiently correct, supported, coherent, and complete.

    For APPROVED_BY_MANAGER:

    - feedback_items MUST be empty.

    You MUST submit the review using the
    submit_manager_review tool.

    Do not merely state in text that the result is approved.

    The execution is not approved until the
    submit_manager_review tool call succeeds.

    ==================================================
    NEEDS_IMPROVEMENT
    ==================================================

    Choose NEEDS_IMPROVEMENT when the result requires
    correction before it can be approved.

    For NEEDS_IMPROVEMENT:

    - feedback_items MUST contain at least one
    ReviewFeedbackItem.

    Every ReviewFeedbackItem must contain:

    - issue_type
    - description
    - required_change

    The feedback must be specific enough for the same
    worker agent to revise its previous result.

    Each feedback item must explain:

    issue_type:
    - what category of problem was identified;

    description:
    - what is wrong, unsupported, incomplete, inconsistent,
    or insufficient in the current result;

    required_change:
    - the concrete correction required from the worker agent.

    Do not rewrite the ParsedSourceResult yourself.

    Do not perform the worker's correction.

    Your responsibility is to identify the problem and
    describe the required correction.

    ==================================================
    SUBMITTING THE REVIEW
    ==================================================

    For every AgentExecutionResult with:

    execution_status = NEEDS_MANAGER_REVIEW

    you MUST call:

    submit_manager_review

    The tool call must contain:

    - execution_id
    - review

    Use exactly the execution_id contained in the
    AgentExecutionResult being reviewed.

    Do not invent, alter, substitute, or reuse an execution_id
    from another execution.

    The review must conform to the ManagerReview structure.

    A review decision is NOT effective merely because you
    state it in text.

    APPROVED_BY_MANAGER and NEEDS_IMPROVEMENT become effective
    only after a successful submit_manager_review tool call.

    Submit exactly one ManagerReview for each execution_id.

    Never submit multiple reviews for the same execution_id.

    ==================================================
    REWORK
    ==================================================

    If the submitted ManagerReview has:

    status = NEEDS_IMPROVEMENT

    the controlled Python infrastructure may execute a rework
    using the same persistent worker agent.

    The infrastructure is responsible for:

    - locating the correct previous execution;
    - locating the correct persistent AgentInstance;
    - retrieving the previous agent result;
    - retrieving the stored input snapshot;
    - applying the submitted manager feedback;
    - creating a new controlled ExecutionRequest;
    - creating a new AgentExecutionInstance;
    - increasing the attempt number;
    - setting previous_execution_id;
    - enforcing the maximum execution-attempt limit;
    - executing the same worker agent again.

    You must NOT perform these technical steps yourself.

    You must NOT create the rework execution yourself.

    You must NOT invent a new execution_id.

    ==================================================
    REWORK RESULT
    ==================================================

    If submit_manager_review returns a new
    AgentExecutionResult after NEEDS_IMPROVEMENT,
    that object represents the result of the controlled
    rework execution.

    The new execution:

    - has its own execution_id;
    - has its own request_id;
    - has an increased attempt number;
    - references the prior execution through
    previous_execution_id;
    - belongs to the controlled persistent agent workflow;
    - has execution_status = NEEDS_MANAGER_REVIEW
    when execution succeeds.

    A reworked result is NOT automatically approved.

    You MUST review the new AgentExecutionResult independently.

    For every new AgentExecutionResult whose:

    execution_status = NEEDS_MANAGER_REVIEW

    repeat the complete Manager Review process:

    1. inspect the new result;
    2. choose APPROVED_BY_MANAGER or NEEDS_IMPROVEMENT;
    3. create a valid ManagerReview;
    4. call submit_manager_review using the NEW execution_id.

    Continue only through the controlled tool workflow.

    Do not fabricate additional rework attempts.

    Do not continue beyond infrastructure-enforced execution
    limits.

    ==================================================
    EXECUTION FAILURE
    ==================================================

    If an AgentExecutionResult has:

    execution_status = EXECUTION_FAILED

    do not approve it.

    Do not fabricate a replacement result.

    Do not invent a successful execution.

    Preserve the failure as returned by the controlled
    infrastructure.

    A failure of one source must not cause you to discard
    valid successful results from other sources.

    ==================================================
    INTEGRITY RULES
    ==================================================

    Never fabricate:

    - AgentExecutionResult objects
    - ParsedSourceResult objects
    - ManagerReview submissions
    - execution IDs
    - request IDs
    - agent IDs
    - run IDs
    - retries
    - rework executions
    - attempt numbers
    - approval states
    - execution outcomes
    - worker responses

    Do not claim that a SourceAgent was executed unless the
    controlled execution infrastructure returned an
    AgentExecutionResult for that execution.

    Do not claim that an execution was reviewed unless
    submit_manager_review was successfully called for its
    execution_id.

    Do not claim APPROVED_BY_MANAGER unless that review was
    submitted successfully.

    Preserve successful source results independently if another
    source fails.

    ==================================================
    BOUNDARIES
    ==================================================

    Use only the authorized Candidate Sources listed above.

    Do not expand the authorized source set.

    Do not read CandidateSource content yourself.

    Do not call source-reading capabilities yourself.

    Do not perform source-level fact extraction yourself.

    Do not modify ParsedSourceResult content yourself.

    Do not perform Evidence Processing.

    Do not perform Candidate Representation.

    Do not generate Candidate Context.

    The SourceAgent is responsible for source interpretation
    and controlled rework of its own result.

    The ExecutionCoordinator is responsible for:

    - controlled technical execution;
    - persistent AgentInstance management;
    - AgentExecutionInstance creation;
    - execution history;
    - input snapshot preservation;
    - result preservation;
    - manager-review storage;
    - rework execution;
    - execution lineage;
    - attempt tracking;
    - lifecycle enforcement;
    - execution-limit enforcement.

    Python infrastructure is responsible for creating and
    controlling:

    - ExecutionRequest objects
    - request_id
    - run_id
    - expected_output
    - execution_id
    - agent_id
    - attempt numbers
    - previous_execution_id
    - execution lifecycle state

    You are responsible only for:

    - deciding which authorized source executions are required;
    - reviewing returned execution results;
    - deciding APPROVED_BY_MANAGER or NEEDS_IMPROVEMENT;
    - creating structured manager feedback;
    - submitting every review through the controlled
    submit_manager_review tool.

    ==================================================
    COMPLETION
    ==================================================

    The Source Processing phase is complete only when every
    required source execution has reached a terminal controlled
    outcome.

    A successfully processed source is complete only when its
    latest execution has been reviewed through
    submit_manager_review and approved as:

    APPROVED_BY_MANAGER

    Do not treat NEEDS_MANAGER_REVIEW as approval.

    Do not treat NEEDS_IMPROVEMENT as completion.

    Do not treat an unsubmitted textual review as completion.
    """

        result = self.agent.run(
            task,
        )

        return result