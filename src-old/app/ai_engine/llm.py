from app.ai_engine.settings import ai_engine_settings
from typing import Optional

import os

def get_chat_model(*, temperature: Optional[float] = None):
    """Return a LangChain chat model based on `AI_PROVIDER` + `AI_MODEL`."""

    provider = ai_engine_settings.provider.strip().lower()
    model = ai_engine_settings.model

    effective_temperature = (
        ai_engine_settings.temperature if temperature is None else temperature
    )

    if provider == "groq":
        if not os.getenv("GROQ_API_KEY"):
            raise ValueError("GROQ_API_KEY is not set. Set it in your environment or .env.docker/.env")
        try:
            from langchain_groq import ChatGroq
        except Exception as e:  # pragma: no cover
            raise RuntimeError("Missing dependency: `langchain-groq`.") from e

        return ChatGroq(
            model=model,
            temperature=effective_temperature,
            max_tokens=ai_engine_settings.max_tokens,
        )

    if provider == "gemini":
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY is not set. Set it in your environment or .env.docker/.env")
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except Exception as e:  # pragma: no cover
            raise RuntimeError("Missing dependency: `langchain-google-genai`.") from e

        return ChatGoogleGenerativeAI(
            model=model,
            temperature=effective_temperature,
            max_tokens=ai_engine_settings.max_tokens,
        )

    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is not set. Set it in your environment or .env.docker/.env")
        try:
            from langchain_openai import ChatOpenAI
        except Exception as e:  # pragma: no cover
            raise RuntimeError("Missing dependency: `langchain-openai`.") from e

        return ChatOpenAI(
            model=model,
            temperature=effective_temperature,
            max_tokens=ai_engine_settings.max_tokens,
        )

    raise ValueError(f"Unsupported AI provider: {ai_engine_settings.provider!r}")
