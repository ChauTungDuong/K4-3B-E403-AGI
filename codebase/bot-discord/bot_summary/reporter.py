from __future__ import annotations

from typing import TypeAlias

import discord

from models import ChatResult, SummaryResult, TaskItem, TopicTrend, TrendResult
from privacy import ensure_safe_output


# guild_id, channel_id, message_id. Bảng này chỉ tồn tại trong RAM và
# không được gửi sang Gemini hay lưu vào snapshot.
SourceMap: TypeAlias = dict[str, tuple[int, int, int]]


def _cut(text: str, limit: int) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _one_line(text: str, limit: int) -> str:
    return _cut(" ".join(text.split()), limit)


def _action(text: str, max_words: int = 12) -> str:
    words = text.split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]).rstrip(".,;:") + "…"


def _window_text(hours: int) -> str:
    return f"{max(1, hours)} giờ qua"


def _source_suffix(
    refs: list[str],
    sources: SourceMap | None,
    link_label: str,
) -> str:
    if not refs:
        return ""
    ref = refs[0]
    source = sources.get(ref) if sources else None
    if source is None:
        return f" • Nguồn: `{ref}`"
    guild_id, channel_id, message_id = source
    url = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
    return f" • <#{channel_id}> • [{link_label}]({url})"


def _multi_source_suffix(
    items_refs: list[list[str]],
    sources: SourceMap | None,
) -> str:
    if not items_refs:
        return ""
    if len(items_refs) == 1:
        return _source_suffix(items_refs[0], sources, "Xem tin gốc ↗")

    links: list[str] = []
    channel_ids: list[int] = []
    fallback_refs: list[str] = []

    for index, refs in enumerate(items_refs, 1):
        if not refs:
            continue
        ref = refs[0]
        source = None
        if sources:
            for r in refs:
                if r in sources:
                    ref = r
                    source = sources[r]
                    break

        if source is not None:
            guild_id, channel_id, message_id = source
            if channel_id not in channel_ids:
                channel_ids.append(channel_id)
            url = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
            links.append(f"[Tin {index} ↗]({url})")
        elif ref:
            fallback_refs.append(f"`{ref}`")

    if links:
        channel_prefix = (
            f" • <#{channel_ids[0]}>" if len(channel_ids) == 1 else ""
        )
        return f"{channel_prefix} • " + " • ".join(links)
    if fallback_refs:
        return " • Nguồn: " + ", ".join(dict.fromkeys(fallback_refs))
    return ""


def _evidence_text(refs: list[str], sources: SourceMap | None) -> str:
    values: list[str] = []
    for index, ref in enumerate(refs[:5], 1):
        source = sources.get(ref) if sources else None
        if source is None:
            values.append(f"`{ref}`")
            continue
        guild_id, channel_id, message_id = source
        url = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
        values.append(f"[Nguồn {index} ↗]({url})")
    return ", ".join(values) or "Không có"


def _summary_task_line(
    item: TaskItem,
    sources: SourceMap | None,
) -> str:
    confirmation = " · ⚠️ Cần xác nhận" if item.status == "needs_confirmation" else ""
    target_tag = ""
    if item.owner_ref == "USER_YOU":
        target_tag = " [Dành cho bạn]"
    elif item.owner_ref == "Learner":
        target_tag = " [Cả lớp]"

    if item.priority == "P0":
        prefix = f"🚨 **BLOCKER KHẨN CẤP{target_tag}{confirmation}:**"
    elif item.priority == "P1":
        qualifier = confirmation
        if not qualifier and item.deadline:
            deadline = _one_line(item.deadline, 40)
            if deadline.casefold().startswith(("trước ", "còn ")):
                qualifier = f" · {deadline[0].upper()}{deadline[1:]}"
            else:
                qualifier = f" · Trước {deadline}"
        prefix = f"🔴 **CẦN LÀM NGAY{target_tag}{qualifier}:**"
    elif item.priority == "P2":
        prefix = f"🟡 **CẦN BIẾT{target_tag}{confirmation}:**"
    else:
        prefix = f"🟢 **ĐỌC THÊM{target_tag}{confirmation}:**"
    return (
        f"{prefix} {_action(item.title)}"
        f"{_source_suffix(item.evidence_refs, sources, 'Xem tin gốc ↗')}"
    )


