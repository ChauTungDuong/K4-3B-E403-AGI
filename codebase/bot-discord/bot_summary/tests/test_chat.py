import unittest
from datetime import UTC, datetime

from chat import ChatService
from models import ChatDraft, ChatSection, SafeMessage


def safe_message(ref: str = "MSG_001") -> SafeMessage:
    return SafeMessage(
        ref=ref,
        channel_ref="CHANNEL_01",
        author_ref="USER_01",
        created_at=datetime(2026, 9, 18, 9, tzinfo=UTC),
        content="Hạn nộp bài là 23:59 hôm nay.",
    )


class ChatServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_answer_keeps_only_sections_with_real_evidence(self) -> None:
        class FakeLLM:
            async def generate(self, prompt, schema, **kwargs):
                return ChatDraft(
                    status="answered",
                    overview="Có một deadline.",
                    sections=[
                        ChatSection(
                            heading="Checklist",
                            content="Nộp bài trước 23:59 hôm nay.",
                            evidence_refs=["MSG_001", "MSG_FAKE"],
                        ),
                        ChatSection(
                            heading="Không có nguồn",
                            content="Nội dung bịa.",
                            evidence_refs=["MSG_FAKE"],
                        ),
                    ],
                )

        result = await ChatService(FakeLLM()).answer(
            [safe_message()],
            "Chỉ liệt kê deadline dạng checklist",
        )

        self.assertEqual(result.status, "answered")
        self.assertEqual(len(result.sections), 1)
        self.assertEqual(result.sections[0].evidence_refs, ["MSG_001"])

    async def test_answer_without_valid_evidence_becomes_not_found(self) -> None:
        class FakeLLM:
            async def generate(self, prompt, schema, **kwargs):
                return ChatDraft(
                    status="answered",
                    overview="Có kết quả.",
                    sections=[
                        ChatSection(
                            heading="Kết quả",
                            content="Không có căn cứ.",
                            evidence_refs=["MSG_FAKE"],
                        )
                    ],
                )

        result = await ChatService(FakeLLM()).answer(
            [safe_message()],
            "Có thông tin review cuối tuần không?",
        )

        self.assertEqual(result.status, "not_found")
        self.assertEqual(result.sections, [])


if __name__ == "__main__":
    unittest.main()
