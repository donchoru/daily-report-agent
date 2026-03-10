"""일보 에이전트 DB — aiosqlite."""

from __future__ import annotations

import json
import logging
from typing import Any

import aiosqlite

from config import DB_PATH, TREND_LOOKBACK_DAYS

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    id TEXT PRIMARY KEY,
    report_date TEXT,
    report_type TEXT,
    department TEXT,
    extracted_data TEXT NOT NULL,
    insights TEXT NOT NULL,
    processing_time_sec REAL DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id TEXT NOT NULL REFERENCES analyses(id),
    filename TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    image_hash TEXT,
    created_at TEXT DEFAULT (datetime('now','localtime'))
);

CREATE INDEX IF NOT EXISTS idx_analyses_date ON analyses(report_date);
CREATE INDEX IF NOT EXISTS idx_analyses_dept ON analyses(department);
CREATE INDEX IF NOT EXISTS idx_images_analysis ON images(analysis_id);

-- 대화 히스토리 (분석 결과에 대한 후속 대화)
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id TEXT NOT NULL REFERENCES analyses(id),
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now','localtime'))
);

-- 장기 메모리 (사용자가 알려준 도메인 지식, 선호, 기준 등)
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    source_analysis_id TEXT,
    created_at TEXT DEFAULT (datetime('now','localtime')),
    updated_at TEXT DEFAULT (datetime('now','localtime'))
);

CREATE INDEX IF NOT EXISTS idx_conv_analysis ON conversations(analysis_id);
CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category);