def _summary_more_line(
    result: SummaryResult,
    displayed_tasks: set[int],
    used_decision: bool,
    sources: SourceMap | None,
) -> str:
    items: list[tuple[str, list[str]]] = []
    has_undisplayed_urgent = False

    for index, item in enumerate(result.tasks):
        if index not in displayed_tasks:
            if item.priority in {"P0", "P1"}:
                has_undisplayed_urgent = True
                items.append((f"⚠️ {_action(item.title, 8)}", item.evidence_refs))
            else:
                items.append((_action(item.title, 8), item.evidence_refs))
    for index, item in enumerate(result.decisions):
        if index == 0 and used_decision:
            continue
        items.append((_one_line(item.text, 100), item.evidence_refs))
    for item in result.open_questions:
        items.append((f"Cần làm rõ: {_one_line(item.text, 90)}", item.evidence_refs))

    if items:
        display_items = items[:3]
        if len(display_items) == 1:
            text = display_items[0][0]
        else:
            text = "; ".join(
                f"{i}. {part}" for i, (part, _) in enumerate(display_items, 1)
            )
        if len(items) > 3:
            text += f"; và {len(items) - 3} nội dung khác"
        suffix = _multi_source_suffix(
            [item_refs for _, item_refs in display_items], sources
        )
    else:
        text = _one_line(result.executive_summary, 220)
        if not text:
            text = "Không có thảo luận ngoài lề quan trọng."
        suffix = ""

    prefix = "🔴 **CẦN LÀM NGAY (KHÁC):**" if has_undisplayed_urgent else "🟢 **ĐỌC THÊM:**"

    return f"{prefix} {_cut(text, 260)}{suffix}"


def summary_embeds(
    result: SummaryResult,
    title: str,
    *,
    hours: int = 24,
    sources: SourceMap | None = None,
) -> list[discord.Embed]:
    """Dựng một digest tối đa 8 dòng theo khung hiển thị chuẩn."""
    ensure_safe_output(result.model_dump_json())
    attention_count = len(result.tasks) + len(result.decisions) + len(
        result.open_questions
    )
    suffix = f" · {attention_count} việc cần chú ý" if attention_count else ""
    embed = discord.Embed(
        title=_cut(
            f"📋 Tóm tắt thông báo — {title} - {_window_text(hours)}{suffix}",
            256,
        ),
        color=discord.Color.blurple(),
    )

    if not attention_count:
        summary = _one_line(result.executive_summary, 500)
        lines = [
            "Chi tiết:",
            f"🟢 **Không tìm thấy việc cần chú ý mới trong {_window_text(hours)}.**",
        ]
        if summary:
            lines.append(summary)
        lines.extend(
            [
                "",
                "[🔍 Quét 48h qua] • [📢 Kiểm tra kênh thông báo]",
            ]
        )
        embed.description = "\n".join(lines)
        return [embed]

    detail_lines: list[str] = []
    displayed_tasks: set[int] = set()
    used_decision = False

    urgent_indexes = [
        index
        for index, item in enumerate(result.tasks)
        if item.priority in {"P0", "P1"}
    ]
    known_indexes = [
        index for index, item in enumerate(result.tasks) if item.priority == "P2"
    ]
    max_urgent = 3 if len(urgent_indexes) >= 3 else 2
    for index in urgent_indexes[:max_urgent]:
        detail_lines.append(_summary_task_line(result.tasks[index], sources))
        displayed_tasks.add(index)

    if len(detail_lines) < 3 and known_indexes:
        index = known_indexes[0]
        detail_lines.append(_summary_task_line(result.tasks[index], sources))
        displayed_tasks.add(index)
    elif len(detail_lines) < 3 and result.decisions:
        decision = result.decisions[0]
        detail_lines.append(
            f"🟡 **CẦN BIẾT:** {_one_line(decision.text, 220)}"
            f"{_source_suffix(decision.evidence_refs, sources, 'Xem tin gốc ↗')}"
        )
        used_decision = True

    # Dòng ĐỌC THÊM luôn là dòng chi tiết cuối, gộp phần còn lại.
    detail_lines.append(
        _summary_more_line(result, displayed_tasks, used_decision, sources)
    )
    detail_lines = detail_lines[:4]
    header = (
        f"📌 {_one_line(result.executive_summary, 220)}"
        if result.executive_summary.strip()
        else "Chi tiết:"
    )
    lines = [header, *detail_lines]
    lines.extend(
        [
            "",
            "👍 👎 *Kết quả này có hữu ích?* • [🔄 Quét 12h] • [⚙️ Bộ lọc kênh]",
        ]
    )
    embed.description = "\n".join(lines)
    return [embed]


