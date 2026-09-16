from app.core.config import get_settings
from app.providers.base import TutorProvider
from app.providers.openai import AIProviderError, OpenAIProvider


def get_tutor_provider() -> TutorProvider:
    settings = get_settings()
    if settings.ai_provider != "openai":
        raise AIProviderError("Configured AI provider is not supported")
    if not settings.openai_api_key:
        raise AIProviderError("OPENAI_API_KEY is not configured")
    return OpenAIProvider(settings.openai_api_key, settings.openai_model, settings.openai_base_url)

