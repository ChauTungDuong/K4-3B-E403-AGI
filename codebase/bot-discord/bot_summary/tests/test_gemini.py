import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from gemini import GeminiClient, _retry_delay_seconds


class DummyOutput(BaseModel):
    value: str


class GeminiTraceTests(unittest.TestCase):
    def test_trace_contains_prompt_and_raw_response(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_path = Path(temp_dir) / "trace.jsonl"
            client = GeminiClient(
                "test-key",
                "test-model",
                trace_enabled=True,
                trace_path=trace_path,
            )

            client._write_trace(
                trace_id="trace-1",
                attempt=1,
                started_at=datetime.now(UTC),
                duration_ms=12,
                schema=DummyOutput,
                prompt="prompt đã ẩn danh",
                raw_response='{"value":"ok"}',
                status="success",
                context={"case_id": "TEST-01"},
            )

            record = json.loads(trace_path.read_text(encoding="utf-8"))
            self.assertEqual(record["prompt"], "prompt đã ẩn danh")
            self.assertEqual(record["raw_response"], '{"value":"ok"}')
            self.assertEqual(record["context"]["case_id"], "TEST-01")

    def test_retry_delay_uses_provider_hint(self) -> None:
        delay = _retry_delay_seconds(
            RuntimeError("429 RESOURCE_EXHAUSTED. Please retry in 12.25s."),
            attempt=0,
        )
        self.assertEqual(delay, 12.75)


if __name__ == "__main__":
    unittest.main()
