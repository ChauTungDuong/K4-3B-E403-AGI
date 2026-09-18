import unittest
from datetime import UTC, datetime

from time_window import make_absolute_time_window, make_time_window, resolve_time_window


class TimeWindowTests(unittest.TestCase):
    def test_defaults_to_window_ending_now(self) -> None:
        now = datetime(2026, 9, 19, 12, tzinfo=UTC)
        window = make_time_window(24, now=now)

        self.assertEqual(window.start, datetime(2026, 9, 18, 12, tzinfo=UTC))
        self.assertEqual(window.end, now)
        self.assertEqual(window.duration_hours, 24)
        self.assertEqual(window.label, "24 giờ qua")

    def test_supports_historical_window(self) -> None:
        now = datetime(2026, 9, 19, 12, tzinfo=UTC)
        window = make_time_window(24, 12, now=now)

        self.assertEqual(window.start, datetime(2026, 9, 18, 12, tzinfo=UTC))
        self.assertEqual(window.end, datetime(2026, 9, 19, 0, tzinfo=UTC))
        self.assertEqual(window.duration_hours, 12)
        self.assertEqual(window.label, "24–12 giờ trước")

    def test_rejects_reversed_or_empty_window(self) -> None:
        with self.assertRaises(ValueError):
            make_time_window(12, 12)
        with self.assertRaises(ValueError):
            make_time_window(12, 24)

    def test_supports_absolute_vietnamese_date_and_time(self) -> None:
        window = make_absolute_time_window(
            "2026-09-20 08:30", "2026-09-20 10:45"
        )

        self.assertEqual(window.start, datetime(2026, 9, 20, 1, 30, tzinfo=UTC))
        self.assertEqual(window.end, datetime(2026, 9, 20, 3, 45, tzinfo=UTC))
        self.assertEqual(window.duration_hours, 2.25)
        self.assertEqual(
            window.label, "20/09/2026 08:30–20/09/2026 10:45 (UTC+7)"
        )

    def test_supports_absolute_iso_times_with_timezone(self) -> None:
        window = make_absolute_time_window(
            "2026-09-20T01:30Z", "2026-09-20T03:45+00:00"
        )

        self.assertEqual(window.start, datetime(2026, 9, 20, 1, 30, tzinfo=UTC))
        self.assertEqual(window.end, datetime(2026, 9, 20, 3, 45, tzinfo=UTC))

    def test_absolute_times_override_relative_defaults(self) -> None:
        window = resolve_time_window(
            24,
            0,
            start_at="2026-09-20 08:30",
            end_at="2026-09-20 10:45",
        )

        self.assertEqual(window.start, datetime(2026, 9, 20, 1, 30, tzinfo=UTC))
        self.assertIsNone(window.start_hours_ago)

    def test_uses_relative_window_when_absolute_times_are_omitted(self) -> None:
        now = datetime(2026, 9, 19, 12, tzinfo=UTC)
        window = resolve_time_window(24, now=now)

        self.assertEqual(window.start, datetime(2026, 9, 18, 12, tzinfo=UTC))
        self.assertEqual(window.end, now)

    def test_requires_both_absolute_times(self) -> None:
        with self.assertRaisesRegex(ValueError, "start_at và end_at"):
            resolve_time_window(24, start_at="2026-09-20 08:30")

    def test_rejects_invalid_or_reversed_absolute_window(self) -> None:
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD HH:mm"):
            make_absolute_time_window("20/09/2026 08:30", "2026-09-20 10:45")
        with self.assertRaisesRegex(ValueError, "sau mốc bắt đầu"):
            make_absolute_time_window(
                "2026-09-20 10:45", "2026-09-20 08:30"
            )
        with self.assertRaisesRegex(ValueError, "168 giờ"):
            make_absolute_time_window(
                "2026-09-01 08:30", "2026-09-09 08:30"
            )


if __name__ == "__main__":
    unittest.main()
