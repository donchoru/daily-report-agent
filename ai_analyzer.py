"""물류 수작업일보 AI 분석기 — Gemini 2.0 Flash (OCR + 분석 + 챗봇)"""
import ssl
import json
import base64
from pathlib import Path

import httpx
from google import genai
from google.genai.types import Part, Content

# ── Gemini 초기화 (사내망 SSL 우회) ──
API_KEY_FILE = Path(__file__).parent.parent / "gemini-key.txt"
if not API_KEY_FILE.exists():
    API_KEY_FILE = Path(__file__).parent / "gemini-key.txt"

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE
_ssl_ctx.set_ciphers("DEFAULT:@SECLEVEL=0")

_http_client = httpx.Client(verify=_ssl_ctx)

MODEL = "gemini-2.0-flash"

PROMPTS_DIR = Path(__file__).parent / "prompts"


def _get_client():
    key = API_KEY_FILE.read_text(encoding="utf-8").strip()
    return genai.Client(api_key=key, http_options={"httpx_client": _http_client})


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.txt"
    return path.read_text(encoding="utf-8").strip()


# ═══════════════════════════════════════
# 1. OCR — 일보 이미지 → 구조화 JSON
# ═══════════════════════════════════════
def ocr_report_image(image_path: str) -> dict:
    """일보 이미지를 Gemini Vision으로 읽어 구조화된 JSON 데이터로 변환한다."""
    client = _get_client()

    img_bytes = Path(image_path).read_bytes()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    # 확장자로 mime type 결정
    ext = Path(image_path).suffix.lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "pdf": "application/pdf"}.get(
        ext.lstrip("."), "image/png"
    )

    prompt = _load_prompt("ocr_extract")

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            Content(parts=[
                Part.from_bytes(data=img_bytes, mime_type=mime),
                Part.from_text(text=prompt),
            ])
        ],
    )

    # JSON 파싱 시도
    text = response.text.strip()
    # ```json ... ``` 감싸인 경우 제거
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw_text": response.text, "parse_error": True}


# ═══════════════════════════════════════
# Helper: 전일비교 요약 생성
# ═══════════════════════════════════════
def _fmt(val, sign=True):
    """숫자 포맷 (부호 포함)."""
    s = "+" if val > 0 and sign else ""
    if isinstance(val, float):
        return f"{s}{val:.1f}"
    return f"{s}{val:,}"


