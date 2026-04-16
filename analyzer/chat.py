"""분석 결과 기반 후속 대화 + 장기 메모리 추출 (vLLM 호환)."""

from __future__ import annotations

import json
import logging

from config import LLM_MODEL, INSIGHT_TEMPERATURE
from analyzer.llm import get_client, safe_completion, parse_json_response

logger = logging.getLogger(__name__)


CHAT_SYSTEM = """당신은 제조 현장 전문 AI 분석가입니다.
사용자가 일보 분석 결과를 보면서 추가 질문을 합니다.

## 분석 결과 컨텍스트
{analysis_context}

## 사용자의 도메인 지식 (장기 메모리)
{memories}

## 규칙
1. 분석 결과의 데이터에 근거하여 답변
2. 사용자가 알려주는 현장 정보(목표치, 설비 특성, 관행 등)는 매우 소중한 도메인 지식
3. 구체적이고 실행 가능한 조언 제공
4. 한국어로 대화
5. 사용자의 질문이 분석과 관련없어도 친절하게 응대"""

MEMORY_EXTRACT_SYSTEM = """대화에서 장기 보존할 도메인 지식을 추출하세요.

## 추출 대상 (사용자가 알려주는 정보만)
- 공장/라인별 특성 (예: "A라인은 원래 가동률이 낮아", "2공장은 불량률 기준이 2%")
- 목표치/기준 (예: "이번 달 생산 목표는 5000개", "불량률 1.5% 이하가 목표")
- 설비 정보 (예: "CNC-3은 다음 주 정비 예정", "프레스 2호기는 야간에 안 돌려")
- 인력/조직 (예: "야간조는 8명", "품질팀 김과장이 담당")
- 분석 선호 (예: "불량률은 항상 먼저 봐줘", "전일 대비 변화가 중요해")

## 규칙
- 사용자가 명시적으로 알려준 정보만 추출
- AI가 생성한 분석 내용은 추출하지 마세요
- 추출할 게 없으면 빈 배열 반환

JSON 배열로 응답:
[
  {"category": "threshold|equipment|workforce|preference|domain", "content": "..."}
]
빈 경우: []"""


async def chat_with_analysis(
    analysis: dict,
    message: str,
    conversation_history: list[dict],
    memories: list[dict],
) -> str:
    """분석 결과를 컨텍스트로 사용자와 대화."""
    client = get_client()

    # 분석 컨텍스트 구성
    analysis_context = json.dumps(
        {
            "report_date": analysis.get("report_date"),
            "department": analysis.get("department"),
            "extracted_data": analysis.get("extracted_data"),
            "insights": analysis.get("insights"),
        },
        ensure_ascii=False,
        indent=2,
    )

    memories_str = "없음"
    if memories:
        memories_str = "\n".join(
            f"- [{m['category']}] {m['content']}" for m in memories
        )

    system = CHAT_SYSTEM.format(
        analysis_context=analysis_context,
        memories=memories_str,
    )

    # 메시지 목록 구성: system + 대화 이력 + 현재 메시지
    messages: list[dict] = [{"role": "system", "content": system}]
    for msg in conversation_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    response = await client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=INSIGHT_TEMPERATURE,
    )
    return response.choices[0].message.content


async def extract_memories(
    user_message: str,
    assistant_response: str,
) -> list[dict]:
    """대화에서 장기 보존할 도메인 지식을 추출."""
    prompt = f"""## 사용자 메시지
{user_message}

## AI 응답
{assistant_response}

위 대화에서 사용자가 알려준 도메인 지식을 추출하세요."""

    raw = await safe_completion(
        messages=[
            {"role": "system", "content": MEMORY_EXTRACT_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        expect_json=True,
    )

    result = parse_json_response(raw)
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        for v in result.values():
            if isinstance(v, list):
                return v
    return []
