from app.ai.agents.profilling_agent.services.candidate_source_service import (
    CandidateSourceService,
)
from app.ai.agents.profilling_agent.agents.profiling_manager.profiling_manager import (
    ProfilingManager,
)


class ProfilingService:

    def __init__(
        self,
        source_service: CandidateSourceService,
    ):
        self.source_service = source_service

    def start_profiling(self) -> str:

        # 1. Gespeicherte Candidate Sources laden
        sources = self.source_service.get_sources()

        # 2. Sicherstellen, dass mindestens eine Source vorhanden ist
        if not sources:
            raise ValueError(
                "No candidate sources available."
            )

        # 3. ProfilingManager erstellen
        manager = ProfilingManager(
            candidate_sources=sources,
            candidate_source_service=self.source_service,
        )

        # 4. Candidate Profiling starten
        result = manager.run()

        return result