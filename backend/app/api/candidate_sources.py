from fastapi import APIRouter, File, UploadFile

from app.schemas.candidate_source import CandidateSource, CandidateUrlRequest
from app.services.candidate_source_service import CandidateSourceService




router = APIRouter(
    prefix="/candidate-sources",
    tags=["Candidate Sources"],
)


service = CandidateSourceService()


@router.post(
    "/file",
    response_model=CandidateSource,
)
async def upload_candidate_file(
    file: UploadFile = File(...),
):
    return await service.save_file(file)


@router.post(
    "/url",
    response_model=CandidateSource,
)
def add_candidate_url(
    request: CandidateUrlRequest,
):
    return service.save_url(str(request.url))