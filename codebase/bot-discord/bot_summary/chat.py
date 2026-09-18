from __future__ import annotations

import json

from gemini import GeminiClient, load_prompt
from models import ChatDraft, ChatResult, ChatSection, SafeMessage
from privacy import redact_pii


class ChatService:
    """Trả lời yêu cầu tự nhiên nhưng chỉ từ message đã ẩn danh, có nguồn."""

    def __init__(self, llm: GeminiClient) -> None:
        self.llm = llm
        self.prompt_template = load_prompt("chat.txt")

    async def answer(
        self,
        messages: list[SafeMessage],
        user_input: str,
    ) -> ChatResult:
        if not messages:
            return ChatResult(
                status="not_found",
                overview="Không có tin nhắn để trả lời yêu cầu này.",
                analyzed_messages=0,
            )

        safe_input = redact_pii(user_input).strip()[:1000]
        if not safe_input:
            return ChatResult(
                status="not_found",
                overview="Yêu cầu không có nội dung sau khi loại thông tin nhạy cảm.",
                analyzed_messages=len(messages),
            )

        prompt = self.prompt_template.replace(
            "{{USER_REQUEST}}",
            json.dumps(safe_input, ensure_ascii=False),
        ).replace(
            "{{MESSAGES}}",
            json.dumps([item.for_prompt() for item in messages], ensure_ascii=False),
        )
        draft = await self.llm.generate(
            prompt,
            ChatDraft,
            trace_context={"pipeline": "chat"},
        )

        if draft.status == "refused":
            return ChatResult(
                status="refused",
                overview=(
                    "Mình chỉ hỗ trợ tìm, lọc và trình bày lại thông tin trong "
                    "các kênh Discord được phép; mình không thể thực hiện yêu cầu này."
                ),
                analyzed_messages=len(messages),
            )

        valid_refs = {item.ref for item in messages}
        sections: list[ChatSection] = []
        for section in draft.sections:
            refs = list(
                dict.fromkeys(
                    ref for ref in section.evidence_refs if ref in valid_refs
                )
            )
            heading = " ".join(section.heading.split())
            content = section.content.strip()
            if heading and content and refs:
                sections.append(
                    ChatSection(
                        heading=heading[:200],
                        content=content[:900],
                        evidence_refs=refs[:5],
                    )
                )

        if draft.status != "answered" or not sections:
            return ChatResult(
                status="not_found",
                overview=(
                    "Không tìm thấy thông tin có nguồn phù hợp với yêu cầu trong "
                    "các kênh và khoảng thời gian đã chọn."
                ),
                analyzed_messages=len(messages),
            )

        overview = draft.overview.strip()[:600]
        if not overview:
            overview = f"Tìm thấy {len(sections)} nội dung phù hợp."
        return ChatResult(
            status="answered",
            overview=overview,
            sections=sections[:5],
            analyzed_messages=len(messages),
        )
