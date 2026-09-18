from __future__ import annotations

import json
from datetime import UTC, datetime

import aiosqlite

from models import TrendResult


class Database:
    """SQLite nhỏ gọn cho cấu hình và snapshot xu hướng."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.connection: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self.connection = await aiosqlite.connect(self.path)
        self.connection.row_factory = aiosqlite.Row
        await self._conn().executescript(
            """
            PRAGMA journal_mode=WAL;

            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id INTEGER PRIMARY KEY,
                output_channel_id INTEGER,
                interval_hours INTEGER NOT NULL DEFAULT 6,
                last_run_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS source_channels (
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                priority_order INTEGER,
                PRIMARY KEY (guild_id, channel_id)
            );

            CREATE TABLE IF NOT EXISTS trend_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                current_hours INTEGER NOT NULL,
                baseline_days INTEGER NOT NULL,
                result_json TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_trend_snapshots_channel_time
            ON trend_snapshots (guild_id, channel_id, created_at);
            """
        )
        columns = await (
            await self._conn().execute("PRAGMA table_info(source_channels)")
        ).fetchall()
        if "priority_order" not in {row[1] for row in columns}:
            await self._conn().execute(
                "ALTER TABLE source_channels ADD COLUMN priority_order INTEGER"
            )
        # CSDL cũ không có thứ tự: rowid là xấp xỉ tốt nhất cho thứ tự đã thêm.
        await self._conn().execute(
            """
            UPDATE source_channels
            SET priority_order = rowid
            WHERE priority_order IS NULL
            """
        )
        await self._conn().commit()

    def _conn(self) -> aiosqlite.Connection:
        if self.connection is None:
            raise RuntimeError("Database chưa được kết nối")
        return self.connection

    async def close(self) -> None:
        if self.connection is not None:
            await self.connection.close()
            self.connection = None

    async def ensure_guild(self, guild_id: int) -> None:
        await self._conn().execute(
            "INSERT OR IGNORE INTO guild_config (guild_id, last_run_at) VALUES (?, ?)",
            (guild_id, datetime.now(UTC).isoformat()),
        )
        await self._conn().commit()

    async def set_output(self, guild_id: int, channel_id: int) -> None:
        await self.ensure_guild(guild_id)
        await self._conn().execute(
            "UPDATE guild_config SET output_channel_id = ? WHERE guild_id = ?",
            (channel_id, guild_id),
        )
        await self._conn().commit()

    async def set_interval(self, guild_id: int, hours: int) -> None:
        await self.ensure_guild(guild_id)
        await self._conn().execute(
            "UPDATE guild_config SET interval_hours = ? WHERE guild_id = ?",
            (hours, guild_id),
        )
        await self._conn().commit()

    async def add_source(self, guild_id: int, channel_id: int) -> bool:
        await self.ensure_guild(guild_id)
        cursor = await self._conn().execute(
            """
            INSERT OR IGNORE INTO source_channels
                (guild_id, channel_id, priority_order)
            VALUES (
                ?,
                ?,
                COALESCE(
                    (SELECT MAX(priority_order) + 1
                     FROM source_channels
                     WHERE guild_id = ?),
                    1
                )
            )
            """,
            (guild_id, channel_id, guild_id),
        )
        await self._conn().commit()
        return cursor.rowcount > 0

    async def remove_source(self, guild_id: int, channel_id: int) -> bool:
        cursor = await self._conn().execute(
            "DELETE FROM source_channels WHERE guild_id = ? AND channel_id = ?",
            (guild_id, channel_id),
        )
        await self._conn().commit()
        return cursor.rowcount > 0

    async def get_config(self, guild_id: int) -> aiosqlite.Row | None:
        cursor = await self._conn().execute(
            "SELECT * FROM guild_config WHERE guild_id = ?", (guild_id,)
        )
        return await cursor.fetchone()

    async def get_sources(self, guild_id: int) -> list[int]:
        cursor = await self._conn().execute(
            """
            SELECT channel_id
            FROM source_channels
            WHERE guild_id = ?
            ORDER BY priority_order, rowid
            """,
            (guild_id,),
        )
        return [row["channel_id"] for row in await cursor.fetchall()]

    async def due_guilds(self) -> list[aiosqlite.Row]:
        cursor = await self._conn().execute(
            """
            SELECT * FROM guild_config
            WHERE output_channel_id IS NOT NULL
              AND datetime(last_run_at, '+' || interval_hours || ' hours') <= datetime('now')
            """
        )
        return list(await cursor.fetchall())

    async def mark_run(self, guild_id: int, run_at: datetime) -> None:
        await self._conn().execute(
            "UPDATE guild_config SET last_run_at = ? WHERE guild_id = ?",
            (run_at.isoformat(), guild_id),
        )
        await self._conn().commit()

    async def save_trend_snapshot(
        self,
        guild_id: int,
        channel_id: int,
        current_hours: int,
        baseline_days: int,
        result: TrendResult,
    ) -> None:
        # Snapshot chỉ chứa dữ liệu đã ẩn danh và metric tổng hợp.
        await self._conn().execute(
            """
            INSERT INTO trend_snapshots
                (guild_id, channel_id, created_at, current_hours, baseline_days, result_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                guild_id,
                channel_id,
                datetime.now(UTC).isoformat(),
                current_hours,
                baseline_days,
                json.dumps(result.model_dump(mode="json"), ensure_ascii=False),
            ),
        )
        await self._conn().commit()
