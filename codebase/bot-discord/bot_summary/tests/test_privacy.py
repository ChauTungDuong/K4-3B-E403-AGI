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

    def test_requester_id_mapped_to_user_you(self) -> None:
        messages = [
            Message(
                message_id=1,
                channel_id=10,
                channel_name="lop-hoc",
                author_id=999,
                author_name="Bob Tran",
                created_at=datetime.now(UTC),
                content="Chào <@555>, bạn nhớ nộp bài nhé",
            )
        ]

        safe = PrivacySanitizer(requester_id=555).sanitize(messages)[0]
        self.assertEqual(safe.author_ref, "USER_02")
        self.assertIn("USER_YOU", safe.content)

    def test_output_guard_blocks_pii(self) -> None:
        with self.assertRaises(PrivacyError):
            ensure_safe_output("Liên hệ user@example.com")

    def test_normalize_ref_pads_leading_zeros(self) -> None:
        from privacy import normalize_ref
        self.assertEqual(normalize_ref("MSG_30"), "MSG_030")
        self.assertEqual(normalize_ref("MSG_030"), "MSG_030")
        self.assertEqual(normalize_ref("msg_1"), "MSG_001")
        self.assertEqual(normalize_ref("MSG_249"), "MSG_249")
        self.assertEqual(normalize_ref("MSG_1000"), "MSG_1000")
        self.assertEqual(normalize_ref("CUSTOM"), "CUSTOM")


if __name__ == "__main__":
    unittest.main()
