import unittest
from datetime import UTC, datetime

from models import Message
from privacy import PrivacyError, PrivacySanitizer, ensure_safe_output


class PrivacyTests(unittest.TestCase):
    def test_sanitize_removes_identity_and_pii(self) -> None:
        messages = [
            Message(
                message_id=1,
                channel_id=10,
                channel_name="khach-hang-a",
                author_id=111,
                author_name="Alice Nguyen",
                created_at=datetime.now(UTC),
                content=(
                    "Alice Nguyen nhắn <@222>, email alice@example.com, "
                    "điện thoại 0901 234 567, địa chỉ: 12 đường ABC; token=abc123"
                ),
            )
        ]

        safe = PrivacySanitizer().sanitize(messages)[0]

        self.assertEqual(safe.author_ref, "USER_01")
        self.assertEqual(safe.channel_ref, "CHANNEL_01")
        self.assertNotIn("Alice Nguyen", safe.content)
        self.assertNotIn("alice@example.com", safe.content)
        self.assertNotIn("0901 234 567", safe.content)
        self.assertNotIn("12 đường ABC", safe.content)
        self.assertNotIn("abc123", safe.content)
        self.assertIn("USER_02", safe.content)

    def test_output_guard_blocks_pii(self) -> None:
        with self.assertRaises(PrivacyError):
            ensure_safe_output("Liên hệ user@example.com")


if __name__ == "__main__":
    unittest.main()
