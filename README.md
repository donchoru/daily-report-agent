# Daily Report Agent — 제조 일보 AI 분석

제조 현장의 일보(daily report) 이미지를 업로드하면, **Gemini Vision**이 데이터를 추출하고 **이상탐지 · 트렌드 · 요약 · 액션아이템**을 자동으로 생성하는 FastAPI 백엔드.

## 핵심 기능

### 1. 2-Stage AI 분석 파이프라인
| Stage | 역할 | Temperature |
|-------|------|-------------|
| **Stage 1** — Extractor | 이미지에서 생산·품질·설비·인력 수치를 JSON으로 추출 | 0.1 (정확도 우선) |
| **Stage 2** — Insight | 추출 데이터 + 과거 7일 트렌드로 이상/요약/액션 생성 | 0.3 (분석 일관성) |

### 2. 이상탐지 (Anomaly Detection)
| 지표 | MEDIUM | HIGH |
|------|--------|------|
| 달성률 | < 95% | < 90% |
| 불량률 | > 2% | > 3% |
| 가동률 | < 90% | < 85% |

전일/전주 대비 ±10% 이상 급변 시 자동 감지.

### 3. 다중 이미지 비교 분석
2~5장의 일보를 동시 업로드하면 날짜별 변화를 비교하여 **개선/악화/안정** 포인트를 분석.

### 4. 관점 전환 재분석 (Perspective Reanalysis)
같은 데이터를 6가지 프리셋 관점으로 재해석:
- `cost` — 원가/비용 관점
- `bottleneck` — 병목 관점
- `trend` — 추세 관점 (이동평균, 변화 가속도)
- `risk` — 리스크/안전 관점
- `efficiency` — OEE/효율성 관점
- `comparison` — 라인/설비 비교 관점

커스텀 관점도 자유 텍스트로 입력 가능.

### 5. 헤드라인 생성
경영진이 한 줄만 봐도 상황을 파악할 수 있는 임팩트 있는 헤드라인 자동 생성. 숫자 포함, sentiment 판별.

### 6. 후속 대화 (Chat)
분석 결과를 컨텍스트로 후속 질문 가능. "불량률이 왜 올랐어?", "A라인 가동률 추이 더 자세히" 등.

### 7. 장기 메모리 (Long-term Memory)
대화 중 사용자가 알려주는 도메인 지식을 자동 추출·저장:
- 목표치/기준 ("불량률 1.5% 이하가 목표")
- 설비 특성 ("CNC-3은 다음 주 정비 예정")
- 분석 선호 ("불량률은 항상 먼저 봐줘")

이후 분석에 자동 반영.

### 8. 관심사 설정 (Interests)
사용자가 중점적으로 보고 싶은 지표를 등록하면, 인사이트·헤드라인 생성 시 해당 지표를 우선 분석.

### 9. 드릴다운 링크 (Drilldown)
분석 결과에서 관련 시스템(MES, QMS, EAM, HR, WMS, EMS) 화면 링크를 자동 매핑.

## 기술 스택

| 항목 | 기술 |
|------|------|
| Framework | FastAPI (uvicorn) |
| AI/LLM | Gemini 2.0 Flash (`google-genai`) |
| DB | SQLite (`aiosqlite`) |
| Python | 3.12+ (`.venv/` 가상환경) |
| 포트 | **8700** |
| API Key | macOS Keychain → `GEMINI_API_KEY` |

## 프로젝트 구조

```
daily-report-agent/
├── main.py              # FastAPI 서버 (엔드포인트 정의)
├── config.py            # 설정값, Keychain 읽기, 임계값, 드릴다운 URL
├── models.py            # Pydantic 스키마 (요청/응답 모델)
├── db.py                # aiosqlite DB 클래스 (analyses, images, conversations, memories, interests)
├── analyzer/
│   ├── extractor.py     # Stage 1: Gemini Vision → 구조화 JSON 추출
│   ├── insights.py      # Stage 2: 인사이트/비교/헤드라인/재분석 생성
│   ├── chat.py          # 후속 대화 + 메모리 자동 추출
│   ├── drilldown.py     # 지표 → 연계 시스템 URL 매핑
│   └── prompts.py       # 모든 AI 프롬프트 모음
├── requirements.txt
├── logs/
│   └── report.log
└── report.db            # SQLite (자동 생성)
```

## DB 스키마

| 테이블 | 용도 |
|--------|------|
| `analyses` | 분석 결과 (extracted_data, insights JSON 저장) |
| `images` | 업로드 이미지 메타 (filename, hash, size) |
| `conversations` | 분석별 후속 대화 이력 |
| `memories` | 장기 메모리 (도메인 지식, 선호, 기준) |
| `interests` | 관심 지표 설정 (priority 기반) |

## API 엔드포인트

### 분석
| Method | Path | 설명 |
|--------|------|------|
| `POST` | `/analyze` | 단일 이미지 분석 (multipart/form-data) |
| `POST` | `/analyze/compare` | 다중 이미지 비교 분석 (2~5장) |

### 이력
| Method | Path | 설명 |
|--------|------|------|
| `GET` | `/history` | 과거 분석 목록 (department, report_type 필터) |
| `GET` | `/history/{id}` | 단건 상세 조회 |

