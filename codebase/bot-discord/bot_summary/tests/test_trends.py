import unittest
from datetime import UTC, datetime, timedelta

from models import SafeMessage, TopicCandidate, TrendDraft
from trends import TrendService, calculate_metrics


def message(ref: str, author: str, hours_ago: int, reactions: int = 0) -> SafeMessage:
    return SafeMessage(
        ref=ref,
        channel_ref="CHANNEL_01",
        author_ref=author,
        created_at=datetime.now(UTC) - timedelta(hours=hours_ago),
        content="topic",
        reaction_count=reactions,
    )


class TrendTests(unittest.TestCase):
    def test_active_topic_gets_high_score(self) -> None:
        current = {
            item.ref: item
            for item in [
                message("MSG_010", "USER_01", 1, 2),
                message("MSG_011", "USER_02", 2, 2),
                message("MSG_012", "USER_03", 3, 2),
                message("MSG_013", "USER_04", 4, 2),
            ]
        }
        baseline = {
            "MSG_001": message("MSG_001", "USER_01", 72),
            "MSG_002": message("MSG_002", "USER_02", 96),
        }
        metric = calculate_metrics(
            list(current), list(baseline), current, baseline, 24, 7
        )
        self.assertGreater(metric.hot_score, 0.7)
        self.assertEqual(metric.participant_count, 4)

    def test_one_author_spam_is_penalized(self) -> None:
        current = {
            f"MSG_{index:03d}": message(f"MSG_{index:03d}", "USER_01", 1)
            for index in range(10, 16)
        }
        metric = calculate_metrics(list(current), [], current, {}, 24, 7)
        self.assertLess(metric.hot_score, 0.7)
        self.assertEqual(metric.dominant_author_share, 1)


class TrendPipelineTests(unittest.IsolatedAsyncioTestCase):
    async def test_without_baseline_does_not_claim_new_or_rising(self) -> None:
        current = [
            message("MSG_010", "USER_01", 1),
            message("MSG_011", "USER_02", 2),
            message("MSG_012", "USER_03", 3),
        ]
        draft = TrendDraft(
            topics=[
                TopicCandidate(
                    topic="Tính năng tìm kiếm",
                    current_refs=[item.ref for item in current],
                    explanation="Nhiều trao đổi về tính năng.",
                )
            ]
        )

        class FakeLLM:
            async def generate(self, prompt, schema):
                return draft

        service = TrendService(FakeLLM())
        result = await service.analyze(current, [], 24, 7)

        self.assertEqual(result.topics[0].classification, "insufficient_data")
        self.assertIn("Chưa có baseline", result.data_quality)


if __name__ == "__main__":
    unittest.main()
