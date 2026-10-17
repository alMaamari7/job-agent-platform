from app.services.candidate_source_service import CandidateSourceService
from app.ai.agents.profilling_agent.profiling_agent import ProfilingAgent
from app.ai.agents.profilling_agent.agents.profiling_manager.profiling_manager import ProfilingManager



class ProfilingService:

    def __init__(
        self,
        source_service: CandidateSourceService,
    ):
        self.source_service = source_service

    def start_profiling(self) -> str:

        # 1. Gespeicherte Quellen abrufen
        sources = self.source_service.get_sources()

        # 2. Prüfen, ob Quellen vorhanden sind
        if not sources:
            raise ValueError(
                "No candidate sources available."
            )

        # 3. Profiling-Agent erstellen
        manager = ProfilingManager(
            candidate_sources=sources
        )

        # 4. Profilanalyse starten
        result = manager.run()

        return result