"""Gemini LLM client utility using LangChain's GooglePalm (API key).

This helper constructs a LangChain `GooglePalm` chat model using an
API key from the `GEMINI_API_KEY` environment variable.
"""

import os
from typing import Optional

try:
    from langchain.chat_models import GooglePalm  # type: ignore

    _HAS_GOOGLE_PALM = True
except Exception:
    _HAS_GOOGLE_PALM = False

from langchain.chat_models import init_chat_model


def create_llm(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    api_key: Optional[str] = None,
) -> object:
    gemini_key = api_key or os.getenv("GEMINI_API_KEY")
    gemini_model = model_name or os.getenv("GEMINI_MODEL", "gemini-pro")

    if not gemini_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    kwargs = {"model": gemini_model, "api_key": gemini_key}
    if temperature is not None:
        kwargs["temperature"] = temperature

    if _HAS_GOOGLE_PALM:
        return GooglePalm(**kwargs)

    try:
        import importlib

        if importlib.util.find_spec("langchain_google_genai"):
            base_kwargs = {k: v for k, v in kwargs.items() if k != "model"}
            return init_chat_model(
                model=gemini_model, model_provider="google_genai", **base_kwargs
            )
    except Exception:
        pass

    try:
        return init_chat_model(**kwargs)
    except Exception as e:  # pragma: no cover - environment dependent
        raise ImportError(
            "Could not initialize Gemini model via LangChain. Install the appropriate "
            "provider integration (e.g. langchain-google-genai or langchain-google-vertexai) "
            "or use a compatible langchain. Original error: " + str(e)
        )