def _build_comparison_summary(data: dict) -> str:
    """데이터에서 전일비교·월간 수치를 미리 계산하여 텍스트로 반환."""
    lines = []

    # ── 일간 지표 (전일비교) ──
    lines.append("## 일간 지표 (전일비교)")

    # 수작업 건수
    daily = data.get("manual_handling_trend", {}).get("daily", [])
    if len(daily) >= 2:
        t, y = daily[-1]["value"], daily[-2]["value"]
        d = t - y
        lines.append(f"- 수작업건수: 금일 {t:,}건 / 전일 {y:,}건 ({_fmt(d)}건)")

    # 수동반송수 / 수동반송율
    tt = data.get("transport_trend", {}).get("daily", [])
    if len(tt) >= 2:
        t_cnt, y_cnt = tt[-1]["manual_count"], tt[-2]["manual_count"]
        t_rate, y_rate = tt[-1]["rate"], tt[-2]["rate"]
        d_cnt = t_cnt - y_cnt
        d_rate = round(t_rate - y_rate, 1)
        dir_rate = "악화" if d_rate > 0 else "개선"
        lines.append(f"- 수동반송수: 금일 {t_cnt:,}건 / 전일 {y_cnt:,}건 ({_fmt(d_cnt)}건)")
        lines.append(f"- 수동반송율: 금일 {t_rate}% / 전일 {y_rate}% ({_fmt(d_rate)}%p {dir_rate})")

    # 반송우선순위 변경
    pct_d = data.get("priority_change_trend", {}).get("daily", [])
    if len(pct_d) >= 2:
        t, y = pct_d[-1]["value"], pct_d[-2]["value"]
        lines.append(f"- 반송우선순위변경: 금일 {t}건 / 전일 {y}건 ({_fmt(t-y)}건)")

    # LOT 우선순위
    lot_d = data.get("lot_priority_trend", {}).get("daily", [])
    if len(lot_d) >= 2:
        t, y = lot_d[-1]["value"], lot_d[-2]["value"]
        lines.append(f"- LOT우선순위: 금일 {t}건 / 전일 {y}건 ({_fmt(t-y)}건)")

    # 기준정보/가중치 변경
    rw_d = data.get("ref_weight_change_trend", {}).get("daily", [])
    if len(rw_d) >= 2:
        t, y = rw_d[-1]["value"], rw_d[-2]["value"]
        lines.append(f"- 기준정보/가중치변경: 금일 {t}건 / 전일 {y}건 ({_fmt(t-y)}건)")

    # TAT (일간)
    tat_daily = data.get("tat_trend", {}).get("daily", [])
    tat_keys = ["processing", "inspection", "transport", "waiting", "hold"]
    tat_names = {"processing": "가공", "inspection": "검사", "transport": "운반", "waiting": "대기", "hold": "Hold"}
    if len(tat_daily) >= 2:
        td, yd = tat_daily[-1], tat_daily[-2]
        t_total = sum(td[k] for k in tat_keys)
        y_total = sum(yd[k] for k in tat_keys)
        lines.append(f"- TAT합계: 금일 {t_total:.1f}분 / 전일 {y_total:.1f}분 ({_fmt(t_total - y_total)}분)")
        for k in tat_keys:
            d = round(td[k] - yd[k], 1)
            if abs(d) >= 3:  # 3분 이상 변동만 표시
                lines.append(f"  · {tat_names[k]}: {td[k]}분 → 전일 {yd[k]}분 ({_fmt(d)}분)")

    # ── 전일대비 악화 지표 요약 ──
    lines.append("\n## ⚠️ 전일대비 악화 지표")
    degraded = []
    if len(tt) >= 2 and tt[-1]["rate"] > tt[-2]["rate"]:
        degraded.append(f"수동반송율 {tt[-1]['rate']}% (전일 {tt[-2]['rate']}%, {_fmt(round(tt[-1]['rate']-tt[-2]['rate'],1))}%p 악화)")
    if len(pct_d) >= 2 and pct_d[-1]["value"] > pct_d[-2]["value"]:
        degraded.append(f"반송우선순위변경 {pct_d[-1]['value']}건 (전일 {pct_d[-2]['value']}건, {_fmt(pct_d[-1]['value']-pct_d[-2]['value'])}건 증가)")
    if len(lot_d) >= 2 and lot_d[-1]["value"] > lot_d[-2]["value"]:
        degraded.append(f"LOT우선순위 {lot_d[-1]['value']}건 (전일 {lot_d[-2]['value']}건, {_fmt(lot_d[-1]['value']-lot_d[-2]['value'])}건 증가)")
    if len(rw_d) >= 2 and rw_d[-1]["value"] > rw_d[-2]["value"]:
        degraded.append(f"기준정보/가중치변경 {rw_d[-1]['value']}건 (전일 {rw_d[-2]['value']}건, {_fmt(rw_d[-1]['value']-rw_d[-2]['value'])}건 증가)")
    if len(tat_daily) >= 2:
        t_total = sum(tat_daily[-1][k] for k in tat_keys)
        y_total = sum(tat_daily[-2][k] for k in tat_keys)
        if t_total > y_total:
            degraded.append(f"TAT합계 {t_total:.1f}분 (전일 {y_total:.1f}분, {_fmt(t_total-y_total)}분 증가)")

    if degraded:
        for item in degraded:
            lines.append(f"- {item}")
    else:
        lines.append("- 전일대비 악화 지표 없음 (전 지표 유지 또는 개선)")

    # ── 월간 목표 달성 현황 (일평균) ──
    lines.append("\n## 월간 목표 달성 현황 (일평균 기준)")
    tva = data.get("target_vs_actual", [])
    # 가장 최근 실적이 있는 월
    for entry in reversed(tva):
        if entry.get("actual") is not None:
            ach = round(entry["actual"] / entry["target"] * 100, 1) if entry["target"] else 0
            lines.append(f"- {entry['label']}월: 목표 {entry['target']}건/일 / 실적 {entry['actual']}건/일 (달성률 {ach}%)")
            break
    # 전월 비교
    actuals = [e for e in tva if e.get("actual") is not None]
    if len(actuals) >= 2:
        curr, prev = actuals[-1], actuals[-2]
        c_ach = round(curr["actual"] / curr["target"] * 100, 1) if curr["target"] else 0
        p_ach = round(prev["actual"] / prev["target"] * 100, 1) if prev["target"] else 0
        diff_ach = round(c_ach - p_ach, 1)
        lines.append(f"- 전월대비 달성률 변화: {_fmt(diff_ach)}%p ({'개선' if diff_ach < 0 else '악화' if diff_ach > 0 else '유지'})")

    # ── Worst 10 요약 ──
    worst = data.get("worst10", [])
    if worst:
        lines.append("\n## Worst Top 3")
        for w in worst[:3]:
            if w["diff"] > 0:
                lines.append(f"- {w['rank']}위: {w['dept']}-{w['process']} (금일 {w['today']}건, 전일 {w['yesterday']}건, +{w['diff']}건)")

    return "\n".join(lines)


