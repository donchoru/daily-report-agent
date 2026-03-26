"""물류 수작업일보 생성기 — 이미지 렌더링 (트렌드 차트 포함)"""
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
from pathlib import Path


# ── 한글 폰트 설정 ──
def setup_font():
    import matplotlib.font_manager as fm
    candidates = ["Malgun Gothic", "맑은 고딕", "NanumGothic", "AppleGothic"]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False


# ── 색상 팔레트 ──
C = {
    "bg": "#F8F9FA",
    "header": "#1B2A4A",
    "accent": "#2E86DE",
    "good": "#27AE60",
    "warn": "#F39C12",
    "bad": "#E74C3C",
    "text": "#2C3E50",
    "light": "#7F8C8D",
    "th": "#2C3E50",
    "row1": "#FFFFFF",
    "row2": "#F0F3F7",
    "border": "#BDC3C7",
    # TAT
    "tat_proc": "#2E86DE",
    "tat_insp": "#27AE60",
    "tat_trans": "#F39C12",
    "tat_wait": "#E74C3C",
    "tat_hold": "#8E44AD",
    # LOT
    "hot": "#E74C3C",
    "normal": "#3498DB",
    "low": "#95A5A6",
    "hold_lot": "#34495E",
    # Cassette
    "load": "#2ECC71",
    "unload": "#E67E22",
    "stk": "#9B59B6",
    # Misc
    "target_line": "#BDC3C7",
    "actual_bar": "#2E86DE",
}


def _color_rate(val, good, warn, lower_better=False):
    if lower_better:
        return C["good"] if val <= good else (C["warn"] if val <= warn else C["bad"])
    return C["good"] if val >= good else (C["warn"] if val >= warn else C["bad"])


def _style_ax(ax):
    """공통 축 스타일."""
    ax.set_facecolor(C["bg"])
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=10)


def _draw_trend_bar(ax, labels, values, title, color=None, ylabel="건수"):
    """간단 바 트렌드 차트."""
    ax.set_title(title, fontsize=13, fontweight="bold", color=C["text"], loc="left", pad=8)
    colors = color if isinstance(color, list) else [color or C["accent"]] * len(values)
    bars = ax.bar(labels, values, color=colors, width=0.5, edgecolor="white")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.02,
                f"{val:,}", ha="center", va="bottom", fontsize=9, fontweight="bold", color=C["text"])
    ax.set_ylabel(ylabel, fontsize=9, color=C["light"])
    _style_ax(ax)


def _draw_dual_trend(ax, labels, vals1, vals2, title, label1, label2, c1, c2):
    """이중 축 바+라인 차트 (바: vals1, 라인: vals2 비율)."""
    ax.set_title(title, fontsize=13, fontweight="bold", color=C["text"], loc="left", pad=8)
    x = np.arange(len(labels))
    bars = ax.bar(x, vals1, color=c1, width=0.45, edgecolor="white", alpha=0.85, label=label1)
    for bar, val in zip(bars, vals1):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(vals1) * 0.02,
                f"{val:,}", ha="center", va="bottom", fontsize=8, color=C["text"])
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    _style_ax(ax)

    ax2 = ax.twinx()
    ax2.plot(x, vals2, color=c2, marker="o", linewidth=2, markersize=5, label=label2)
    for xi, v in zip(x, vals2):
        ax2.annotate(f"{v}%", (xi, v), textcoords="offset points", xytext=(0, 8),
                     ha="center", fontsize=8, fontweight="bold", color=c2)
    ax2.set_ylabel(label2, fontsize=9, color=c2)
    ax2.spines[["top"]].set_visible(False)

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc="upper left")


