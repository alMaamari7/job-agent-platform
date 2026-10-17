from smolagents import Tool

from app.ai.agents.profilling_agent.agents.source_agent.source_agent import SourceAgent





class ProcessCandidateSource(Tool):

    name = "process_candidate_source"

    description = """
    Process exactly one authorized CandidateSource through the SourceAgent.

    Call this tool once for each CandidateSource.
    Never combine multiple source IDs in one call.
    """

    inputs = {
        "source_id": {
            "type": "string",
            "description": (
                "The unique ID of exactly one authorized CandidateSource."
            ),
        }
    }

    output_type = "string"

    def __init__(
        self,
        source_agent: SourceAgent,
        candidate_sources,
    ):
        super().__init__()

        self.source_agent = source_agent

        self.sources_by_id = {
            str(source.source_id): source
            for source in candidate_sources
        }

    def forward(
        self,
        source_id: str,
    ) -> str:

        source = self.sources_by_id.get(
            str(source_id)
        )

        if source is None:
            raise ValueError(
                f"Unknown or unauthorized source_id: {source_id}"
            )

        return self.source_agent.run(
            source=source
        )