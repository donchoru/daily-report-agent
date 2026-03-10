"""일보 에이전트 — Pydantic 스키마."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── 요청 ───────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """POST /analyze 의 폼 필드 (이미지는 UploadFile로 별도 수신)."""
    report_date: str | None = Field(None, description="일보 날짜 (YYYY-MM-DD)")
    report_type: str | None = Field(None, description="일보 유형 (production, quality, equipment 등)")
    department: str | None = Field(None, description="부서/라인명")
    context: str | None = Field(None, description="추가 맥락 (목표치, 특이사항 등)")


# ── Stage 1: 추출 결과 ─────────────────────────────────────────

class ExtractedData(BaseModel):
    production: dict = Field(default_factory=dict, description="생산 관련 수치")
    quality: dict = Field(default_factory=dict, description="품질 관련 수치")
    equipment: dict = Field(default_factory=dict, description="설비 관련 수치")
    workforce: dict = Field(default_factory=dict, description="인력 관련 수치")
    other: dict = Field(default_factory=dict, description="기타 수치/메모")
    metadata: dict = Field(default_factory=dict, description="표/차트 메타 정보")


# ── Stage 2: 인사이트 ──────────────────────────────────────────

class Anomaly(BaseModel):
    metric: str = Field(description="이상 지표명")
    value: str = Field(description="실제 값")
    expected: str = Field(default="", description="기대 값/기준")
    severity: str = Field(default="MEDIUM", description="HIGH / MEDIUM / LOW")
    description: str = Field(default="", description="설명")


class Trend(BaseModel):
    metric: str = Field(description="지표명")
    direction: str = Field(description="up / down / stable")
    description: str = Field(default="", description="트렌드 설명")


class ActionItem(BaseModel):
    priority: str = Field(default="MEDIUM", description="HIGH / MEDIUM / LOW")
    action: str = Field(description="액션 내용")
    responsible: str = Field(default="", description="담당자/부서")


class Insights(BaseModel):
    anomalies: list[Anomaly] = Field(default_factory=list)
    trends: list[Trend] = Field(default_factory=list)
    summary: str = Field(default="", description="종합 요약 (3~5문장)")
    action_items: list[ActionItem] = Field(default_factory=list)


# ── 응답 ───────────────────────────────────────────────────────

class AnalysisResponse(BaseModel):
    id: str
    report_date: str | None = None
    report_type: str | None = None
    department: str | None = None
    extracted_data: ExtractedData
    insights: Insights
    processing_time_sec: float


class CompareResponse(BaseModel):
    individual: list[AnalysisResponse]
    comparison: dict = Field(default_factory=dict, description="변화/개선/악화 비교")
    processing_time_sec: float


class HistoryItem(BaseModel):
    id: str
    report_date: str | None = None
    report_type: str | None = None
    department: str | None = None
    summary: str = ""
    processing_time_sec: float = 0.0
    created_at: str = ""
