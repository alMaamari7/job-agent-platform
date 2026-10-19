from smolagents import InferenceClientModel

from app.core.config import settings


from smolagents import InferenceClientModel

from app.core.config import settings


def get_huggingface_model() -> InferenceClientModel:
    if not settings.HF_TOKEN:
        raise RuntimeError(
            "HF_TOKEN is required to initialize "
            "the profiling AI model."
        )

    return InferenceClientModel(
        model_id=settings.ai_profilingagent_model,
        provider=settings.ai_profilingagent_provider,
        token=settings.HF_TOKEN,
    )