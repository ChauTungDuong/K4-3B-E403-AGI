from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from gemini import GeminiClient, load_prompt
from models import (
    SafeMessage,
    TopicCandidate,
    TopicTrend,
    ToxicityResult,
    TrendDraft,
    TrendResult,
)


@dataclass(slots=True)
class TrendMetrics:
    current_count: int
    baseline_count: int
    participant_count: int
    growth_rate: float | None
    hot_score: float
    novelty_score: float
    dominant_author_share: float


class TrendService:
    def __init__(
        self,
        llm: GeminiClient,
        min_messages: int = 3,
        min_participants: int = 2,
        hot_threshold: float = 0.70,
    ) -> None:
        self.llm = llm
        self.min_messages = min_messages
        self.min_participants = min_participants
        self.hot_threshold = hot_threshold
        self.prompt_template = load_prompt("trends.txt")

    async def analyze(
        self,
        current: list[SafeMessage],
        baseline: list[SafeMessage],
        current_hours: int,
        baseline_days: int,
        current_end: datetime | None = None,
    ) -> TrendResult:
        if not current:
            return _empty_result(len(baseline))

        prompt = (
            self.prompt_template.replace(
                "{{CURRENT}}",
                json.dumps([item.for_prompt() for item in current], ensure_ascii=False),
            )
            .replace(
                "{{BASELINE}}",
                json.dumps([item.for_prompt() for item in baseline], ensure_ascii=False),
            )
        )
        draft = await self.llm.generate(prompt, TrendDraft)
        current_by_ref = {item.ref: item for item in current}
        baseline_by_ref = {item.ref: item for item in baseline}
        topics: list[TopicTrend] = []
        toxic_refs: set[str] = set()

        for candidate in _merge_candidates(draft.topics):
            current_refs = _valid_refs(candidate.current_refs, current_by_ref)
            baseline_refs = _valid_refs(candidate.baseline_refs, baseline_by_ref)
            if not current_refs:
                continue
            toxic_refs.update(_valid_refs(candidate.toxic_refs, current_by_ref))
            metrics = calculate_metrics(
                current_refs,
                baseline_refs,
                current_by_ref,
                baseline_by_ref,
                current_hours,
                baseline_days,
                current_end,
            )
            classification = self._classify(metrics, bool(baseline))
            confidence = min(
                1.0,
                0.35 + 0.08 * metrics.current_count + 0.08 * metrics.participant_count,
            )
            if classification == "insufficient_data":
                confidence = min(confidence, 0.55)

            topics.append(
                TopicTrend(
                    topic=candidate.topic.strip(),
                    classification=classification,
                    message_count=metrics.current_count,
                    participant_count=metrics.participant_count,
                    growth_rate=metrics.growth_rate,
                    hot_score=metrics.hot_score,
                    novelty_score=metrics.novelty_score,
                    sentiment=candidate.sentiment,
                    confidence=confidence,
                    explanation=candidate.explanation.strip(),
                    evidence_refs=current_refs[:5],
                )
            )

        topics.sort(key=lambda item: (item.hot_score, item.message_count), reverse=True)
        toxicity = _toxicity_result(toxic_refs, current_by_ref, draft.toxicity_summary)
        quality = (
            f"Đã so sánh {len(current)} tin hiện tại với {len(baseline)} tin baseline."
            if baseline
            else "Chưa có baseline; không kết luận chủ đề mới hoặc đang tăng."
        )
        top_names = ", ".join(item.topic for item in topics[:3])
        overview = (
            f"Các chủ đề nổi bật: {top_names}." if top_names else "Chưa đủ dữ liệu tạo xu hướng."
        )
        return TrendResult(
            overview=overview,
            data_quality=quality,
            topics=topics[:8],
            toxicity=toxicity,
            current_message_count=len(current),
            baseline_message_count=len(baseline),
        )

    def _classify(self, metric: TrendMetrics, has_baseline: bool) -> str:
        if (
            metric.current_count < self.min_messages
            or metric.participant_count < self.min_participants
            or not has_baseline
        ):
            return "insufficient_data"
        if metric.baseline_count == 0 and metric.novelty_score >= 0.8:
            return "new"
        if metric.hot_score >= self.hot_threshold:
            return "hot"
        if metric.growth_rate is not None and metric.growth_rate > 0.25:
            return "rising"
        if metric.growth_rate is not None and metric.growth_rate < -0.25:
            return "declining"
        return "stable"


