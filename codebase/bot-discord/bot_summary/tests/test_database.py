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


if __name__ == "__main__":
    unittest.main()