def chat_embeds(
    result: ChatResult,
    channel_count: int,
    *,
    hours: int = 24,
    sources: SourceMap | None = None,
) -> list[discord.Embed]:
    """Dựng câu trả lời tùy biến; link nguồn chỉ được nối sau output guard."""
    ensure_safe_output(result.model_dump_json())
    embed = discord.Embed(
        title=_cut(
            f"💬 Trả lời theo yêu cầu · {channel_count} kênh · "
            f"{_window_text(hours)}",
            256,
        ),
        description=_cut(result.overview, 1200),
        color=(
            discord.Color.blurple()
            if result.status == "answered"
            else discord.Color.orange()
            if result.status == "not_found"
            else discord.Color.red()
        ),
    )
    for section in result.sections[:5]:
        sources_text = _evidence_text(section.evidence_refs, sources)
        embed.add_field(
            name=_cut(section.heading, 256),
            value=_cut(f"{section.content}\n🔎 Nguồn: {sources_text}", 1024),
            inline=False,
        )
    embed.set_footer(text=f"Đã kiểm tra {result.analyzed_messages} tin nhắn")
    return [embed]


def _classification_text(value: str) -> str:
    return {
        "hot": "Đang được quan tâm mạnh",
        "new": "Chủ đề mới xuất hiện",
        "rising": "Mức độ thảo luận đang tăng",
        "stable": "Mức độ thảo luận ổn định",
        "declining": "Mức độ thảo luận đang giảm",
        "insufficient_data": "Chưa đủ dữ liệu để xác nhận xu hướng",
    }.get(value, "Chưa xác định")


def _score_text(score: float, *, novelty: bool = False) -> str:
    if novelty:
        label = "Rất mới" if score >= 0.8 else "Khá mới" if score >= 0.5 else "Đã quen thuộc"
    else:
        label = (
            "Rất cao"
            if score >= 0.8
            else "Cao"
            if score >= 0.6
            else "Trung bình"
            if score >= 0.4
            else "Thấp"
        )
    return f"**{score:.0%}** — {label}"


def _confidence_text(score: float) -> str:
    label = "Cao" if score >= 0.75 else "Trung bình" if score >= 0.5 else "Thấp"
    return f"**{score:.0%}** — {label}"


def _growth_text(growth: float | None) -> str:
    if growth is None:
        return "**Chưa có dữ liệu lịch sử để so sánh**"
    if growth > 0.01:
        return f"**Tăng {growth:.0%}** so với mức thông thường"
    if growth < -0.01:
        return f"**Giảm {abs(growth):.0%}** so với mức thông thường"
    return "**Gần như không đổi**"


def _sentiment_text(value: str) -> str:
    return {
        "positive": "Tích cực",
        "neutral": "Trung tính",
        "negative": "Tiêu cực",
        "mixed": "Đan xen tích cực và tiêu cực",
    }.get(value, "Chưa xác định")


def _topic_color(classification: str) -> discord.Color:
    return {
        "hot": discord.Color.orange(),
        "new": discord.Color.teal(),
        "rising": discord.Color.green(),
        "stable": discord.Color.blue(),
        "declining": discord.Color.red(),
        "insufficient_data": discord.Color.light_grey(),
    }.get(classification, discord.Color.light_grey())


def _trend_line(
    item: TopicTrend,
    index: int,
    sources: SourceMap | None,
) -> str:
    if index == 0:
        heading = f"CHỦ ĐỀ NÓNG NHẤT · {item.message_count} lượt trao đổi"
    else:
        heading = "ĐANG THẢO LUẬN NHIỀU"
    explanation = _one_line(item.explanation, 180)
    body = _one_line(item.topic, 100)
    if explanation and explanation.casefold() != body.casefold():
        body = f"{body} — {explanation}"
    return (
        f"🔥 **{heading}:** {_cut(body, 290)}"
        f"{_source_suffix(item.evidence_refs, sources, 'Xem thảo luận ↗')}"
    )


def _trend_detail_embeds(
    result: TrendResult,
    sources: SourceMap | None,
) -> list[discord.Embed]:
    embeds: list[discord.Embed] = []
    for item in result.topics[:8]:
        topic = discord.Embed(
            title=f"📌 {_cut(item.topic, 240)}",
            description=_cut(item.explanation, 1600),
            color=_topic_color(item.classification),
        )
        metrics = [
            f"🧭 **Kết luận:** {_classification_text(item.classification)}",
            (
                f"💬 **Quy mô thảo luận:** **{item.message_count} tin nhắn** "
                f"từ **{item.participant_count} người tham gia**"
            ),
            f"🔥 **Mức độ nổi bật:** {_score_text(item.hot_score)}",
            f"🆕 **Tín hiệu mới:** {_score_text(item.novelty_score, novelty=True)}",
            f"📈 **So với lịch sử:** {_growth_text(item.growth_rate)}",
            f"💭 **Sắc thái chung:** **{_sentiment_text(item.sentiment)}**",
            f"🎯 **Độ tin cậy:** {_confidence_text(item.confidence)}",
        ]
        if item.classification == "insufficient_data":
            metrics.append(
                "ℹ️ _Các điểm trên chỉ là tín hiệu ban đầu vì chưa đủ tin nhắn, "
                "người tham gia hoặc dữ liệu lịch sử._"
            )
        metrics.append(f"🔎 **Bằng chứng:** {_evidence_text(item.evidence_refs, sources)}")
        topic.add_field(
            name="📊 Số liệu nổi bật",
            value=_cut("\n".join(metrics), 1024),
            inline=False,
        )
        embeds.append(topic)

    if result.toxicity.level != "none":
        toxic = discord.Embed(title="⚠️ Tín hiệu toxic", color=discord.Color.red())
        toxic_level = {
            "low": "Thấp",
            "medium": "Trung bình",
            "high": "Cao",
        }.get(result.toxicity.level, "Không có")
        toxic.add_field(
            name=f"Mức {toxic_level} · {result.toxicity.ratio:.0%} tin được gắn cờ",
            value=_cut(
                f"{result.toxicity.summary}\nNguồn: "
                f"{_evidence_text(result.toxicity.evidence_refs, sources)}",
                1024,
            ),
            inline=False,
        )
        embeds.append(toxic)
    return embeds


