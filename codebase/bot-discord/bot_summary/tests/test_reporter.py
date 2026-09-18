import unittest

from models import (
    EvidenceItem,
    SummaryResult,
    TaskItem,
    TopicTrend,
    ToxicityResult,
    TrendResult,
)
from reporter import TrendDetailsView, summary_embeds, trend_embeds


class SummaryReporterTests(unittest.TestCase):
    def test_digest_matches_compact_format_and_uses_discord_source_link(self) -> None:
        result = SummaryResult(
            executive_summary="Có hai việc cần theo dõi.",
            tasks=[
                TaskItem(
                    title="Nộp lab Day04 trên VLearn",
                    priority="P1",
                    status="open",
                    deadline="12:00",
                    reason="Hạn nộp sắp tới",
                    confidence=0.95,
                    evidence_refs=["MSG_001"],
                ),
                TaskItem(
                    title="Xem slide Day03",
                    priority="P2",
                    status="open",
                    reason="Tài liệu mới",
                    confidence=0.9,
                    evidence_refs=["MSG_002"],
                ),
            ],
            decisions=[
                EvidenceItem(
                    text="Dùng repo template mới.", evidence_refs=["MSG_002"]
                )
            ],
            analyzed_messages=4,
        )
        sources = {
            "MSG_001": (111111111111111111, 222222222222222222, 333333333333333333),
            "MSG_002": (111111111111111111, 222222222222222222, 444444444444444444),
        }

        embeds = summary_embeds(
            result, "#thông-báo", hours=24, sources=sources
        )

        self.assertEqual(len(embeds), 1)
        embed = embeds[0]
        self.assertIn("📋 Tóm tắt thông báo", embed.title)
        self.assertIn("24 giờ qua · 3 việc cần chú ý", embed.title)
        self.assertIn("🔴 **CẦN LÀM NGAY · Trước 12:00:**", embed.description)
        self.assertIn("🟡 **CẦN BIẾT:**", embed.description)
        self.assertIn("🟢 **ĐỌC THÊM:**", embed.description)
        self.assertIn("<#222222222222222222>", embed.description)
        self.assertIn(
            "https://discord.com/channels/111111111111111111/"
            "222222222222222222/333333333333333333",
            embed.description,
        )
        self.assertLessEqual(1 + len(embed.description.splitlines()), 8)

    def test_empty_digest_uses_zero_state_format(self) -> None:
        result = SummaryResult(
            executive_summary="Không có task mới.", analyzed_messages=3
        )

        embed = summary_embeds(result, "#chung", hours=12)[0]

        self.assertNotIn("việc cần chú ý", embed.title)
        self.assertIn("Không tìm thấy việc cần chú ý mới", embed.description)
        self.assertLessEqual(1 + len(embed.description.splitlines()), 8)


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
        overview = embeds[0]
        topic = embeds[1]
        metrics = topic.fields[0].value

        self.assertIn("📊 Phân tích xu hướng thảo luận", overview.title)
        self.assertIn("🔥 **CHỦ ĐỀ NÓNG NHẤT", overview.description)
        self.assertIn("💡 **LỐI TẮT XỬ LÝ:**", overview.description)
        self.assertLessEqual(1 + len(overview.description.splitlines()), 10)
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

    def test_quiet_trend_uses_zero_state_format(self) -> None:
        result = TrendResult(
            overview="Chưa đủ dữ liệu tạo xu hướng.",
            data_quality="Chưa có baseline.",
            toxicity=ToxicityResult(
                level="none", ratio=0, summary="Không có tín hiệu toxic."
            ),
            current_message_count=8,
            baseline_message_count=0,
        )

        embeds = trend_embeds(result, "#chung", hours=24)

        self.assertEqual(len(embeds), 1)
        self.assertIn("Chưa phát hiện xu hướng nổi bật", embeds[0].description)
        self.assertLessEqual(1 + len(embeds[0].description.splitlines()), 10)


class TrendDetailsViewTests(unittest.IsolatedAsyncioTestCase):
    async def test_view_has_detail_button_and_one_hour_timeout(self) -> None:
        view = TrendDetailsView([])
        self.assertEqual(view.timeout, 3600)
        self.assertEqual(len(view.children), 1)
        self.assertEqual(view.children[0].label, "Xem chi tiết")


if __name__ == "__main__":
    unittest.main()
