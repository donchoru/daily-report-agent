"""일보 에이전트 설정 — Keychain + 상수."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


# ── Keychain 읽기 ──────────────────────────────────────────────

def _read_keychain(service: str) -> str:
    try:
        r = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-w"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return ""


# ── 시크릿 ─────────────────────────────────────────────────────

LLM_BASE_URL: str = os.environ.get(
    "LLM_BASE_URL",
    "http://localhost:8000/v1",
)
LLM_API_KEY: str = (
    os.environ.get("LLM_API_KEY", "")
    or os.environ.get("GEMINI_API_KEY", "")
    or _read_keychain("GEMINI_API_KEY")
    or "not-needed"  # 인하우스 LLM은 키 불필요할 수 있음
)
LLM_MODEL: str = os.environ.get("LLM_MODEL", "Qwen/Qwen2.5-72B-Instruct")

# ── 경로 ───────────────────────────────────────────────────────
# PyInstaller 번들: 정적 파일은 _MEIPASS, DB/로그는 실행파일 옆

if getattr(sys, "frozen", False):
    BUNDLE_DIR = Path(sys._MEIPASS)              # 번들된 데이터 (static, analyzer 등)
    RUNTIME_DIR = Path(sys.executable).parent     # DB, 로그 저장 위치
else:
    BUNDLE_DIR = Path(__file__).resolve().parent
    RUNTIME_DIR = BUNDLE_DIR

BASE_DIR = BUNDLE_DIR  # 하위 호환
DB_PATH = RUNTIME_DIR / "report.db"
LOGS_DIR = RUNTIME_DIR / "logs"

LOGS_DIR.mkdir(exist_ok=True)

# ── LLM 설정 ───────────────────────────────────────────────────

# Stage 1: 추출 — 정확도 우선
EXTRACT_TEMPERATURE: float = 0.1
# Stage 2: 인사이트 — 분석 일관성
INSIGHT_TEMPERATURE: float = 0.3

# ── 분석 상수 ──────────────────────────────────────────────────

# 이상 판단 임계값
THRESHOLDS = {
    "achievement_rate_low": 90,      # 달성률 < 90% → HIGH
    "defect_rate_high": 3.0,         # 불량률 > 3% → HIGH
    "utilization_rate_low": 85,      # 가동률 < 85% → HIGH
    "achievement_rate_warning": 95,  # 달성률 < 95% → MEDIUM
    "defect_rate_warning": 2.0,      # 불량률 > 2% → MEDIUM
    "utilization_rate_warning": 90,  # 가동률 < 90% → MEDIUM
}

# 비교 분석 최대 이미지 수
MAX_COMPARE_IMAGES: int = 5

# 트렌드 분석 — 과거 데이터 참조 일수
TREND_LOOKBACK_DAYS: int = 7

# 업로드 이미지 최대 크기 (10MB)
MAX_IMAGE_SIZE: int = 10 * 1024 * 1024

# 허용 MIME 타입
ALLOWED_MIME_TYPES: set[str] = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
}

# ── 드릴다운 URL 매핑 ────────────────────────────────────────
# 지표 키워드 → 연계 시스템/화면 URL
# 실제 환경에 맞게 수정하세요

DRILLDOWN_LINKS: dict[str, list[dict]] = {
    "production": [
        {"name": "MES 생산 현황", "url": "/mes/production", "description": "실시간 생산 실적 모니터링"},
        {"name": "MES 작업 지시", "url": "/mes/work-order", "description": "작업 지시서 상세"},
    ],
    "quality": [
        {"name": "QMS 불량 현황", "url": "/qms/defects", "description": "불량 유형별 상세 분석"},
        {"name": "QMS SPC 관리도", "url": "/qms/spc", "description": "통계적 공정 관리"},
        {"name": "QMS 검사 이력", "url": "/qms/inspection", "description": "검사 결과 이력 조회"},
    ],
    "equipment": [
        {"name": "EAM 설비 현황", "url": "/eam/status", "description": "설비 가동/비가동 실시간"},
        {"name": "EAM 정비 이력", "url": "/eam/maintenance", "description": "정비 이력 및 예정"},
        {"name": "EAM 고장 분석", "url": "/eam/failure", "description": "고장 유형별 분석"},
    ],
    "workforce": [
        {"name": "HR 근태 현황", "url": "/hr/attendance", "description": "출퇴근/잔업 현황"},
        {"name": "HR 인력 배치", "url": "/hr/assignment", "description": "라인별 인력 배치 현황"},
    ],
    "inventory": [
        {"name": "WMS 재고 현황", "url": "/wms/inventory", "description": "자재/완제품 재고"},
        {"name": "WMS 입출고", "url": "/wms/io", "description": "입출고 이력"},
    ],
    "energy": [
        {"name": "EMS 에너지 현황", "url": "/ems/usage", "description": "전력/가스/용수 사용량"},
    ],
    "cost": [
        {"name": "원가 분석", "url": "/cost/analysis", "description": "제조 원가 상세"},
    ],
}

# 드릴다운 베이스 URL (프론트엔드 기준 — 실제 환경에 맞게 수정)
DRILLDOWN_BASE_URL: str = os.environ.get("DRILLDOWN_BASE_URL", "")


# ── DB에서 설정 로드 ──────────────────────────────────────────────

async def load_settings_from_db(db) -> None:
    """DB settings 테이블에서 LLM 설정을 로드하여 모듈 변수에 반영."""
    global LLM_BASE_URL, LLM_API_KEY, LLM_MODEL
    settings = await db.get_all_settings()
    if "llm_base_url" in settings:
        LLM_BASE_URL = settings["llm_base_url"]
    if "llm_api_key" in settings:
        LLM_API_KEY = settings["llm_api_key"]
    if "llm_model" in settings:
        LLM_MODEL = settings["llm_model"]
