from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, timezone


VIETNAM_TIMEZONE = timezone(timedelta(hours=7), name="UTC+7")
MAX_WINDOW_HOURS = 168
_ABSOLUTE_TIME_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})?$"
)


@dataclass(frozen=True, slots=True)
class TimeWindow:
    start: datetime
    end: datetime
    start_hours_ago: int | None
    end_hours_ago: int | None

    @property
    def duration_hours(self) -> float:
        return (self.end - self.start).total_seconds() / 3600

    @property
    def label(self) -> str:
        if self.start_hours_ago is None or self.end_hours_ago is None:
            start = self.start.astimezone(VIETNAM_TIMEZONE).strftime("%d/%m/%Y %H:%M")
            end = self.end.astimezone(VIETNAM_TIMEZONE).strftime("%d/%m/%Y %H:%M")
            return f"{start}–{end} (UTC+7)"
        if self.end_hours_ago == 0:
            return f"{self.start_hours_ago} giờ qua"
        return f"{self.start_hours_ago}–{self.end_hours_ago} giờ trước"


def make_time_window(
    start_hours_ago: int,
    end_hours_ago: int = 0,
    *,
    now: datetime | None = None,
) -> TimeWindow:
    """Đổi hai mốc "giờ trước" thành cửa sổ UTC nửa kín [start, end)."""
    if start_hours_ago < 1:
        raise ValueError("Mốc bắt đầu phải cách hiện tại ít nhất 1 giờ")
    if end_hours_ago < 0:
        raise ValueError("Mốc kết thúc không được là số âm")
    if end_hours_ago >= start_hours_ago:
        raise ValueError("Mốc kết thúc phải gần hiện tại hơn mốc bắt đầu")

    current = now or datetime.now(UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return TimeWindow(
        start=current - timedelta(hours=start_hours_ago),
        end=current - timedelta(hours=end_hours_ago),
        start_hours_ago=start_hours_ago,
        end_hours_ago=end_hours_ago,
    )


def make_absolute_time_window(start_at: str, end_at: str) -> TimeWindow:
    """Đổi hai mốc ngày giờ phút thành cửa sổ UTC nửa kín [start, end)."""
    start = _parse_absolute_time(start_at)
    end = _parse_absolute_time(end_at)
    if end <= start:
        raise ValueError("Mốc kết thúc phải sau mốc bắt đầu")
    if end - start > timedelta(hours=MAX_WINDOW_HOURS):
        raise ValueError(f"Khoảng thời gian không được dài quá {MAX_WINDOW_HOURS} giờ")
    return TimeWindow(
        start=start,
        end=end,
        start_hours_ago=None,
        end_hours_ago=None,
    )


def resolve_time_window(
    start_hours_ago: int,
    end_hours_ago: int = 0,
    *,
    start_at: str | None = None,
    end_at: str | None = None,
    now: datetime | None = None,
) -> TimeWindow:
    """Ưu tiên hai mốc tuyệt đối; nếu bỏ trống thì giữ cách tính theo số giờ."""
    if (start_at is None) != (end_at is None):
        raise ValueError("Phải truyền đồng thời cả start_at và end_at")
    if start_at is not None and end_at is not None:
        return make_absolute_time_window(start_at, end_at)
    return make_time_window(start_hours_ago, end_hours_ago, now=now)


def _parse_absolute_time(value: str) -> datetime:
    clean_value = value.strip()
    if not _ABSOLUTE_TIME_PATTERN.fullmatch(clean_value):
        raise ValueError(
            "Thời gian phải có dạng YYYY-MM-DD HH:mm (giờ Việt Nam, UTC+7) "
            "hoặc ISO 8601 kèm múi giờ"
        )
    try:
        parsed = datetime.fromisoformat(clean_value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Ngày hoặc giờ không hợp lệ") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=VIETNAM_TIMEZONE)
    return parsed.astimezone(UTC)
