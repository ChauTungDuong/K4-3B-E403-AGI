from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Priority = Literal["P0", "P1", "P2", "P3"]
Sentiment = Literal["positive", "neutral", "negative", "mixed"]
ChatStatus = Literal["answered", "not_found", "refused"]


class Message(BaseModel):
    """Tin nhắn nội bộ còn danh tính thật; không được gửi trực tiếp tới LLM."""

    message_id: int
    channel_id: int
    channel_name: str
    author_id: int
    author_name: str
    created_at: datetime
    content: str
    reaction_count: int = 0
    reply_count: int = 0
    reply_to_id: int | None = None


class SafeMessage(BaseModel):
    """Tin nhắn đã ẩn danh, an toàn để đưa vào prompt."""

    ref: str
    channel_ref: str
    author_ref: str
    created_at: datetime
    content: str
    reaction_count: int = 0
    reply_count: int = 0
    reply_to_ref: str | None = None

    def for_prompt(self) -> dict[str, object]:
        return {
            "ref": self.ref,
            "channel": self.channel_ref,
            "author": self.author_ref,
            "created_at": self.created_at.isoformat(),
            "reactions": self.reaction_count,
            "replies": self.reply_count,
            "reply_to": self.reply_to_ref,
            "content": self.content,
        }


class TaskCandidate(BaseModel):
    title: str
    priority: Priority
    status: Literal[
        "open", "in_progress", "blocked", "done", "cancelled", "needs_confirmation"
    ]
    owner_ref: str | None = None
    deadline: str | None = None
    reason: str
    confidence: float = Field(ge=0, le=1)
    evidence_refs: list[str] = Field(default_factory=list)


class TaskItem(BaseModel):
    title: str
    priority: Priority
    status: Literal["open", "in_progress", "blocked", "needs_confirmation"]
    owner_ref: str | None = None
    deadline: str | None = None
    reason: str
    confidence: float = Field(ge=0, le=1)
    evidence_refs: list[str] = Field(default_factory=list)


class EvidenceItem(BaseModel):
    text: str
    evidence_refs: list[str] = Field(default_factory=list)


class SummaryDraft(BaseModel):
    executive_summary: str
    tasks: list[TaskCandidate] = Field(default_factory=list)
    decisions: list[EvidenceItem] = Field(default_factory=list)
    open_questions: list[EvidenceItem] = Field(default_factory=list)


class SummaryResult(BaseModel):
    executive_summary: str
    tasks: list[TaskItem] = Field(default_factory=list)
    decisions: list[EvidenceItem] = Field(default_factory=list)
    open_questions: list[EvidenceItem] = Field(default_factory=list)
    analyzed_messages: int = 0


class ChatSection(BaseModel):
    heading: str
    content: str
    evidence_refs: list[str] = Field(default_factory=list)


class ChatDraft(BaseModel):
    status: ChatStatus
    overview: str
    sections: list[ChatSection] = Field(default_factory=list)


class ChatResult(BaseModel):
    status: ChatStatus
    overview: str
    sections: list[ChatSection] = Field(default_factory=list)
    analyzed_messages: int = 0


class TopicCandidate(BaseModel):
    topic: str
    current_refs: list[str] = Field(default_factory=list)
    baseline_refs: list[str] = Field(default_factory=list)
    sentiment: Sentiment = "neutral"
    toxic_refs: list[str] = Field(default_factory=list)
    explanation: str


class TrendDraft(BaseModel):
    topics: list[TopicCandidate] = Field(default_factory=list)
    toxicity_summary: str = "Không thấy tín hiệu toxic rõ ràng."


class TopicTrend(BaseModel):
    topic: str
    classification: Literal[
        "hot", "new", "rising", "stable", "declining", "insufficient_data"
    ]
    message_count: int
    participant_count: int
    growth_rate: float | None = None
    hot_score: float = Field(ge=0, le=1)
    novelty_score: float = Field(ge=0, le=1)
    sentiment: Sentiment
    confidence: float = Field(ge=0, le=1)
    explanation: str
    evidence_refs: list[str] = Field(default_factory=list)


class ToxicityResult(BaseModel):
    level: Literal["none", "low", "medium", "high"]
    ratio: float = Field(ge=0, le=1)
    summary: str
    evidence_refs: list[str] = Field(default_factory=list)


class TrendResult(BaseModel):
    overview: str
    data_quality: str
    topics: list[TopicTrend] = Field(default_factory=list)
    toxicity: ToxicityResult
    current_message_count: int = 0
    baseline_message_count: int = 0
