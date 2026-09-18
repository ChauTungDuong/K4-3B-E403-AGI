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

    def test_same_day_urgency_promotes_to_p1(self) -> None:
        self.assertEqual(
            assign_priority("P2", "Trước 11h: các nhóm cần đề cử 01 thành viên chấm điểm"),
            "P1",
        )
        self.assertEqual(
            assign_priority("P2", "chiều nay có chương trình Mini Hackathon AI lúc 17:30"),
            "P1",
        )
        self.assertEqual(
            assign_priority("P2", "nhớ nộp bài trước 23:59 đêm nay"),
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

    async def test_learner_and_user_you_owners_are_preserved(self) -> None:
        draft = SummaryDraft(
            executive_summary="Có hai việc cần làm.",
            tasks=[
                TaskCandidate(
                    title="Nộp checkpoint đúng lớp",
                    priority="P1",
                    status="open",
                    owner_ref="Learner",
                    reason="Yêu cầu cho học viên",
                    confidence=0.95,
                    evidence_refs=["MSG_001"],
                ),
                TaskCandidate(
                    title="Cập nhật thông tin nhóm",
                    priority="P1",
                    status="open",
                    owner_ref="USER_YOU",
                    reason="Yêu cầu riêng",
                    confidence=0.95,
                    evidence_refs=["MSG_002"],
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
                    content="Lưu ý @Learner nộp bài đúng hạn",
                ),
                SafeMessage(
                    ref="MSG_002",
                    channel_ref="CHANNEL_01",
                    author_ref="USER_01",
                    created_at=datetime.now(UTC),
                    content="USER_YOU cập nhật thông tin nhóm nhé",
                ),
            ]
        )

        self.assertEqual(len(result.tasks), 2)
        self.assertEqual(result.tasks[0].owner_ref, "Learner")
        self.assertEqual(result.tasks[1].owner_ref, "USER_YOU")

    async def test_unpadded_refs_match_padded_messages(self) -> None:
        draft = SummaryDraft(
            executive_summary="Có việc cần làm.",
            tasks=[
                TaskCandidate(
                    title="Đề cử thành viên chấm điểm",
                    priority="P2",
                    status="open",
                    reason="Chấm điểm chéo",
                    confidence=0.9,
                    evidence_refs=["MSG_30"],
                )
            ],
        )

        class FakeLLM:
            async def generate(self, prompt, schema):
                return draft

        service = SummaryService(FakeLLM())
        result = await service.analyze(
            [
                SafeMessage(
                    ref="MSG_030",
                    channel_ref="CHANNEL_01",
                    author_ref="USER_01",
                    created_at=datetime.now(UTC),
                    content="Trước 11h đề cử 01 thành viên chấm điểm",
                )
            ]
        )

        self.assertEqual(len(result.tasks), 1)
        self.assertEqual(result.tasks[0].evidence_refs, ["MSG_030"])

    async def test_hours_and_relative_day_deadlines_are_preserved(self) -> None:
        draft = SummaryDraft(
            executive_summary="Có việc cần làm đúng giờ.",
            tasks=[
                TaskCandidate(
                    title="Cập nhật slide pitching",
                    priority="P1",
                    status="open",
                    deadline="trước 17:00 chiều mai",
                    reason="Hạn nộp BTC",
                    confidence=0.95,
                    evidence_refs=["MSG_001"],
                ),
                TaskCandidate(
                    title="Đề cử chấm điểm zone",
                    priority="P1",
                    status="open",
                    deadline="Trước 11h",
                    reason="Chấm điểm",
                    confidence=0.9,
                    evidence_refs=["MSG_002"],
                ),
                TaskCandidate(
                    title="Tham gia Mini Hackathon",
                    priority="P1",
                    status="open",
                    deadline="17:30",
                    reason="Sự kiện phòng E403",
                    confidence=0.9,
                    evidence_refs=["MSG_003"],
                ),
            ],
        )

        class FakeLLM:
            async def generate(self, prompt, schema):
                return draft

        service = SummaryService(FakeLLM())
        result = await service.analyze(
            [
                SafeMessage(
                    ref="MSG_001",
                    channel_ref="CHANNEL_01",
                    author_ref="USER_01",
                    created_at=datetime.now(UTC),
                    content="nhớ cập nhật slide pitching của nhóm trước 17:00 chiều mai để kịp nộp BTC nhé",
                ),
                SafeMessage(
                    ref="MSG_002",
                    channel_ref="CHANNEL_01",
                    author_ref="USER_01",
                    created_at=datetime.now(UTC),
                    content="Trước 11h: các nhóm cần đề cử 01 thành viên",
                ),
                SafeMessage(
                    ref="MSG_003",
                    channel_ref="CHANNEL_01",
                    author_ref="USER_01",
                    created_at=datetime.now(UTC),
                    content="chiều nay có chương trình Mini Hackathon AI, bắt đầu vào 17:30",
                ),
            ]
        )

        self.assertEqual(len(result.tasks), 3)
        self.assertEqual(result.tasks[0].deadline, "trước 17:00 chiều mai")
        self.assertEqual(result.tasks[1].deadline, "Trước 11h")
        self.assertEqual(result.tasks[2].deadline, "17:30")


if __name__ == "__main__":
    unittest.main()
