import tempfile
import unittest
from pathlib import Path

import aiosqlite

from database import Database


class SourcePriorityTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.database = Database(":memory:")
        await self.database.connect()

    async def asyncTearDown(self) -> None:
        await self.database.close()

    async def test_sources_keep_the_order_in_which_they_were_selected(self) -> None:
        self.assertTrue(await self.database.add_source(1, 30))
        self.assertTrue(await self.database.add_source(1, 10))
        self.assertTrue(await self.database.add_source(1, 20))
        self.assertFalse(await self.database.add_source(1, 10))

        self.assertEqual(await self.database.get_sources(1), [30, 10, 20])

    async def test_connect_migrates_legacy_source_table(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "legacy.db"
            legacy = await aiosqlite.connect(path)
            await legacy.executescript(
                """
                CREATE TABLE source_channels (
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    PRIMARY KEY (guild_id, channel_id)
                );
                INSERT INTO source_channels (guild_id, channel_id) VALUES (1, 30);
                INSERT INTO source_channels (guild_id, channel_id) VALUES (1, 10);
                """
            )
            await legacy.commit()
            await legacy.close()

            migrated = Database(str(path))
            await migrated.connect()
            try:
                self.assertEqual(await migrated.get_sources(1), [30, 10])
                self.assertTrue(await migrated.add_source(1, 20))
                self.assertEqual(await migrated.get_sources(1), [30, 10, 20])
            finally:
                await migrated.close()

    async def test_channel_group_is_case_insensitive_and_keeps_priority(self) -> None:
        for channel_id in (30, 10, 20):
            await self.database.add_source(1, channel_id)

        await self.database.set_channel_group(1, "Dự Án A", [30, 10, 20, 10])

        self.assertEqual(
            await self.database.get_channel_group(1, "dự án a"),
            [30, 10, 20],
        )
        groups = await self.database.list_channel_groups(1)
        self.assertEqual(
            [(row["name"], row["channel_count"]) for row in groups],
            [("Dự Án A", 3)],
        )

        await self.database.set_channel_group(1, "Dự án A", [20, 30])
        self.assertEqual(
            await self.database.get_channel_group(1, "DỰ ÁN A"),
            [20, 30],
        )

    async def test_removing_source_updates_and_removes_empty_group(self) -> None:
        await self.database.add_source(1, 10)
        await self.database.add_source(1, 20)
        await self.database.set_channel_group(1, "backend", [10, 20])

        await self.database.remove_source(1, 10)
        self.assertEqual(await self.database.get_channel_group(1, "backend"), [20])

        await self.database.remove_source(1, 20)
        self.assertIsNone(await self.database.get_channel_group(1, "backend"))


if __name__ == "__main__":
    unittest.main()
