"""물류 수작업일보 AI Agent — FastAPI + NiceGUI (Premium Glassmorphism)"""
import asyncio
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path

from nicegui import ui, app, events
from fastapi.staticfiles import StaticFiles

from sample_data import generate_daily_report_data
from report_generator import generate_report_image
from ai_analyzer import ocr_report_image, extract_key_issues, summarize_for_role, chat_with_report

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# 정적 파일 서빙
app.add_static_files("/output", str(OUTPUT_DIR))

# ══════════════════════════════════════════
# Premium Glassmorphism CSS
# ══════════════════════════════════════════
GLASS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --glass-bg: rgba(255,255,255,0.07);
    --glass-bg-hover: rgba(255,255,255,0.12);
    --glass-border: rgba(255,255,255,0.12);
    --glass-shadow: 0 8px 32px rgba(0,0,0,0.37);
    --accent: #60a5fa;
    --accent2: #a78bfa;
    --accent3: #34d399;
    --success: #34d399;
    --warn: #fbbf24;
    --danger: #f87171;
    --surface: rgba(15,23,42,0.6);
}

* { box-sizing: border-box; }

body {
    font-family: 'Inter', 'Malgun Gothic', sans-serif !important;
    background: #070b14 !important;
    min-height: 100vh;
    overflow-x: hidden;
    color: rgba(255,255,255,0.9);
}

/* ── Animated Mesh Gradient Background ── */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 10% 20%, rgba(59,130,246,0.15) 0%, transparent 60%),
        radial-gradient(ellipse 60% 80% at 90% 80%, rgba(139,92,246,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 70% 50% at 50% 50%, rgba(52,211,153,0.06) 0%, transparent 60%);
    animation: meshFloat 25s ease-in-out infinite;
    z-index: -2;
}

body::after {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 50% 40% at 70% 30%, rgba(96,165,250,0.08) 0%, transparent 50%),
        radial-gradient(ellipse 40% 60% at 20% 70%, rgba(167,139,250,0.08) 0%, transparent 50%);
    animation: meshFloat2 30s ease-in-out infinite;
    z-index: -1;
}

@keyframes meshFloat {
    0%, 100% { transform: translate(0, 0) scale(1); }
    25% { transform: translate(3%, -2%) scale(1.02); }
    50% { transform: translate(-2%, 3%) scale(0.98); }
    75% { transform: translate(1%, -1%) scale(1.01); }
}

@keyframes meshFloat2 {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    33% { transform: translate(-3%, 2%) rotate(2deg); }
    66% { transform: translate(2%, -3%) rotate(-1deg); }
}

/* ── Floating Particles ── */
.particles {
    position: fixed;
    inset: 0;
    z-index: -1;
    pointer-events: none;
    overflow: hidden;
}

.particle {
    position: absolute;
    border-radius: 50%;
    animation: particleFloat linear infinite;
    opacity: 0;
}

@keyframes particleFloat {
    0% { transform: translateY(100vh) scale(0); opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { transform: translateY(-10vh) scale(1); opacity: 0; }
}

/* ── Glass Card ── */
.glass-card {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(24px) saturate(1.2) !important;
    -webkit-backdrop-filter: blur(24px) saturate(1.2) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 20px !important;
    box-shadow: var(--glass-shadow), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative;
    overflow: hidden;
}

.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
}

.glass-card:hover {
    background: var(--glass-bg-hover) !important;
    border-color: rgba(255,255,255,0.2) !important;
    box-shadow: 0 12px 48px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.08) !important;
    transform: translateY(-2px) !important;
}

/* ── Hero Header ── */
.hero-header {
    background: linear-gradient(135deg, rgba(59,130,246,0.12), rgba(139,92,246,0.08), rgba(52,211,153,0.06)) !important;
    backdrop-filter: blur(40px) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 28px !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.4) !important;
    position: relative;
    overflow: hidden;
}

.hero-header::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: conic-gradient(from 0deg at 50% 50%, transparent 0deg, rgba(96,165,250,0.03) 60deg, transparent 120deg, rgba(139,92,246,0.03) 180deg, transparent 240deg, rgba(52,211,153,0.03) 300deg, transparent 360deg);
    animation: heroRotate 20s linear infinite;
}

@keyframes heroRotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.hero-title {
    font-size: 2.8rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #ffffff 0%, #60a5fa 50%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    position: relative;
    z-index: 1;
}

.hero-subtitle {
    font-size: 0.95rem;
    font-weight: 400;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.35);
    position: relative;
    z-index: 1;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 500;
    border: 1px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.05);
    color: rgba(255,255,255,0.6);
    position: relative;
    z-index: 1;
}

