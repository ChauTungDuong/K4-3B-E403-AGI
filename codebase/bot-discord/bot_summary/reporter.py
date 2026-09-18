from __future__ import annotations

from datetime import UTC, datetime

import discord

from models import SummaryResult, TrendResult
from privacy import ensure_safe_output


def _cut(text: str, limit: int) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


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
        label = "Rất cao" if score >= 0.8 else "Cao" if score >= 0.6 else "Trung bình" if score >= 0.4 else "Thấp"
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


def summary_embeds(result: SummaryResult, title: str) -> list[discord.Embed]:
    ensure_safe_output(result.model_dump_json())
    overview = discord.Embed(
        title=f"📝 Tóm tắt · {title}",
        description=_cut(result.executive_summary, 3500),
        color=discord.Color.blurple(),
        timestamp=datetime.now(UTC),
    )
    overview.set_footer(text=f"Đã phân tích {result.analyzed_messages} tin nhắn")
    embeds = [overview]

    if result.tasks:
        # Chia nhóm để không vượt giới hạn 6000 ký tự của một Discord embed.
        for start in range(0, min(len(result.tasks), 16), 8):
            tasks = discord.Embed(
                title="✅ Danh sách công việc", color=discord.Color.green()
            )
            for item in result.tasks[start : start + 8]:
                details = [item.reason, f"Trạng thái: **{item.status}**"]
                if item.owner_ref:
                    details.append(f"Owner: **{item.owner_ref}**")
                if item.deadline:
                    details.append(f"Deadline: **{item.deadline}**")
                details.append(
                    f"Tin cậy: **{item.confidence:.0%}** · "
                    f"Nguồn: {', '.join(item.evidence_refs)}"
                )
                tasks.add_field(
                    name=_cut(f"[{item.priority}] {item.title}", 180),
                    value=_cut("\n".join(details), 480),
                    inline=False,
                )
            embeds.append(tasks)

    if result.decisions or result.open_questions:
        context = discord.Embed(title="📌 Thông tin liên quan", color=discord.Color.teal())
        if result.decisions:
            value = "\n".join(
                f"• {item.text} ({', '.join(item.evidence_refs)})"
                for item in result.decisions[:5]
            )
            context.add_field(name="Quyết định", value=_cut(value, 1024), inline=False)
        if result.open_questions:
            value = "\n".join(
                f"• {item.text} ({', '.join(item.evidence_refs)})"
                for item in result.open_questions[:5]
            )
            context.add_field(name="Cần làm rõ", value=_cut(value, 1024), inline=False)
        embeds.append(context)
    return embeds


def trend_embeds(result: TrendResult, title: str) -> list[discord.Embed]:
    ensure_safe_output(result.model_dump_json())
    overview = discord.Embed(
        title=f"📈 Xu hướng · {title}",
        description=_cut(f"{result.overview}\n\n_{result.data_quality}_", 3500),
        color=discord.Color.orange(),
        timestamp=datetime.now(UTC),
    )
    overview.set_footer(
        text=(
            f"Hiện tại: {result.current_message_count} tin · "
            f"Baseline: {result.baseline_message_count} tin"
        )
    )
    embeds = [overview]

    for item in result.topics[:8]:
        # Mỗi trend có 2 phần rõ ràng: nội dung và khối số liệu nổi bật.
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
        metrics.append(f"🔎 **Bằng chứng:** {', '.join(item.evidence_refs)}")
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
                f"{', '.join(result.toxicity.evidence_refs)}",
                1024,
            ),
            inline=False,
        )
        embeds.append(toxic)
    return embeds


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
) -> None:
    """Gửi tổng quan công khai; chi tiết chỉ hiện sau khi bấm nút."""
    embeds = trend_embeds(result, title)
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
