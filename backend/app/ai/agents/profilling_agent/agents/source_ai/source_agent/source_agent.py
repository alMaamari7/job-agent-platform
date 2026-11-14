import json
from pathlib import Path

from pydantic import ValidationError
from smolagents import ToolCallingAgent

from app.ai.agents.profilling_agent.agents.source_ai.schema.parsed_source_result import ParsedSourceResult, ParsedSourceReviewStatus
from app.ai.agents.profilling_agent.schema.candidate_source import CandidateSource
from app.ai.agents.profilling_agent.services.spec_loader import AgentSpecLoader
from app.ai.agents.profilling_agent.tools.read_candidate_source import ReadCandidateSource
from app.ai.providers.huggingface import get_huggingface_model
from typing import Any

from app.ai.agents.profilling_agent.agents.moduls.agent_run_output import AgentRunOutput







class SourceAgent:
    """
    Processes exactly one authorized CandidateSource and returns
    one validated source-level result.

    The SourceAgent is responsible only for source interpretation.

    It does not:
    - create execution metadata;
    - control execution lifecycle state;
    - approve its own result;
    - decide whether manager review is complete.

    Initial executions read the assigned CandidateSource once and
    capture the exact source snapshot used by the agent.

    Rework executions reuse the captured input snapshot together
    with the previous ParsedSourceResult and structured manager
    feedback.
    """

    def __init__(
        self,
        candidate_sources: list[CandidateSource],
    ):
        """
        Initialize the SourceAgent.

        Args:
            candidate_sources:
                Complete set of CandidateSource objects that
                this SourceAgent is authorized to access.
        """

        self.candidate_sources = candidate_sources

        specs_dir = Path(__file__).resolve().parent

        self.spec_loader = AgentSpecLoader(
            agent_dir=specs_dir,
        )

        instructions = self.spec_loader.load_all()

        # -------------------------------------------------
        # Source reading tool
        # -------------------------------------------------

        self.read_candidate_source_tool = ReadCandidateSource(
            sources=candidate_sources,
        )

        # -------------------------------------------------
        # AI agent
        # -------------------------------------------------

        self.agent = ToolCallingAgent(
            model=get_huggingface_model(),
            tools=[
                self.read_candidate_source_tool,
            ],
            instructions=instructions,
            name="source_agent",
            description=(
                "Processes exactly one authorized CandidateSource "
                "per execution and returns source-level facts while "
                "preserving context, contribution, provenance, and "
                "uncertainty."
            ),
            max_steps=10,
            provide_run_summary=True,
        )

    def run(
        self,
        source: CandidateSource | None = None,
        input_snapshot: str | None = None,
        previous_result: ParsedSourceResult | None = None,
        review_feedback: list | None = None,
    ) -> AgentRunOutput:
        """
        Execute either an initial source-processing run or a rework run.

        Initial execution:
            - requires source;
            - reads the CandidateSource through ReadCandidateSource;
            - captures the exact source snapshot;
            - returns ParsedSourceResult + input snapshot.

        Rework execution:
            - requires input_snapshot;
            - requires previous_result;
            - requires manager review feedback;
            - does not read the CandidateSource again;
            - returns a revised ParsedSourceResult using the same snapshot.
        """

        is_rework = previous_result is not None

        # =================================================
        # REWORK EXECUTION
        # =================================================

        if is_rework:

            if source is not None:
                raise ValueError(
                    "Rework execution must not receive CandidateSource."
                )

            if input_snapshot is None:
                raise ValueError(
                    "Rework execution requires input_snapshot."
                )

            if not review_feedback:
                raise ValueError(
                    "Rework execution requires review_feedback."
                )

            task = f"""
You are revising a previous ParsedSourceResult.

SOURCE SNAPSHOT

{input_snapshot}

PREVIOUS RESULT

{previous_result.model_dump_json(indent=2)}

MANAGER REVIEW FEEDBACK

{review_feedback}

REWORK RESPONSIBILITY

You must revise the previous ParsedSourceResult based only on:

- the provided source snapshot;
- the previous ParsedSourceResult;
- the manager review feedback.

REWORK RULES

1. Do not call read_candidate_source.

2. Do not read the CandidateSource again.

3. Apply every required change contained in the manager review feedback.

4. Preserve valid facts and information that are not affected by the review.

5. Do not introduce new facts unless they are directly supported by
   the provided source snapshot.

6. Do not inflate candidate contribution.

7. Repository ownership does not prove sole authorship,
   ownership, leadership, or creation.

8. If candidate-specific contribution is not supported,
   use:

   "contribution": null

   Never return a CandidateContribution object whose
   level is null.

9. Preserve uncertainties where the source does not support
   a definitive conclusion.

10. Return one complete revised ParsedSourceResult.

SOURCE IDENTITY

The revised result MUST retain:

source_id={previous_result.source_id}

source_type={previous_result.source_type}

OUTPUT SCHEMA

{json.dumps(
    ParsedSourceResult.model_json_schema(),
    indent=2,
)}
"""

            raw_result = self.agent.run(
                task,
            )

            parsed_result = self._parse_result(
                raw_result=raw_result,
                expected_source_id=str(
                    previous_result.source_id
                ),
                expected_source_type=str(
                    previous_result.source_type
                ),
            )

            return AgentRunOutput(
                result=parsed_result,
                input_snapshot=input_snapshot,
            )

        # =================================================
        # INITIAL EXECUTION
        # =================================================

        if source is None:
            raise ValueError(
                "Initial SourceAgent execution requires source."
            )

        self._validate_authorized_source(
            source=source,
        )

        # Reset previous snapshot so an earlier execution
        # cannot accidentally be reused.
        self.read_candidate_source_tool.last_source_id = None
        self.read_candidate_source_tool.last_snapshot = None

        task = f"""
Process exactly one assigned Candidate Source.

ASSIGNED SOURCE

source_id={source.source_id}
source_type={source.source_type.value}

SOURCE ACCESS

You MUST read exactly the assigned CandidateSource using
the read_candidate_source tool.

Call:

read_candidate_source(
    source_id="{source.source_id}"
)

Do not read another CandidateSource.

Do not substitute another source.

SOURCE INTERPRETATION

Extract source-level candidate facts only.

Preserve:

- factual statements;
- source context;
- candidate contribution where supported;
- methods;
- tools or resources;
- stakeholders;
- outcomes;
- provenance;
- uncertainty.

CANDIDATE CONTRIBUTION

If the source supports a specific candidate contribution,
provide a CandidateContribution with a non-null string level.

If candidate-specific contribution is not supported,
use:

"contribution": null

Never return:

{{
    "level": null,
    "description": null
}}

Repository ownership does not prove sole authorship,
ownership, leadership, or creation.

Do not inflate candidate contribution.

BOUNDARIES

Do not perform Evidence Processing.

Do not perform Candidate Representation.

Do not generate Candidate Context.

Do not approve your own result.

Return only the source-processing result.

OUTPUT REQUIREMENTS

Return exactly one complete ParsedSourceResult.

The result MUST contain:

source_id="{source.source_id}"

source_type="{source.source_type.value}"

OUTPUT SCHEMA

{json.dumps(
    ParsedSourceResult.model_json_schema(),
    indent=2,
)}
"""

        raw_result = self.agent.run(
            task,
        )

        parsed_result = self._parse_result(
            raw_result=raw_result,
            expected_source_id=str(
                source.source_id
            ),
            expected_source_type=str(
                source.source_type.value
            ),
        )

        snapshot = (
            self.read_candidate_source_tool
            .last_snapshot
        )

        snapshot_source_id = (
            self.read_candidate_source_tool
            .last_source_id
        )

        if snapshot is None:
            raise ValueError(
                "SourceAgent completed without a captured input snapshot."
            )

        if snapshot_source_id != str(source.source_id):
            raise ValueError(
                "Captured input snapshot does not belong "
                "to the assigned CandidateSource."
            )

        return AgentRunOutput(
            result=parsed_result,
            input_snapshot=snapshot,
        )

    def _parse_result(
        self,
        raw_result: Any,
        expected_source_id: str,
        expected_source_type: str,
    ) -> ParsedSourceResult:
        """
        Convert the raw SourceAgent output into a validated
        ParsedSourceResult.

        Validation consists of:

        1. JSON parsing.
        2. Pydantic structural validation.
        3. Source identity validation.

        Args:
            raw_result:
                Raw value returned by the underlying AI agent.

            expected_source_id:
                Source ID that the result must belong to.

            expected_source_type:
                Source type that the result must belong to.

        Returns:
            Validated ParsedSourceResult.

        Raises:
            ValueError:
                If parsing, structural validation, or
                source identity validation fails.
        """

        if isinstance(
            raw_result,
            ParsedSourceResult,
        ):
            result = raw_result

        elif isinstance(
            raw_result,
            dict,
        ):
            try:
                result = ParsedSourceResult.model_validate(
                    raw_result,
                )

            except ValidationError as error:
                raise ValueError(
                    "SourceAgent output does not conform "
                    "to ParsedSourceResult."
                ) from error

        else:
            raw_text = str(
                raw_result
            ).strip()

            try:
                raw_data = json.loads(
                    raw_text,
                )

            except json.JSONDecodeError as error:
                raise ValueError(
                    "SourceAgent returned invalid JSON."
                ) from error

            try:
                result = ParsedSourceResult.model_validate(
                    raw_data,
                )

            except ValidationError as error:
                raise ValueError(
                    "SourceAgent output does not conform "
                    "to ParsedSourceResult."
                ) from error

        self._validate_source_identity(
            result=result,
            expected_source_id=expected_source_id,
            expected_source_type=expected_source_type,
        )

        return result

    def _validate_authorized_source(
        self,
        source: CandidateSource,
    ) -> None:
        """
        Ensure that the assigned CandidateSource belongs
        to the authorized source set of this SourceAgent.
        """

        authorized_source_ids = {
            str(candidate_source.source_id)
            for candidate_source in self.candidate_sources
        }

        if str(source.source_id) not in authorized_source_ids:
            raise ValueError(
                "SourceAgent received a CandidateSource "
                "that is not part of its authorized source set."
            )

    @staticmethod
    def _validate_source_identity(
        result: ParsedSourceResult,
        expected_source_id: str,
        expected_source_type: str,
    ) -> None:
        """
        Ensure that the ParsedSourceResult belongs exactly
        to the source assigned to this execution.
        """

        if str(result.source_id) != str(
            expected_source_id
        ):
            raise ValueError(
                "SourceAgent returned a source_id "
                "that does not match the expected source."
            )

        if str(result.source_type) != str(
            expected_source_type
        ):
            raise ValueError(
                "SourceAgent returned a source_type "
                "that does not match the expected source."
            )