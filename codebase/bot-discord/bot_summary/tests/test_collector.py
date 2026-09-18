import unittest
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

from collector import DiscordCollector
from models import Message


def message(message_id: int, channel_id: int, content: str = "nội dung") -> Message:
    return Message(
        message_id=message_id,
        channel_id=channel_id,
        channel_name=f"kenh-{channel_id}",
        author_id=100 + message_id,
        author_name=f"user-{message_id}",
        created_at=datetime(2026, 9, 18, message_id, tzinfo=UTC),
        content=content,
    )


class PrioritizedCollectionTests(unittest.IsolatedAsyncioTestCase):
    async def test_omits_whole_channel_and_every_lower_priority_channel(self) -> None:
        collector = DiscordCollector(
            max_per_channel=10,
            max_total=3,
            max_characters=1_000,
        )
        channels = [
            SimpleNamespace(id=1, name="mot"),
            SimpleNamespace(id=2, name="hai"),
            SimpleNamespace(id=3, name="ba"),
        ]
        collector._collect_complete_channel = AsyncMock(  # type: ignore[method-assign]
            side_effect=[
                SimpleNamespace(
                    messages=[message(1, 1), message(2, 1)],
                    complete=True,
                    reason=None,
                ),
                SimpleNamespace(
                    messages=[message(3, 2), message(4, 2)],
                    complete=True,
                    reason=None,
                ),
            ]
        )

        result = await collector.collect_channels_atomic(
            channels,
            datetime(2026, 9, 17, tzinfo=UTC),
            datetime(2026, 9, 19, tzinfo=UTC),
        )

        self.assertEqual([item.channel_id for item in result.included], [1])
        self.assertEqual([item.message_id for item in result.messages], [1, 2])
        self.assertEqual(
            [(item.channel_id, item.reason) for item in result.skipped],
            [(2, "context_budget"), (3, "lower_priority")],
        )
        self.assertEqual(collector._collect_complete_channel.await_count, 2)

    async def test_incomplete_channel_is_never_partially_included(self) -> None:
        collector = DiscordCollector(
            max_per_channel=2,
            max_total=10,
            max_characters=1_000,
        )
        channels = [
            SimpleNamespace(id=1, name="mot"),
            SimpleNamespace(id=2, name="hai"),
        ]
        collector._collect_complete_channel = AsyncMock(  # type: ignore[method-assign]
            return_value=SimpleNamespace(
                messages=[message(1, 1), message(2, 1)],
                complete=False,
                reason="channel_message_limit",
            )
        )

        result = await collector.collect_channels_atomic(
            channels,
            datetime(2026, 9, 17, tzinfo=UTC),
            datetime(2026, 9, 19, tzinfo=UTC),
        )

        self.assertEqual(result.messages, [])
        self.assertEqual(
            [(item.channel_id, item.reason) for item in result.skipped],
            [(1, "channel_message_limit"), (2, "lower_priority")],
        )


if __name__ == "__main__":
    unittest.main()
