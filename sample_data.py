"""물류 수작업일보 샘플 데이터 생성 (트렌드 포함)"""
import random
from datetime import datetime, date, timedelta
from calendar import monthrange


def _seed_for(d: date, salt: int = 0):
    """날짜 기반 시드 — 같은 날짜면 항상 같은 데이터."""
    random.seed(d.toordinal() + salt)


def _month_range(base_date: date, months_back: int):
    """base_date 기준 months_back 개월 전부터의 월 리스트 반환."""
    result = []
    for i in range(months_back, -1, -1):
        y = base_date.year
        m = base_date.month - i
        while m <= 0:
            m += 12
            y -= 1
        result.append(date(y, m, 1))
    return result


def _week_starts(base_date: date, weeks_back: int):
    """base_date 기준 weeks_back 주 전부터의 주 시작일(월요일) 리스트."""
    # 이번 주 월요일
    current_monday = base_date - timedelta(days=base_date.weekday())
    return [current_monday - timedelta(weeks=w) for w in range(weeks_back, -1, -1)]


def _day_range(base_date: date, days_back: int):
    """base_date 기준 days_back 일 전부터의 날짜 리스트."""
    return [base_date - timedelta(days=d) for d in range(days_back, -1, -1)]


def generate_daily_report_data(report_date: date | None = None) -> dict:
    """물류 수작업일보 데이터를 생성한다. 트렌드/과거 비교 데이터 포함."""
    if report_date is None:
        report_date = date.today()

    _seed_for(report_date)

    shift = random.choice(["주간 (Day)", "야간 (Night)"])
    reporter = random.choice(["김물류", "박반송", "이관리", "최운영"])

    # ═══════════════════════════════════════
    # 1. 수작업 현황 트렌드
    #    - 월별: 3개월 실적
    #    - 주별: 4주 실적
    #    - 일별: 7일 실적
    # ═══════════════════════════════════════
    monthly_dates = _month_range(report_date, 2)  # 3개월
    monthly_trend = []
    for md in monthly_dates:
        _seed_for(md, salt=100)
        monthly_trend.append({
            "label": md.strftime("%Y-%m"),
            "value": random.randint(6000, 14000),
        })

    weekly_dates = _week_starts(report_date, 3)  # 4주
    weekly_trend = []
    for wd in weekly_dates:
        _seed_for(wd, salt=200)
        weekly_trend.append({
            "label": f'{wd.strftime("%m/%d")}~',
            "value": random.randint(1500, 3500),
        })

    daily_dates = _day_range(report_date, 6)  # 7일
    daily_trend = []
    for dd in daily_dates:
        _seed_for(dd, salt=300)
        daily_trend.append({
            "label": dd.strftime("%m/%d"),
            "value": random.randint(300, 800),
        })

    manual_handling_trend = {
        "monthly": monthly_trend,
        "weekly": weekly_trend,
        "daily": daily_trend,
    }

    # ═══════════════════════════════════════
    # 2. 목표 vs 실적 (일평균, 월단위)
    #    2025-10 ~ 2026-10 (13개월)
    # ═══════════════════════════════════════
    target_start = date(report_date.year - 1, 10, 1)
    target_months = _month_range(target_start, 0)
    # 13개월 생성
    all_months = [target_start]
    for i in range(1, 13):
        y = target_start.year
        m = target_start.month + i
        while m > 12:
            m -= 12
            y += 1
        all_months.append(date(y, m, 1))

    target_vs_actual = []
    for md in all_months:
        _seed_for(md, salt=400)
        target_avg = random.randint(350, 550)
        # 미래 월은 실적 없음
        if md <= date(report_date.year, report_date.month, 1):
            actual_avg = target_avg + random.randint(-80, 60)
            actual_avg = max(0, actual_avg)
        else:
            actual_avg = None
        target_vs_actual.append({
            "label": md.strftime("%Y-%m"),
            "target": target_avg,
            "actual": actual_avg,
        })

    # ═══════════════════════════════════════
    # 3. 수동반송수 / 수동반송율 트렌드 (월/주/일)
    # ═══════════════════════════════════════
    def _transport_trend(dates, salt_base, scale_m, scale_w):
        result = []
        for d in dates:
            _seed_for(d, salt=salt_base)
            total = random.randint(scale_m, scale_w)
            auto = random.randint(int(total * 0.85), int(total * 0.98))
            manual = total - auto
            rate = round(manual / total * 100, 1) if total else 0
            result.append({
                "label": d.strftime("%Y-%m") if salt_base < 600 else (
                    f'{d.strftime("%m/%d")}~' if salt_base < 700 else d.strftime("%m/%d")
                ),
                "manual_count": manual,
                "rate": rate,
            })
        return result

    transport_trend = {
        "monthly": _transport_trend(monthly_dates, 500, 15000, 30000),
        "weekly": _transport_trend(weekly_dates, 600, 4000, 8000),
        "daily": _transport_trend(daily_dates, 700, 600, 1500),
    }

    # ═══════════════════════════════════════
    # 4. 반송우선순위 변경 / LOT우선순위 / 기준정보·가중치 변경 트렌드
    # ═══════════════════════════════════════
    def _count_trend(dates, salt_base, lo, hi, label_fmt):
        result = []
        for d in dates:
            _seed_for(d, salt=salt_base)
            result.append({
                "label": d.strftime(label_fmt) if label_fmt != "week" else f'{d.strftime("%m/%d")}~',
                "value": random.randint(lo, hi),
            })
        return result

    priority_change_trend = {
        "monthly": _count_trend(monthly_dates, 800, 30, 150, "%Y-%m"),
        "weekly": _count_trend(weekly_dates, 810, 8, 40, "week"),
        "daily": _count_trend(daily_dates, 820, 1, 15, "%m/%d"),
    }
    lot_priority_trend = {
        "monthly": _count_trend(monthly_dates, 830, 40, 200, "%Y-%m"),
        "weekly": _count_trend(weekly_dates, 840, 10, 50, "week"),
        "daily": _count_trend(daily_dates, 850, 2, 20, "%m/%d"),
    }
    ref_weight_change_trend = {
        "monthly": _count_trend(monthly_dates, 860, 10, 80, "%Y-%m"),
        "weekly": _count_trend(weekly_dates, 870, 3, 20, "week"),
        "daily": _count_trend(daily_dates, 880, 0, 8, "%m/%d"),
    }

    # ═══════════════════════════════════════
    # 5. TAT 트렌드 (월/주/일)
    # ═══════════════════════════════════════
    def _tat_trend(dates, salt_base, label_fmt):
        result = []
        for d in dates:
            _seed_for(d, salt=salt_base)
            result.append({
                "label": d.strftime(label_fmt) if label_fmt != "week" else f'{d.strftime("%m/%d")}~',
                "processing": round(random.uniform(20, 60), 1),
                "inspection": round(random.uniform(10, 35), 1),
                "transport": round(random.uniform(15, 45), 1),
                "waiting": round(random.uniform(25, 80), 1),
                "hold": round(random.uniform(5, 30), 1),
            })
        return result

    tat_trend = {
        "monthly": _tat_trend(monthly_dates, 900, "%Y-%m"),
        "weekly": _tat_trend(weekly_dates, 910, "week"),
        "daily": _tat_trend(daily_dates, 920, "%m/%d"),
    }

    # ═══════════════════════════════════════
    # 6. 카세트 수동반송 트렌드 (Load/Unload/STK × 월/주/일)
    # ═══════════════════════════════════════
    def _cassette_trend(dates, salt_base, lo, hi, label_fmt):
        result = []
        for d in dates:
            _seed_for(d, salt=salt_base)
            result.append({
                "label": d.strftime(label_fmt) if label_fmt != "week" else f'{d.strftime("%m/%d")}~',
                "load": random.randint(lo, hi),
                "unload": random.randint(lo, hi),
                "stk": random.randint(lo, hi),
            })
        return result

    cassette_trend = {
        "monthly": _cassette_trend(monthly_dates, 1000, 300, 1500, "%Y-%m"),
        "weekly": _cassette_trend(weekly_dates, 1010, 80, 400, "week"),
        "daily": _cassette_trend(daily_dates, 1020, 20, 120, "%m/%d"),
    }

    # ═══════════════════════════════════════
    # 7. 공정군별 수동반송수
    # ═══════════════════════════════════════
    _seed_for(report_date, salt=1100)
    process_groups = ["DIFF", "PHOTO", "ETCH", "CVD/PVD", "CMP", "IMP", "METAL"]
    process_group_transport = [
        {"process": pg, "count": random.randint(30, 300)}
        for pg in process_groups
    ]

    # ═══════════════════════════════════════
    # 8. LOT 우선순위별 재공현황
    # ═══════════════════════════════════════
    _seed_for(report_date, salt=1200)
    lot_priority_wip = {
        "Hot": random.randint(20, 80),
        "Normal": random.randint(200, 500),
        "Low": random.randint(50, 150),
        "Hold": random.randint(5, 40),
    }

    # ═══════════════════════════════════════
    # 9. Worst 10
    # ═══════════════════════════════════════
    _seed_for(report_date, salt=1300)
    depts = ["A동", "B동", "C동", "D동", "E동"]
    processes = ["DIFF", "PHOTO", "ETCH", "CVD", "CMP", "IMP", "METAL", "PKG"]
    worst_candidates = []
    for _ in range(20):
        today_val = random.randint(10, 120)
        yesterday_val = random.randint(5, 100)
        worst_candidates.append({
            "dept": random.choice(depts),
            "process": random.choice(processes),
            "today": today_val,
            "yesterday": yesterday_val,
            "diff": today_val - yesterday_val,
        })
    worst_candidates.sort(key=lambda x: x["diff"], reverse=True)
    worst10 = [{**item, "rank": i + 1} for i, item in enumerate(worst_candidates[:10])]

    # ═══════════════════════════════════════
    # 10. 주요 이슈
    # ═══════════════════════════════════════
    _seed_for(report_date, salt=1400)
    issue_pool = [
        "AGV #3 고장으로 B동 수동반송 증가 (30분 다운타임)",
        "A동 STK-05 정비 완료, 정상 가동 복귀",
        "C동 PHOTO 구간 카세트 적체 → 수동반송 긴급 투입",
        "신규 LOT 긴급 투입 (Hot Lot: Product-X)",
        "D동 반송 우선순위 기준 가중치 변경 적용",
        "야간조 인원 변경: 홍길동 → 이순신 (교대근무 조정)",
        "E동 CMP 구간 AGV 경로 변경으로 수동반송 감소",
        "B동 Unload 구간 카세트 파손 1건 발생",
        "전일 대비 수동반송율 0.5%p 개선",
        "월간 수동반송 목표 대비 95% 달성 중",
    ]
    issues = random.sample(issue_pool, k=random.randint(3, 5))

    # ═══════════════════════════════════════
    # UI 요약 필드
    # ═══════════════════════════════════════
    today_total = daily_trend[-1]["value"]
    today_target = target_vs_actual[-1]["target"] if target_vs_actual[-1]["actual"] is None else target_vs_actual[-1]["target"]
    # 가장 최근 실적이 있는 월의 target 사용
    for tva in reversed(target_vs_actual):
        if tva["actual"] is not None:
            today_target = tva["target"]
            break

    target_achievement = round(today_total / today_target * 100, 1) if today_target else 0
    current_transport = transport_trend["daily"][-1]

    return {
        "report_date": report_date.strftime("%Y-%m-%d"),
        "report_title": "물류 수작업일보",
        "shift": shift,
        "reporter": reporter,
        # 트렌드 데이터
        "manual_handling_trend": manual_handling_trend,
        "target_vs_actual": target_vs_actual,
        "transport_trend": transport_trend,
        "priority_change_trend": priority_change_trend,
        "lot_priority_trend": lot_priority_trend,
        "ref_weight_change_trend": ref_weight_change_trend,
        "tat_trend": tat_trend,
        "cassette_trend": cassette_trend,
        # 단일 데이터
        "process_group_transport": process_group_transport,
        "lot_priority_wip": lot_priority_wip,
        "worst10": worst10,
        "issues": issues,
        # UI 요약
        "total_manual_today": today_total,
        "target_achievement": target_achievement,
        "manual_transport_rate": current_transport["rate"],
        "management_kpis": {
            "priority_change_count": priority_change_trend["daily"][-1]["value"],
        },
    }
