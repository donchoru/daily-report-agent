"""일보 에이전트 — extracted_data → daily_metrics 행 변환.

한국어 수치 문자열 파싱 + 단일/다중 날짜 감지.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


# ── 수치 파서 ────────────────────────────────────────────────────

def parse_numeric(v: Any) -> float | None:
    """한국어 수치 문자열 → float.

    "1,234개" → 1234.0, "98.5%" → 98.5, "없음" → None
    """
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s or s in ("없음", "해당없음", "-", "N/A", ""):
        return None
    # 콤마·단위 제거, 숫자+소수점만 추출
    cleaned = re.sub(r"[^\d.\-]", "", s.replace(",", ""))
    if not cleaned or cleaned in (".", "-"):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_duration_to_minutes(v: Any) -> float | None:
    """시간 표현 → 분 단위 float.

    "2시간 30분" → 150.0, "38분" → 38.0, "1.5시간" → 90.0
    """
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s or s in ("없음", "-", "N/A"):
        return None

    total = 0.0
    found = False

    # 시간 매칭
    h_match = re.search(r"(\d+(?:\.\d+)?)\s*시간", s)
    if h_match:
        total += float(h_match.group(1)) * 60
        found = True

    # 분 매칭
    m_match = re.search(r"(\d+(?:\.\d+)?)\s*분", s)
    if m_match:
        total += float(m_match.group(1))
        found = True

    if found:
        return total

    # 순수 숫자면 분으로 간주
    num = parse_numeric(s)
    return num


# ── 단일 날짜 데이터 → metric dict ──────────────────────────────

def _extract_single(
    data: dict,
    analysis_id: str,
    report_date: str,
    department: str,
) -> dict:
    """extracted_data (단일 날짜) → daily_metrics 행 dict."""
    prod = data.get("production", {})
    qual = data.get("quality", {})
    equip = data.get("equipment", {})
    workforce = data.get("workforce", {})
    other = data.get("other", {})

    # 불량 유형 → JSON array
    defect_types = qual.get("불량유형") or qual.get("주요불량")
    if isinstance(defect_types, list):
        defect_types_json = json.dumps(defect_types, ensure_ascii=False)
    elif isinstance(defect_types, str) and defect_types:
        defect_types_json = json.dumps([defect_types], ensure_ascii=False)
    else:
        defect_types_json = None

    return {
        "analysis_id": analysis_id,
        "report_date": report_date,
        "department": department,
        # 생산
        "prod_target": parse_numeric(prod.get("목표") or prod.get("계획")),
        "prod_actual": parse_numeric(prod.get("실적")),
        "prod_achievement_rate": parse_numeric(prod.get("달성률")),
        "prod_unit": str(prod.get("단위") or prod.get("unit") or "pcs"),
        # 품질
        "quality_defect_count": parse_numeric(qual.get("불량수")),
        "quality_defect_rate": parse_numeric(qual.get("불량률")),
        "quality_defect_types": defect_types_json,
        # 설비
        "equip_uptime_min": parse_duration_to_minutes(equip.get("가동시간")),
        "equip_downtime_min": parse_duration_to_minutes(equip.get("비가동시간")),
        "equip_utilization_rate": parse_numeric(equip.get("가동률")),
        "equip_downtime_reason": equip.get("사유") or equip.get("비가동사유"),
        # 인력
        "workforce_count": parse_numeric(
            workforce.get("투입인원") or workforce.get("출근인원")
        ),
        "workforce_absent": parse_numeric(workforce.get("결근")),
        "workforce_overtime": str(workforce.get("잔업") or ""),
        # 기타
        "notes": other.get("특이사항") or other.get("비고"),
        "raw_json": json.dumps(data, ensure_ascii=False),
    }


# ── 메인 진입점 ─────────────────────────────────────────────────

def extracted_to_metrics(
    extracted: dict,
    analysis_id: str,
    fallback_date: str | None = None,
    fallback_dept: str | None = None,
) -> list[dict]:
    """extracted_data → daily_metrics 행 리스트.

    - 다중 날짜 ("dates" 배열): N개 행 반환
    - 단일 날짜: 1개 행 반환
    """
    results: list[dict] = []
    dept = fallback_dept or ""

    # 다중 날짜 감지
    dates_list = extracted.get("dates")
    if isinstance(dates_list, list) and len(dates_list) > 0:
        logger.info("다중 날짜 감지: %d건", len(dates_list))
        for entry in dates_list:
            rd = entry.get("report_date") or fallback_date
            if not rd:
                continue
            d = entry.get("department") or dept
            results.append(_extract_single(entry, analysis_id, rd, d))
        return results

    # 단일 날짜
    meta = extracted.get("metadata", {})
    rd = meta.get("report_date") or fallback_date
    d = meta.get("department") or dept
    if not rd:
        logger.warning("report_date 없음 — 메트릭 스킵 (analysis_id=%s)", analysis_id)
        return []

    results.append(_extract_single(extracted, analysis_id, rd, d))
    return results
