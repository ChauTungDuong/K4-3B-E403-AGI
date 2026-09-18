import unittest
from datetime import UTC, datetime

from time_window import make_time_window


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


if __name__ == "__main__":
    unittest.main()
