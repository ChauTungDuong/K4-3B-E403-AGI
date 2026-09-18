from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _int(name: str, default: int) -> int:
    """Đọc số nguyên từ môi trường và báo lỗi cấu hình dễ hiểu."""
    try:
        return int(os.getenv(name, str(default)))
    except ValueError as exc:
        raise ValueError(f"{name} phải là số nguyên") from exc


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError as exc:
        raise ValueError(f"{name} phải là số") from exc


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name, str(default)).strip().casefold()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} phải là true hoặc false")


@dataclass(frozen=True, slots=True)
class Settings:
    discord_token: str
    gemini_api_key: str
    gemini_model: str
    database_path: str
    dev_guild_id: int | None
    log_level: str
    max_messages_per_channel: int
    max_total_messages: int
    max_input_characters: int
    include_bot_messages: bool
    summary_default_hours: int
    trend_current_hours: int
    trend_baseline_days: int
    min_task_confidence: float
    min_topic_messages: int
    min_topic_participants: int
    hot_score_threshold: float

    @classmethod
    def from_env(cls) -> "Settings":
        guild_id = _int("DISCORD_GUILD_ID", 0)
        return cls(
            discord_token=os.getenv("DISCORD_BOT_TOKEN", ""),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            database_path=os.getenv("DATABASE_PATH", "bot.db"),
            dev_guild_id=guild_id or None,
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            max_messages_per_channel=_int("MAX_MESSAGES_PER_CHANNEL", 500),
            max_total_messages=_int("MAX_TOTAL_MESSAGES", 1000),
            max_input_characters=_int("MAX_INPUT_CHARACTERS", 200_000),
            include_bot_messages=_bool("INCLUDE_BOT_MESSAGES", False),
            summary_default_hours=_int("SUMMARY_DEFAULT_HOURS", 24),
            trend_current_hours=_int("TREND_CURRENT_HOURS", 24),
            trend_baseline_days=_int("TREND_BASELINE_DAYS", 7),
            min_task_confidence=_float("MIN_TASK_CONFIDENCE", 0.75),
            min_topic_messages=_int("MIN_TOPIC_MESSAGES", 3),
            min_topic_participants=_int("MIN_TOPIC_PARTICIPANTS", 2),
            hot_score_threshold=_float("HOT_SCORE_THRESHOLD", 0.70),
        )

    def validate(self) -> None:
        missing = [
            name
            for name, value in {
                "DISCORD_BOT_TOKEN": self.discord_token,
                "GEMINI_API_KEY": self.gemini_api_key,
            }.items()
            if not value
        ]
        if missing:
            raise ValueError(f"Thiếu biến môi trường: {', '.join(missing)}")
        if not 0 <= self.min_task_confidence <= 1:
            raise ValueError("MIN_TASK_CONFIDENCE phải nằm trong khoảng 0..1")
        if not 0 <= self.hot_score_threshold <= 1:
            raise ValueError("HOT_SCORE_THRESHOLD phải nằm trong khoảng 0..1")


settings = Settings.from_env()
