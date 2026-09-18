from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from gemini import GeminiClient, load_prompt


DigestTier = Literal["P1", "P2", "P3", "EXCLUDE", "REFUSE", "NO_DATA"]


class PriorityDigestDecision(BaseModel):
    """Quyết định có cấu trúc để đo được từng tiêu chí của golden set."""

    tier: DigestTier
    response: str = Field(min_length=1)
    needs_confirmation: bool = False
    source_quote: str | None = None


class PriorityDigestService:
    """Lát cắt quyết định P1/P2/P3 dùng chung adapter AI thật của sản phẩm."""

    def __init__(self, llm: GeminiClient) -> None:
        self.llm = llm
        self.prompt_template = load_prompt("priority_digest.txt")

    async def analyze(
        self,
        channel: str,
        input_text: str,
        *,
        case_id: str | None = None,
    ) -> PriorityDigestDecision:
        prompt = self.prompt_template.replace("{{CHANNEL}}", channel).replace(
            "{{INPUT}}", input_text
        )
        context = {"pipeline": "priority_digest"}
        if case_id:
            context["case_id"] = case_id
        return await self.llm.generate(
            prompt,
            PriorityDigestDecision,
            trace_context=context,
        )