def calculate_metrics(
    current_refs: list[str],
    baseline_refs: list[str],
    current_by_ref: dict[str, SafeMessage],
    baseline_by_ref: dict[str, SafeMessage],
    current_hours: int,
    baseline_days: int,
    current_end: datetime | None = None,
) -> TrendMetrics:
    current = [current_by_ref[ref] for ref in current_refs]
    baseline = [baseline_by_ref[ref] for ref in baseline_refs]
    current_count = len(current)
    baseline_count = len(baseline)
    authors = Counter(item.author_ref for item in current)
    participant_count = len(authors)
    dominant_share = max(authors.values(), default=0) / max(current_count, 1)

    # Quy đổi baseline về cùng độ dài với current window trước khi so sánh.
    baseline_hours = max(baseline_days * 24, 1)
    expected = baseline_count * current_hours / baseline_hours
    growth_rate = None if baseline_count == 0 else (current_count - expected) / max(expected, 1)
    growth_score = _clamp((current_count - expected) / max(expected * 2, 1))

    window_end = current_end or datetime.now(UTC)
    midpoint = window_end - timedelta(hours=current_hours / 2)
    recent = sum(item.created_at >= midpoint for item in current)
    older = current_count - recent
    velocity_score = _clamp((recent - older) / max(current_count, 1))

    current_engagement = sum(item.reaction_count + item.reply_count for item in current) / max(
        current_count, 1
    )
    baseline_engagement = sum(
        item.reaction_count + item.reply_count for item in baseline
    ) / max(baseline_count, 1)
    engagement_score = _clamp(
        (current_engagement - baseline_engagement) / max(baseline_engagement + 1, 1)
    )
    participant_score = _clamp(participant_count / 5)

    hot_score = (
        0.40 * growth_score
        + 0.25 * velocity_score
        + 0.20 * engagement_score
        + 0.15 * participant_score
    )
    if dominant_share > 0.70 and current_count >= 3:
        hot_score *= 0.35  # Một người lặp nhiều không được tạo trend mạnh.

    novelty = 1.0 if baseline_count == 0 else _clamp(1 - expected / max(current_count, 1))
    return TrendMetrics(
        current_count=current_count,
        baseline_count=baseline_count,
        participant_count=participant_count,
        growth_rate=round(growth_rate, 3) if growth_rate is not None else None,
        hot_score=round(_clamp(hot_score), 3),
        novelty_score=round(novelty, 3),
        dominant_author_share=round(dominant_share, 3),
    )


def _valid_refs(refs: list[str], messages: dict[str, SafeMessage]) -> list[str]:
    return list(dict.fromkeys(ref for ref in refs if ref in messages))


def _merge_candidates(candidates: list[TopicCandidate]) -> list[TopicCandidate]:
    merged: dict[str, TopicCandidate] = {}
    for item in candidates:
        key = re.sub(r"\W+", " ", item.topic.casefold()).strip()
        if not key:
            continue
        if key not in merged:
            merged[key] = item.model_copy(deep=True)
            continue
        target = merged[key]
        target.current_refs = list(dict.fromkeys(target.current_refs + item.current_refs))
        target.baseline_refs = list(dict.fromkeys(target.baseline_refs + item.baseline_refs))
        target.toxic_refs = list(dict.fromkeys(target.toxic_refs + item.toxic_refs))
    return list(merged.values())


def _toxicity_result(
    toxic_refs: set[str],
    current_by_ref: dict[str, SafeMessage],
    summary: str,
) -> ToxicityResult:
    valid = sorted(toxic_refs & set(current_by_ref))
    ratio = len(valid) / max(len(current_by_ref), 1)
    level = "none"
    if ratio >= 0.15:
        level = "high"
    elif ratio >= 0.05:
        level = "medium"
    elif valid:
        level = "low"
    return ToxicityResult(
        level=level,
        ratio=round(ratio, 3),
        summary=summary.strip(),
        evidence_refs=valid[:5],
    )


def _empty_result(baseline_count: int) -> TrendResult:
    return TrendResult(
        overview="Không có tin nhắn trong cửa sổ hiện tại.",
        data_quality="Không đủ dữ liệu để phân tích xu hướng.",
        toxicity=ToxicityResult(
            level="none", ratio=0, summary="Không có dữ liệu để đánh giá."
        ),
        current_message_count=0,
        baseline_message_count=baseline_count,
    )


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
