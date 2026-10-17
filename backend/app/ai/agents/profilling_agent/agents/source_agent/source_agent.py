from pathlib import Path


from smolagents import ToolCallingAgent


from app.ai.providers.huggingface import get_huggingface_model

from app.schemas.candidate_source import CandidateSource
from app.ai.agents.profilling_agent.services.spec_loader import AgentSpecLoader
from app.ai.agents.profilling_agent.tools.read_candidate_source import ReadCandidateSource




class SourceAgent:

    def __init__(
        self,
        candidate_sources: list[CandidateSource],
    ):
        self.candidate_sources = candidate_sources

        specs_dir = Path(__file__).resolve().parent

        self.spec_loader = AgentSpecLoader(
            agent_dir=specs_dir
        )

        instructions = self.spec_loader.load_all()

        self.agent = ToolCallingAgent(
            model=get_huggingface_model(),
            tools=[
                ReadCandidateSource(
                    sources=candidate_sources
                )
            ],
            instructions=instructions,
            name="source_agent",
            description=(
                "Processes exactly one authorized "
                "CandidateSource per execution and returns "
                "source-level facts while preserving "
                "context, contribution, provenance, and "
                "uncertainty."
            ),
            max_steps=10,
            provide_run_summary=True,
        )

    def run(
        self,
        source: CandidateSource,
    ) -> str:

        task = f"""
Process exactly one authorized CandidateSource.

Source:
- source_id: {source.source_id}
- source_type: {source.source_type.value}

Your task is limited to this source only.

Use read_candidate_source with exactly this source_id:

{source.source_id}

Return one ParsedSourceResult for this source.

Preserve:
- source-level facts;
- context;
- candidate contribution;
- outcomes;
- provenance;
- source-level uncertainty.

Do not inspect any other CandidateSource.
Do not perform cross-source reconciliation.
Do not assign candidate-wide support levels.
Do not perform evidence synthesis.
Do not perform capability synthesis.
Do not generate a candidate profile.
"""

        return self.agent.run(
            task
        )