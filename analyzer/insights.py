"""Stage 2: 추출 데이터 → 인사이트 생성 (OpenAI-compatible)."""

from __future__ import annotations

import json
import logging

from config import LLM_MODEL, INSIGHT_TEMPERATURE
from analyzer.llm import get_client
from analyzer.prompts import (
    INSIGHT_SYSTEM,
    COMPARE_SYSTEM,
    HEADLINE_SYSTEM,
    REANALYZE_SYSTEM,
    build_insight_prompt,
    build_compare_prompt,
    build_headline_prompt,
    build_reanalyze_prompt,
)

logger = logging.getLogger(__name__)


async def generate_insights(
    extracted_data: dict,
    historical_data: list[dict] | None = None,
    context: str | None = None,
    interests: list[dict] | None = None,
) -> dict:
    """추출 데이터 + 과거 데이터로 인사이트 생성."""
    client = get_client()

    hist_str = "없음"
    if historical_data:
        hist_str = json.dumps(historical_data, ensure_ascii=False, indent=2)

    interests_str = "없음"
    if interests:
        interests_str = "\n".join(
            f"- [{i.get('priority', 1)}순위] {i['metric']}: {i.get('description', '')}"
            for i in interests
        )

    prompt = build_insight_prompt(
        extracted_data=json.dumps(extracted_data, ensure_ascii=False, indent=2),
        historical_data=hist_str,
        context=context,
        interests=interests_str,
    )

    response = await client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": INSIGHT_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=INSIGHT_TEMPERATURE,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    logger.info("Stage 2 인사이트 생성 완료 (%d chars)", len(raw))

    try:
        insights = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("인사이트 JSON 파싱 실패")
        insights = {
            "anomalies": [],
            "trends": [],
            "summary": raw[:500],
            "action_items": [],
        }

    # 기본 구조 보장
    for key in ("anomalies", "trends", "action_items"):
        if key not in insights:
            insights[key] = []
    if "summary" not in insights:
        insights["summary"] = ""

    return insights


async def generate_comparison(analyses: list[dict]) -> dict:
    """다중 분석 결과를 비교."""
    client = get_client()

    analyses_str = json.dumps(analyses, ensure_ascii=False, indent=2)
    prompt = build_compare_prompt(analyses_str, len(analyses))

    response = await client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": COMPARE_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=INSIGHT_TEMPERATURE,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    logger.info("비교 분석 완료 (%d chars)", len(raw))

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"overall_assessment": raw[:500], "parse_error": True}


async def generate_headlines(
    analysis: dict,
    interests: list[dict] | None = None,
) -> dict:
    """분석 결과에서 헤드라인 생성."""
    client = get_client()

    analysis_str = json.dumps(
        {
            "extracted_data": analysis.get("extracted_data"),
            "insights": analysis.get("insights"),
            "report_date": analysis.get("report_date"),
            "department": analysis.get("department"),
        },
        ensure_ascii=False,
        indent=2,
    )

    interests_str = "없음"
    if interests:
        interests_str = "\n".join(
            f"- [{i.get('priority', 1)}순위] {i['metric']}: {i.get('description', '')}"
            for i in interests
        )

    prompt = build_headline_prompt(analysis_str, interests_str)

    response = await client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": HEADLINE_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    logger.info("헤드라인 생성 완료 (%d chars)", len(raw))

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "main_headline": raw[:100],
            "sub_headlines": [],
            "sentiment": "neutral",
        }


async def reanalyze_with_perspective(
    extracted_data: dict,
    original_insights: dict,
    perspective: str,
    interests: list[dict] | None = None,
) -> dict:
    """기존 추출 데이터를 다른 관점으로 재분석."""
    client = get_client()

    interests_str = "없음"
    if interests:
        interests_str = "\n".join(
            f"- [{i.get('priority', 1)}순위] {i['metric']}: {i.get('description', '')}"
            for i in interests
        )

    prompt = build_reanalyze_prompt(
        extracted_data=json.dumps(extracted_data, ensure_ascii=False, indent=2),
        original_insights=json.dumps(original_insights, ensure_ascii=False, indent=2),
        perspective=perspective,
        interests=interests_str,
    )

    response = await client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": REANALYZE_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=INSIGHT_TEMPERATURE,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    logger.info("재분석 완료: %s (%d chars)", perspective, len(raw))

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"perspective": perspective, "summary": raw[:500], "parse_error": True}
