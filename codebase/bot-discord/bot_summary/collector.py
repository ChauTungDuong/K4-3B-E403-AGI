from __future__ import annotations

import logging
from datetime import datetime
from typing import AsyncIterator

import discord

from models import Message


log = logging.getLogger(__name__)


class CollectionPermissionError(RuntimeError):
    """Bot không có đủ quyền để đọc lịch sử kênh Discord."""


class CollectionReadError(RuntimeError):
    """Discord API lỗi khi bot đang đọc lịch sử kênh."""


class DiscordCollector:
    def __init__(
        self,
        max_per_channel: int,
        max_total: int,
        max_characters: int,
        include_bot_messages: bool = False,
    ) -> None:
        self.max_per_channel = max_per_channel
        self.max_total = max_total
        self.max_characters = max_characters
        self.include_bot_messages = include_bot_messages

    async def collect_channel(
        self,
        channel: discord.TextChannel,
        start: datetime,
        end: datetime,
        *,
        include_threads: bool = True,
    ) -> list[Message]:
        """Đọc một kênh và thread, sau đó giữ quan hệ reply."""
        messages: dict[int, Message] = {}
        characters = 0

        async def consume(history: AsyncIterator[discord.Message]) -> bool:
            nonlocal characters
            async for item in history:
                if not item.content.strip():
                    continue
                if item.author.bot:
                    is_this_bot = (
                        channel.guild.me is not None
                        and item.author.id == channel.guild.me.id
                    )
                    # Luôn bỏ tin của chính Bot Summary để tránh vòng lặp báo cáo.
                    if is_this_bot or not self.include_bot_messages:
                        continue
                content = item.content.strip()[:2000]
                if characters + len(content) > self.max_characters:
                    return False
                messages[item.id] = self._to_model(item, channel)
                characters += len(content)
                if len(messages) >= self.max_per_channel:
                    return False
            return True

        try:
            can_continue = await consume(
                channel.history(
                    limit=self.max_per_channel,
                    after=start,
                    before=end,
                    oldest_first=True,
                )
            )
            if include_threads and can_continue:
                for thread in await self._threads(channel, start, end):
                    can_continue = await consume(
                        thread.history(
                            limit=self.max_per_channel - len(messages),
                            after=start,
                            before=end,
                            oldest_first=True,
                        )
                    )
                    if not can_continue:
                        break
        except discord.Forbidden as exc:
            log.warning("Bot thiếu quyền đọc kênh %s", channel.id)
            raise CollectionPermissionError(
                f"Bot không có quyền đọc {channel.mention}. "
                "Hãy cấp quyền **View Channel** và **Read Message History** cho bot."
            ) from exc
        except discord.HTTPException as exc:
            log.warning("Discord API lỗi khi đọc kênh %s", channel.id)
            raise CollectionReadError(
                f"Bot chưa thể đọc lịch sử {channel.mention}. Vui lòng thử lại sau."
            ) from exc

        result = sorted(messages.values(), key=lambda item: item.created_at)
        by_id = {item.message_id: item for item in result}
        for item in result:
            if item.reply_to_id in by_id:
                by_id[item.reply_to_id].reply_count += 1
        return result

    async def collect_channels(
        self,
        channels: list[discord.TextChannel],
        start: datetime,
        end: datetime,
    ) -> list[Message]:
        collected: list[Message] = []
        for channel in channels:
            collected.extend(await self.collect_channel(channel, start, end))
        collected.sort(key=lambda item: item.created_at)

        # Giới hạn tổng nhưng vẫn ưu tiên dữ liệu mới nhất trong cửa sổ.
        if len(collected) > self.max_total:
            collected = collected[-self.max_total :]
        while sum(len(item.content) for item in collected) > self.max_characters:
            collected.pop(0)
        return collected

    async def _threads(
        self,
        channel: discord.TextChannel,
        start: datetime,
        end: datetime,
    ) -> list[discord.Thread]:
        threads = list(channel.threads)
        try:
            async for thread in channel.archived_threads(limit=50, before=end):
                if thread.archive_timestamp and thread.archive_timestamp < start:
                    break
                threads.append(thread)
        except discord.Forbidden:
            pass
        return list({thread.id: thread for thread in threads}.values())

    @staticmethod
    def _to_model(item: discord.Message, parent: discord.TextChannel) -> Message:
        reply_to = item.reference.message_id if item.reference else None
        return Message(
            message_id=item.id,
            channel_id=parent.id,
            channel_name=parent.name,
            author_id=item.author.id,
            author_name=item.author.display_name,
            created_at=item.created_at,
            content=item.content.strip()[:2000],
            reaction_count=sum(reaction.count for reaction in item.reactions),
            reply_to_id=reply_to,
        )
