from pathlib import Path

from smolagents import ToolCallingAgent

from app.schemas.candidate_source import CandidateSource
from app.ai.agents.profilling_agent.agents.profiling_manager.process_candidate_source import ProcessCandidateSource
from app.ai.agents.profilling_agent.agents.source_agent.source_agent import SourceAgent
from app.ai.agents.profilling_agent.services.spec_loader import AgentSpecLoader
from app.ai.providers.huggingface import get_huggingface_model


class ProfilingManager:

    def __init__(
        self,
        candidate_sources: list[CandidateSource],
    ):
        self.candidate_sources = candidate_sources

        # -------------------------------------------------
        # SourceAgent
        # -------------------------------------------------

        self.source_agent = SourceAgent(
            candidate_sources=candidate_sources,
        )

        # -------------------------------------------------
        # Controlled Manager -> SourceAgent boundary
        # -------------------------------------------------

        self.process_candidate_source_tool = (
            ProcessCandidateSource(
                source_agent=self.source_agent,
                candidate_sources=candidate_sources,
            )
        )

        # -------------------------------------------------
        # Load ProfilingManager specifications
        # -------------------------------------------------

        specs_dir = (
            Path(__file__).resolve().parent
        )

        spec_loader = AgentSpecLoader(
            agent_dir=specs_dir
        )

        instructions = spec_loader.load_all()

        # -------------------------------------------------
        # ProfilingManager Agent
        # -------------------------------------------------

        self.agent = ToolCallingAgent(
            model=get_huggingface_model(),
            tools=[
                self.process_candidate_source_tool,
            ],
            instructions=instructions,
            max_steps=10,
        )

    def _prepare_sources(self) -> str:

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

    def run(self):

        sources = self._prepare_sources()

        task = f"""
Run only the source-processing stage of the
candidate profiling workflow.

Authorized candidate sources:

{sources}

Process every authorized CandidateSource independently.

For each CandidateSource:

1. Call the process_candidate_source tool.
2. Pass exactly one source_id.
3. Never combine multiple CandidateSources into one call.
4. Preserve the result of each source independently.
5. If one source fails, continue processing the remaining sources.
6. Do not discard successful source results because another source failed.

Every authorized source must be attempted.

For this experiment, stop after source processing.

Return:

1. execution mode;
2. sources requested;
3. independent SourceAgent result for every source;
4. sources that could not be processed;
5. whether source processing completed successfully.

Do not perform evidence processing.
Do not generate a candidate profile.
"""

        return self.agent.run(
            task
        )