def generate_report_image(data: dict, output_path: str = "manual_report.png") -> str:
    setup_font()

    fig = plt.figure(figsize=(22, 72), facecolor=C["bg"])
    fig.subplots_adjust(left=0.06, right=0.94, top=0.98, bottom=0.01)

    # 13 rows x 3 cols
    gs = GridSpec(13, 3, figure=fig, hspace=0.35, wspace=0.3,
                  height_ratios=[0.4, 1.0, 1.3, 1.2, 1.2, 1.2, 1.2, 1.2, 1.0, 1.0, 1.0, 1.5, 0.8])

    trend = data["manual_handling_trend"]
    tva = data["target_vs_actual"]
    tt = data["transport_trend"]
    pct = data["priority_change_trend"]
    lpt = data["lot_priority_trend"]
    rwt = data["ref_weight_change_trend"]
    tat = data["tat_trend"]
    cas = data["cassette_trend"]

    # ═══════════════════════════════════════
    # Row 0: 헤더
    # ═══════════════════════════════════════
    ax_h = fig.add_subplot(gs[0, :])
    ax_h.set_xlim(0, 10)
    ax_h.set_ylim(0, 1)
    ax_h.set_facecolor(C["header"])
    ax_h.axis("off")

    ax_h.text(0.3, 0.62, data["report_title"],
              fontsize=28, fontweight="bold", color="white", va="center")
    ax_h.text(0.3, 0.22,
              f'보고일: {data["report_date"]}    |    근무조: {data["shift"]}    |    작성자: {data["reporter"]}',
              fontsize=12, color="#BDC3C7", va="center")

    ax_h.add_patch(mpatches.FancyBboxPatch(
        (6.8, 0.1), 3.0, 0.8, boxstyle="round,pad=0.1",
        facecolor=C["accent"], edgecolor="none", alpha=0.9))
    ax_h.text(8.3, 0.62, f'금일 수작업: {data["total_manual_today"]:,} 건',
              fontsize=14, fontweight="bold", color="white", ha="center", va="center")
    ax_h.text(8.3, 0.28, f'달성률: {data["target_achievement"]}%',
              fontsize=11, color="#D6EAF8", ha="center", va="center")

    # ═══════════════════════════════════════
    # Row 1: 수작업 현황 트렌드 (월/주/일)
    # ═══════════════════════════════════════
    for col_idx, (period, period_data) in enumerate([
        ("월별 (3개월)", trend["monthly"]),
        ("주별 (4주)", trend["weekly"]),
        ("일별 (7일)", trend["daily"]),
    ]):
        ax = fig.add_subplot(gs[1, col_idx])
        labels = [d["label"] for d in period_data]
        values = [d["value"] for d in period_data]
        _draw_trend_bar(ax, labels, values, f"수작업 현황 — {period}")
        ax.tick_params(axis="x", rotation=15)

    # ═══════════════════════════════════════
    # Row 2: 목표 vs 실적 (일평균, 13개월)
    # ═══════════════════════════════════════
    ax_tva = fig.add_subplot(gs[2, :])
    ax_tva.set_title("  목표 vs 실적 (일평균, 월단위) — 2025.10 ~ 2026.10",
                      fontsize=15, fontweight="bold", color=C["text"], loc="left", pad=10)

    tva_labels = [t["label"] for t in tva]
    tva_targets = [t["target"] for t in tva]
    tva_actuals = [t["actual"] for t in tva]

    x_tva = np.arange(len(tva_labels))
    w_tva = 0.35

    ax_tva.bar(x_tva - w_tva / 2, tva_targets, w_tva, label="목표", color=C["target_line"],
               edgecolor="white", alpha=0.7)

    actual_colors = []
    actual_vals = []
    for t in tva:
        if t["actual"] is not None:
            actual_vals.append(t["actual"])
            pct_val = t["actual"] / t["target"] * 100 if t["target"] else 0
            actual_colors.append(_color_rate(pct_val, 100, 90))
        else:
            actual_vals.append(0)
            actual_colors.append("#DDDDDD")

    ax_tva.bar(x_tva + w_tva / 2, actual_vals, w_tva, label="실적", color=actual_colors,
               edgecolor="white")

    for xi, t in zip(x_tva, tva):
        if t["actual"] is not None:
            pct_val = round(t["actual"] / t["target"] * 100, 1) if t["target"] else 0
            ax_tva.text(xi + w_tva / 2, t["actual"] + 8,
                        f'{pct_val}%', ha="center", fontsize=8, fontweight="bold",
                        color=_color_rate(pct_val, 100, 90))

    ax_tva.set_xticks(x_tva)
    ax_tva.set_xticklabels(tva_labels, fontsize=9, rotation=30)
    ax_tva.set_ylabel("일평균 건수", fontsize=10)
    ax_tva.legend(fontsize=10, loc="upper left")
    _style_ax(ax_tva)

    # ═══════════════════════════════════════
    # Row 3: 수동반송수/수동반송율 트렌드 (월/주/일)
    # ═══════════════════════════════════════
    for col_idx, (period, period_data) in enumerate([
        ("월별", tt["monthly"]),
        ("주별", tt["weekly"]),
        ("일별", tt["daily"]),
    ]):
        ax = fig.add_subplot(gs[3, col_idx])
        labels = [d["label"] for d in period_data]
        counts = [d["manual_count"] for d in period_data]
        rates = [d["rate"] for d in period_data]
        _draw_dual_trend(ax, labels, counts, rates,
                         f"수동반송수/반송율 — {period}", "수동반송수", "반송율(%)",
                         C["accent"], C["bad"])
        ax.tick_params(axis="x", rotation=15)

    # ═══════════════════════════════════════
    # Row 4: 반송 우선순위 변경 트렌드 (월/주/일)
    # ═══════════════════════════════════════
    for col_idx, (period, period_data) in enumerate([
        ("월별", pct["monthly"]),
        ("주별", pct["weekly"]),
        ("일별", pct["daily"]),
    ]):
        ax = fig.add_subplot(gs[4, col_idx])
        labels = [d["label"] for d in period_data]
        values = [d["value"] for d in period_data]
        _draw_trend_bar(ax, labels, values, f"반송 우선순위 변경 — {period}", C["warn"])
        ax.tick_params(axis="x", rotation=15)

    # ═══════════════════════════════════════
    # Row 5: LOT 우선순위 트렌드 (월/주/일)
    # ═══════════════════════════════════════
    for col_idx, (period, period_data) in enumerate([
        ("월별", lpt["monthly"]),
        ("주별", lpt["weekly"]),
        ("일별", lpt["daily"]),
    ]):
        ax = fig.add_subplot(gs[5, col_idx])
        labels = [d["label"] for d in period_data]
        values = [d["value"] for d in period_data]
        _draw_trend_bar(ax, labels, values, f"LOT 우선순위 — {period}", C["accent"])
        ax.tick_params(axis="x", rotation=15)

    # ═══════════════════════════════════════
    # Row 6: 기준정보/가중치 변경 트렌드 (월/주/일)
    # ═══════════════════════════════════════
    for col_idx, (period, period_data) in enumerate([
        ("월별", rwt["monthly"]),
        ("주별", rwt["weekly"]),
        ("일별", rwt["daily"]),
    ]):
        ax = fig.add_subplot(gs[6, col_idx])
        labels = [d["label"] for d in period_data]
        values = [d["value"] for d in period_data]
        _draw_trend_bar(ax, labels, values, f"기준정보/가중치 변경 — {period}", "#8E44AD")
        ax.tick_params(axis="x", rotation=15)

    # ═══════════════════════════════════════
    # Row 7: TAT 트렌드 (월/주/일) — 스택 바차트
    # ═══════════════════════════════════════
    tat_keys = ["processing", "inspection", "transport", "waiting", "hold"]
    tat_names = ["가공", "검사", "운반", "대기", "Hold"]
    tat_colors = [C["tat_proc"], C["tat_insp"], C["tat_trans"], C["tat_wait"], C["tat_hold"]]

    for col_idx, (period, period_data) in enumerate([
        ("월별", tat["monthly"]),
        ("주별", tat["weekly"]),
        ("일별", tat["daily"]),
    ]):
        ax = fig.add_subplot(gs[7, col_idx])
        ax.set_title(f"TAT — {period}", fontsize=13, fontweight="bold", color=C["text"], loc="left", pad=8)

        labels = [d["label"] for d in period_data]
        x = np.arange(len(labels))
        bottom = np.zeros(len(labels))

        for key, name, color in zip(tat_keys, tat_names, tat_colors):
            vals = [d[key] for d in period_data]
            ax.bar(x, vals, bottom=bottom, color=color, width=0.5, label=name, edgecolor="white", linewidth=0.5)
            bottom += np.array(vals)

        # 합계 표시
        for xi, total in zip(x, bottom):
            ax.text(xi, total + 1, f"{total:.0f}", ha="center", fontsize=8, fontweight="bold", color=C["text"])

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9, rotation=15)
        ax.set_ylabel("분", fontsize=9, color=C["light"])
        if col_idx == 0:
            ax.legend(fontsize=7, loc="upper left", ncol=3)
        _style_ax(ax)

    # ═══════════════════════════════════════
    # Row 8: 카세트 수동반송 트렌드 (Load/Unload/STK × 월/주/일)
    # ═══════════════════════════════════════
    for col_idx, (period, period_data) in enumerate([
        ("월별", cas["monthly"]),
        ("주별", cas["weekly"]),
        ("일별", cas["daily"]),
    ]):
        ax = fig.add_subplot(gs[8, col_idx])
        ax.set_title(f"카세트 반송 — {period}", fontsize=13, fontweight="bold",
                      color=C["text"], loc="left", pad=8)

        labels = [d["label"] for d in period_data]
        x = np.arange(len(labels))
        w = 0.22
        ax.bar(x - w, [d["load"] for d in period_data], w, label="Load", color=C["load"], edgecolor="white")
        ax.bar(x, [d["unload"] for d in period_data], w, label="Unload", color=C["unload"], edgecolor="white")
        ax.bar(x + w, [d["stk"] for d in period_data], w, label="STK", color=C["stk"], edgecolor="white")

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9, rotation=15)
        ax.legend(fontsize=8, loc="upper right")
        _style_ax(ax)

    # ═══════════════════════════════════════
    # Row 9: 공정군별 수동반송수 (left) + LOT 우선순위 파이 (right)
    # ═══════════════════════════════════════
    ax_pg = fig.add_subplot(gs[9, :2])
    ax_pg.set_title("  공정군별 수동반송수", fontsize=14, fontweight="bold",
                     color=C["text"], loc="left", pad=10)
    pg_names = [p["process"] for p in data["process_group_transport"]]
    pg_vals = [p["count"] for p in data["process_group_transport"]]
    pg_colors = plt.cm.Blues(np.linspace(0.4, 0.85, len(pg_vals)))
    bars_pg = ax_pg.bar(pg_names, pg_vals, color=pg_colors, width=0.55, edgecolor="white")
    for bar, val in zip(bars_pg, pg_vals):
        ax_pg.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3,
                   f"{val}", ha="center", fontsize=10, fontweight="bold", color=C["text"])
    _style_ax(ax_pg)

    ax_lot = fig.add_subplot(gs[9, 2])
    ax_lot.set_title("LOT 우선순위별 재공", fontsize=14, fontweight="bold",
                      color=C["text"], loc="left", pad=10)
    lot_wip = data["lot_priority_wip"]
    lot_labels = list(lot_wip.keys())
    lot_values = list(lot_wip.values())
    lot_colors = [C["hot"], C["normal"], C["low"], C["hold_lot"]]
    wedges, texts, autotexts = ax_lot.pie(
        lot_values, labels=lot_labels, colors=lot_colors, autopct="%1.0f%%",
        startangle=90, pctdistance=0.75, textprops={"fontsize": 11})
    for at in autotexts:
        at.set_fontweight("bold")
        at.set_color("white")
    ax_lot.text(0, 0, f"총 {sum(lot_values)}", ha="center", va="center",
                fontsize=14, fontweight="bold", color=C["text"])

    # ═══════════════════════════════════════
    # Row 10: KPI 요약 카드
    # ═══════════════════════════════════════
    ax_kpi = fig.add_subplot(gs[10, :])
    ax_kpi.axis("off")
    ax_kpi.set_xlim(0, 10)
    ax_kpi.set_ylim(0, 1)
    ax_kpi.set_title("  핵심 KPI 요약", fontsize=15, fontweight="bold",
                      color=C["text"], loc="left", pad=10)

    today_tat = data["tat_trend"]["daily"][-1]
    total_tat = sum(today_tat[k] for k in ["processing", "inspection", "transport", "waiting", "hold"])
    today_tt = data["transport_trend"]["daily"][-1]

    kpi_items = [
        ("금일 수작업", f'{data["total_manual_today"]:,} 건', C["accent"]),
        ("달성률", f'{data["target_achievement"]}%', _color_rate(data["target_achievement"], 100, 90)),
        ("수동반송율", f'{today_tt["rate"]}%', _color_rate(today_tt["rate"], 5, 10, lower_better=True)),
        ("금일 TAT", f'{total_tat:.0f}분', _color_rate(total_tat, 120, 180, lower_better=True)),
    ]

    for i, (label, value, color) in enumerate(kpi_items):
        x_pos = 0.3 + i * 2.4
        ax_kpi.add_patch(mpatches.FancyBboxPatch(
            (x_pos, 0.1), 2.0, 0.75, boxstyle="round,pad=0.15",
            facecolor="white", edgecolor=color, linewidth=2.5))
        ax_kpi.text(x_pos + 1.0, 0.58, value, ha="center", va="center",
                    fontsize=18, fontweight="bold", color=color)
        ax_kpi.text(x_pos + 1.0, 0.28, label, ha="center", va="center",
                    fontsize=11, color=C["light"])

    # ═══════════════════════════════════════
    # Row 11: Worst 10 테이블
    # ═══════════════════════════════════════
    ax_w10 = fig.add_subplot(gs[11, :])
    ax_w10.axis("off")
    ax_w10.set_title("  부서별 공정별 수동반송 전일비교 (Worst 10)", fontsize=15, fontweight="bold",
                      color=C["text"], loc="left", pad=12)

    columns = ["순위", "부서", "공정", "금일", "전일", "증감"]
    col_widths = [0.08, 0.15, 0.15, 0.18, 0.18, 0.18]
    table_data = []
    for item in data["worst10"]:
        diff_str = f"+{item['diff']}" if item["diff"] > 0 else str(item["diff"])
        table_data.append([
            str(item["rank"]), item["dept"], item["process"],
            str(item["today"]), str(item["yesterday"]), diff_str
        ])

    table = ax_w10.table(cellText=table_data, colLabels=columns, colWidths=col_widths,
                          loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.0)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(C["border"])
        if row == 0:
            cell.set_facecolor(C["th"])
            cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor(C["row1"] if row % 2 == 1 else C["row2"])
            if col == 5 and row > 0:
                txt = cell.get_text().get_text()
                if txt.startswith("+"):
                    cell.set_text_props(color=C["bad"], fontweight="bold")
                else:
                    cell.set_text_props(color=C["good"], fontweight="bold")
            if col == 0 and row > 0:
                rank = int(cell.get_text().get_text())
                if rank <= 3:
                    cell.set_text_props(color=C["bad"], fontweight="bold")

    # ═══════════════════════════════════════
    # Row 12: 주요 이슈
    # ═══════════════════════════════════════
    ax_iss = fig.add_subplot(gs[12, :])
    ax_iss.axis("off")
    ax_iss.set_xlim(0, 10)
    ax_iss.set_ylim(0, 1)
    ax_iss.set_title("  주요 이슈 / 특이사항", fontsize=15, fontweight="bold",
                      color=C["text"], loc="left", pad=10)

    for i, issue in enumerate(data["issues"]):
        y = 0.85 - i * 0.17
        ax_iss.plot(0.3, y, "s", color=C["accent"], markersize=8)
        ax_iss.text(0.55, y, issue, fontsize=11, va="center", color=C["text"])

    # ── 저장 ──
    output = Path(output_path)
    fig.savefig(output, dpi=150, bbox_inches="tight", facecolor=C["bg"])
    plt.close(fig)
    return str(output.resolve())
