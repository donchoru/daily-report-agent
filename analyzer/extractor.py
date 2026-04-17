"""Stage 1: 이미지 → 구조화 데이터 추출.

두 가지 모드:
1. Vision 모델 (Qwen2.5-VL, GPT-4V 등) → 이미지 직접 전송
2. 텍스트 모델 (Qwen3.0, Llama 등) → OCR로 텍스트 추출 후 LLM 분석
"""

from __future__ import annotations

import base64
import io
import json
import logging

from config import LLM_MODEL, EXTRACT_TEMPERATURE
from analyzer.llm import get_client, safe_completion, parse_json_response, _is_gemini_model
from analyzer.prompts import EXTRACT_SYSTEM, build_extract_prompt

logger = logging.getLogger(__name__)


def _ocr_image(image_bytes: bytes) -> str:
    """OCR로 이미지에서 텍스트 추출. tesseract(한글) 우선, rapidocr 폴백."""
    from analyzer.ocr import ocr_image
    return ocr_image(image_bytes)


async def extract_data(
    image_bytes: bytes,
    mime_type: str,
    context: str | None = None,
) -> dict:
    """이미지에서 제조 일보 데이터를 JSON으로 추출.

    1) Vision API 시도
    2) 실패 시 OCR → 텍스트 LLM 폴백
    """
    # ── 1차: Vision API 시도 ──────────────────────────────────
    try:
        data = await _extract_with_vision(image_bytes, mime_type, context)
        return data
    except Exception as e:
        err = str(e).lower()
        vision_fail = any(kw in err for kw in (
            "image", "vision", "multimodal", "content_type",
            "invalid_request", "does not support", "cannot process",
            "unsupported", "content part", "invalid value",
            "invalid_value", "not support",
        ))
        if vision_fail:
            logger.info("Vision 미지원 → OCR 폴백 (%s: %s)", LLM_MODEL, e)
        else:
            # 연결 오류 등은 OCR로도 안 됨 — 바로 raise
            connection_err = any(kw in err for kw in (
                "connection", "connect", "timeout", "refused", "unreachable",
            ))
            if connection_err:
                raise
            logger.warning("Vision 호출 실패 → OCR 폴백 시도: %s", e)

    # ── 2차: OCR + 텍스트 LLM ─────────────────────────────────
    return await _extract_with_ocr(image_bytes, context)


async def _extract_with_vision(
    image_bytes: bytes,
    mime_type: str,
    context: str | None,
) -> dict:
    """Vision 모델로 이미지 직접 분석."""
    client = get_client()
    b64 = base64.b64encode(image_bytes).decode()
    user_prompt = build_extract_prompt(context)

    # Qwen/vLLM: response_format 사용 안 함 (peer closed 방지)
    kwargs: dict = {
        "model": LLM_MODEL,
        "messages": [
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
        "temperature": EXTRACT_TEMPERATURE,
    }
    if _is_gemini_model():
        kwargs["response_format"] = {"type": "json_object"}
    else:
        # Qwen: 프롬프트로 JSON 유도
        kwargs["messages"][1]["content"][-1]["text"] += "\n\n반드시 JSON으로만 응답하세요."

    response = await client.chat.completions.create(**kwargs)

    raw = response.choices[0].message.content
    logger.info("Vision 추출 완료 (%d chars)", len(raw))
    return _parse_extracted(raw)


async def _extract_with_ocr(
    image_bytes: bytes,
    context: str | None,
) -> dict:
    """OCR로 텍스트 추출 후 텍스트 LLM으로 분석."""
    logger.info("OCR 모드로 추출 시작")
    ocr_text = _ocr_image(image_bytes)

    if ocr_text.startswith("(이미지에서"):
        return {
            "raw_text": ocr_text,
            "parse_error": True,
            "production": {}, "quality": {}, "equipment": {},
            "workforce": {}, "other": {}, "metadata": {"ocr_mode": True},
        }

    # OCR 텍스트를 LLM에 전달하여 구조화
    ocr_prompt = f"""아래는 제조 일보 이미지에서 OCR로 추출한 텍스트입니다.
이 텍스트를 분석하여 구조화된 JSON으로 변환해주세요.

## OCR 추출 텍스트
{ocr_text}

{f"## 추가 맥락{chr(10)}{context}" if context else ""}

다음 구조로 응답하세요:
{{
  "production": {{
    "계획": "...", "실적": "...", "달성률": "...",
    "품목별": [...]
  }},
  "quality": {{
    "불량수": "...", "불량률": "...",
    "불량유형": [...]
  }},
  "equipment": {{
    "가동시간": "...", "비가동시간": "...", "가동률": "...",
    "설비별": [...]
  }},
  "workforce": {{
    "출근인원": "...", "결근": "...", "잔업": "..."
  }},
  "other": {{
    "특이사항": "...", "기타_수치": {{}}
  }},
  "metadata": {{
    "report_date": "...",
    "department": "...",
    "report_type": "...",
    "tables_found": 0,
    "charts_found": 0,
    "ocr_mode": true
  }}
}}

해당 카테고리에 데이터가 없으면 빈 객체 {{}}로 두세요.
OCR 텍스트에 있는 모든 수치를 빠짐없이 매핑하는 것이 가장 중요합니다."""

    raw = await safe_completion(
        messages=[
            {"role": "system", "content": EXTRACT_SYSTEM},
            {"role": "user", "content": ocr_prompt},
        ],
        temperature=EXTRACT_TEMPERATURE,
        expect_json=True,
    )
    logger.info("OCR→LLM 추출 완료 (%d chars)", len(raw))
    return _parse_extracted(raw)


def _parse_extracted(raw: str) -> dict:
    """LLM 응답을 파싱하고 기본 구조 보장."""
    data = parse_json_response(raw)
    if not isinstance(data, dict):
        logger.warning("JSON 파싱 실패, raw 텍스트 반환")
        data = {"raw_text": raw[:2000], "parse_error": True}

    for key in ("production", "quality", "equipment", "workforce", "other", "metadata"):
        if key not in data:
            data[key] = {}

    return data