def trend_embeds(
    result: TrendResult,
    title: str,
    *,
    hours: int = 24,
    sources: SourceMap | None = None,
) -> list[discord.Embed]:
    """Dựng bản tin trend tối đa 10 dòng và giữ chi tiết sau nút bấm."""
    ensure_safe_output(result.model_dump_json())
    topic_count = len(result.topics)
    topic_suffix = f" · {topic_count} chủ đề nổi bật" if topic_count else ""
    overview = discord.Embed(
        title=_cut(
            f"📊 Phân tích xu hướng thảo luận — {title} - "
            f"{_window_text(hours)}{topic_suffix}",
            256,
        ),
        color=discord.Color.orange(),
    )

    if not result.topics:
        overview.description = "\n".join(
            [
                "Chi tiết:",
                f"🟢 **Chưa phát hiện xu hướng nổi bật trong {_window_text(hours)}.**",
                f"• Đã phân tích {result.current_message_count} tin nhắn trong cửa sổ hiện tại.",
                f"• {_one_line(result.data_quality, 500)}",
                "",
                "💡 *Gợi ý:* Tiếp tục theo dõi kênh và quét lại khi có thêm trao đổi.",
                "",
                "[🔄 Quét lại] • [📋 Xem Tóm tắt thông báo]",
            ]
        )
        return [overview]

    lines = ["Chi tiết:"]
    lines.extend(
        _trend_line(item, index, sources)
        for index, item in enumerate(result.topics[:3])
    )
    lines.append(
        f"💡 **LỐI TẮT XỬ LÝ:** Ưu tiên kiểm tra “"
        f"{_one_line(result.topics[0].topic, 100)}”, sau đó theo dõi các chủ đề còn lại."
    )
    lines.extend(
        [
            "",
            "👍 👎 *Bản tin này có hữu ích?* • [📌 Lọc theo kênh] • [🙋 Gửi câu hỏi cho TA]",
        ]
    )
    overview.description = "\n".join(lines)
    return [overview, *_trend_detail_embeds(result, sources)]


class TrendDetailsView(discord.ui.View):
    """Nút mở chi tiết riêng cho người bấm, tránh làm đầy kênh báo cáo."""

    def __init__(self, detail_embeds: list[discord.Embed]) -> None:
        super().__init__(timeout=3600)
        self.detail_embeds = detail_embeds
        self.message: discord.Message | None = None

    async def on_timeout(self) -> None:
        # Hiển thị trạng thái hết hạn thay vì để lại nút có vẻ vẫn bấm được.
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        if self.message is not None:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass

    @discord.ui.button(
        label="Xem chi tiết",
        emoji="📊",
        style=discord.ButtonStyle.primary,
    )
    async def show_details(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button["TrendDetailsView"],
    ) -> None:
        del button
        await interaction.response.send_message(
            embeds=self.detail_embeds,
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none(),
        )


async def send_trend_report(
    channel: discord.TextChannel,
    result: TrendResult,
    title: str,
    *,
    hours: int = 24,
    sources: SourceMap | None = None,
) -> None:
    """Gửi tổng quan công khai; chi tiết chỉ hiện sau khi bấm nút."""
    embeds = trend_embeds(result, title, hours=hours, sources=sources)
    overview, details = embeds[0], embeds[1:]
    view = TrendDetailsView(details) if details else None
    message = await channel.send(
        embed=overview,
        view=view,
        allowed_mentions=discord.AllowedMentions.none(),
    )
    if view is not None:
        view.message = message


async def send_embeds(
    channel: discord.TextChannel,
    embeds: list[discord.Embed],
) -> None:
    for embed in embeds:
        await channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
