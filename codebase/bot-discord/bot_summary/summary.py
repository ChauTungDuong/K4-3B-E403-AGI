from __future__ import annotations

import json
import re
import unicodedata

from gemini import GeminiClient, load_prompt
from models import (
    EvidenceItem,
    Priority,
    SafeMessage,
    SummaryDraft,
    SummaryResult,
    TaskCandidate,
    TaskItem,
)


_P0_WORDS = {
    "khẩn cấp",
    "blocker",
    "production sập",
    "mất dữ liệu",
    "security incident",
    "ngừng hoạt động",
    "sập server",
    "hỏng link thi",
    "lỗi hệ thống nộp bài",
}
_P1_WORDS = {
    "hạn chót",
    "ưu tiên cao",
    "gấp",
    "nộp nhầm repo",
    "đổi phòng sát giờ",
    "đổi giờ sát giờ",
    "hết hạn trong ngày",
}
_NEGATION_WORDS = {
    "không có deadline",
    "ko có deadline",
    "không cần gấp",
    "chưa cần gấp",
    "không gấp",
    "khi tiện",
    "tham khảo",
    "không bắt buộc",
    "chưa cần xử lý",
    "tùy chọn",
    "khi rảnh",
}
_TIME_PATTERN = re.compile(
    r"\b(?:hôm nay|ngày mai|tuần này|today|tomorrow|this week|thứ [2-7]|"
    r"chủ nhật|deadline|\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?|\d{4}-\d{2}-\d{2})\b",
    re.I,
)
_PRIORITY_ORDER: dict[Priority, int] = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


class SummaryService:
    def __init__(self, llm: GeminiClient, min_confidence: float = 0.75) -> None:
        self.llm = llm
        self.min_confidence = min_confidence
        self.prompt_template = load_prompt("summary.txt")

    async def analyze(self, messages: list[SafeMessage]) -> SummaryResult:
        if not messages:
            return SummaryResult(
                executive_summary="Không có tin nhắn để tóm tắt.",
                analyzed_messages=0,
            )

        prompt = self.prompt_template.replace(
            "{{MESSAGES}}",
            json.dumps([item.for_prompt() for item in messages], ensure_ascii=False),
        )
        draft = await self.llm.generate(prompt, SummaryDraft)
        by_ref = {item.ref: item for item in messages}

        tasks: list[TaskItem] = []
        for candidate in draft.tasks:
            task = self._validate_task(candidate, by_ref)
            if task is not None:
                tasks.append(task)

        return SummaryResult(
            executive_summary=draft.executive_summary.strip(),
            tasks=merge_duplicate_tasks(tasks)[:16],
            decisions=_valid_evidence_items(draft.decisions, set(by_ref))[:5],
            open_questions=_valid_evidence_items(draft.open_questions, set(by_ref))[:5],
            analyzed_messages=len(messages),
        )

    def _validate_task(
        self,
        candidate: TaskCandidate,
        by_ref: dict[str, SafeMessage],
    ) -> TaskItem | None:
        # ID bịa bị loại; task không còn nguồn hợp lệ cũng bị loại.
        refs = list(dict.fromkeys(ref for ref in candidate.evidence_refs if ref in by_ref))
        if (
            not refs
            or not candidate.title.strip()
            or candidate.status in {"done", "cancelled"}
        ):
            return None

        evidence = " ".join(by_ref[ref].content for ref in refs)
        authors = {by_ref[ref].author_ref for ref in refs}
        owner = candidate.owner_ref
        if owner and owner not in authors and owner not in evidence:
            owner = None

        # Prompt phải giữ nguyên cụm deadline; giá trị không có trong nguồn bị coi là suy đoán.
        deadline = candidate.deadline
        if (
            not deadline
            or not _TIME_PATTERN.search(evidence)
            or deadline.casefold() not in evidence.casefold()
        ):
            deadline = None
        status = candidate.status
        if candidate.confidence < self.min_confidence:
            if candidate.confidence < 0.5:
                return None
            status = "needs_confirmation"

        return TaskItem(
            title=candidate.title.strip(),
            priority=assign_priority(candidate.priority, candidate.title + " " + evidence),
            status=status,
            owner_ref=owner,
            deadline=deadline,
            reason=candidate.reason.strip(),
            confidence=candidate.confidence,
            evidence_refs=refs[:5],
        )


def assign_priority(proposed: Priority, evidence_text: str) -> Priority:
    """Code xác nhận các mức cao để model không tùy ý gắn P0 và tránh nâng hạng sai khi có phủ định."""
    text = evidence_text.casefold()
    if any(word in text for word in _NEGATION_WORDS):
        return "P3"
    if any(word in text for word in _P0_WORDS):
        return "P0"
    if proposed == "P0":
        return "P1"
    if any(word in text for word in _P1_WORDS) and proposed in {"P2", "P3"}:
        return "P1"
    return proposed


def merge_duplicate_tasks(tasks: list[TaskItem]) -> list[TaskItem]:
    """Gộp task có tiêu đề gần nhau bằng token overlap, không cần thêm thư viện."""
    merged: list[TaskItem] = []
    for task in tasks:
        duplicate = next(
            (item for item in merged if _similarity(item.title, task.title) >= 0.72),
            None,
        )
        if duplicate is None:
            merged.append(task.model_copy(deep=True))
            continue

        duplicate.evidence_refs = list(
            dict.fromkeys(duplicate.evidence_refs + task.evidence_refs)
        )[:5]
        duplicate.confidence = max(duplicate.confidence, task.confidence)
        if _PRIORITY_ORDER[task.priority] < _PRIORITY_ORDER[duplicate.priority]:
            duplicate.priority = task.priority
        if task.status == "blocked":
            duplicate.status = "blocked"

    return sorted(merged, key=lambda item: _PRIORITY_ORDER[item.priority])


def _similarity(left: str, right: str) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _tokens(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", text.casefold().replace("đ", "d"))
    plain = "".join(char for char in normalized if not unicodedata.combining(char))
    return set(re.findall(r"[a-z0-9]{2,}", plain))


def _valid_evidence_items(
    items: list[EvidenceItem], valid_refs: set[str]
) -> list[EvidenceItem]:
    result: list[EvidenceItem] = []
    for item in items:
        refs = list(dict.fromkeys(ref for ref in item.evidence_refs if ref in valid_refs))
        if refs and item.text.strip():
            result.append(EvidenceItem(text=item.text.strip(), evidence_refs=refs[:5]))
    return result
