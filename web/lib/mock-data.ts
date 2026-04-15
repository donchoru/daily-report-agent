import type { ExtractedData, Insights } from "./types";

interface DayData {
  date: string;
  department: string;
  extracted_data: ExtractedData;
  insights: Insights;
}

export const MOCK_7DAYS: DayData[] = [
  {
    date: "2026-04-08",
    department: "SMT-1라인",
    extracted_data: {
      production: { 목표: 5000, 실적: 4860, 달성률: 97.2, 단위: "pcs" },
      quality: { 불량수: 54, 불량률: 1.1, 주요불량: "납땜 불량 23건, 미삽 8건" },
      equipment: { 가동률: 94.5, 비가동시간: "22분", 사유: "자재 교체" },
      workforce: { 투입인원: 12, 잔업: "없음" },
      other: {},
      metadata: { 작성자: "김반장" },
    },
    insights: {
      anomalies: [],
      trends: [{ metric: "달성률", direction: "stable", description: "최근 3일 97% 내외 안정" }],
      summary: "정상 운영 상태. 모든 지표가 목표 범위 내. 납땜 불량 비중이 다소 높으나 관리 범위.",
      action_items: [{ priority: "LOW", action: "납땜 불량 추이 모니터링 지속", responsible: "품질팀" }],
    },
  },
  {
    date: "2026-04-09",
    department: "SMT-1라인",
    extracted_data: {
      production: { 목표: 5000, 실적: 4790, 달성률: 95.8, 단위: "pcs" },
      quality: { 불량수: 67, 불량률: 1.4, 주요불량: "납땜 불량 31건, 부품 파손 12건" },
      equipment: { 가동률: 92.1, 비가동시간: "38분", 사유: "프로그램 수정" },
      workforce: { 투입인원: 12, 잔업: "1시간" },
      other: {},
      metadata: { 작성자: "김반장" },
    },
    insights: {
      anomalies: [],
      trends: [{ metric: "달성률", direction: "down", description: "전일 대비 1.4%p 하락" }],
      summary: "소폭 하락세. 달성률 95.8%로 전일 대비 감소. 납땜 불량 증가 추세 주의 필요.",
      action_items: [
        { priority: "MEDIUM", action: "납땜 장비 점검 실시", responsible: "설비팀" },
        { priority: "LOW", action: "부품 파손 원인 조사", responsible: "품질팀" },
      ],
    },
  },
  {
    date: "2026-04-10",
    department: "SMT-1라인",
    extracted_data: {
      production: { 목표: 5000, 실적: 4650, 달성률: 93.0, 단위: "pcs" },
      quality: { 불량수: 130, 불량률: 2.8, 주요불량: "납땜 불량 72건, 브릿지 28건, 미삽 18건" },
      equipment: { 가동률: 91.0, 비가동시간: "43분", 사유: "리플로우 온도 조정" },
      workforce: { 투입인원: 12, 잔업: "2시간" },
      other: {},
      metadata: { 작성자: "김반장" },
    },
    insights: {
      anomalies: [
        { metric: "불량률", value: "2.8%", expected: "< 2.0%", severity: "MEDIUM", description: "불량률 경고 기준 초과. 납땜 불량 급증." },
      ],
      trends: [
        { metric: "불량률", direction: "up", description: "3일 연속 상승 (1.1% → 1.4% → 2.8%)" },
        { metric: "달성률", direction: "down", description: "3일 연속 하락" },
      ],
      summary: "품질 이슈 발생. 불량률 2.8%로 경고 기준 초과. 리플로우 공정 중심 긴급 점검 필요.",
      action_items: [
        { priority: "HIGH", action: "리플로우 오븐 긴급 점검 및 온도 프로파일 재설정", responsible: "설비팀" },
        { priority: "HIGH", action: "납땜 불량 시료 SPC 분석", responsible: "품질팀" },
        { priority: "MEDIUM", action: "솔더 페이스트 로트 변경 여부 확인", responsible: "자재팀" },
      ],
    },
  },
  {
    date: "2026-04-11",
    department: "SMT-1라인",
    extracted_data: {
      production: { 목표: 5000, 실적: 4100, 달성률: 82.0, 단위: "pcs" },
      quality: { 불량수: 131, 불량률: 3.2, 주요불량: "납땜 불량 68건, 브릿지 32건, 쇼트 15건" },
      equipment: { 가동률: 78.0, 비가동시간: "132분", 사유: "리플로우 #2 고장 (히터 이상)" },
      workforce: { 투입인원: 14, 잔업: "3시간" },
      other: { 특이사항: "야간 긴급 정비 투입" },
      metadata: { 작성자: "김반장" },
    },
    insights: {
      anomalies: [
        { metric: "가동률", value: "78%", expected: "> 85%", severity: "HIGH", description: "리플로우 #2 히터 고장으로 2시간 이상 비가동" },
        { metric: "불량률", value: "3.2%", expected: "< 2.0%", severity: "HIGH", description: "설비 이상과 연계된 품질 악화. 쇼트 불량 신규 발생." },
      ],
      trends: [
        { metric: "가동률", direction: "down", description: "급격한 하락 (91% → 78%)" },
        { metric: "불량률", direction: "up", description: "4일 연속 상승, 위험 수준" },
      ],
      summary: "심각한 설비 고장 발생. 리플로우 #2 히터 이상으로 가동률 78%까지 하락. 불량률 3.2%로 위험 기준 초과. 야간 긴급 정비 투입.",
      action_items: [
        { priority: "HIGH", action: "리플로우 #2 히터 교체 완료 확인", responsible: "설비팀" },
        { priority: "HIGH", action: "고장 중 생산분 전수 검사", responsible: "품질팀" },
        { priority: "MEDIUM", action: "백업 장비 가동 계획 수립", responsible: "생산팀" },
        { priority: "MEDIUM", action: "야간 정비 결과 보고서 작성", responsible: "설비팀" },
      ],
    },
  },
  {
    date: "2026-04-12",
    department: "SMT-1라인",
    extracted_data: {
      production: { 목표: 5000, 실적: 4500, 달성률: 90.0, 단위: "pcs" },
      quality: { 불량수: 95, 불량률: 2.1, 주요불량: "납땜 불량 42건, 브릿지 18건" },
      equipment: { 가동률: 88.0, 비가동시간: "58분", 사유: "리플로우 #2 재가동 안정화" },
      workforce: { 투입인원: 14, 잔업: "2시간" },
      other: {},
      metadata: { 작성자: "김반장" },
    },
    insights: {
      anomalies: [
        { metric: "불량률", value: "2.1%", expected: "< 2.0%", severity: "MEDIUM", description: "경고 기준 소폭 초과. 전일 대비 개선 중." },
      ],
      trends: [
        { metric: "가동률", direction: "up", description: "78% → 88%로 회복 중" },
        { metric: "불량률", direction: "down", description: "3.2% → 2.1%로 개선" },
      ],
      summary: "회복 시작. 리플로우 #2 수리 후 재가동. 가동률·불량률 모두 개선 추세이나 아직 정상 범위 미달.",
      action_items: [
        { priority: "MEDIUM", action: "리플로우 #2 안정화 모니터링 (48시간)", responsible: "설비팀" },
        { priority: "LOW", action: "잔여 불량 원인 분석 완료", responsible: "품질팀" },
      ],
    },
  },
  {
    date: "2026-04-13",
    department: "SMT-1라인",
    extracted_data: {
      production: { 목표: 5000, 실적: 4825, 달성률: 96.5, 단위: "pcs" },
      quality: { 불량수: 72, 불량률: 1.5, 주요불량: "납땜 불량 35건, 미삽 12건" },
      equipment: { 가동률: 93.0, 비가동시간: "34분", 사유: "정기 점검" },
      workforce: { 투입인원: 12, 잔업: "1시간" },
      other: {},
      metadata: { 작성자: "김반장" },
    },
    insights: {
      anomalies: [],
      trends: [
        { metric: "가동률", direction: "up", description: "88% → 93%로 지속 개선" },
        { metric: "불량률", direction: "down", description: "2.1% → 1.5%로 정상 복귀 중" },
        { metric: "달성률", direction: "up", description: "90% → 96.5%로 회복" },
      ],
      summary: "개선 중. 모든 주요 지표 정상 범위 복귀. 리플로우 수리 후 안정적 가동 확인.",
      action_items: [
        { priority: "LOW", action: "주간 설비 종합 점검 실시", responsible: "설비팀" },
      ],
    },
  },
  {
    date: "2026-04-14",
    department: "SMT-1라인",
    extracted_data: {
      production: { 목표: 5000, 실적: 4905, 달성률: 98.1, 단위: "pcs" },
      quality: { 불량수: 44, 불량률: 0.9, 주요불량: "납땜 불량 18건, 미삽 8건" },
      equipment: { 가동률: 96.2, 비가동시간: "18분", 사유: "자재 교체" },
      workforce: { 투입인원: 12, 잔업: "없음" },
      other: {},
      metadata: { 작성자: "김반장" },
    },
    insights: {
      anomalies: [],
      trends: [
        { metric: "달성률", direction: "up", description: "98.1%로 주간 최고치 달성" },
        { metric: "불량률", direction: "down", description: "0.9%로 주간 최저 — 완전 정상" },
        { metric: "가동률", direction: "up", description: "96.2%로 목표 초과" },
      ],
      summary: "정상 복귀 완료. 달성률 98.1%, 불량률 0.9%, 가동률 96.2% — 모든 지표 우수. 설비 고장 이후 완벽하게 회복.",
      action_items: [
        { priority: "LOW", action: "금주 품질 개선 사례 공유 (리플로우 고장 대응)", responsible: "품질팀" },
      ],
    },
  },
];
