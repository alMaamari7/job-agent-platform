

from pathlib import Path

from smolagents import Tool
from app.schemas.candidate_source import (
    CandidateSource,
)
from app.enums.candidate_source import SourceType
from app.ai.agents.profilling_agent.tools.source_access.readers.document_reader import DocumentReader
from app.ai.agents.profilling_agent.tools.source_access.readers.github_reader import GitHubReader






class ReadCandidateSource(Tool):

    name = "read_candidate_source"

    description = (
        "Read one authorized candidate source by source ID. "
        "The source may be a local candidate document or "
        "a supported external candidate source such as a GitHub repository."
    )

    inputs = {
        "source_id": {
            "type": "string",
            "description": (
                "The unique source ID of the candidate source to read."
            ),
        }
    }

    output_type = "string"

    def __init__(
        self,
        sources: list[CandidateSource],
    ):
        self.sources = {
            str(source.source_id): source
            for source in sources
        }

        self.document_reader = DocumentReader()
        self.github_reader = GitHubReader()

        super().__init__()

    def forward(
        self,
        source_id: str,
    ) -> str:

        source = self.sources.get(source_id)

        if source is None:
            raise ValueError(
                f"Unknown candidate source: {source_id}"
            )

        if source.source_type == SourceType.FILE:

            if not source.file_path:
                raise ValueError(
                    f"Candidate source {source_id} "
                    "has no file path."
                )

            return self.document_reader.read(
                source.file_path
            )

        if source.source_type == SourceType.GITHUB:

            if not source.source_url:
                raise ValueError(
                    f"Candidate source {source_id} "
                    "has no source URL."
                )

            return self.github_reader.read(
                source.source_url
            )

        raise ValueError(
            f"Unsupported candidate source type: "
            f"{source.source_type}"
        )