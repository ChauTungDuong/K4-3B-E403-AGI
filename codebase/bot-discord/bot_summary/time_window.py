from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True, slots=True)
class TimeWindow:
    start: datetime
    end: datetime
    start_hours_ago: int
    end_hours_ago: int

    @property
    def duration_hours(self) -> int:
        return self.start_hours_ago - self.end_hours_ago

    @property
    def label(self) -> str:
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
