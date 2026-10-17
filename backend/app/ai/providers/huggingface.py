from smolagents import InferenceClientModel

from app.core.config import settings


def get_huggingface_model() -> InferenceClientModel:
    return InferenceClientModel(
        model_id=settings.ai_profilingagent_model,
        provider= settings.ai_profilingagent_provider,
        token=settings.HF_TOKEN,
    )