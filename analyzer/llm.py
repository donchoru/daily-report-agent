"""공유 OpenAI 클라이언트 — any OpenAI-compatible endpoint.

인하우스 vLLM/Ollama 호환: response_format 미지원 시 자동 폴백.
FLOPI 검증 패턴 적용: URL 정규화, keepalive 비활성화, timeout 세분화.
"""

from __future__ import annotations

import json
import logging
import os
import re

import httpx
from openai import AsyncOpenAI

import config

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None


def _normalize_base_url(url: str) -> str:
    """사내 LLM URL 정규화 — FLOPI 검증 패턴."""
    url = url.strip().rstrip("/")
    if url.endswith("/chat/completions"):
        url = url.removesuffix("/chat/completions")
        logger.info("base_url에서 /chat/completions 자동 제거: %s", url)
    if url and not url.startswith(("http://", "https://")):
        url = f"http://{url}"
        logger.info("base_url에 http:// 자동 추가: %s", url)
    return url


def get_client() -> AsyncOpenAI:
    global _client
    if not _client:
        base_url = _normalize_base_url(config.LLM_BASE_URL)
        api_key = config.LLM_API_KEY or "sk-placeholder"
        ssl_verify = os.getenv("LLM_SSL_VERIFY", "true").lower() != "false"
        _client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            max_retries=0,
            http_client=httpx.AsyncClient(
                verify=ssl_verify,
                timeout=httpx.Timeout(
                    connect=10.0,
                    read=120.0,
                    write=10.0,
                    pool=10.0,
                ),
                limits=httpx.Limits(
                    max_keepalive_connections=0,
                    keepalive_expiry=0,
                ),
            ),
        )
        logger.info("LLM client 생성: %s (model=%s)", base_url, config.LLM_MODEL)
    return _client


def reset_client() -> None:
    """설정 변경 시 기존 클라이언트 폐기 — 다음 get_client() 호출 시 재생성."""
    global _client
    _client = None


def parse_json_response(text: str) -> dict | list | None:
    """LLM 응답에서 JSON을 추출. 마크다운 코드블록도 처리."""
    if not text:
        return None

    # 1) 그대로 파싱
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2) ```json ... ``` 블록 추출
    m = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 3) 첫 { ... 마지막 } 범위 추출
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    # 4) 배열 형태 [ ... ]
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    return None


async def safe_completion(
    messages: list[dict],
    *,
    temperature: float = 0.3,
    expect_json: bool = True,
) -> str:
    """LLM 호출 — response_format 미지원 시 자동 폴백.

    Args:
        messages: OpenAI 형식 메시지 목록
        temperature: 생성 온도
        expect_json: True면 JSON 응답을 유도 (프롬프트 보강 + 파싱)

    Returns:
        LLM 응답 텍스트 (raw)
    """
    client = get_client()
    model = config.LLM_MODEL

    # 1차: response_format 사용 시도
    if expect_json:
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content
        except Exception as e:
            err_msg = str(e).lower()
            # response_format 미지원 에러만 폴백
            if any(kw in err_msg for kw in (
                "response_format", "json_object", "not supported",
                "unrecognized", "unexpected keyword", "extra inputs",
            )):
                logger.info("response_format 미지원 — 폴백 모드")
            else:
                raise  # 다른 에러는 그대로 raise

    # 2차: response_format 없이 호출 (JSON 프롬프트 보강)
    if expect_json:
        # 마지막 user 메시지에 JSON 강조 추가
        msgs = [m.copy() for m in messages]
        for m in reversed(msgs):
            if m["role"] == "user":
                if isinstance(m["content"], str):
                    m["content"] += "\n\n반드시 JSON으로만 응답하세요. 다른 텍스트 없이 JSON만 출력하세요."
                break
    else:
        msgs = messages

    response = await client.chat.completions.create(
        model=model,
        messages=msgs,
        temperature=temperature,
    )
    return response.choices[0].message.content
