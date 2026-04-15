"""Stage 1: 이미지 → 구조화 데이터 추출 (OpenAI Vision)."""

from __future__ import annotations

import base64
import json
import logging

from config import LLM_MODEL, EXTRACT_TEMPERATURE
from analyzer.llm import get_client
from analyzer.prompts import EXTRACT_SYSTEM, build_extract_prompt

logger = logging.getLogger(__name__)


async def extract_data(
    image_bytes: bytes,
    mime_type: str,
    context: str | None = None,
) -> dict:
    """이미지에서 제조 일보 데이터를 JSON으로 추출."""
    client = get_client()

    b64 = base64.b64encode(image_bytes).decode()
    user_prompt = build_extract_prompt(context)

    response = await client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": EXTRACT_SYSTEM},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{b64}"},
                    },
                    {"type": "text", "text": user_prompt},
                ],
            },
        ],
        temperature=EXTRACT_TEMPERATURE,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
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