-- 관심사 설정 (사용자가 중점적으로 보고 싶은 지표/영역)
CREATE TABLE IF NOT EXISTS interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric TEXT NOT NULL,
    priority INTEGER DEFAULT 1,
    description TEXT DEFAULT '',
    active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now','localtime'))
);
"""


class Database:
    def __init__(self) -> None:
        self._db: aiosqlite.Connection | None = None

    async def open(self) -> None:
        self._db = await aiosqlite.connect(str(DB_PATH))
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(SCHEMA)
        await self._db.commit()
        logger.info("DB opened: %s", DB_PATH)

    async def close(self) -> None:
        if self._db:
            await self._db.close()

    # ── 분석 저장 ──────────────────────────────────────────────

    async def save_analysis(
        self,
        analysis_id: str,
        report_date: str | None,
        report_type: str | None,
        department: str | None,
        extracted_data: dict,
        insights: dict,
        processing_time_sec: float,
    ) -> None:
        await self._db.execute(
            """INSERT INTO analyses (id, report_date, report_type, department,
               extracted_data, insights, processing_time_sec)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                analysis_id,
                report_date,
                report_type,
                department,
                json.dumps(extracted_data, ensure_ascii=False),
                json.dumps(insights, ensure_ascii=False),
                processing_time_sec,
            ),
        )
        await self._db.commit()

    async def save_image_meta(
        self,
        analysis_id: str,
        filename: str,
        mime_type: str,
        file_size: int,
        image_hash: str,
    ) -> int:
        cur = await self._db.execute(
            """INSERT INTO images (analysis_id, filename, mime_type, file_size, image_hash)
               VALUES (?, ?, ?, ?, ?)""",
            (analysis_id, filename, mime_type, file_size, image_hash),
        )
        await self._db.commit()
        return cur.lastrowid

    # ── 조회 ───────────────────────────────────────────────────

    async def get_analysis(self, analysis_id: str) -> dict | None:
        cur = await self._db.execute(
            "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
        )
        row = await cur.fetchone()
        if not row:
            return None
        result = dict(row)
        result["extracted_data"] = json.loads(result["extracted_data"])
        result["insights"] = json.loads(result["insights"])
        return result

    async def get_history(
        self,
        department: str | None = None,
        report_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        conditions: list[str] = []
        params: list[Any] = []
        if department:
            conditions.append("department = ?")
            params.append(department)
        if report_type:
            conditions.append("report_type = ?")
            params.append(report_type)
        where = " AND ".join(conditions) if conditions else "1=1"
        cur = await self._db.execute(
            f"""SELECT id, report_date, report_type, department,
                       insights, processing_time_sec, created_at
                FROM analyses WHERE {where}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?""",
            [*params, limit, offset],
        )
        rows = await cur.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            ins = json.loads(d["insights"])
            d["summary"] = ins.get("summary", "")
            del d["insights"]
            result.append(d)
        return result

    # ── 트렌드용 과거 데이터 ───────────────────────────────────

    async def get_recent_extracted(
        self,
        department: str | None = None,
        days: int = TREND_LOOKBACK_DAYS,
    ) -> list[dict]:
        conditions = ["report_date >= date('now', 'localtime', ?)"]
        params: list[Any] = [f"-{days} days"]
        if department:
            conditions.append("department = ?")
            params.append(department)
        where = " AND ".join(conditions)
        cur = await self._db.execute(
            f"""SELECT report_date, extracted_data FROM analyses
                WHERE {where} ORDER BY report_date""",
            params,
        )
        rows = await cur.fetchall()
        return [
            {"date": r["report_date"], "data": json.loads(r["extracted_data"])}
            for r in rows
        ]

    # ── 통계 ───────────────────────────────────────────────────

    async def get_stats(self) -> dict:
        cur = await self._db.execute("SELECT COUNT(*) as cnt FROM analyses")
        total = (await cur.fetchone())["cnt"]

        cur = await self._db.execute(
            """SELECT COUNT(*) as cnt FROM analyses
               WHERE date(created_at) = date('now','localtime')"""
        )
        today = (await cur.fetchone())["cnt"]

        return {"total_analyses": total, "today_analyses": today}

    # ── 대화 ───────────────────────────────────────────────────

    async def add_conversation(
        self, analysis_id: str, role: str, content: str
    ) -> int:
        cur = await self._db.execute(
            """INSERT INTO conversations (analysis_id, role, content)
               VALUES (?, ?, ?)""",
            (analysis_id, role, content),
        )
        await self._db.commit()
        return cur.lastrowid

    async def get_conversations(
        self, analysis_id: str, limit: int = 50
    ) -> list[dict]:
        cur = await self._db.execute(
            """SELECT role, content, created_at FROM conversations
               WHERE analysis_id = ? ORDER BY id LIMIT ?""",
            (analysis_id, limit),
        )
        return [dict(r) for r in await cur.fetchall()]

    # ── 장기 메모리 ────────────────────────────────────────────

    async def save_memory(
        self,
        category: str,
        content: str,
        source_analysis_id: str | None = None,
    ) -> int:
        cur = await self._db.execute(
            """INSERT INTO memories (category, content, source_analysis_id)
               VALUES (?, ?, ?)""",
            (category, content, source_analysis_id),
        )
        await self._db.commit()
        return cur.lastrowid

    async def get_memories(
        self, category: str | None = None, limit: int = 100
    ) -> list[dict]:
        if category:
            cur = await self._db.execute(
                """SELECT * FROM memories WHERE category = ?
                   ORDER BY updated_at DESC LIMIT ?""",
                (category, limit),
            )
        else:
            cur = await self._db.execute(
                "SELECT * FROM memories ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            )
        return [dict(r) for r in await cur.fetchall()]

    async def delete_memory(self, memory_id: int) -> bool:
        cur = await self._db.execute(
            "DELETE FROM memories WHERE id = ?", (memory_id,)
        )
        await self._db.commit()
        return cur.rowcount > 0

    # ── 관심사 ─────────────────────────────────────────────────

    async def set_interest(
        self, metric: str, priority: int = 1, description: str = ""
    ) -> int:
        # UPSERT by metric name
        cur = await self._db.execute(
            "SELECT id FROM interests WHERE metric = ? AND active = 1",
            (metric,),
        )
        existing = await cur.fetchone()
        if existing:
            await self._db.execute(
                """UPDATE interests SET priority = ?, description = ?
                   WHERE id = ?""",
                (priority, description, existing["id"]),
            )
            await self._db.commit()
            return existing["id"]
        cur = await self._db.execute(
            """INSERT INTO interests (metric, priority, description)
               VALUES (?, ?, ?)""",
            (metric, priority, description),
        )
        await self._db.commit()
        return cur.lastrowid

    async def get_interests(self) -> list[dict]:
        cur = await self._db.execute(
            "SELECT * FROM interests WHERE active = 1 ORDER BY priority"
        )
        return [dict(r) for r in await cur.fetchall()]

    async def delete_interest(self, interest_id: int) -> bool:
        cur = await self._db.execute(
            "UPDATE interests SET active = 0 WHERE id = ?", (interest_id,)
        )
        await self._db.commit()
        return cur.rowcount > 0

    # ── 분석 업데이트 (재분석 결과 저장) ──────────────────────

    async def update_analysis_insights(
        self, analysis_id: str, insights: dict, processing_time_sec: float
    ) -> None:
        await self._db.execute(
            """UPDATE analyses SET insights = ?, processing_time_sec = ?
               WHERE id = ?""",
            (json.dumps(insights, ensure_ascii=False), processing_time_sec, analysis_id),
        )
        await self._db.commit()
