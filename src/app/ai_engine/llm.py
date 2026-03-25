from app.ai_engine.settings import ai_engine_settings


def get_chat_model():
    """Return a LangChain chat model based on `AI_PROVIDER` + `AI_MODEL`."""

    provider = ai_engine_settings.provider.strip().lower()
    model = ai_engine_settings.model

    if provider == "groq":
        try:
            from langchain_groq import ChatGroq
        except Exception as e:  # pragma: no cover
            raise RuntimeError("Missing dependency: `langchain-groq`.") from e

        return ChatGroq(
            model=model,
            temperature=ai_engine_settings.temperature,
            max_tokens=ai_engine_settings.max_tokens,
        )

    if provider == "gemini":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except Exception as e:  # pragma: no cover
            raise RuntimeError("Missing dependency: `langchain-google-genai`.") from e

        return ChatGoogleGenerativeAI(
            model=model,
            temperature=ai_engine_settings.temperature,
            max_tokens=ai_engine_settings.max_tokens,
        )

    if provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
        except Exception as e:  # pragma: no cover
            raise RuntimeError("Missing dependency: `langchain-openai`.") from e

        return ChatOpenAI(
            model=model,
            temperature=ai_engine_settings.temperature,
            max_tokens=ai_engine_settings.max_tokens,
        )

    raise ValueError(f"Unsupported AI provider: {ai_engine_settings.provider!r}")
