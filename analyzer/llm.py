"""공유 OpenAI 클라이언트 — any OpenAI-compatible endpoint."""

from __future__ import annotations

from openai import AsyncOpenAI

import config

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if not _client:
        _client = AsyncOpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)
    return _client


def reset_client() -> None:
    """설정 변경 시 기존 클라이언트 폐기 — 다음 get_client() 호출 시 재생성."""
    global _client
    _client = None
