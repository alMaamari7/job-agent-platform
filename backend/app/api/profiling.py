from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool


from app.services.candidate_source_service import CandidateSourceService
from app.ai.agents.profilling_agent.services.profiling_service import ProfilingService


router = APIRouter(
    prefix="/profiling",
    tags=["Profiling"],
)

profiling_service = ProfilingService(
    source_service=CandidateSourceService()
)


@router.post("/start")
async def start_profiling():

    try:
        result = await run_in_threadpool(
            profiling_service.start_profiling
        )

        return {
            "status": "completed",
            "result": result,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error