/* ── Form Inputs ── */
.glass-input .q-field__control {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    color: white !important;
    transition: all 0.3s ease !important;
}

.glass-input .q-field__control:hover {
    border-color: rgba(96,165,250,0.3) !important;
    background: rgba(255,255,255,0.06) !important;
}

.glass-input .q-field__control--focused {
    border-color: rgba(96,165,250,0.5) !important;
    box-shadow: 0 0 0 3px rgba(96,165,250,0.1) !important;
}

.glass-input .q-field__label {
    color: rgba(255,255,255,0.5) !important;
}

.glass-input input, .glass-input .q-field__native {
    color: white !important;
    font-weight: 500 !important;
}

/* ── Buttons ── */
.glass-btn {
    background: linear-gradient(135deg, #3b82f6, #7c3aed) !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 24px rgba(59,130,246,0.35), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    text-transform: none !important;
    position: relative;
    overflow: hidden;
}

.glass-btn::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.15), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.glass-btn:hover {
    box-shadow: 0 8px 36px rgba(59,130,246,0.5), inset 0 1px 0 rgba(255,255,255,0.2) !important;
    transform: translateY(-3px) !important;
}

.glass-btn:hover::before { opacity: 1; }

.glass-btn-danger {
    background: linear-gradient(135deg, #ef4444, #b91c1c) !important;
    box-shadow: 0 4px 24px rgba(239,68,68,0.3) !important;
}

.glass-btn-danger:hover {
    box-shadow: 0 8px 36px rgba(239,68,68,0.45) !important;
}

/* ── Stat Cards ── */
.stat-card {
    background: rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 20px !important;
    padding: 28px 24px !important;
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 20px 20px 0 0;
}

.stat-card:hover {
    border-color: rgba(255,255,255,0.15) !important;
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 40px rgba(0,0,0,0.3) !important;
}

.stat-card-blue::before { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.stat-card-purple::before { background: linear-gradient(90deg, #7c3aed, #a78bfa); }
.stat-card-green::before { background: linear-gradient(90deg, #059669, #34d399); }

.stat-icon {
    width: 48px; height: 48px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    margin-bottom: 16px;
}

.stat-icon-blue { background: rgba(59,130,246,0.15); color: #60a5fa; }
.stat-icon-purple { background: rgba(139,92,246,0.15); color: #a78bfa; }
.stat-icon-green { background: rgba(52,211,153,0.15); color: #34d399; }

.stat-number {
    font-size: 2.2rem;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}

.stat-number-blue {
    background: linear-gradient(135deg, #60a5fa, #93c5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-number-purple {
    background: linear-gradient(135deg, #a78bfa, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-number-green {
    background: linear-gradient(135deg, #34d399, #6ee7b7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ── Progress Bar ── */
.progress-container {
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    overflow: hidden;
    position: relative;
}

.progress-fill {
    background: linear-gradient(90deg, #3b82f6, #7c3aed, #34d399) !important;
    background-size: 300% 100% !important;
    animation: progressShimmer 3s ease-in-out infinite !important;
    border-radius: 12px !important;
    height: 100%;
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative;
}

.progress-fill::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);
    animation: progressGlow 2s ease-in-out infinite;
}

@keyframes progressShimmer {
    0% { background-position: 0% 0; }
    50% { background-position: 100% 0; }
    100% { background-position: 0% 0; }
}

@keyframes progressGlow {
    0%, 100% { transform: translateX(-100%); }
    100% { transform: translateX(200%); }
}

/* ── Report Cards ── */
.report-card {
    background: rgba(255,255,255,0.04) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 20px !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    overflow: hidden;
    position: relative;
}

.report-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, #3b82f6, #7c3aed);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.report-card:hover {
    transform: translateY(-3px) scale(1.005) !important;
    border-color: rgba(96,165,250,0.25) !important;
    box-shadow: 0 16px 48px rgba(59,130,246,0.15) !important;
}

.report-card:hover::before { opacity: 1; }

.report-thumb {
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    transition: all 0.3s ease;
}

.report-card:hover .report-thumb {
    border-color: rgba(96,165,250,0.3);
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}

/* ── Badges ── */
.data-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 5px 12px;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.01em;
    transition: all 0.3s ease;
}

.data-badge:hover {
    transform: translateY(-1px);
    filter: brightness(1.2);
}

/* ── Section Title ── */
.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: rgba(255,255,255,0.9);
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 10px;
}

.section-title::before {
    content: '';
    width: 4px;
    height: 22px;
    border-radius: 2px;
    background: linear-gradient(180deg, #60a5fa, #a78bfa);
}

/* ── Date Range Label ── */
.date-range {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: rgba(255,255,255,0.4);
    padding: 8px 16px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
}

/* ── Download Button ── */
.dl-btn {
    width: 44px; height: 44px;
    border-radius: 12px !important;
    background: rgba(96,165,250,0.1) !important;
    border: 1px solid rgba(96,165,250,0.2) !important;
    color: #60a5fa !important;
    transition: all 0.3s ease !important;
}

.dl-btn:hover {
    background: rgba(96,165,250,0.2) !important;
    border-color: rgba(96,165,250,0.4) !important;
    transform: scale(1.1) !important;
    box-shadow: 0 4px 16px rgba(96,165,250,0.2) !important;
}

/* ── Animations ── */
.fade-up {
    animation: fadeUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) both;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.stagger-1 { animation-delay: 0.05s; }
.stagger-2 { animation-delay: 0.1s; }
.stagger-3 { animation-delay: 0.15s; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

.nicegui-content { padding: 0 !important; }

/* ── Pulse dot for live status ── */
.pulse-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #34d399;
    position: relative;
}
.pulse-dot::before {
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    background: rgba(52,211,153,0.3);
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.5); opacity: 0; }
}

/* ── Tooltip / Divider ── */
.glass-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    margin: 4px 0;
}
</style>
"""

# ── Floating particle injection ──
PARTICLES_JS = """
<script>
document.addEventListener('DOMContentLoaded', () => {
    const container = document.createElement('div');
    container.className = 'particles';
    document.body.appendChild(container);
    const colors = ['rgba(96,165,250,0.4)', 'rgba(139,92,246,0.3)', 'rgba(52,211,153,0.3)'];
    for (let i = 0; i < 30; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        const size = Math.random() * 4 + 1;
        p.style.cssText = `
            width: ${size}px; height: ${size}px;
            left: ${Math.random() * 100}%;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            animation-duration: ${Math.random() * 20 + 15}s;
            animation-delay: ${Math.random() * 15}s;
        `;
        container.appendChild(p);
    }
});
</script>
"""


def format_date(d: date) -> str:
    return d.strftime("%Y-%m-%d")


@ui.page("/")
async def index():
    ui.add_head_html(GLASS_CSS)
    ui.add_head_html(PARTICLES_JS)

    # ── 상태 변수 ──
    generated_reports: list[dict] = []

    with ui.column().classes("w-full items-center p-4 md:p-8 gap-8"):
        # ═══════════════════════════════════════
        # 히어로 헤더
        # ═══════════════════════════════════════
        with ui.column().classes("hero-header w-full max-w-6xl p-10 items-center gap-3"):
            # 상단 상태 바
            with ui.row().classes("items-center gap-3 mb-2").style("position: relative; z-index: 1"):
                ui.element("div").classes("pulse-dot")
                ui.label("SYSTEM ONLINE").style(
                    "font-family: 'JetBrains Mono'; font-size: 0.7rem; font-weight: 600; "
                    "letter-spacing: 0.15em; color: #34d399;"
                )

            ui.label("물류 수작업일보 생성기").classes("hero-title")
            ui.label("Logistics Manual Handling Daily Report Generator").classes("hero-subtitle")

            with ui.row().classes("gap-3 mt-4"):
                with ui.element("div").classes("hero-badge"):
                    ui.icon("local_shipping").classes("text-blue-400").style("font-size: 1rem")
                    ui.label("수작업 관리")
                with ui.element("div").classes("hero-badge"):
                    ui.icon("analytics").classes("text-purple-400").style("font-size: 1rem")
                    ui.label("지표 분석")
                with ui.element("div").classes("hero-badge"):
                    ui.icon("download").classes("text-emerald-400").style("font-size: 1rem")
                    ui.label("PNG 리포트")

        # ═══════════════════════════════════════
        # 설정 카드
        # ═══════════════════════════════════════
        with ui.card().classes("glass-card w-full max-w-6xl p-8"):
            ui.label("생성 설정").classes("section-title mb-6")

            with ui.row().classes("w-full gap-6 items-end flex-wrap"):
                start_input = ui.input(
                    label="시작일",
                    value=format_date(date.today()),
                    placeholder="YYYY-MM-DD",
                ).classes("glass-input flex-1 min-w-[200px]")

                count_input = ui.number(
                    label="생성 개수 (일)",
                    value=5,
                    min=1,
                    max=90,
                    step=1,
                ).classes("glass-input flex-1 min-w-[180px]")

                end_label = ui.label("").classes("date-range pb-2")

            def update_end_label():
                try:
                    start = datetime.strptime(start_input.value, "%Y-%m-%d").date()
                    cnt = int(count_input.value or 1)
                    end = start + timedelta(days=cnt - 1)
                    end_label.set_text(f"{start}  →  {end}  ({cnt}일치)")
                except Exception:
                    end_label.set_text("")

            start_input.on("update:model-value", lambda: update_end_label())
            count_input.on("update:model-value", lambda: update_end_label())
            update_end_label()

        # ═══════════════════════════════════════
        # 네비게이션
        # ═══════════════════════════════════════
        with ui.row().classes("gap-3"):
            ui.button("일보 생성기", icon="description").classes(
                "glass-btn px-6 py-2 text-white text-sm"
            )
            ui.button("AI 분석 Agent", icon="psychology",
                      on_click=lambda: ui.navigate.to("/ai")).classes(
                "glass-btn px-6 py-2 text-white text-sm"
            ).style("background: linear-gradient(135deg, #059669, #34d399) !important")

        # ═══════════════════════════════════════
        # 액션 버튼
        # ═══════════════════════════════════════
        with ui.row().classes("gap-4"):
            generate_btn = ui.button("일보 생성 시작", icon="rocket_launch").classes(
                "glass-btn px-10 py-3 text-white text-base"
            )
            clear_btn = ui.button("초기화", icon="restart_alt").classes(
                "glass-btn glass-btn-danger px-7 py-3 text-white text-base"
            )

        # ═══════════════════════════════════════
        # 진행 상황
        # ═══════════════════════════════════════
        progress_card = ui.card().classes("glass-card w-full max-w-6xl p-8")
        progress_card.set_visibility(False)

        with progress_card:
            with ui.row().classes("w-full justify-between items-center mb-4"):
                with ui.row().classes("items-center gap-3"):
                    ui.icon("hourglass_top").classes("text-blue-400 text-xl")
                    progress_text = ui.label("").classes("text-white font-semibold text-base")
                progress_pct = ui.label("").classes(
                    "text-sm font-mono font-semibold"
                ).style("color: rgba(255,255,255,0.5); font-family: 'JetBrains Mono'")

            with ui.element("div").classes("progress-container w-full").style("height: 10px"):
                progress_fill = ui.element("div").classes("progress-fill").style("width: 0%")

        # ═══════════════════════════════════════
        # 통계 카드
        # ═══════════════════════════════════════
        stats_row = ui.row().classes("w-full max-w-6xl gap-5 flex-wrap justify-center")
        stats_row.set_visibility(False)

        with stats_row:
            with ui.card().classes("stat-card stat-card-blue flex-1 min-w-[220px]").style("padding: 28px 24px"):
                with ui.element("div").classes("stat-icon stat-icon-blue"):
                    ui.icon("check_circle")
                stat_count = ui.label("0").classes("stat-number stat-number-blue")
                ui.label("생성 완료").classes("text-sm mt-2 font-medium").style("color: rgba(255,255,255,0.45)")

            with ui.card().classes("stat-card stat-card-purple flex-1 min-w-[220px]").style("padding: 28px 24px"):
                with ui.element("div").classes("stat-icon stat-icon-purple"):
                    ui.icon("pan_tool")
                stat_total_wf = ui.label("0").classes("stat-number stat-number-purple")
                ui.label("총 수작업건수").classes("text-sm mt-2 font-medium").style("color: rgba(255,255,255,0.45)")

            with ui.card().classes("stat-card stat-card-green flex-1 min-w-[220px]").style("padding: 28px 24px"):
                with ui.element("div").classes("stat-icon stat-icon-green"):
                    ui.icon("percent")
                stat_avg_yield = ui.label("0%").classes("stat-number stat-number-green")
                ui.label("평균 달성률").classes("text-sm mt-2 font-medium").style("color: rgba(255,255,255,0.45)")

        # ═══════════════════════════════════════
        # 결과 그리드
        # ═══════════════════════════════════════
        results_label = ui.label("").classes("section-title")
        results_label.set_visibility(False)
        results_container = ui.column().classes("w-full max-w-6xl gap-4")

        # ── 생성 로직 ──
        async def do_generate():
            nonlocal generated_reports
            try:
                start = datetime.strptime(start_input.value, "%Y-%m-%d").date()
            except ValueError:
                ui.notify("날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)", type="negative")
                return

            cnt = int(count_input.value or 1)
            if cnt < 1:
                ui.notify("1개 이상 입력해주세요", type="warning")
                return

            generate_btn.disable()
            progress_card.set_visibility(True)
            stats_row.set_visibility(True)
            results_label.set_visibility(True)
            results_label.set_text(f"생성된 일보 ({cnt}건)")

            generated_reports = []
            total_wf = 0
            total_yield = 0

            for i in range(cnt):
                report_date = start + timedelta(days=i)
                pct = (i + 1) / cnt * 100

                progress_text.set_text(f"생성 중 · {report_date}")
                progress_pct.set_text(f"{i+1} / {cnt}")
                progress_fill.style(f"width: {pct}%")

                # 비동기로 무거운 작업 실행
                data = await asyncio.get_event_loop().run_in_executor(
                    None, generate_daily_report_data, report_date
                )
                output_path = str(OUTPUT_DIR / f"manual_report_{report_date}.png")
                await asyncio.get_event_loop().run_in_executor(
                    None, generate_report_image, data, output_path
                )

                generated_reports.append({"date": report_date, "data": data, "path": output_path})

                total_wf += data["total_manual_today"]
                total_yield += data["target_achievement"]

                # 통계 업데이트
                stat_count.set_text(str(i + 1))
                stat_total_wf.set_text(f"{total_wf:,}")
                stat_avg_yield.set_text(f"{total_yield / (i+1):.1f}%")

                # 결과 카드 추가
                delay_class = f"stagger-{(i % 3) + 1}"
                with results_container:
                    with ui.card().classes(f"report-card w-full fade-up {delay_class}"):
                        with ui.row().classes("w-full items-center gap-6 p-5"):
                            # 썸네일
                            ui.image(f"/output/manual_report_{report_date}.png").classes(
                                "report-thumb"
                            ).style("width: 220px; height: 150px; object-fit: cover")

                            # 정보
                            with ui.column().classes("flex-1 gap-2"):
                                with ui.row().classes("items-center gap-3"):
                                    ui.label(f"{report_date}").classes(
                                        "text-lg font-bold text-white"
                                    )
                                    ui.label("일보").classes("text-lg font-light").style(
                                        "color: rgba(255,255,255,0.5)"
                                    )

                                with ui.row().classes("items-center gap-2"):
                                    ui.icon("schedule").style(
                                        "font-size: 0.85rem; color: rgba(255,255,255,0.3)"
                                    )
                                    ui.label(f'{data["shift"]}').classes("text-sm").style(
                                        "color: rgba(255,255,255,0.4)"
                                    )
                                    ui.label("·").style("color: rgba(255,255,255,0.2)")
                                    ui.icon("person").style(
                                        "font-size: 0.85rem; color: rgba(255,255,255,0.3)"
                                    )
                                    ui.label(f'{data["reporter"]}').classes("text-sm").style(
                                        "color: rgba(255,255,255,0.4)"
                                    )

                                ui.element("div").classes("glass-divider").style("width: 100%")

                                with ui.row().classes("gap-2 mt-1 flex-wrap"):
                                    _badge(f'수작업 {data["total_manual_today"]:,} 건', "#3b82f6")
                                    _badge(
                                        f'달성 {data["target_achievement"]}%',
                                        "#34d399" if data["target_achievement"] >= 100 else "#fbbf24",
                                    )
                                    _badge(
                                        f'반송율 {data["manual_transport_rate"]}%',
                                        "#34d399" if data["manual_transport_rate"] < 5 else (
                                            "#fbbf24" if data["manual_transport_rate"] < 10 else "#f87171"
                                        ),
                                    )
                                    _badge(
                                        f'우선순위변경 {data["management_kpis"]["priority_change_count"]}건',
                                        "#34d399" if data["management_kpis"]["priority_change_count"] < 10 else (
                                            "#fbbf24" if data["management_kpis"]["priority_change_count"] < 20 else "#f87171"
                                        ),
                                    )

                            # 다운로드 버튼
                            ui.button(
                                icon="download",
                                on_click=lambda p=output_path: ui.download(p),
                            ).props("flat round").classes("dl-btn")

                await asyncio.sleep(0.05)  # UI 갱신

            progress_text.set_text(f"완료! {cnt}건 생성됨")
            progress_fill.style("width: 100%")
            generate_btn.enable()
            ui.notify(f"{cnt}건 일보 생성 완료!", type="positive", position="top")

        # ── 초기화 ──
        def do_clear():
            nonlocal generated_reports
            generated_reports = []
            results_container.clear()
            progress_card.set_visibility(False)
            stats_row.set_visibility(False)
            results_label.set_visibility(False)
            stat_count.set_text("0")
            stat_total_wf.set_text("0")
            stat_avg_yield.set_text("0%")
            progress_fill.style("width: 0%")

        generate_btn.on_click(do_generate)
        clear_btn.on_click(do_clear)


def _badge(text: str, color: str):
    """데이터 뱃지"""
    ui.label(text).classes("data-badge").style(
        f"background: {color}15; color: {color}; border: 1px solid {color}30"
    )


# ═══════════════════════════════════════
# AI 분석 페이지
# ═══════════════════════════════════════
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app.add_static_files("/uploads", str(UPLOAD_DIR))


@ui.page("/ai")
async def ai_page():
    ui.add_head_html(GLASS_CSS)
    ui.add_head_html(PARTICLES_JS)

    # 상태
    current_data: dict = {}
    chat_history: list[dict] = []

    with ui.column().classes("w-full items-center p-4 md:p-8 gap-8"):
        # ── 헤더 ──
        with ui.column().classes("hero-header w-full max-w-6xl p-10 items-center gap-3"):
            with ui.row().classes("items-center gap-3 mb-2").style("position: relative; z-index: 1"):
                ui.element("div").classes("pulse-dot")
                ui.label("AI AGENT").style(
                    "font-family: 'JetBrains Mono'; font-size: 0.7rem; font-weight: 600; "
                    "letter-spacing: 0.15em; color: #34d399;"
                )
            ui.label("일보 AI 분석 Agent").classes("hero-title")
            ui.label("Daily Report AI Analysis & Chat Agent").classes("hero-subtitle")

            with ui.row().classes("gap-3 mt-4"):
                with ui.element("div").classes("hero-badge"):
                    ui.icon("image_search").classes("text-blue-400").style("font-size: 1rem")
                    ui.label("OCR 추출")
                with ui.element("div").classes("hero-badge"):
                    ui.icon("psychology").classes("text-purple-400").style("font-size: 1rem")
                    ui.label("AI 분석")
                with ui.element("div").classes("hero-badge"):
                    ui.icon("chat").classes("text-emerald-400").style("font-size: 1rem")
                    ui.label("대화형 Q&A")

        # ── 네비게이션 ──
        with ui.row().classes("gap-3"):
            ui.button("일보 생성기", icon="description",
                      on_click=lambda: ui.navigate.to("/")).classes(
                "glass-btn px-6 py-2 text-white text-sm"
            ).style("background: rgba(255,255,255,0.1) !important; box-shadow: none !important")
            ui.button("AI 분석", icon="psychology").classes(
                "glass-btn px-6 py-2 text-white text-sm"
            )

        # ═══════════════════════════════════════
        # 1. 일보 이미지 업로드
        # ═══════════════════════════════════════
        with ui.card().classes("glass-card w-full max-w-6xl p-8"):
            ui.label("일보 이미지 업로드").classes("section-title mb-4")
            ui.label("일보 이미지(PNG/JPG)를 업로드하면 AI가 OCR로 데이터를 추출하고 분석합니다.").style(
                "color: rgba(255,255,255,0.5); font-size: 0.9rem; margin-bottom: 16px"
            )

            with ui.row().classes("w-full gap-4 items-end"):
                upload = ui.upload(
                    label="일보 이미지 선택",
                    auto_upload=True,
                    max_files=1,
                ).classes("glass-input flex-1").props('accept=".png,.jpg,.jpeg"')

                # 또는 샘플 데이터로 테스트
                sample_btn = ui.button("샘플 데이터로 테스트", icon="science").classes(
                    "glass-btn px-6 py-3 text-white text-sm"
                ).style("background: linear-gradient(135deg, #059669, #34d399) !important")

            upload_preview = ui.row().classes("w-full mt-4")
            upload_preview.set_visibility(False)

        # ═══════════════════════════════════════
        # 2. OCR 결과 + 핵심이슈
        # ═══════════════════════════════════════
        analysis_section = ui.column().classes("w-full max-w-6xl gap-6")
        analysis_section.set_visibility(False)

        with analysis_section:
            # 로딩
            loading_card = ui.card().classes("glass-card w-full p-6 items-center")
            with loading_card:
                ui.spinner("dots", size="lg").classes("text-blue-400")
                loading_text = ui.label("AI가 일보를 분석하고 있습니다...").classes(
                    "text-white mt-3 font-medium"
                )

            # 핵심이슈
            issues_card = ui.card().classes("glass-card w-full p-8")
            issues_card.set_visibility(False)
            with issues_card:
                ui.label("AI 핵심이슈 분석").classes("section-title mb-4")
                issues_content = ui.markdown("").classes("text-sm").style("color: rgba(255,255,255,0.85)")

            # 역할별 요약 탭
            summary_card = ui.card().classes("glass-card w-full p-8")
            summary_card.set_visibility(False)
            with summary_card:
                ui.label("역할별 맞춤 요약").classes("section-title mb-4")
                with ui.tabs().classes("w-full") as tabs:
                    exec_tab = ui.tab("임원용", icon="business")
                    oper_tab = ui.tab("실무자용", icon="engineering")

                with ui.tab_panels(tabs, value=exec_tab).classes("w-full").style(
                    "background: transparent; color: rgba(255,255,255,0.85)"
                ):
                    with ui.tab_panel(exec_tab):
                        exec_content = ui.markdown("분석 중...")
                    with ui.tab_panel(oper_tab):
                        oper_content = ui.markdown("분석 중...")

        # ═══════════════════════════════════════
        # 3. 대화형 챗봇
        # ═══════════════════════════════════════
        chat_section = ui.card().classes("glass-card w-full max-w-6xl p-8")
        chat_section.set_visibility(False)

        with chat_section:
            with ui.row().classes("w-full items-center gap-3 mb-4"):
                ui.icon("chat").classes("text-blue-400 text-xl")
                ui.label("일보 AI 챗봇").classes("section-title")
                ui.label("일보 데이터를 기반으로 질문하세요").style(
                    "color: rgba(255,255,255,0.4); font-size: 0.85rem; margin-left: 8px"
                )

            chat_container = ui.column().classes("w-full gap-3").style(
                "max-height: 500px; overflow-y: auto; padding: 8px"
            )

            # 추천 질문
            with ui.row().classes("w-full gap-2 flex-wrap mt-2"):
                for q in [
                    "오늘 가장 큰 이슈가 뭐야?",
                    "TAT 병목 구간은 어디야?",
                    "Worst 10 중 즉시 조치가 필요한 건?",
                    "수동반송율 추이는 어때?",
                ]:
                    ui.button(q, on_click=lambda question=q: send_message(question)).classes(
                        "text-xs px-3 py-1"
                    ).style(
                        "background: rgba(96,165,250,0.1); color: #60a5fa; "
                        "border: 1px solid rgba(96,165,250,0.2); border-radius: 100px; "
                        "text-transform: none; font-weight: 500"
                    )

            ui.element("div").classes("glass-divider w-full mt-2 mb-2")

            with ui.row().classes("w-full gap-3"):
                chat_input = ui.input(placeholder="질문을 입력하세요...").classes(
                    "glass-input flex-1"
                ).on("keydown.enter", lambda: send_message(chat_input.value))
                send_btn = ui.button(icon="send", on_click=lambda: send_message(chat_input.value)).classes(
                    "glass-btn px-4 py-3 text-white"
                )

        # ── 이벤트 핸들러 ──
        async def process_ocr(image_path: str):
            """OCR + AI 분석 실행."""
            nonlocal current_data, chat_history
            chat_history = []

            analysis_section.set_visibility(True)
            loading_card.set_visibility(True)
            issues_card.set_visibility(False)
            summary_card.set_visibility(False)
            chat_section.set_visibility(False)

            # Step 1: OCR
            loading_text.set_text("📸 일보 이미지를 OCR로 읽는 중...")
            await asyncio.sleep(0.1)

            try:
                ocr_data = await asyncio.get_event_loop().run_in_executor(
                    None, ocr_report_image, image_path
                )
                if ocr_data.get("parse_error"):
                    loading_text.set_text("⚠️ OCR 결과를 구조화하지 못했습니다. 원본 텍스트를 사용합니다.")
                    current_data = ocr_data
                else:
                    current_data = ocr_data
            except Exception as e:
                loading_text.set_text(f"❌ OCR 오류: {e}")
                return

            # Step 2: 핵심이슈 추출
            loading_text.set_text("🔍 핵심 이슈를 분석하는 중...")
            await asyncio.sleep(0.1)

            try:
                issues_text = await asyncio.get_event_loop().run_in_executor(
                    None, extract_key_issues, current_data
                )
                issues_content.set_content(issues_text)
                issues_card.set_visibility(True)
            except Exception as e:
                issues_content.set_content(f"분석 오류: {e}")
                issues_card.set_visibility(True)

            # Step 3: 역할별 요약 (병렬)
            loading_text.set_text("📊 역할별 맞춤 요약을 생성하는 중...")
            await asyncio.sleep(0.1)

            try:
                exec_text, oper_text = await asyncio.gather(
                    asyncio.get_event_loop().run_in_executor(
                        None, summarize_for_role, current_data, "executive"
                    ),
                    asyncio.get_event_loop().run_in_executor(
                        None, summarize_for_role, current_data, "operator"
                    ),
                )
                exec_content.set_content(exec_text)
                oper_content.set_content(oper_text)
                summary_card.set_visibility(True)
            except Exception as e:
                exec_content.set_content(f"요약 오류: {e}")
                oper_content.set_content(f"요약 오류: {e}")
                summary_card.set_visibility(True)

            loading_card.set_visibility(False)
            chat_section.set_visibility(True)

        async def process_sample():
            """샘플 데이터로 AI 분석 실행."""
            nonlocal current_data, chat_history
            chat_history = []

            analysis_section.set_visibility(True)
            loading_card.set_visibility(True)
            issues_card.set_visibility(False)
            summary_card.set_visibility(False)
            chat_section.set_visibility(False)

            loading_text.set_text("📦 샘플 데이터를 생성하는 중...")
            await asyncio.sleep(0.1)

            current_data = await asyncio.get_event_loop().run_in_executor(
                None, generate_daily_report_data, date.today()
            )

            # Step 2: 핵심이슈
            loading_text.set_text("🔍 핵심 이슈를 분석하는 중...")
            await asyncio.sleep(0.1)

            try:
                issues_text = await asyncio.get_event_loop().run_in_executor(
                    None, extract_key_issues, current_data
                )
                issues_content.set_content(issues_text)
                issues_card.set_visibility(True)
            except Exception as e:
                issues_content.set_content(f"분석 오류: {e}")
                issues_card.set_visibility(True)

            # Step 3: 역할별 요약
            loading_text.set_text("📊 역할별 맞춤 요약을 생성하는 중...")
            await asyncio.sleep(0.1)

            try:
                exec_text, oper_text = await asyncio.gather(
                    asyncio.get_event_loop().run_in_executor(
                        None, summarize_for_role, current_data, "executive"
                    ),
                    asyncio.get_event_loop().run_in_executor(
                        None, summarize_for_role, current_data, "operator"
                    ),
                )
                exec_content.set_content(exec_text)
                oper_content.set_content(oper_text)
                summary_card.set_visibility(True)
            except Exception as e:
                exec_content.set_content(f"요약 오류: {e}")
                oper_content.set_content(f"요약 오류: {e}")
                summary_card.set_visibility(True)

            loading_card.set_visibility(False)
            chat_section.set_visibility(True)

        async def handle_upload(e: events.UploadEventArguments):
            """파일 업로드 처리."""
            content = e.content.read()
            filename = e.name
            save_path = UPLOAD_DIR / filename
            save_path.write_bytes(content)

            with upload_preview:
                upload_preview.clear()
                ui.image(f"/uploads/{filename}").style(
                    "max-width: 400px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.1)"
                )
            upload_preview.set_visibility(True)

            await process_ocr(str(save_path))

        async def send_message(question: str):
            """챗봇 메시지 전송."""
            nonlocal chat_history
            if not question or not question.strip():
                return
            if not current_data:
                ui.notify("먼저 일보를 업로드하거나 샘플 데이터를 로드하세요.", type="warning")
                return

            question = question.strip()
            chat_input.set_value("")

            # 사용자 메시지 표시
            with chat_container:
                with ui.row().classes("w-full justify-end"):
                    ui.label(question).classes("px-4 py-2 rounded-2xl text-sm text-white").style(
                        "background: linear-gradient(135deg, #3b82f6, #7c3aed); "
                        "max-width: 70%; word-wrap: break-word"
                    )

            chat_history.append({"role": "user", "content": question})

            # AI 응답
            with chat_container:
                with ui.row().classes("w-full"):
                    thinking = ui.label("💭 생각하는 중...").classes("text-sm").style(
                        "color: rgba(255,255,255,0.4)"
                    )

            try:
                answer = await asyncio.get_event_loop().run_in_executor(
                    None, chat_with_report, current_data, question, chat_history
                )
                chat_history.append({"role": "assistant", "content": answer})

                thinking.delete()
                with chat_container:
                    with ui.row().classes("w-full"):
                        ui.markdown(answer).classes("px-4 py-3 rounded-2xl text-sm").style(
                            "background: rgba(255,255,255,0.06); "
                            "border: 1px solid rgba(255,255,255,0.08); "
                            "max-width: 85%; color: rgba(255,255,255,0.85)"
                        )
            except Exception as e:
                thinking.delete()
                with chat_container:
                    with ui.row().classes("w-full"):
                        ui.label(f"❌ 오류: {e}").classes("text-sm").style("color: #f87171")

            # 스크롤 맨 아래로
            chat_container.scroll_to(percent=1.0)

        upload.on_upload(handle_upload)
        sample_btn.on_click(process_sample)


ui.run(title="물류 수작업일보 AI Agent", favicon="📦", port=8090, reload=False)
