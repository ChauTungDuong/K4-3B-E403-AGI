from __future__ import annotations

import re

from models import Message, SafeMessage


class PrivacyError(RuntimeError):
    pass


_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("[EMAIL]", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)),
    ("[ROLE_MENTION]", re.compile(r"<@&\d+>")),
    ("[MENTION]", re.compile(r"<@!?\d+>")),
    ("[IP]", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    ("[DISCORD_ID]", re.compile(r"(?<!\w)\d{17,20}(?!\w)")),
    ("[PHONE]", re.compile(r"(?<!\w)(?:\+?\d[ .-]?){9,14}\d(?!\w)")),
    (
        "[PERSONAL_ID]",
        re.compile(
            r"\b(?:cccd|cmnd|căn cước|passport|số tài khoản)\s*[:=]?\s*[A-Z0-9 .-]{6,24}",
            re.I,
        ),
    ),
    (
        "[ADDRESS]",
        re.compile(r"\b(?:địa chỉ|address)\s*[:=]\s*[^\n,;]{4,100}", re.I),
    ),
    ("[URL]", re.compile(r"https?://\S+", re.I)),
    (
        "[SECRET]",
        re.compile(r"\b(?:api[_ -]?key|token|password|secret)\s*[:=]\s*\S+", re.I),
    ),
)


def redact_pii(text: str) -> str:
    """Che các mẫu PII phổ biến. Không dùng kết quả này để khôi phục danh tính."""
    for replacement, pattern in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def contains_pii(text: str) -> bool:
    return any(pattern.search(text) for _, pattern in _PATTERNS)


def ensure_safe_output(text: str) -> None:
    """Chặn report nếu model tạo lại dữ liệu có hình dạng PII."""
    if contains_pii(text):
        raise PrivacyError("Báo cáo bị chặn vì còn dấu hiệu thông tin cá nhân")


class PrivacySanitizer:
    """Tạo bí danh mới cho từng lần phân tích; không lưu bảng ánh xạ."""

    def __init__(self) -> None:
        self.user_aliases: dict[int, str] = {}
        self.channel_aliases: dict[int, str] = {}

    def sanitize(self, messages: list[Message]) -> list[SafeMessage]:
        ordered = sorted(messages, key=lambda item: item.created_at)
        message_refs = {
            item.message_id: f"MSG_{index:03d}" for index, item in enumerate(ordered, 1)
        }

        # Tạo alias trước để mention và tên hiển thị dùng cùng một mã.
        for item in ordered:
            self._user_ref(item.author_id)
            self._channel_ref(item.channel_id)

        safe: list[SafeMessage] = []
        for item in ordered:
            content = self._sanitize_content(item.content, ordered)
            safe.append(
                SafeMessage(
                    ref=message_refs[item.message_id],
                    channel_ref=self._channel_ref(item.channel_id),
                    author_ref=self._user_ref(item.author_id),
                    created_at=item.created_at,
                    content=content,
                    reaction_count=item.reaction_count,
                    reply_count=item.reply_count,
                    reply_to_ref=message_refs.get(item.reply_to_id),
                )
            )
        return safe

    def _sanitize_content(self, content: str, messages: list[Message]) -> str:
        def replace_mention(match: re.Match[str]) -> str:
            user_id = int(re.sub(r"\D", "", match.group(0)))
            return self._user_ref(user_id)

        content = re.sub(r"<@!?\d+>", replace_mention, content)
        # Thay cả display name xuất hiện dưới dạng text thường.
        for item in messages:
            name = item.author_name.strip()
            if len(name) >= 3:
                content = re.sub(
                    rf"(?<!\w){re.escape(name)}(?!\w)",
                    self._user_ref(item.author_id),
                    content,
                    flags=re.I,
                )
        return redact_pii(content)

    def _user_ref(self, user_id: int) -> str:
        if user_id not in self.user_aliases:
            self.user_aliases[user_id] = f"USER_{len(self.user_aliases) + 1:02d}"
        return self.user_aliases[user_id]

    def _channel_ref(self, channel_id: int) -> str:
        if channel_id not in self.channel_aliases:
            self.channel_aliases[channel_id] = (
                f"CHANNEL_{len(self.channel_aliases) + 1:02d}"
            )
        return self.channel_aliases[channel_id]
