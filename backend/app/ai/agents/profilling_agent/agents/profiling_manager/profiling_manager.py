from pathlib import Path

from smolagents import ToolCallingAgent

from app.ai.agents.profilling_agent.schema.candidate_source import (
    CandidateSource,
)
from app.ai.agents.profilling_agent.services.spec_loader import (
    AgentSpecLoader,
)
from app.ai.agents.profilling_agent.services.execution_coordinator import (
    ExecutionCoordinator,
)
from app.ai.agents.profilling_agent.agents.source_ai.source_agent.source_agent import (
    SourceAgent,
)
from app.ai.agents.profilling_agent.agents.source_ai.source_manager.source_manager import (
    SourceManager,
)
from app.ai.providers.huggingface import get_huggingface_model
from app.ai.agents.profilling_agent.services.candidate_source_service import CandidateSourceService


class ProfilingManager:

    def __init__(
        self,
        candidate_sources: list[CandidateSource],
        candidate_source_service: CandidateSourceService,
    ):
        self.candidate_sources = candidate_sources
        self.candidate_source_service = candidate_source_service

        # -------------------------------------------------
        # SourceAgent
        # -------------------------------------------------

        self.source_agent = SourceAgent(
            candidate_sources=candidate_sources,
        )

        # -------------------------------------------------
        # ExecutionCoordinator
        # -------------------------------------------------

        self.execution_coordinator = ExecutionCoordinator(
            candidate_source_service=self.candidate_source_service,
            source_agent=self.source_agent,
        )

        # -------------------------------------------------
        # SourceManager
        # -------------------------------------------------

        self.source_manager = SourceManager(
            candidate_sources=candidate_sources,
            execution_coordinator=self.execution_coordinator,
        )

        # -------------------------------------------------
        # Load ProfilingManager specifications
        # -------------------------------------------------

        specs_dir = Path(__file__).resolve().parent

        spec_loader = AgentSpecLoader(
            agent_dir=specs_dir,
        )

        instructions = spec_loader.load_all()

        # -------------------------------------------------
        # ProfilingManager AI
        # -------------------------------------------------

        self.agent = ToolCallingAgent(
            model=get_huggingface_model(),

            tools=[],

            managed_agents=[
                self.source_manager.agent,
            ],

            instructions=instructions,

            name="profiling_manager",

            description=(
                "Top-level AI manager responsible for "
                "coordinating the complete Candidate "
                "Profiling workflow."
            ),

            max_steps=10,

            provide_run_summary=True,
        )

    def _prepare_sources(
        self,
    ) -> str:

        prepared_sources: list[str] = []

        for source in self.candidate_sources:

            fields = [
                f"source_id={source.source_id}",
                f"source_type={source.source_type.value}",
            ]

            if source.original_filename:
                fields.append(
                    f"original_filename="
                    f"{source.original_filename}"
                )

            if source.source_url:
                fields.append(
                    f"source_url="
                    f"{source.source_url}"
                )

            prepared_sources.append(
                "- " + ", ".join(fields)
            )

        return "\n".join(
            prepared_sources
        )

    def run(
        self,
    ):

        sources = self._prepare_sources()

        task = f"""
Start the Candidate Profiling workflow.

Authorized Candidate Sources:

{sources}

For the current implementation stage,
execute only Source Processing.

Your responsibilities:

1. Resolve the execution mode.

2. Confirm the authorized Candidate Source scope.

3. Delegate the Source Processing phase
   to the SourceManager.

4. Provide the SourceManager with the
   information required to process the
   authorized sources.

5. Receive the SourceProcessingResult
   from the SourceManager.

6. Evaluate whether the Source Processing
   phase returned successfully.

7. Stop after Source Processing.

Do not process Candidate Sources yourself.

Do not call SourceAgent directly.

Do not perform source-level fact extraction.

Do not perform Evidence Processing.

Do not perform Candidate Representation.

Do not generate Candidate Context.

Return:

- resolved execution mode;
- SourceProcessingResult;
- whether Source Processing returned
  control successfully.

This implementation test ends after
the SourceManager result.
"""

        return self.agent.run(
            task,
        )