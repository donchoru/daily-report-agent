"""드릴다운 링크 매핑 — 지표별 연계 시스템/화면 URL 제공."""

from __future__ import annotations

from config import DRILLDOWN_BASE_URL, DRILLDOWN_LINKS


def get_drilldown_links(extracted_data: dict, insights: dict) -> list[dict]:
    """분석 결과에서 관련 드릴다운 링크를 추출.

    추출 데이터의 어떤 카테고리에 데이터가 있는지 + 이상 지표를 보고
    관련 시스템 링크를 제공.
    """
    links: list[dict] = []
    seen: set[str] = set()

    # 1) 추출 데이터에 있는 카테고리에 대해 링크 제공
    for category in ("production", "quality", "equipment", "workforce"):
        cat_data = extracted_data.get(category, {})
        if cat_data:  # 데이터가 있으면
            for link in DRILLDOWN_LINKS.get(category, []):
                key = link["url"]
                if key not in seen:
                    links.append({
                        "category": category,
                        "name": link["name"],
                        "url": f"{DRILLDOWN_BASE_URL}{link['url']}",
                        "description": link["description"],
                        "reason": f"{category} 데이터 존재",
                    })
                    seen.add(key)

    # 2) 이상 지표에서 관련 카테고리 매핑
    anomalies = insights.get("anomalies", [])
    keyword_map = {
        "생산": "production",
        "달성률": "production",
        "실적": "production",
        "불량": "quality",
        "품질": "quality",
        "검사": "quality",
        "가동": "equipment",
        "설비": "equipment",
        "정비": "equipment",
        "고장": "equipment",
        "인력": "workforce",
        "근태": "workforce",
        "결근": "workforce",
        "잔업": "workforce",
        "재고": "inventory",
        "자재": "inventory",
        "에너지": "energy",
        "전력": "energy",
        "원가": "cost",
        "비용": "cost",
    }

    for anomaly in anomalies:
        metric = anomaly.get("metric", "")
        desc = anomaly.get("description", "")
        text = f"{metric} {desc}"

        for keyword, category in keyword_map.items():
            if keyword in text:
                for link in DRILLDOWN_LINKS.get(category, []):
                    key = link["url"]
                    if key not in seen:
                        links.append({
                            "category": category,
                            "name": link["name"],
                            "url": f"{DRILLDOWN_BASE_URL}{link['url']}",
                            "description": link["description"],
                            "reason": f"이상 감지: {metric}",
                        })
                        seen.add(key)

    return links