def _prepare_context(data: dict) -> str:
    """AI에게 전달할 컨텍스트 문자열."""
    comparison = _build_comparison_summary(data)
    data_str = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    return f"{comparison}\n\n## 전체 일보 데이터\n```json\n{data_str}\n```"


# ═══════════════════════════════════════
# 2. 핵심이슈 자동 추출
# ═══════════════════════════════════════
def extract_key_issues(data: dict) -> str:
    """일보 데이터에서 핵심 이슈를 추출한다."""
    client = _get_client()
    prompt = _load_prompt("key_issues")
    context = _prepare_context(data)

    response = client.models.generate_content(
        model=MODEL,
        contents=f"{prompt}\n\n{context}",
    )
    return response.text


# ═══════════════════════════════════════
# 3. 역할별 맞춤 요약
# ═══════════════════════════════════════
def summarize_for_role(data: dict, role: str = "executive") -> str:
    """역할별 맞춤 요약 생성. role: executive / operator"""
    client = _get_client()
    prompt = _load_prompt(role)
    context = _prepare_context(data)

    response = client.models.generate_content(
        model=MODEL,
        contents=f"{prompt}\n\n{context}",
    )
    return response.text


# ═══════════════════════════════════════
# 4. 대화형 Q&A
# ═══════════════════════════════════════
def chat_with_report(data: dict, question: str, history: list[dict] | None = None) -> str:
    """
    일보 데이터를 컨텍스트로 사용자 질문에 답변한다.
    history: [{"role": "user"|"assistant", "content": "..."}, ...]
    """
    client = _get_client()
    system_prompt = _load_prompt("chat_system")
    data_str = json.dumps(data, ensure_ascii=False, indent=2, default=str)

    messages = f"{system_prompt}\n\n## 일보 데이터\n```json\n{data_str}\n```\n\n"

    if history:
        for msg in history:
            role_label = "사용자" if msg["role"] == "user" else "AI"
            messages += f"[{role_label}]: {msg['content']}\n"

    messages += f"[사용자]: {question}\n[AI]:"

    response = client.models.generate_content(model=MODEL, contents=messages)
    return response.text
