from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncIterator

import discord

from models import Message


log = logging.getLogger(__name__)


class CollectionPermissionError(RuntimeError):
    """Bot không có đủ quyền để đọc lịch sử kênh Discord."""


class CollectionReadError(RuntimeError):
    """Discord API lỗi khi bot đang đọc lịch sử kênh."""


@dataclass(slots=True)
class CollectedChannel:
    """Toàn bộ tin hợp lệ của một kênh trong cửa sổ được yêu cầu."""

    channel_id: int
    channel_name: str
    messages: list[Message] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class SkippedChannel:
    """Kênh bị bỏ nguyên khối, không đưa dữ liệu cắt dở sang LLM."""

    channel_id: int
    channel_name: str
    reason: str


@dataclass(slots=True)
class PrioritizedCollection:
    """Kết quả lấy nhiều kênh theo thứ tự ưu tiên từ cao xuống thấp."""

    included: list[CollectedChannel] = field(default_factory=list)
    skipped: list[SkippedChannel] = field(default_factory=list)

    @property
    def messages(self) -> list[Message]:
        return [message for channel in self.included for message in channel.messages]

    @property
    def message_count(self) -> int:
        return sum(len(channel.messages) for channel in self.included)


@dataclass(slots=True)
class _ChannelRead:
    messages: list[Message]
    complete: bool
    reason: str | None = None


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

    async def collect_channels_atomic(
        self,
        channels: list[discord.TextChannel],
        start: datetime,
        end: datetime,
    ) -> PrioritizedCollection:
        """Chỉ nhận các kênh đầy đủ và giữ đúng thứ tự ưu tiên đầu vào.

        Khi một kênh không thể nằm trọn trong ngân sách, kênh đó và mọi kênh
        ưu tiên thấp hơn đều bị bỏ. Nhờ vậy không có dữ liệu nửa kênh trong
        prompt và kênh chọn sau không thể chiếm chỗ của kênh chọn trước.
        """
        result = PrioritizedCollection()
        used_messages = 0
        used_characters = 0
        priority_blocked = False

        for channel in channels:
            if priority_blocked:
                result.skipped.append(
                    SkippedChannel(
                        channel_id=channel.id,
                        channel_name=channel.name,
                        reason="lower_priority",
                    )
                )
                continue

            read = await self._collect_complete_channel(channel, start, end)
            if not read.complete:
                result.skipped.append(
                    SkippedChannel(
                        channel_id=channel.id,
                        channel_name=channel.name,
                        reason=read.reason or "channel_limit",
                    )
                )
                priority_blocked = True
                continue

            message_count = len(read.messages)
            character_count = sum(len(item.content) for item in read.messages)
            if (
                used_messages + message_count > self.max_total
                or used_characters + character_count > self.max_characters
            ):
                result.skipped.append(
                    SkippedChannel(
                        channel_id=channel.id,
                        channel_name=channel.name,
                        reason="context_budget",
                    )
                )
                priority_blocked = True
                continue

            result.included.append(
                CollectedChannel(
                    channel_id=channel.id,
                    channel_name=channel.name,
                    messages=read.messages,
                )
            )
            used_messages += message_count
            used_characters += character_count

        return result

    async def _collect_complete_channel(
        self,
        channel: discord.TextChannel,
        start: datetime,
        end: datetime,
    ) -> _ChannelRead:
        """Đọc đến hết kênh hoặc dừng ngay khi biết kênh không thể lấy đủ."""
        messages: dict[int, Message] = {}
        characters = 0
        incomplete_reason: str | None = None

        async def consume(history: AsyncIterator[discord.Message]) -> bool:
            nonlocal characters, incomplete_reason
            async for item in history:
                if not item.content.strip():
                    continue
                if item.author.bot:
                    is_this_bot = (
                        channel.guild.me is not None
                        and item.author.id == channel.guild.me.id
                    )
                    if is_this_bot or not self.include_bot_messages:
                        continue
                if item.id in messages:
                    continue

                content = item.content.strip()[:2000]
                if len(messages) + 1 > self.max_per_channel:
                    incomplete_reason = "channel_message_limit"
                    return False
                if characters + len(content) > self.max_characters:
                    incomplete_reason = "channel_character_limit"
                    return False

                messages[item.id] = self._to_model(item, channel)
                characters += len(content)
            return True

        try:
            can_continue = await consume(
                channel.history(
                    limit=None,
                    after=start,
                    before=end,
                    oldest_first=True,
                )
            )
            if can_continue:
                for thread in await self._threads(channel, start, end):
                    can_continue = await consume(
                        thread.history(
                            limit=None,
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
        return _ChannelRead(
            messages=result,
            complete=incomplete_reason is None,
            reason=incomplete_reason,
        )

    async def _threads(
        self,
        channel: discord.TextChannel,
        start: datetime,
        end: datetime,
    ) -> list[discord.Thread]:
        threads = list(channel.threads)
        try:
            async for thread in channel.archived_threads(limit=None, before=end):
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