### 대화
| Method | Path | 설명 |
|--------|------|------|
| `POST` | `/chat/{id}` | 분석 결과 기반 후속 질문 |
| `GET` | `/chat/{id}/history` | 대화 이력 조회 |

### 재분석 / 헤드라인
| Method | Path | 설명 |
|--------|------|------|
| `GET` | `/headlines/{id}` | 헤드라인 생성 |
| `POST` | `/reanalyze/{id}` | 관점 전환 재분석 |
| `GET` | `/reanalyze/perspectives` | 사용 가능한 관점 프리셋 목록 |

### 드릴다운
| Method | Path | 설명 |
|--------|------|------|
| `GET` | `/drilldown/{id}` | 분석 결과 기반 연계 시스템 링크 |

### 메모리 / 관심사
| Method | Path | 설명 |
|--------|------|------|
| `GET` | `/memories` | 장기 메모리 조회 |
| `DELETE` | `/memories/{id}` | 메모리 삭제 |
| `GET` | `/interests` | 관심 지표 목록 |
| `POST` | `/interests` | 관심 지표 추가/수정 (UPSERT) |
| `DELETE` | `/interests/{id}` | 관심 지표 비활성화 |

### 시스템
| Method | Path | 설명 |
|--------|------|------|
| `GET` | `/health` | 헬스체크 + DB 통계 |

## 사용 예시

### 단일 이미지 분석
```bash
curl -X POST http://localhost:8700/analyze \
  -F "image=@daily_report.png" \
  -F "report_date=2026-03-10" \
  -F "department=1공장 A라인" \
  -F "context=이번 주 생산 목표 5000개"
```

### 다중 비교
```bash
curl -X POST http://localhost:8700/analyze/compare \
  -F "images=@report_0308.png" \
  -F "images=@report_0309.png" \
  -F "images=@report_0310.png" \
  -F "report_dates=2026-03-08,2026-03-09,2026-03-10" \
  -F "department=1공장 A라인"
```

### 후속 질문
```bash
curl -X POST http://localhost:8700/chat/abc12345 \
  -H "Content-Type: application/json" \
  -d '{"message": "불량률이 어제보다 올라간 이유가 뭘까?"}'
```

### 관점 전환 재분석
```bash
# 프리셋 관점
curl -X POST http://localhost:8700/reanalyze/abc12345 \
  -H "Content-Type: application/json" \
  -d '{"perspective": "cost"}'

# 커스텀 관점
curl -X POST http://localhost:8700/reanalyze/abc12345 \
  -H "Content-Type: application/json" \
  -d '{"perspective": "야간 교대조 관점에서 생산성과 품질 변화 분석"}'
```

### 관심사 등록
```bash
curl -X POST http://localhost:8700/interests \
  -H "Content-Type: application/json" \
  -d '{"metric": "불량률", "priority": 1, "description": "불량률 1.5% 이하 유지가 목표"}'
```

## 설치 및 실행

```bash
cd /workspace/daily-report-agent

# 가상환경 생성 + 의존성 설치
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 실행
python main.py
# → http://localhost:8700
# → Swagger UI: http://localhost:8700/docs
```

GEMINI_API_KEY는 macOS Keychain에서 자동으로 읽어옵니다. 환경변수로 직접 주입도 가능.

## 응답 예시 (POST /analyze)

```json
{
  "id": "a1b2c3d4",
  "report_date": "2026-03-10",
  "department": "1공장 A라인",
  "extracted_data": {
    "production": {
      "계획": "5,000개",
      "실적": "4,720개",
      "달성률": "94.4%"
    },
    "quality": {
      "불량수": "85개",
      "불량률": "1.8%"
    },
    "equipment": {
      "가동률": "92.3%"
    },
    "workforce": {
      "출근인원": "32명"
    }
  },
  "insights": {
    "anomalies": [
      {
        "metric": "생산 달성률",
        "value": "94.4%",
        "expected": "95% 이상",
        "severity": "MEDIUM",
        "description": "목표 대비 5.6% 미달. 설비 비가동 시간 증가가 원인으로 추정"
      }
    ],
    "trends": [
      {
        "metric": "불량률",
        "direction": "up",
        "description": "3일 연속 상승 추세 (1.2% → 1.5% → 1.8%)"
      }
    ],
    "summary": "A라인 생산 달성률 94.4%로 목표 소폭 미달. 불량률 1.8%는 기준 내이나 3일 연속 상승 추세로 주의 필요. 가동률 92.3%는 양호.",
    "action_items": [
      {
        "priority": "MEDIUM",
        "action": "불량률 상승 원인 조사 (자재 로트 변경 여부 확인)",
        "responsible": "품질관리팀"
      }
    ]
  },
  "headlines": {
    "main_headline": "A라인 달성률 94.4%, 목표 미달 — 불량률 3일 연속 상승 주의",
    "sub_headlines": [
      "가동률 92.3% 양호, 설비 상태 안정",
      "불량률 1.8%로 기준 내이나 상승 추세 지속"
    ],
    "sentiment": "negative"
  },
  "drilldown_links": [
    {
      "category": "production",
      "name": "MES 생산 현황",
      "url": "/mes/production",
      "description": "실시간 생산 실적 모니터링"
    }
  ],
  "processing_time_sec": 3.42
}
```
