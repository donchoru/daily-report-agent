"""공유 OpenAI 클라이언트 — any OpenAI-compatible endpoint."""

from __future__ import annotations

from openai import AsyncOpenAI

from config import LLM_BASE_URL, LLM_API_KEY

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if not _client:
        _client = AsyncOpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)
    return _client
