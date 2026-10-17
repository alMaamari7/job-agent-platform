
from smolagents import ToolCallingAgent

from app.ai.providers.huggingface import get_huggingface_model

from app.schemas.candidate_source import CandidateSource
from app.enums.candidate_source import SourceType
from app.ai.agents.profilling_agent.tools.read_candidate_source import  ReadCandidateSource



class ProfilingAgent:

    def __init__(
        self,
        candidate_sources: list[CandidateSource],
    ):
        self.candidate_sources = candidate_sources

        self.model = get_huggingface_model()

        self.tools = [
            ReadCandidateSource(
                sources=candidate_sources
            )
        ]

        self.agent = ToolCallingAgent(
            model=self.model,
            tools=self.tools,
            max_steps=max(4, len(candidate_sources) * 3),
            instructions="""
            You are a candidate profiling agent.

            Analyze the candidate's provided sources.

            Rules:
            - Read every provided file source.
            - Use the available tools to access documents.
            - Extract education, skills, experience and projects.
            - Distinguish facts from inferences.
            - Never invent candidate qualifications.
            - Support important claims with source evidence.
            - Mark unavailable information as unknown.
            """,
        )

    def _prepare_sources(self) -> str:
        prepared_sources: list[str] = []

        for source in self.candidate_sources:

            source_info = [
                f"source_id: {source.source_id}",
                f"source_type: {source.source_type.value}",
            ]

            if source.original_filename:
                source_info.append(
                    f"original_filename: {source.original_filename}"
                )

            if source.source_url:
                source_info.append(
                    f"source_url: {source.source_url}"
                )

            prepared_sources.append(
                "- " + ", ".join(source_info)
            )

        return "\n".join(prepared_sources)




    
    def run(self) -> str:

        sources_description = self._prepare_sources()

        task = f"""
        Analyze the following authorized candidate sources:

        {sources_description}

        Read every listed candidate source using the
        read_candidate_source tool and its source_id.

        After reading all sources, produce a candidate profile containing:

        1. Education
        2. Work Experience
        3. Technical Skills
        4. Projects
        5. Demonstrated Capabilities
        6. Evidence supporting important claims
        7. Missing or uncertain information

        Do not invent information.
        """

        result = self.agent.run(task)

        return str(result)
