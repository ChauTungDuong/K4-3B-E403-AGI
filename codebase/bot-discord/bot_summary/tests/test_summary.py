import unittest
from datetime import UTC, datetime

from models import SafeMessage, SummaryDraft, TaskCandidate, TaskItem
from summary import SummaryService, assign_priority, merge_duplicate_tasks


def task(title: str, priority: str, ref: str) -> TaskItem:
    return TaskItem(
        title=title,
        priority=priority,
        status="open",
        reason="Có yêu cầu rõ ràng",
        confidence=0.9,
        evidence_refs=[ref],
    )


class SummaryTests(unittest.TestCase):
    def test_p0_requires_emergency_evidence(self) -> None:
        self.assertEqual(assign_priority("P0", "việc thông thường"), "P1")
        self.assertEqual(assign_priority("P2", "production sập cần xử lý"), "P0")

    def test_negation_downgrades_priority_to_p3(self) -> None:
        self.assertEqual(
            assign_priority("P1", "Khi tiện xem lại slide, không có deadline và không cần gấp"),
            "P3",
        )
        self.assertEqual(
            assign_priority("P2", "Đọc thêm tài liệu khi tiện"),
            "P3",
        )
        self.assertEqual(
            assign_priority("P2", "hạn chót nộp bài"),
            "P1",
        )

    def test_duplicate_tasks_are_merged(self) -> None:
        result = merge_duplicate_tasks(
            [
                task("Sửa lỗi đăng nhập", "P2", "MSG_001"),
                task("Sửa lỗi đăng nhập", "P1", "MSG_002"),
            ]
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].priority, "P1")
        self.assertEqual(result[0].evidence_refs, ["MSG_001", "MSG_002"])


class SummaryPipelineTests(unittest.IsolatedAsyncioTestCase):
    async def test_invalid_evidence_and_invented_fields_are_removed(self) -> None:
        draft = SummaryDraft(
            executive_summary="Có một việc cần xác nhận.",
            tasks=[
                TaskCandidate(
                    title="Cập nhật tài liệu",
                    priority="P2",
                    status="open",
                    owner_ref="USER_99",
                    deadline="2026-09-30",
                    reason="Có đề xuất cập nhật",
                    confidence=0.6,
                    evidence_refs=["MSG_001", "MSG_FAKE"],
                ),
                TaskCandidate(
                    title="Task không có nguồn",
                    priority="P2",
                    status="open",
                    reason="Không hợp lệ",
                    confidence=0.9,
                    evidence_refs=["MSG_FAKE"],
                ),
            ],
        )

        class FakeLLM:
            async def generate(self, prompt, schema):
                return draft

        service = SummaryService(FakeLLM(), min_confidence=0.75)
        result = await service.analyze(
            [
                SafeMessage(
                    ref="MSG_001",
                    channel_ref="CHANNEL_01",
                    author_ref="USER_01",
                    created_at=datetime.now(UTC),
                    content="Có thể cập nhật tài liệu không?",
                )
            ]
        )

        self.assertEqual(len(result.tasks), 1)
        self.assertEqual(result.tasks[0].status, "needs_confirmation")
        self.assertIsNone(result.tasks[0].owner_ref)
        self.assertIsNone(result.tasks[0].deadline)


if __name__ == "__main__":
    unittest.main()
