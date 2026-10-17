from fastapi import FastAPI

from app.api.candidate_sources import (
    router as candidate_sources_router,
)
from app.api.profiling import (
    router as profiling_router,
)


app = FastAPI(title="Job Agent Platform")

app.include_router(candidate_sources_router)
app.include_router(profiling_router)