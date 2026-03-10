"""일보 에이전트 — FastAPI 서버 (8700).

제조 일보 이미지를 Gemini Vision으로 분석하여
이상탐지·트렌드·요약·액션아이템을 제공.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from analyzer.chat import chat_with_analysis, extract_memories
from analyzer.drilldown import get_drilldown_links
from analyzer.extractor import extract_data
from analyzer.insights import (
    generate_comparison,
    generate_headlines,
    generate_insights,
    reanalyze_with_perspective,
)
from config import ALLOWED_MIME_TYPES, MAX_COMPARE_IMAGES, MAX_IMAGE_SIZE
from db import Database
from models import AnalysisResponse, CompareResponse, HistoryItem

# ── 로깅 ──────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/report.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("daily-report")

# ── 전역 객체 ─────────────────────────────────────────────────

db = Database()


# ── Lifespan ──────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.open()
    logger.info("DB initialized")
    yield
    await db.close()
    logger.info("Shutdown complete")


# ── FastAPI ───────────────────────────────────────────────────

app = FastAPI(
    title="Daily Report Agent",
    version="1.0.0",
    description="제조 일보 이미지 AI 분석 API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 유틸 ──────────────────────────────────────────────────────

def _validate_image(file: UploadFile, content: bytes) -> None:
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            400,
            f"지원하지 않는 이미지 형식: {file.content_type}. "
            f"허용: {', '.join(ALLOWED_MIME_TYPES)}",
        )
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            400,
            f"이미지 크기 초과: {len(content) / 1024 / 1024:.1f}MB "
            f"(최대 {MAX_IMAGE_SIZE / 1024 / 1024:.0f}MB)",
        )


# ── POST /analyze — 단일 이미지 분석 ─────────────────────────

@app.post("/analyze")
async def analyze(
    image: UploadFile = File(..., description="일보 이미지"),
    report_date: str | None = Form(None, description="일보 날짜 (YYYY-MM-DD)"),
    report_type: str | None = Form(None, description="일보 유형"),
    department: str | None = Form(None, description="부서/라인명"),
    context: str | None = Form(None, description="추가 맥락"),
):
    start = time.time()
    content = await image.read()
    _validate_image(image, content)

    analysis_id = str(uuid.uuid4())[:8]
    image_hash = hashlib.sha256(content).hexdigest()

    # 관심사 로드
    interests = await db.get_interests()

    # Stage 1: 이미지 → 구조화 데이터
    logger.info("분석 시작: %s (image=%s, %d bytes)", analysis_id, image.filename, len(content))
    extracted = await extract_data(content, image.content_type, context)

    # 과거 데이터 조회 (트렌드용)
    historical = await db.get_recent_extracted(department)

    # Stage 2: 데이터 → 인사이트 (관심사 반영)
    insights = await generate_insights(extracted, historical, context, interests)

    # 헤드라인 생성
    analysis_for_headline = {
        "extracted_data": extracted,
        "insights": insights,
        "report_date": report_date,
        "department": department,
    }
    headlines = await generate_headlines(analysis_for_headline, interests)

    # 드릴다운 링크
    drilldown = get_drilldown_links(extracted, insights)

    elapsed = round(time.time() - start, 2)

    # DB 저장
    await db.save_analysis(
        analysis_id=analysis_id,
        report_date=report_date,
        report_type=report_type,
        department=department,
        extracted_data=extracted,
        insights=insights,
        processing_time_sec=elapsed,
    )
    await db.save_image_meta(
        analysis_id=analysis_id,
        filename=image.filename or "unknown",
        mime_type=image.content_type,
        file_size=len(content),
        image_hash=image_hash,
    )

    logger.info("분석 완료: %s (%.2fs)", analysis_id, elapsed)

    return {
        "id": analysis_id,
        "report_date": report_date,
        "report_type": report_type,
        "department": department,
        "extracted_data": extracted,
        "insights": insights,
        "headlines": headlines,
        "drilldown_links": drilldown,
        "processing_time_sec": elapsed,
    }


# ── POST /compare — DB 누적 데이터 기반 비교 분석 ─────────────


class CompareRequest(BaseModel):
    analysis_ids: list[str] | None = None
    date_from: str | None = None
    date_to: str | None = None
    department: str | None = None


@app.post("/compare")
async def compare_analyses(req: CompareRequest):
    start = time.time()

    # 방법 1: analysis_ids 직접 지정
    if req.analysis_ids:
        if len(req.analysis_ids) < 2:
            raise HTTPException(400, "최소 2개의 분석 ID가 필요합니다")
        analyses = []
        for aid in req.analysis_ids:
            a = await db.get_analysis(aid)
            if not a:
                raise HTTPException(404, f"분석 결과를 찾을 수 없습니다: {aid}")
            analyses.append(a)

    # 방법 2: 날짜 범위로 조회
    elif req.date_from:
        analyses = await db.get_analyses_by_date_range(
            date_from=req.date_from,
            date_to=req.date_to,
            department=req.department,
        )
        if len(analyses) < 2:
            raise HTTPException(400, f"해당 기간에 분석 결과가 {len(analyses)}건뿐입니다. 최소 2건 필요.")
    else:
        raise HTTPException(400, "analysis_ids 또는 date_from을 지정하세요")

    if len(analyses) > MAX_COMPARE_IMAGES:
        raise HTTPException(400, f"최대 {MAX_COMPARE_IMAGES}건까지 비교 가능합니다. ({len(analyses)}건 조회됨)")

    # 비교용 데이터 구성
    analyses_for_compare = [
        {
            "date": a.get("report_date") or a["id"],
            "department": a.get("department"),
            "extracted_data": a["extracted_data"],
            "insights": a["insights"],
        }
        for a in analyses
    ]

    comparison = await generate_comparison(analyses_for_compare)
    elapsed = round(time.time() - start, 2)

    logger.info("비교 분석 완료: %d건, %.2fs", len(analyses), elapsed)

    return {
        "analyses": [
            {
                "id": a["id"],
                "report_date": a.get("report_date"),
                "department": a.get("department"),
                "summary": a["insights"].get("summary", ""),
            }
            for a in analyses
        ],
        "comparison": comparison,
        "processing_time_sec": elapsed,
    }


# ── GET /timeline — 날짜별 누적 데이터 타임라인 ──────────────

@app.get("/timeline")
async def get_timeline(
    department: str | None = None,
    days: int = 30,
):
    items = await db.get_timeline(department=department, days=days)
    return {"items": items, "count": len(items), "days": days}


# ── GET /history — 과거 분석 조회 ─────────────────────────────

@app.get("/history")
async def get_history(
    department: str | None = None,
    report_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    items = await db.get_history(
        department=department,
        report_type=report_type,
        limit=limit,
        offset=offset,
    )
    return {"items": items, "count": len(items)}


# ── GET /history/{id} — 단건 조회 ────────────────────────────

@app.get("/history/{analysis_id}")
async def get_analysis_detail(analysis_id: str):
    result = await db.get_analysis(analysis_id)
    if not result:
        raise HTTPException(404, f"분석 결과를 찾을 수 없습니다: {analysis_id}")
    return result


# ── POST /chat/{analysis_id} — 분석 결과 기반 대화 ────────────


class ChatRequest(BaseModel):
    message: str


@app.post("/chat/{analysis_id}")
async def chat(analysis_id: str, req: ChatRequest):
    analysis = await db.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(404, f"분석 결과를 찾을 수 없습니다: {analysis_id}")

    # 대화 이력 + 메모리 로드
    history = await db.get_conversations(analysis_id)
    memories = await db.get_memories()

    # AI 응답 생성
    response = await chat_with_analysis(analysis, req.message, history, memories)

    # 대화 저장
    await db.add_conversation(analysis_id, "user", req.message)
    await db.add_conversation(analysis_id, "assistant", response)

    # 장기 메모리 자동 추출 (백그라운드)
    new_memories = await extract_memories(req.message, response)
    saved_memories = []
    for mem in new_memories:
        mid = await db.save_memory(
            category=mem.get("category", "domain"),
            content=mem["content"],
            source_analysis_id=analysis_id,
        )
        saved_memories.append({"id": mid, **mem})

    logger.info(
        "대화: %s — 메모리 %d건 추출",
        analysis_id,
        len(saved_memories),
    )

    return {
        "response": response,
        "memories_extracted": saved_memories,
    }


# ── GET /chat/{analysis_id}/history — 대화 이력 조회 ──────────

@app.get("/chat/{analysis_id}/history")
async def get_chat_history(analysis_id: str):
    analysis = await db.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(404, f"분석 결과를 찾을 수 없습니다: {analysis_id}")
    history = await db.get_conversations(analysis_id)
    return {"analysis_id": analysis_id, "messages": history}


# ── GET /memories — 장기 메모리 조회 ──────────────────────────

@app.get("/memories")
async def get_memories(category: str | None = None, limit: int = 100):
    memories = await db.get_memories(category=category, limit=limit)
    return {"memories": memories, "count": len(memories)}


# ── DELETE /memories/{id} — 메모리 삭제 ──────────────────────

@app.delete("/memories/{memory_id}")
async def delete_memory(memory_id: int):
    deleted = await db.delete_memory(memory_id)
    if not deleted:
        raise HTTPException(404, f"메모리를 찾을 수 없습니다: {memory_id}")
    return {"deleted": True}


# ── 관심사 (Interests) ────────────────────────────────────────


class InterestRequest(BaseModel):
    metric: str
    priority: int = 1
    description: str = ""


@app.get("/interests")
async def get_interests():
    interests = await db.get_interests()
    return {"interests": interests, "count": len(interests)}


@app.post("/interests")
async def set_interest(req: InterestRequest):
    interest_id = await db.set_interest(
        metric=req.metric,
        priority=req.priority,
        description=req.description,
    )
    logger.info("관심사 설정: %s (priority=%d)", req.metric, req.priority)
    return {"id": interest_id, "metric": req.metric, "priority": req.priority}


@app.delete("/interests/{interest_id}")
async def delete_interest(interest_id: int):
    deleted = await db.delete_interest(interest_id)
    if not deleted:
        raise HTTPException(404, f"관심사를 찾을 수 없습니다: {interest_id}")
    return {"deleted": True}


# ── GET /headlines/{id} — 헤드라인 생성 ──────────────────────

@app.get("/headlines/{analysis_id}")
async def get_headlines(analysis_id: str):
    analysis = await db.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(404, f"분석 결과를 찾을 수 없습니다: {analysis_id}")
    interests = await db.get_interests()
    headlines = await generate_headlines(analysis, interests)
    return {"analysis_id": analysis_id, "headlines": headlines}


# ── POST /reanalyze/{id} — 기존 데이터를 다른 관점으로 재분석 ──


class ReanalyzeRequest(BaseModel):
    perspective: str


PERSPECTIVE_PRESETS: dict[str, str] = {
    "cost": "원가/비용 관점: 생산 원가, 불량 비용, 에너지 비용 등 금액 기반으로 재해석",
    "bottleneck": "병목 관점: 전체 공정에서 가장 느린 구간, 대기시간, 처리량 제약 분석",
    "trend": "추세 관점: 시계열 변화에 집중. 일별/주별 추이, 이동평균, 변화 가속도",
    "risk": "리스크 관점: 잠재적 위험 요소, 안전 이슈, 품질 리스크 우선 분석",
    "efficiency": "효율성 관점: OEE, 시간당 생산량, 인당 생산성 등 효율 지표 중심",
    "comparison": "라인/설비 비교 관점: 라인별, 설비별 성과 차이 및 Best/Worst 분석",
}


@app.get("/reanalyze/perspectives")
async def list_perspectives():
    return {
        "presets": [
            {"key": k, "description": v}
            for k, v in PERSPECTIVE_PRESETS.items()
        ],
        "custom": "직접 관점을 텍스트로 입력할 수도 있습니다",
    }


@app.post("/reanalyze/{analysis_id}")
async def reanalyze(analysis_id: str, req: ReanalyzeRequest):
    analysis = await db.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(404, f"분석 결과를 찾을 수 없습니다: {analysis_id}")

    # 프리셋이면 상세 설명으로 변환
    perspective = PERSPECTIVE_PRESETS.get(req.perspective, req.perspective)

    interests = await db.get_interests()

    start = time.time()
    result = await reanalyze_with_perspective(
        extracted_data=analysis["extracted_data"],
        original_insights=analysis["insights"],
        perspective=perspective,
        interests=interests,
    )

    # 드릴다운 링크 (재분석 결과에도 제공)
    drilldown = get_drilldown_links(analysis["extracted_data"], analysis["insights"])
    elapsed = round(time.time() - start, 2)

    logger.info("재분석 완료: %s → %s (%.2fs)", analysis_id, req.perspective, elapsed)

    return {
        "analysis_id": analysis_id,
        "perspective": req.perspective,
        "result": result,
        "drilldown_links": drilldown,
        "processing_time_sec": elapsed,
    }


# ── GET /drilldown/{id} — 드릴다운 링크 조회 ─────────────────

@app.get("/drilldown/{analysis_id}")
async def get_drilldown(analysis_id: str):
    analysis = await db.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(404, f"분석 결과를 찾을 수 없습니다: {analysis_id}")
    links = get_drilldown_links(analysis["extracted_data"], analysis["insights"])
    return {"analysis_id": analysis_id, "drilldown_links": links}


# ── GET /health — 헬스체크 ────────────────────────────────────

@app.get("/health")
async def health():
    stats = await db.get_stats()
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "db_stats": stats,
    }


# ── 메인 ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8700)
