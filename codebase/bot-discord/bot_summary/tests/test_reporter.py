import unittest

from models import TopicTrend, ToxicityResult, TrendResult
from reporter import TrendDetailsView, trend_embeds


class TrendReporterTests(unittest.TestCase):
    def test_topic_uses_natural_vietnamese_and_highlighted_metrics(self) -> None:
        result = TrendResult(
            overview="Có một chủ đề nổi bật.",
            data_quality="Chưa có baseline.",
            topics=[
                TopicTrend(
                    topic="Cảnh báo tin giả",
                    classification="insufficient_data",
                    message_count=1,
                    participant_count=1,
                    hot_score=0.68,
                    novelty_score=1,
                    sentiment="neutral",
                    confidence=0.51,
                    explanation="Nhắc học viên kiểm tra nguồn thông báo chính thức.",
                    evidence_refs=["MSG_016"],
                )
            ],
            toxicity=ToxicityResult(
                level="none", ratio=0, summary="Không có tín hiệu toxic."
            ),
            current_message_count=1,
            baseline_message_count=0,
        )

        embeds = trend_embeds(result, "#thông-báo")
        topic = embeds[1]
        metrics = topic.fields[0].value

        self.assertEqual(topic.title, "📌 Cảnh báo tin giả")
        self.assertEqual(topic.description, result.topics[0].explanation)
        self.assertEqual(topic.fields[0].name, "📊 Số liệu nổi bật")
        self.assertIn("**68%**", metrics)
        self.assertIn("**100%**", metrics)
        self.assertIn("Chưa đủ dữ liệu để xác nhận xu hướng", metrics)
        self.assertIn("Chưa có dữ liệu lịch sử để so sánh", metrics)
        self.assertIn("Trung tính", metrics)
        self.assertNotIn("insufficient_data", metrics)
        self.assertNotIn("neutral", metrics)
        self.assertNotIn("N/A", metrics)


class TrendDetailsViewTests(unittest.IsolatedAsyncioTestCase):
    async def test_view_has_detail_button_and_one_hour_timeout(self) -> None:
        view = TrendDetailsView([])
        self.assertEqual(view.timeout, 3600)
        self.assertEqual(len(view.children), 1)
        self.assertEqual(view.children[0].label, "Xem chi tiết")


if __name__ == "__main__":
    unittest.main()
