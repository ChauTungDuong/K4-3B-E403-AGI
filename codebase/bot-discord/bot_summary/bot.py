from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands, tasks

from chat import ChatService
from collector import DiscordCollector, PrioritizedCollection, SkippedChannel
from config import settings
from database import Database
from gemini import GeminiClient
from models import Message, SafeMessage
from privacy import PrivacySanitizer
from reporter import chat_embeds, send_embeds, send_trend_report, summary_embeds
from summary import SummaryService
from time_window import TimeWindow, resolve_time_window
from trends import TrendService


logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("discord-gemini-bot")


class SummaryBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)

        llm = GeminiClient(settings.gemini_api_key, settings.gemini_model)
        self.db = Database(settings.database_path)
        self.collector = DiscordCollector(
            settings.max_messages_per_channel,
            settings.max_total_messages,
            settings.max_input_characters,
            settings.include_bot_messages,
        )
        self.summary_service = SummaryService(llm, settings.min_task_confidence)
        self.chat_service = ChatService(llm)
        self.trend_service = TrendService(
            llm,
            settings.min_topic_messages,
            settings.min_topic_participants,
            settings.hot_score_threshold,
        )
        self.guild_locks: dict[int, asyncio.Lock] = {}

    async def setup_hook(self) -> None:
        await self.db.connect()
        if settings.dev_guild_id:
            guild = discord.Object(id=settings.dev_guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
        else:
            synced = await self.tree.sync()
        log.info("Đã đồng bộ %s slash command", len(synced))
        self.scheduler.start()

    async def close(self) -> None:
        self.scheduler.cancel()
        await self.db.close()
        await super().close()

    async def on_ready(self) -> None:
        log.info("Bot đã sẵn sàng: %s", self.user)

    def _lock(self, guild_id: int) -> asyncio.Lock:
        return self.guild_locks.setdefault(guild_id, asyncio.Lock())

    async def run_summary(
        self,
        guild: discord.Guild,
        output: discord.TextChannel,
        channels: list[discord.TextChannel],
        start: datetime,
        end: datetime,
        window_label: str | None = None,
    ) -> PrioritizedCollection:
        async with self._lock(guild.id):
            collection = await self.collector.collect_channels_atomic(
                channels, start, end
            )
            raw = collection.messages
            if not raw:
                return collection
            safe = PrivacySanitizer().sanitize(raw)
            sources = _report_sources(guild.id, raw, safe)
            safe_by_channel: dict[int, list[SafeMessage]] = {
                item.channel_id: [] for item in collection.included
            }
            ordered_raw = sorted(raw, key=lambda item: item.created_at)
            for raw_item, safe_item in zip(ordered_raw, safe, strict=True):
                safe_by_channel[raw_item.channel_id].append(safe_item)

            hours = max(1, round((end - start).total_seconds() / 3600))
            embeds: list[discord.Embed] = []
            for priority, item in enumerate(collection.included, 1):
                channel_messages = safe_by_channel[item.channel_id]
                if not channel_messages:
                    continue
                result = await self.summary_service.analyze(channel_messages)
                embeds.extend(
                    summary_embeds(
                        result,
                        f"Ưu tiên {priority} · #{item.channel_name}",
                        hours=hours,
                        window_label=window_label,
                        sources=sources,
                    )
                )
            await send_embeds(output, embeds)
            return collection

    async def run_chat(
        self,
        guild: discord.Guild,
        channels: list[discord.TextChannel],
        start: datetime,
        end: datetime,
        user_input: str,
        window_label: str | None = None,
    ) -> tuple[PrioritizedCollection, list[discord.Embed]]:
        async with self._lock(guild.id):
            collection = await self.collector.collect_channels_atomic(
                channels, start, end
            )
            raw = collection.messages
            if not raw:
                return collection, []

            safe = PrivacySanitizer().sanitize(raw)
            sources = _report_sources(guild.id, raw, safe)
            result = await self.chat_service.answer(safe, user_input)
            hours = max(1, round((end - start).total_seconds() / 3600))
            embeds = chat_embeds(
                result,
                len(collection.included),
                hours=hours,
                window_label=window_label,
                sources=sources,
            )
            return collection, embeds

    async def run_trends(
        self,
        guild: discord.Guild,
        output: discord.TextChannel,
        channel: discord.TextChannel,
        current_start: datetime,
        current_end: datetime,
        baseline_days: int,
        window_label: str | None = None,
    ) -> int:
        async with self._lock(guild.id):
            baseline_start = current_start - timedelta(days=baseline_days)
            current_raw = await self.collector.collect_channel(
                channel, current_start, current_end
            )
            if not current_raw:
                return 0
            baseline_raw = await self.collector.collect_channel(
                channel, baseline_start, current_start
            )
            baseline_raw, current_raw = _fit_trend_input(baseline_raw, current_raw)

            # Sanitize cùng lúc để alias và MSG ref nhất quán giữa hai cửa sổ.
            safe = PrivacySanitizer().sanitize(baseline_raw + current_raw)
            sources = _report_sources(
                guild.id, baseline_raw + current_raw, safe
            )
            baseline_safe = [item for item in safe if item.created_at < current_start]
            current_safe = [item for item in safe if item.created_at >= current_start]
            current_hours = max(
                1, round((current_end - current_start).total_seconds() / 3600)
            )
            result = await self.trend_service.analyze(
                current_safe,
                baseline_safe,
                current_hours,
                baseline_days,
                current_end,
            )
            await self.db.save_trend_snapshot(
                guild.id, channel.id, current_hours, baseline_days, result
            )
            await send_trend_report(
                output,
                result,
                f"#{channel.name}",
                hours=current_hours,
                window_label=window_label,
                sources=sources,
            )
            return len(current_safe)

    @tasks.loop(minutes=1)
    async def scheduler(self) -> None:
        for config in await self.db.due_guilds():
            guild = self.get_guild(config["guild_id"])
            if guild is None:
                continue
            output = guild.get_channel(config["output_channel_id"])
            if not isinstance(output, discord.TextChannel):
                continue
            channels = _text_channels(guild, await self.db.get_sources(guild.id))
            if not channels:
                continue

            now = datetime.now(UTC)
            last_run = datetime.fromisoformat(config["last_run_at"])
            if last_run.tzinfo is None:
                last_run = last_run.replace(tzinfo=UTC)
            try:
                summary_run = await self.run_summary(
                    guild, output, channels, last_run, now
                )
                if summary_run.skipped:
                    await output.send(
                        _skipped_channels_notice(summary_run.skipped),
                        allowed_mentions=discord.AllowedMentions.none(),
                    )
                for channel in channels:
                    await self.run_trends(
                        guild,
                        output,
                        channel,
                        now - timedelta(hours=int(config["interval_hours"])),
                        now,
                        settings.trend_baseline_days,
                    )
            except Exception as exc:
                # Không log nội dung prompt/message để tránh rò rỉ PII.
                log.error(
                    "Báo cáo định kỳ lỗi guild=%s type=%s",
                    guild.id,
                    type(exc).__name__,
                )
            finally:
                # Tránh gửi lặp báo cáo mỗi phút khi một phần pipeline gặp lỗi.
                await self.db.mark_run(guild.id, now)

    @scheduler.before_loop
    async def before_scheduler(self) -> None:
        await self.wait_until_ready()


bot = SummaryBot()


def _report_sources(
    guild_id: int,
    raw: list[Message],
    safe: list[SafeMessage],
) -> dict[str, tuple[int, int, int]]:
    """Nối alias với jump link sau khi AI xử lý; không làm lộ ID cho model."""
    ordered = sorted(raw, key=lambda item: item.created_at)
    return {
        safe_item.ref: (guild_id, raw_item.channel_id, raw_item.message_id)
        for raw_item, safe_item in zip(ordered, safe, strict=True)
    }


def _fit_trend_input(
    baseline: list[Message], current: list[Message]
) -> tuple[list[Message], list[Message]]:
    """Ưu tiên current, sau đó dùng phần ngân sách còn lại cho baseline mới nhất."""
    current = current[-settings.max_total_messages :]
    remaining = max(settings.max_total_messages - len(current), 0)
    baseline = baseline[-remaining:] if remaining else []
    while sum(len(item.content) for item in baseline + current) > settings.max_input_characters:
        if baseline:
            baseline.pop(0)
        elif current:
            current.pop(0)
        else:
            break
    return baseline, current


def _text_channels(
    guild: discord.Guild, channel_ids: list[int]
) -> list[discord.TextChannel]:
    return [
        channel
        for channel_id in channel_ids
        if isinstance((channel := guild.get_channel(channel_id)), discord.TextChannel)
    ]


def _unique_channels(
    channels: list[discord.TextChannel | None],
) -> list[discord.TextChannel]:
    """Bỏ lựa chọn trống/trùng nhưng giữ nguyên thứ tự ưu tiên người dùng."""
    result: list[discord.TextChannel] = []
    seen: set[int] = set()
    for channel in channels:
        if channel is not None and channel.id not in seen:
            result.append(channel)
            seen.add(channel.id)
    return result


def _clean_group_name(name: str) -> str:
    clean_name = " ".join(name.split())
    if not clean_name:
        raise app_commands.CheckFailure("Tên nhóm không được để trống")
    if len(clean_name) > 50:
        raise app_commands.CheckFailure("Tên nhóm không được dài quá 50 ký tự")
    if any(not (character.isalnum() or character in " _-") for character in clean_name):
        raise app_commands.CheckFailure(
            "Tên nhóm chỉ được chứa chữ, số, khoảng trắng, dấu gạch ngang hoặc gạch dưới"
        )
    return clean_name


def _command_time_window(
    start_hours_ago: int,
    end_hours_ago: int,
    start_at: str | None = None,
    end_at: str | None = None,
) -> TimeWindow:
    try:
        return resolve_time_window(
            start_hours_ago,
            end_hours_ago,
            start_at=start_at,
            end_at=end_at,
        )
    except ValueError as exc:
        raise app_commands.CheckFailure(str(exc)) from exc


async def _requested_channels(
    interaction: discord.Interaction,
    group: str | None,
    selected: list[discord.TextChannel | None],
    *,
    use_all_sources_by_default: bool = False,
) -> tuple[discord.Guild, list[discord.TextChannel]]:
    """Giải quyết lựa chọn nhóm/kênh và áp dụng cùng một kiểm tra quyền."""
    guild = _guild(interaction)
    channels = _unique_channels(selected)
    if group and channels:
        raise app_commands.CheckFailure(
            "Chỉ chọn `group` hoặc các tham số `channel`, không dùng đồng thời."
        )

    if group:
        clean_name = _clean_group_name(group)
        channel_ids = await bot.db.get_channel_group(guild.id, clean_name)
        if channel_ids is None:
            raise app_commands.CheckFailure(
                f"Không tìm thấy nhóm **{clean_name}**. Dùng /groups để xem danh sách."
            )
        channels = _text_channels(guild, channel_ids)
        if len(channels) != len(channel_ids):
            raise app_commands.CheckFailure(
                f"Nhóm **{clean_name}** có kênh không còn tồn tại. "
                "Quản trị viên hãy cập nhật lại bằng /group-set."
            )
    elif not channels and use_all_sources_by_default:
        channels = _text_channels(guild, await bot.db.get_sources(guild.id))

    if not channels:
        raise app_commands.CheckFailure(
            "Cần chọn một nhóm hoặc ít nhất một kênh nguồn."
        )
    for channel in channels:
        await _check_source(interaction, channel)
    return guild, channels


def _skipped_channels_notice(skipped: list[SkippedChannel]) -> str:
    channels = ", ".join(f"<#{item.channel_id}>" for item in skipped)
    first_reason = skipped[0].reason
    if first_reason == "context_budget":
        reason = "context còn lại không đủ chứa trọn kênh ưu tiên kế tiếp"
    elif first_reason in {"channel_message_limit", "channel_character_limit"}:
        reason = "kênh ưu tiên kế tiếp vượt giới hạn an toàn đã cấu hình"
    else:
        reason = "một kênh ưu tiên cao hơn không thể được lấy đầy đủ"
    return (
        f"⚠️ Đã bỏ nguyên kênh {channels}: {reason}. "
        "Bot không dùng dữ liệu cắt dở; các kênh đứng sau cũng được bỏ để giữ "
        "đúng thứ tự ưu tiên."
    )


def _guild(interaction: discord.Interaction) -> discord.Guild:
    if interaction.guild is None:
        raise app_commands.CheckFailure("Lệnh này chỉ dùng trong server")
    return interaction.guild


async def _output(guild: discord.Guild) -> tuple[aiosqlite.Row, discord.TextChannel]:
    config = await bot.db.get_config(guild.id)
    if config is None or config["output_channel_id"] is None:
        raise RuntimeError("Chưa cấu hình kênh báo cáo bằng /setup-output")
    channel = guild.get_channel(config["output_channel_id"])
    if not isinstance(channel, discord.TextChannel):
        raise RuntimeError("Kênh báo cáo không tồn tại hoặc không phải text channel")
    if guild.me is not None:
        permissions = channel.permissions_for(guild.me)
        missing: list[str] = []
        if not permissions.view_channel:
            missing.append("View Channel")
        if not permissions.send_messages:
            missing.append("Send Messages")
        if not permissions.embed_links:
            missing.append("Embed Links")
        if missing:
            raise app_commands.CheckFailure(
                f"Bot thiếu quyền tại {channel.mention}: **{', '.join(missing)}**."
            )
    return config, channel


async def _check_source(
    interaction: discord.Interaction, channel: discord.TextChannel
) -> discord.Guild:
    guild = _guild(interaction)
    if channel.id not in await bot.db.get_sources(guild.id):
        raise app_commands.CheckFailure("Kênh này chưa được quản trị viên cho phép phân tích")
    if guild.me is not None:
        bot_permissions = channel.permissions_for(guild.me)
        missing: list[str] = []
        if not bot_permissions.view_channel:
            missing.append("View Channel")
        if not bot_permissions.read_message_history:
            missing.append("Read Message History")
        if missing:
            raise app_commands.CheckFailure(
                f"Bot thiếu quyền tại {channel.mention}: **{', '.join(missing)}**. "
                "Quản trị viên cần cấp quyền này cho bot."
            )
    if isinstance(interaction.user, discord.Member):
        permissions = channel.permissions_for(interaction.user)
        if not permissions.view_channel or not permissions.read_message_history:
            raise app_commands.CheckFailure("Bạn không có quyền đọc lịch sử kênh này")
    return guild


admin_permission = app_commands.default_permissions(manage_guild=True)
admin_check = app_commands.checks.has_permissions(manage_guild=True)


@bot.tree.command(name="setup-output", description="Chọn kênh nhận báo cáo")
@admin_permission
@admin_check
async def setup_output(
    interaction: discord.Interaction, channel: discord.TextChannel
) -> None:
    guild = _guild(interaction)
    await bot.db.set_output(guild.id, channel.id)
    await interaction.response.send_message(
        f"Đã đặt kênh báo cáo là {channel.mention}.", ephemeral=True
    )


@bot.tree.command(name="add-source", description="Cho phép bot phân tích một kênh")
@admin_permission
@admin_check
async def add_source(
    interaction: discord.Interaction, channel: discord.TextChannel
) -> None:
    guild = _guild(interaction)
    added = await bot.db.add_source(guild.id, channel.id)
    message = f"Đã thêm {channel.mention}." if added else "Kênh này đã được thêm."
    await interaction.response.send_message(message, ephemeral=True)


@bot.tree.command(name="remove-source", description="Bỏ một kênh khỏi danh sách phân tích")
@admin_permission
@admin_check
async def remove_source(
    interaction: discord.Interaction, channel: discord.TextChannel
) -> None:
    guild = _guild(interaction)
    removed = await bot.db.remove_source(guild.id, channel.id)
    message = f"Đã bỏ {channel.mention}." if removed else "Kênh này chưa được thêm."
    await interaction.response.send_message(message, ephemeral=True)


@bot.tree.command(
    name="group-set",
    description="Tạo hoặc cập nhật một nhóm gồm tối đa 6 kênh nguồn",
)
@app_commands.describe(
    name="Tên nhóm dùng trong summary, chat hoặc trends",
    channel="Kênh ưu tiên 1 (cao nhất)",
    channel_2="Kênh ưu tiên 2",
    channel_3="Kênh ưu tiên 3",
    channel_4="Kênh ưu tiên 4",
    channel_5="Kênh ưu tiên 5",
    channel_6="Kênh ưu tiên 6",
)
@admin_permission
@admin_check
async def set_group(
    interaction: discord.Interaction,
    name: app_commands.Range[str, 1, 50],
    channel: discord.TextChannel,
    channel_2: discord.TextChannel | None = None,
    channel_3: discord.TextChannel | None = None,
    channel_4: discord.TextChannel | None = None,
    channel_5: discord.TextChannel | None = None,
    channel_6: discord.TextChannel | None = None,
) -> None:
    clean_name = _clean_group_name(str(name))
    guild, channels = await _requested_channels(
        interaction,
        None,
        [channel, channel_2, channel_3, channel_4, channel_5, channel_6],
    )
    await bot.db.set_channel_group(
        guild.id, clean_name, [selected.id for selected in channels]
    )
    mentions = ", ".join(selected.mention for selected in channels)
    await interaction.response.send_message(
        f"Đã lưu nhóm **{clean_name}** theo thứ tự: {mentions}.",
        ephemeral=True,
        allowed_mentions=discord.AllowedMentions.none(),
    )


@bot.tree.command(name="group-remove", description="Xóa một nhóm kênh đã lưu")
@app_commands.describe(name="Tên nhóm cần xóa")
@admin_permission
@admin_check
async def remove_group(
    interaction: discord.Interaction,
    name: app_commands.Range[str, 1, 50],
) -> None:
    guild = _guild(interaction)
    clean_name = _clean_group_name(str(name))
    removed = await bot.db.remove_channel_group(guild.id, clean_name)
    message = (
        f"Đã xóa nhóm **{clean_name}**."
        if removed
        else f"Không tìm thấy nhóm **{clean_name}**."
    )
    await interaction.response.send_message(message, ephemeral=True)


@bot.tree.command(name="groups", description="Xem các nhóm kênh đã lưu")
async def list_groups(interaction: discord.Interaction) -> None:
    guild = _guild(interaction)
    groups = await bot.db.list_channel_groups(guild.id)
    if groups:
        lines = [
            f"• **{row['name']}** — {row['channel_count']} kênh"
            for row in groups[:25]
        ]
        if len(groups) > 25:
            lines.append(f"• …và {len(groups) - 25} nhóm khác")
        message = "**Nhóm kênh trong server:**\n" + "\n".join(lines)
    else:
        message = "Chưa có nhóm kênh. Quản trị viên có thể tạo bằng /group-set."
    await interaction.response.send_message(
        message,
        ephemeral=True,
        allowed_mentions=discord.AllowedMentions.none(),
    )


@bot.tree.command(name="set-interval", description="Đặt chu kỳ báo cáo tự động")
@admin_permission
@admin_check
async def set_interval(
    interaction: discord.Interaction,
    hours: app_commands.Range[int, 1, 168],
) -> None:
    guild = _guild(interaction)
    await bot.db.set_interval(guild.id, int(hours))
    await interaction.response.send_message(
        f"Đã đặt chu kỳ **{hours} giờ**.", ephemeral=True
    )


@bot.tree.command(name="config", description="Xem cấu hình bot trong server")
@admin_permission
@admin_check
async def show_config(interaction: discord.Interaction) -> None:
    guild = _guild(interaction)
    config = await bot.db.get_config(guild.id)
    source_ids = await bot.db.get_sources(guild.id)
    group_rows = await bot.db.list_channel_groups(guild.id)
    output = (
        f"<#{config['output_channel_id']}>"
        if config and config["output_channel_id"]
        else "Chưa đặt"
    )
    interval = config["interval_hours"] if config else 6
    sources = ", ".join(f"<#{item}>" for item in source_ids) or "Chưa có"
    groups = ", ".join(row["name"] for row in group_rows[:20]) or "Chưa có"
    if len(group_rows) > 20:
        groups += f", … (+{len(group_rows) - 20})"
    await interaction.response.send_message(
        f"**Kênh nguồn (ưu tiên cao → thấp):** {sources}\n"
        f"**Nhóm kênh:** {groups}\n"
        f"**Kênh báo cáo:** {output}\n"
        f"**Chu kỳ:** {interval} giờ",
        ephemeral=True,
        allowed_mentions=discord.AllowedMentions.none(),
    )


@bot.tree.command(
    name="summary",
    description="Tóm tắt một nhóm hoặc tối đa 6 kênh theo thứ tự ưu tiên",
)
@app_commands.describe(
    channel="Kênh ưu tiên 1; bỏ trống nếu dùng group",
    group="Tên nhóm kênh đã lưu bằng /group-set",
    channel_2="Kênh ưu tiên 2",
    channel_3="Kênh ưu tiên 3",
    channel_4="Kênh ưu tiên 4",
    channel_5="Kênh ưu tiên 5",
    channel_6="Kênh ưu tiên 6",
    hours="Mốc bắt đầu: số giờ trước (mặc định 24)",
    end_hours_ago="Mốc kết thúc: số giờ trước (mặc định 0 = hiện tại)",
    start_at="Mốc bắt đầu tuyệt đối: YYYY-MM-DD HH:mm (giờ Việt Nam)",
    end_at="Mốc kết thúc tuyệt đối: YYYY-MM-DD HH:mm (giờ Việt Nam)",
)
@app_commands.checks.cooldown(1, 60, key=lambda item: (item.guild_id, item.user.id))
async def summary_command(
    interaction: discord.Interaction,
    channel: discord.TextChannel | None = None,
    group: str | None = None,
    channel_2: discord.TextChannel | None = None,
    channel_3: discord.TextChannel | None = None,
    channel_4: discord.TextChannel | None = None,
    channel_5: discord.TextChannel | None = None,
    channel_6: discord.TextChannel | None = None,
    hours: app_commands.Range[int, 1, 168] = settings.summary_default_hours,
    end_hours_ago: app_commands.Range[int, 0, 167] = 0,
    start_at: str | None = None,
    end_at: str | None = None,
) -> None:
    guild, channels = await _requested_channels(
        interaction,
        group,
        [channel, channel_2, channel_3, channel_4, channel_5, channel_6],
    )
    _, output = await _output(guild)
    window = _command_time_window(
        int(hours), int(end_hours_ago), start_at, end_at
    )
    await interaction.response.defer(ephemeral=True, thinking=True)
    run = await bot.run_summary(
        guild,
        output,
        channels,
        window.start,
        window.end,
        window.label,
    )
    if run.message_count:
        message = (
            f"Đã phân tích đầy đủ **{run.message_count}** tin từ "
            f"**{len(run.included)} kênh** và gửi từng phần vào {output.mention}."
        )
    elif run.skipped:
        message = "Không có kênh nào nằm trọn trong ngân sách context hiện tại."
    else:
        message = "Không có tin nhắn phù hợp trong khoảng thời gian này."
    if run.skipped:
        message += "\n" + _skipped_channels_notice(run.skipped)
    await interaction.followup.send(
        message,
        ephemeral=True,
        allowed_mentions=discord.AllowedMentions.none(),
    )


@bot.tree.command(
    name="chat",
    description="Hỏi hoặc tùy biến kết quả bằng ngôn ngữ tự nhiên",
)
@app_commands.describe(
    input="Ví dụ: Chỉ liệt kê deadline dưới dạng checklist",
    channel="Kênh ưu tiên 1; bỏ trống để dùng group hoặc mọi kênh nguồn",
    group="Tên nhóm kênh đã lưu bằng /group-set",
    channel_2="Kênh ưu tiên 2",
    channel_3="Kênh ưu tiên 3",
    channel_4="Kênh ưu tiên 4",
    channel_5="Kênh ưu tiên 5",
    channel_6="Kênh ưu tiên 6",
    hours="Mốc bắt đầu: số giờ trước (mặc định 24)",
    end_hours_ago="Mốc kết thúc: số giờ trước (mặc định 0 = hiện tại)",
    start_at="Mốc bắt đầu tuyệt đối: YYYY-MM-DD HH:mm (giờ Việt Nam)",
    end_at="Mốc kết thúc tuyệt đối: YYYY-MM-DD HH:mm (giờ Việt Nam)",
)
@app_commands.checks.cooldown(1, 30, key=lambda item: (item.guild_id, item.user.id))
async def chat_command(
    interaction: discord.Interaction,
    input: app_commands.Range[str, 1, 1000],
    channel: discord.TextChannel | None = None,
    group: str | None = None,
    channel_2: discord.TextChannel | None = None,
    channel_3: discord.TextChannel | None = None,
    channel_4: discord.TextChannel | None = None,
    channel_5: discord.TextChannel | None = None,
    channel_6: discord.TextChannel | None = None,
    hours: app_commands.Range[int, 1, 168] = settings.summary_default_hours,
    end_hours_ago: app_commands.Range[int, 0, 167] = 0,
    start_at: str | None = None,
    end_at: str | None = None,
) -> None:
    guild, channels = await _requested_channels(
        interaction,
        group,
        [channel, channel_2, channel_3, channel_4, channel_5, channel_6],
        use_all_sources_by_default=True,
    )
    window = _command_time_window(
        int(hours), int(end_hours_ago), start_at, end_at
    )

    await interaction.response.defer(ephemeral=True, thinking=True)
    run, embeds = await bot.run_chat(
        guild,
        channels,
        window.start,
        window.end,
        str(input),
        window.label,
    )

    notice = _skipped_channels_notice(run.skipped) if run.skipped else None
    if embeds:
        await interaction.followup.send(
            content=notice,
            embeds=embeds,
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        return

    message = "Không có tin nhắn phù hợp trong khoảng thời gian này."
    if notice:
        message += "\n" + notice
    await interaction.followup.send(
        message,
        ephemeral=True,
        allowed_mentions=discord.AllowedMentions.none(),
    )


@bot.tree.command(name="trends", description="Phân tích xu hướng của một nhóm hoặc một kênh")
@app_commands.describe(
    channel="Kênh cần phân tích; bỏ trống nếu dùng group",
    group="Tên nhóm kênh đã lưu bằng /group-set",
    current_hours="Mốc bắt đầu: số giờ trước (mặc định 24)",
    end_hours_ago="Mốc kết thúc: số giờ trước (mặc định 0 = hiện tại)",
    start_at="Mốc bắt đầu tuyệt đối: YYYY-MM-DD HH:mm (giờ Việt Nam)",
    end_at="Mốc kết thúc tuyệt đối: YYYY-MM-DD HH:mm (giờ Việt Nam)",
    baseline_days="Số ngày dùng làm baseline",
)
@app_commands.checks.cooldown(1, 60, key=lambda item: (item.guild_id, item.user.id))
async def trends_command(
    interaction: discord.Interaction,
    channel: discord.TextChannel | None = None,
    group: str | None = None,
    current_hours: app_commands.Range[int, 1, 168] = settings.trend_current_hours,
    end_hours_ago: app_commands.Range[int, 0, 167] = 0,
    start_at: str | None = None,
    end_at: str | None = None,
    baseline_days: app_commands.Range[int, 1, 30] = settings.trend_baseline_days,
) -> None:
    guild, channels = await _requested_channels(interaction, group, [channel])
    _, output = await _output(guild)
    window = _command_time_window(
        int(current_hours), int(end_hours_ago), start_at, end_at
    )
    await interaction.response.defer(ephemeral=True, thinking=True)
    count = 0
    channels_with_data = 0
    for selected_channel in channels:
        channel_count = await bot.run_trends(
            guild,
            output,
            selected_channel,
            window.start,
            window.end,
            int(baseline_days),
            window.label,
        )
        count += channel_count
        channels_with_data += int(channel_count > 0)
    message = (
        f"Đã phân tích **{count}** tin từ **{channels_with_data} kênh** "
        f"và gửi vào {output.mention}."
        if count
        else "Không có tin nhắn trong khoảng thời gian đã chọn."
    )
    await interaction.followup.send(message, ephemeral=True)


@bot.tree.command(name="help", description="Xem hướng dẫn sử dụng các lệnh của bot")
async def help_command(interaction: discord.Interaction) -> None:
    embed = discord.Embed(
        title="Hướng dẫn Discord Summary Bot",
        description=(
            "Các kết quả chỉ dùng những kênh nguồn mà quản trị viên đã cho phép. "
            "Bạn cũng phải có quyền đọc mọi kênh được chọn."
        ),
        color=discord.Color.blurple(),
    )
    embed.add_field(
        name="Lệnh phân tích",
        value=(
            "`/summary` — tóm tắt một nhóm hoặc tối đa 6 kênh.\n"
            "`/chat` — hỏi dữ liệu trong các kênh bằng ngôn ngữ tự nhiên.\n"
            "`/trends` — phân tích xu hướng cho một kênh hoặc cả nhóm."
        ),
        inline=False,
    )
    embed.add_field(
        name="Nhóm kênh",
        value=(
            "Quản trị viên dùng `/group-set` để tạo/cập nhật nhóm và "
            "`/group-remove` để xóa. Dùng `/groups` để xem danh sách.\n"
            "Ví dụ: `/summary group:du-an-a`. Không chọn `group` cùng lúc với `channel`."
        ),
        inline=False,
    )
    embed.add_field(
        name="Khoảng thời gian",
        value=(
            "`hours`/`current_hours` là mốc bắt đầu; `end_hours_ago` là mốc kết thúc.\n"
            "Ví dụ `hours:24 end_hours_ago:12` đọc từ 24 giờ trước đến 12 giờ trước. "
            "Hoặc truyền đủ `start_at` và `end_at` theo dạng `YYYY-MM-DD HH:mm` "
            "(giờ Việt Nam). Bỏ các tham số này sẽ dùng 24 giờ trước đến hiện tại."
        ),
        inline=False,
    )
    embed.add_field(
        name="Lệnh quản trị",
        value=(
            "`/add-source`, `/remove-source`, `/setup-output`, `/set-interval`, "
            "`/config`, `/group-set`, `/group-remove`."
        ),
        inline=False,
    )
    await interaction.response.send_message(
        embed=embed,
        ephemeral=True,
        allowed_mentions=discord.AllowedMentions.none(),
    )


@set_group.autocomplete("name")
@remove_group.autocomplete("name")
@summary_command.autocomplete("group")
@chat_command.autocomplete("group")
@trends_command.autocomplete("group")
async def group_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    if interaction.guild_id is None:
        return []
    search = current.strip().casefold()
    groups = await bot.db.list_channel_groups(interaction.guild_id)
    return [
        app_commands.Choice(
            name=f"{row['name']} ({row['channel_count']} kênh)",
            value=row["name"],
        )
        for row in groups
        if search in row["name"].casefold()
    ][:25]


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
) -> None:
    original = getattr(error, "original", error)
    if isinstance(error, app_commands.CommandOnCooldown):
        message = f"Vui lòng thử lại sau {error.retry_after:.0f} giây."
    elif isinstance(error, app_commands.MissingPermissions):
        message = "Bạn cần quyền **Manage Server** để dùng lệnh này."
    elif isinstance(error, app_commands.CheckFailure):
        message = str(error) or "Bạn không có quyền dùng lệnh này."
    else:
        message = str(original) or "Có lỗi khi xử lý lệnh."
        log.error("Slash command lỗi type=%s", type(original).__name__)

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


def main() -> None:
    try:
        settings.validate()
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    bot.run(settings.discord_token, log_handler=None)


if __name__ == "__main__":
    main()
