"""Stage 1: 이미지 → 구조화 데이터 추출 (Gemini Vision)."""

from __future__ import annotations

import asyncio
import json
import logging

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL, EXTRACT_TEMPERATURE
from analyzer.prompts import EXTRACT_SYSTEM, build_extract_prompt

logger = logging.getLogger(__name__)

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if not _client:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


async def extract_data(
    image_bytes: bytes,
    mime_type: str,
    context: str | None = None,
) -> dict:
    """이미지에서 제조 일보 데이터를 JSON으로 추출."""
    client = _get_client()

    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    user_prompt = build_extract_prompt(context)

    def _call():
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[image_part, types.Part.from_text(text=user_prompt)],
                ),
            ],
            config=types.GenerateContentConfig(
                system_instruction=EXTRACT_SYSTEM,
                temperature=EXTRACT_TEMPERATURE,
                response_mime_type="application/json",
            ),
        )
        return response.text

    raw = await asyncio.to_thread(_call)
    logger.info("Stage 1 추출 완료 (%d chars)", len(raw))

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("JSON 파싱 실패, raw 텍스트 반환")
        data = {"raw_text": raw, "parse_error": True}

    # 기본 구조 보장
    for key in ("production", "quality", "equipment", "workforce", "other", "metadata"):
        if key not in data:
            data[key] = {}

    return data
