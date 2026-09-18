from __future__ import annotations

from datetime import UTC, datetime

import discord

from models import SummaryResult, TrendResult
from privacy import ensure_safe_output


def _cut(text: str, limit: int) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


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

    if result.topics:
        topics = discord.Embed(title="🔥 Chủ đề", color=discord.Color.gold())
        for item in result.topics[:8]:
            growth = "N/A" if item.growth_rate is None else f"{item.growth_rate:+.0%}"
            value = (
                f"{item.explanation}\n"
                f"Phân loại: **{item.classification}** · Hot: **{item.hot_score:.0%}** · "
                f"Mới: **{item.novelty_score:.0%}**\n"
                f"Tin: **{item.message_count}** · Người tham gia: **{item.participant_count}** · "
                f"Tăng trưởng: **{growth}** · Cảm xúc: **{item.sentiment}**\n"
                f"Tin cậy: **{item.confidence:.0%}** · Nguồn: {', '.join(item.evidence_refs)}"
            )
            topics.add_field(
                name=_cut(item.topic, 160), value=_cut(value, 520), inline=False
            )
        embeds.append(topics)

    if result.toxicity.level != "none":
        toxic = discord.Embed(title="⚠️ Tín hiệu toxic", color=discord.Color.red())
        toxic.add_field(
            name=f"Mức {result.toxicity.level} · {result.toxicity.ratio:.0%} tin được gắn cờ",
            value=_cut(
                f"{result.toxicity.summary}\nNguồn: "
                f"{', '.join(result.toxicity.evidence_refs)}",
                1024,
            ),
            inline=False,
        )
        embeds.append(toxic)
    return embeds


async def send_embeds(
    channel: discord.TextChannel,
    embeds: list[discord.Embed],
) -> None:
    for embed in embeds:
        await channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
