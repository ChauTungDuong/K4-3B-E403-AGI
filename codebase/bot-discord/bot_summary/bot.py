from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands, tasks

from collector import DiscordCollector
from config import settings
from database import Database
from gemini import GeminiClient
from models import Message, SafeMessage
from privacy import PrivacySanitizer
from reporter import send_embeds, send_trend_report, summary_embeds
from summary import SummaryService
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
        title: str,
    ) -> int:
        async with self._lock(guild.id):
            raw = await self.collector.collect_channels(channels, start, end)
            if not raw:
                return 0
            safe = PrivacySanitizer().sanitize(raw)
            sources = _report_sources(guild.id, raw, safe)
            result = await self.summary_service.analyze(safe)
            hours = max(1, round((end - start).total_seconds() / 3600))
            await send_embeds(
                output,
                summary_embeds(result, title, hours=hours, sources=sources),
            )
            return len(raw)

    async def run_trends(
        self,
        guild: discord.Guild,
        output: discord.TextChannel,
        channel: discord.TextChannel,
        current_hours: int,
        baseline_days: int,
    ) -> int:
        async with self._lock(guild.id):
            end = datetime.now(UTC)
            current_start = end - timedelta(hours=current_hours)
            baseline_start = current_start - timedelta(days=baseline_days)
            current_raw = await self.collector.collect_channel(channel, current_start, end)
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
            result = await self.trend_service.analyze(
                current_safe,
                baseline_safe,
                current_hours,
                baseline_days,
            )
            await self.db.save_trend_snapshot(
                guild.id, channel.id, current_hours, baseline_days, result
            )
            await send_trend_report(
                output,
                result,
                f"#{channel.name}",
                hours=current_hours,
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
                await self.run_summary(
                    guild, output, channels, last_run, now, "Báo cáo định kỳ"
                )
                for channel in channels:
                    await self.run_trends(
                        guild,
                        output,
                        channel,
                        int(config["interval_hours"]),
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
    output = (
        f"<#{config['output_channel_id']}>"
        if config and config["output_channel_id"]
        else "Chưa đặt"
    )
    interval = config["interval_hours"] if config else 6
    sources = ", ".join(f"<#{item}>" for item in source_ids) or "Chưa có"
    await interaction.response.send_message(
        f"**Kênh nguồn:** {sources}\n**Kênh báo cáo:** {output}\n"
        f"**Chu kỳ:** {interval} giờ",
        ephemeral=True,
        allowed_mentions=discord.AllowedMentions.none(),
    )


@bot.tree.command(name="summary", description="Tóm tắt và tạo danh sách công việc")
@app_commands.describe(channel="Kênh cần tóm tắt", hours="Số giờ cần đọc")
@app_commands.checks.cooldown(1, 60, key=lambda item: (item.guild_id, item.user.id))
async def summary_command(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    hours: app_commands.Range[int, 1, 168] = settings.summary_default_hours,
) -> None:
    guild = await _check_source(interaction, channel)
    _, output = await _output(guild)
    await interaction.response.defer(ephemeral=True, thinking=True)
    end = datetime.now(UTC)
    count = await bot.run_summary(
        guild,
        output,
        [channel],
        end - timedelta(hours=int(hours)),
        end,
        f"#{channel.name}",
    )
    message = (
        f"Đã phân tích **{count}** tin và gửi vào {output.mention}."
        if count
        else "Không có tin nhắn phù hợp trong khoảng thời gian này."
    )
    await interaction.followup.send(message, ephemeral=True)


@bot.tree.command(name="trends", description="Phân tích xu hướng của một kênh")
@app_commands.describe(
    channel="Kênh cần phân tích",
    current_hours="Cửa sổ hiện tại",
    baseline_days="Số ngày dùng làm baseline",
)
@app_commands.checks.cooldown(1, 60, key=lambda item: (item.guild_id, item.user.id))
async def trends_command(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    current_hours: app_commands.Range[int, 1, 168] = settings.trend_current_hours,
    baseline_days: app_commands.Range[int, 1, 30] = settings.trend_baseline_days,
) -> None:
    guild = await _check_source(interaction, channel)
    _, output = await _output(guild)
    await interaction.response.defer(ephemeral=True, thinking=True)
    count = await bot.run_trends(
        guild, output, channel, int(current_hours), int(baseline_days)
    )
    message = (
        f"Đã phân tích **{count}** tin hiện tại và gửi vào {output.mention}."
        if count
        else "Không có tin nhắn trong cửa sổ hiện tại."
    )
    await interaction.followup.send(message, ephemeral=True)


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
