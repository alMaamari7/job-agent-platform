from pydantic import BaseModel, HttpUrl
from uuid import UUID

from app.enums.candidate_source import SourceType


class CandidateSource(BaseModel):
    source_id: UUID
    source_type: SourceType

    original_filename: str | None = None
    file_path: str | None = None
    source_url: str | None = None



class CandidateUrlRequest(BaseModel):
    url: HttpUrl