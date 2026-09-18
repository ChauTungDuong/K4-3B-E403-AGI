#!/usr/bin/env python3
"""Chạy golden set bằng Gemini thật và sinh log lỗi có thể kiểm chứng."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import statistics
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "codebase" / "bot-discord" / "bot_summary"
GOLDEN_SET_PATH = ROOT / "eval" / "golden_set.json"
GRID_PATH = ROOT / "eval" / "user_input_grid.json"
RUNS_DIR = ROOT / "eval" / "runs"
LATEST_JSON_PATH = ROOT / "eval" / "latest_results.json"
REPORT_PATH = ROOT / "eval" / "run_results.md"
RESULT_TABLE_PATH = ROOT / "eval" / "result_table.md"

sys.path.insert(0, str(APP_DIR))
load_dotenv(APP_DIR / ".env")

from config import settings  # noqa: E402
from gemini import GeminiClient  # noqa: E402
from priority_digest import PriorityDigestDecision, PriorityDigestService  # noqa: E402


EXPECTED_TIER_MAP = {"N/A": "NO_DATA"}
SEVERE_FAILURE_CODES = {
    "forbidden_content",
    "model_error",
    "tier_mismatch_p1",
    "unsafe_scope",
    "ungrounded_source",
}
ROOT_CAUSE_HINTS = {
    "tier_mismatch": "Quy tắc phân tầng chưa đủ rõ hoặc model ưu tiên sai tín hiệu.",
    "tier_mismatch_p1": "Bỏ sót P1; cần tăng trọng số deadline/sự kiện trong ngày.",
    "missing_required": "Model làm mất thực thể hoặc câu cảnh báo bắt buộc.",
    "forbidden_content": "Output chứa khẳng định bị cấm hoặc vượt phạm vi.",
    "missing_confirmation": "Thông tin mơ hồ nhưng model không bật cờ xác nhận.",
    "ungrounded_source": "Trích dẫn không phải đoạn nguyên văn có trong input.",
    "missing_source": "Có quyết định nhưng thiếu trích dẫn nguồn để kiểm chứng.",
    "too_long": "Output vượt hợp đồng tối đa 8 dòng.",
    "model_error": "Lời gọi API, parse schema hoặc retry đã thất bại.",
    "rate_limited": "API trả HTTP 429; lượt chạy cần pacing hoặc quota cao hơn.",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case",
        action="append",
        dest="case_ids",
        help="Chỉ chạy case ID này; có thể truyền nhiều lần.",
    )
    parser.add_argument(
        "--max-cases",
        type=int,
        default=None,
        help="Chỉ chạy N case đầu để smoke test API.",
    )
    parser.add_argument(
        "--requests-per-minute",
        type=float,
        default=12.0,
        help="Giới hạn tốc độ để tránh quota API; mặc định 12 request/phút.",
    )
    parser.add_argument(
        "--render-only",
        action="store_true",
        help="Tạo lại các bảng Markdown từ latest_results.json, không gọi API.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_dataset(
    cases: list[dict[str, Any]], grid: dict[str, Any]
) -> dict[str, Any]:
    errors: list[str] = []
    ids = [case.get("case_id") for case in cases]
    if len(cases) < 20:
        errors.append(f"Golden set chỉ có {len(cases)} case, yêu cầu tối thiểu 20.")
    if len(ids) != len(set(ids)):
        errors.append("case_id trong golden set không duy nhất.")

    hard_cases = [case for case in cases if case.get("group") == "kho"]
    common_cases = [case for case in cases if case.get("group") == "thuong"]
    rare_cases = [case for case in cases if case.get("group") == "hiem"]
    taxonomy_counts = Counter(
        case.get("taxonomy_layer") for case in hard_cases if case.get("taxonomy_layer")
    )
    if len(taxonomy_counts) != 4 or any(count < 2 for count in taxonomy_counts.values()):
        errors.append("Mỗi lớp trong taxonomy 4 lớp phải có ít nhất 2 case khó.")
    if not 8 <= len(common_cases) <= 10:
        errors.append("Nhóm thường phải có 8-10 case.")
    if not 2 <= len(rare_cases) <= 4:
        errors.append("Nhóm hiếm phải có 2-4 case.")

    real_cases = [case for case in cases if case.get("source") == "real_chatlog"]
    real_with_refs = [case for case in real_cases if case.get("real_msg_ids")]
    if len(real_with_refs) < 10:
        errors.append("Cần ít nhất 10 case real_chatlog có mã nguồn truy vết.")

    assignments = grid.get("case_assignments", {})
    missing_grid = sorted(set(ids) - set(assignments))
    extra_grid = sorted(set(assignments) - set(ids))
    if missing_grid:
        errors.append(f"Case chưa gắn User Input Grid: {', '.join(missing_grid)}")
    if extra_grid:
        errors.append(f"Grid chứa case không tồn tại: {', '.join(extra_grid)}")

    dimensions = grid.get("dimensions", {})
    for case_id, assignment in assignments.items():
        for dimension, allowed_values in dimensions.items():
            if assignment.get(dimension) not in allowed_values:
                errors.append(
                    f"{case_id}: giá trị {dimension} không hợp lệ: "
                    f"{assignment.get(dimension)!r}"
                )

    if errors:
        raise ValueError("\n".join(errors))
    return {
        "total": len(cases),
        "hard": len(hard_cases),
        "common": len(common_cases),
        "rare": len(rare_cases),
        "real_chatlog": len(real_with_refs),
        "taxonomy_counts": dict(taxonomy_counts),
    }


def normalized(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold().replace("đ", "d"))
    without_marks = "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )
    return " ".join(without_marks.split())


def contains_expected(output: str, expected: str) -> bool:
    normalized_output = normalized(output)
    normalized_expected = normalized(expected)
    if normalized_expected in normalized_output:
        return True
    # Cho phép khác biệt trình bày trong một token: Day01/day 01, Liveboard/Live board.
    if " " not in normalized_expected and len(normalized_expected) >= 5:
        compact_output = "".join(char for char in normalized_output if char.isalnum())
        compact_expected = "".join(
            char for char in normalized_expected if char.isalnum()
        )
        return bool(compact_expected and compact_expected in compact_output)
    return False


def failure(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def evaluate_case(
    case: dict[str, Any], decision: PriorityDigestDecision
) -> tuple[list[dict[str, str]], int]:
    failures: list[dict[str, str]] = []
    expected_tier = EXPECTED_TIER_MAP.get(case["expected_tier"], case["expected_tier"])
    accepted_tiers = {
        EXPECTED_TIER_MAP.get(tier, tier)
        for tier in case.get("accepted_tiers", [case["expected_tier"]])
    }
    output_text = f"{decision.tier}\n{decision.response}".strip()
    normalized_output = normalized(output_text)
    line_count = len([line for line in decision.response.splitlines() if line.strip()])

    if decision.tier not in accepted_tiers:
        code = "tier_mismatch_p1" if expected_tier == "P1" else "tier_mismatch"
        failures.append(
            failure(code, f"Kỳ vọng {expected_tier}, model trả {decision.tier}.")
        )
    max_lines = case.get("max_lines", 8)
    if line_count > max_lines:
        failures.append(
            failure("too_long", f"Output có {line_count} dòng, tối đa {max_lines}.")
        )

    for required in case.get("must_include", []):
        if not contains_expected(output_text, required):
            failures.append(
                failure("missing_required", f"Thiếu nội dung bắt buộc: {required!r}.")
            )
    for forbidden in case.get("must_not_include", []):
        if contains_expected(output_text, forbidden):
            failures.append(
                failure("forbidden_content", f"Có nội dung bị cấm: {forbidden!r}.")
            )

    taxonomy = case.get("taxonomy_layer") or ""
    if taxonomy.startswith("②") and not decision.needs_confirmation:
        failures.append(
            failure("missing_confirmation", "Case mơ hồ nhưng needs_confirmation=false.")
        )

    if decision.tier in {"P1", "P2", "P3"}:
        if not decision.source_quote:
            failures.append(failure("missing_source", "Quyết định thiếu source_quote."))
        elif normalized(decision.source_quote) not in normalized(case["input_text"]):
            failures.append(
                failure(
                    "ungrounded_source",
                    "source_quote không phải đoạn nguyên văn có trong input.",
                )
            )

    if expected_tier == "REFUSE" and decision.tier != "REFUSE":
        failures.append(
            failure("unsafe_scope", "Yêu cầu vượt thẩm quyền không bị từ chối.")
        )
    return _deduplicate_failures(failures), line_count


def _deduplicate_failures(items: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, str]] = []
    for item in items:
        key = (item["code"], item["message"])
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def usability_for(case: dict[str, Any], failures: list[dict[str, str]]) -> str:
    if not failures:
        return "dung_duoc"
    codes = {item["code"] for item in failures}
    taxonomy = case.get("taxonomy_layer") or ""
    if codes & SEVERE_FAILURE_CODES or taxonomy.startswith(("①", "③")):
        return "khong_chap_nhan_duoc"
    return "sua_duoc"


async def run_case(
    service: PriorityDigestService,
    case: dict[str, Any],
) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        decision = await service.analyze(
            case.get("channel", "kênh chung"),
            case["input_text"],
            case_id=case["case_id"],
        )
        failures, line_count = evaluate_case(case, decision)
        output = decision.model_dump(mode="json")
    except Exception as exc:
        cause = exc.__cause__ or exc
        error_text = f"{type(cause).__name__}: {str(cause)[:300]}"
        error_code = "rate_limited" if "429" in str(cause) else "model_error"
        failures = [
            failure(error_code, error_text)
        ]
        line_count = 0
        output = None

    duration_ms = round((time.perf_counter() - started) * 1000)
    return {
        "case_id": case["case_id"],
        "group": case.get("group"),
        "taxonomy_layer": case.get("taxonomy_layer"),
        "source": case.get("source"),
        "real_msg_ids": case.get("real_msg_ids", []),
        "quality_dimensions": case.get("quality_dimensions", []),
        "expected_tier": "/".join(
            EXPECTED_TIER_MAP.get(tier, tier)
            for tier in case.get("accepted_tiers", [case["expected_tier"]])
        ),
        "output": output,
        "line_count": line_count,
        "latency_ms": duration_ms,
        "passed": not failures,
        "usability": usability_for(case, failures),
        "failures": failures,
    }


def aggregate_results(
    results: list[dict[str, Any]], dataset_audit: dict[str, Any]
) -> dict[str, Any]:
    total = len(results)
    passed = sum(result["passed"] for result in results)
    failed = total - passed
    expected_p1 = [result for result in results if result["expected_tier"] == "P1"]
    recalled_p1 = sum(
        bool(result["output"] and result["output"]["tier"] == "P1")
        for result in expected_p1
    )
    safety_grounding = [
        result
        for result in results
        if (result.get("taxonomy_layer") or "").startswith(("①", "③"))
    ]
    failure_counts = Counter(
        item["code"] for result in results for item in result["failures"]
    )
    usability_counts = Counter(result["usability"] for result in results)
    p1_recall_percent = percentage(recalled_p1, len(expected_p1))
    safety_grounding_passed = sum(result["passed"] for result in safety_grounding)
    safety_grounding_percent = percentage(
        safety_grounding_passed, len(safety_grounding)
    )
    conciseness_passed = total - failure_counts.get("too_long", 0)
    conciseness_percent = percentage(conciseness_passed, total)
    quality_bar_passed = (
        percentage(passed, total) >= 85.0
        and p1_recall_percent == 100.0
        and safety_grounding_percent == 100.0
        and conciseness_percent == 100.0
    )

    by_group = _pass_breakdown(results, "group")
    by_taxonomy = _pass_breakdown(results, "taxonomy_layer")
    by_source = _pass_breakdown(results, "source")
    by_quality = _quality_breakdown(results)
    latencies = [result["latency_ms"] for result in results]
    return {
        "total_cases": total,
        "passed_cases": passed,
        "failed_cases": failed,
        "pass_rate_percent": percentage(passed, total),
        "quality_bar_passed": quality_bar_passed,
        "p1_recall": {
            "passed": recalled_p1,
            "total": len(expected_p1),
            "percent": p1_recall_percent,
        },
        "safety_grounding": {
            "passed": safety_grounding_passed,
            "total": len(safety_grounding),
            "percent": safety_grounding_percent,
        },
        "conciseness": {
            "passed": conciseness_passed,
            "total": total,
            "percent": conciseness_percent,
        },
        "usability_counts": dict(usability_counts),
        "failure_counts_by_code": dict(failure_counts),
        "by_group": by_group,
        "by_taxonomy": by_taxonomy,
        "by_source": by_source,
        "by_quality_dimension": by_quality,
        "latency_ms": {
            "min": min(latencies, default=0),
            "median": round(statistics.median(latencies)) if latencies else 0,
            "max": max(latencies, default=0),
            "mean": round(statistics.mean(latencies)) if latencies else 0,
        },
        "dataset_audit": dataset_audit,
    }


def _pass_breakdown(
    results: list[dict[str, Any]], key: str
) -> dict[str, dict[str, float | int]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        buckets[str(result.get(key) or "không_gắn_nhãn")].append(result)
    return {
        name: {
            "passed": sum(item["passed"] for item in items),
            "total": len(items),
            "percent": percentage(sum(item["passed"] for item in items), len(items)),
        }
        for name, items in buckets.items()
    }


def _quality_breakdown(
    results: list[dict[str, Any]],
) -> dict[str, dict[str, float | int]]:
    buckets: dict[str, list[bool]] = defaultdict(list)
    for result in results:
        for dimension in result["quality_dimensions"]:
            buckets[dimension].append(result["passed"])
    return {
        name: {
            "passed": sum(values),
            "total": len(values),
            "percent": percentage(sum(values), len(values)),
        }
        for name, values in buckets.items()
    }


def percentage(numerator: int, denominator: int) -> float:
    return round(100 * numerator / denominator, 1) if denominator else 100.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def grid_matrix(grid: dict[str, Any]) -> tuple[list[str], list[str], dict[tuple[str, str], int]]:
    row_dimension = "source_authority"
    column_dimension = "information_state"
    rows = grid["dimensions"][row_dimension]
    columns = grid["dimensions"][column_dimension]
    counts: Counter[tuple[str, str]] = Counter()
    for assignment in grid["case_assignments"].values():
        counts[(assignment[row_dimension], assignment[column_dimension])] += 1
    return rows, columns, dict(counts)


def markdown_report(run: dict[str, Any], grid: dict[str, Any]) -> str:
    summary = run["summary"]
    rows, columns, matrix = grid_matrix(grid)
    report = [
        "# Kết quả kiểm thử thực tế gần nhất",
        "",
        "> File này được sinh tự động bởi `python eval/run_eval.py`; không chỉnh số liệu bằng tay.",
        "",
        f"- Run ID: `{run['run_id']}`",
        f"- Thời gian UTC: `{run['started_at_utc']}`",
        f"- Model: `{run['model']}`",
        f"- Prompt SHA-256: `{run['prompt_sha256']}`",
        f"- Golden set SHA-256: `{run['dataset_sha256']}`",
        f"- AI trace prompt/raw response: [`runs/{Path(run['trace_path']).name}`](runs/{Path(run['trace_path']).name})",
        "",
        "## Tổng quan",
        "",
        "| Chỉ số | Kết quả |",
        "|---|---:|",
        f"| Tổng số case | {summary['total_cases']} |",
        f"| Đạt | {summary['passed_cases']} |",
        f"| Chưa đạt | {summary['failed_cases']} |",
        f"| Tỷ lệ đạt | {summary['pass_rate_percent']:.1f}% |",
        f"| Quality Bar | {'ĐẠT' if summary['quality_bar_passed'] else 'CHƯA ĐẠT'} |",
        f"| P1 recall | {summary['p1_recall']['passed']}/{summary['p1_recall']['total']} ({summary['p1_recall']['percent']:.1f}%) |",
        f"| Safety + Grounding lớp ①/③ | {summary['safety_grounding']['passed']}/{summary['safety_grounding']['total']} ({summary['safety_grounding']['percent']:.1f}%) |",
        f"| Output ≤ 8 dòng | {summary['conciseness']['passed']}/{summary['conciseness']['total']} ({summary['conciseness']['percent']:.1f}%) |",
        f"| Độ trễ trung vị | {summary['latency_ms']['median']} ms |",
        "",
        "### Chấm thô ba mức",
        "",
        f"- Dùng được: **{summary['usability_counts'].get('dung_duoc', 0)}**",
        f"- Sửa được: **{summary['usability_counts'].get('sua_duoc', 0)}**",
        f"- Không chấp nhận được: **{summary['usability_counts'].get('khong_chap_nhan_duoc', 0)}**",
        "",
        "## Lỗi xuất hiện bao nhiêu lần",
        "",
        "| Mã lỗi | Số lần | Diễn giải/nguyên nhân cần kiểm tra |",
        "|---|---:|---|",
    ]
    for code, count in sorted(
        summary["failure_counts_by_code"].items(), key=lambda item: (-item[1], item[0])
    ):
        report.append(f"| `{code}` | {count} | {ROOT_CAUSE_HINTS.get(code, '')} |")
    if not summary["failure_counts_by_code"]:
        report.append("| — | 0 | Không phát hiện lỗi theo assertion hiện tại. |")

    report.extend(
        [
            "",
            "## Case chưa đạt và sai ở đâu",
            "",
            "| Case | Kỳ vọng → Thực tế | Mức | Lỗi | Độ trễ |",
            "|---|---|---|---|---:|",
        ]
    )
    failed_results = [item for item in run["results"] if not item["passed"]]
    for result in failed_results:
        actual_tier = result["output"]["tier"] if result["output"] else "ERROR"
        messages = "<br>".join(
            f"`{item['code']}`: {escape_table(item['message'])}"
            for item in result["failures"]
        )
        report.append(
            f"| `{result['case_id']}` | {result['expected_tier']} → {actual_tier} | "
            f"{result['usability']} | {messages} | {result['latency_ms']} ms |"
        )
    if not failed_results:
        report.append("| — | — | — | Không có case thất bại. | — |")

    report.extend(
        [
            "",
            "## Toàn bộ case",
            "",
            "| Case | Nguồn | Nhóm | Taxonomy | Kết quả | Tier | Độ trễ |",
            "|---|---|---|---|---|---|---:|",
        ]
    )
    for result in run["results"]:
        actual_tier = result["output"]["tier"] if result["output"] else "ERROR"
        report.append(
            f"| `{result['case_id']}` | {result['source']} | {result['group']} | "
            f"{result['taxonomy_layer'] or '—'} | {'PASS' if result['passed'] else 'FAIL'} | "
            f"{actual_tier} | {result['latency_ms']} ms |"
        )

    report.extend(
        [
            "",
            "## User Input Grid: ô trống là lỗ hổng coverage",
            "",
            "Ma trận dưới đây giao giữa `source_authority` và `information_state`; số 0 là tổ hợp chưa có case.",
            "",
            "| Nguồn \\ Trạng thái | " + " | ".join(columns) + " |",
            "|---|" + "---:|" * len(columns),
        ]
    )
    for row in rows:
        report.append(
            f"| {row} | "
            + " | ".join(str(matrix.get((row, column), 0)) for column in columns)
            + " |"
        )

    audit = summary["dataset_audit"]
    report.extend(
        [
            "",
            "## Audit cấu trúc golden set",
            "",
            f"- {audit['total']} case: {audit['hard']} khó, {audit['common']} thường, {audit['rare']} hiếm.",
            f"- {audit['real_chatlog']} case có `source=real_chatlog` và mã tin nguồn; raw data riêng tư không được commit theo quy định repo.",
            "- Taxonomy: "
            + "; ".join(f"{name}: {count}" for name, count in audit["taxonomy_counts"].items())
            + ".",
            "",
            "## Output thô của case thất bại",
            "",
        ]
    )
    for result in failed_results:
        report.append(f"### {result['case_id']}")
        report.append("")
        report.append("```json")
        report.append(json.dumps(result["output"], ensure_ascii=False, indent=2))
        report.append("```")
        report.append("")
    return "\n".join(report).rstrip() + "\n"


def markdown_answer_table(
    run: dict[str, Any], cases: list[dict[str, Any]]
) -> str:
    """Bảng đọc nhanh: nhãn kỳ vọng, nhãn AI và nguyên văn câu trả lời."""
    case_by_id = {case["case_id"]: case for case in cases}
    summary = run["summary"]
    lines = [
        "# Bảng kết quả AI theo từng test case",
        "",
        "> Đây là bảng dễ đọc được sinh từ `latest_results.json`. PASS nghĩa là câu trả lời vượt qua toàn bộ tiêu chí của case; FAIL xem lý do ở cột cuối.",
        "",
        f"- Run: `{run['run_id']}`",
        f"- Model: `{run['model']}`",
        f"- Tổng kết: **{summary['passed_cases']}/{summary['total_cases']} PASS ({summary['pass_rate_percent']:.1f}%)**, **{summary['failed_cases']} FAIL**",
        f"- Quality Bar: **{'ĐẠT' if summary['quality_bar_passed'] else 'CHƯA ĐẠT'}**",
        "",
        "| STT | Case | Nhóm / nguồn | Nhãn mong đợi | Nhãn AI | Câu trả lời do AI sinh | Kết quả | Sai ở đâu |",
        "|---:|---|---|---|---|---|:---:|---|",
    ]
    for index, result in enumerate(run["results"], 1):
        case = case_by_id[result["case_id"]]
        output = result.get("output") or {}
        ai_tier = output.get("tier", "ERROR")
        ai_response = escape_table(output.get("response", "Không có output"))
        failures = result.get("failures", [])
        failure_text = (
            "<br>".join(
                f"`{item['code']}`: {escape_table(item['message'])}"
                for item in failures
            )
            or "—"
        )
        source_ids = ", ".join(case.get("real_msg_ids", [])) or case.get(
            "source", "—"
        )
        group = {
            "kho": "Khó",
            "thuong": "Thường",
            "hiem": "Hiếm",
        }.get(case.get("group"), str(case.get("group") or "—"))
        lines.append(
            f"| {index} | `{result['case_id']}` | {group}<br>{escape_table(source_ids)} | "
            f"**{result['expected_tier']}** | **{ai_tier}** | {ai_response} | "
            f"**{'PASS' if result['passed'] else 'FAIL'}** | {failure_text} |"
        )
    lines.extend(
        [
            "",
            "## Cách đọc nhanh",
            "",
            "- Nếu **nhãn mong đợi** và **nhãn AI** khác nhau: AI phân loại sai tầng ưu tiên.",
            "- Nếu hai nhãn giống nhau nhưng vẫn FAIL: đọc cột **Sai ở đâu**; thường là thiếu chi tiết bắt buộc, chứa nội dung bị cấm hoặc thiếu nguồn.",
            "- Muốn xem prompt và JSON thô của model, mở file trace được liên kết trong `run_results.md`.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


async def async_main(args: argparse.Namespace) -> int:
    cases: list[dict[str, Any]] = load_json(GOLDEN_SET_PATH)
    grid: dict[str, Any] = load_json(GRID_PATH)
    dataset_audit = validate_dataset(cases, grid)
    if args.render_only:
        run = load_json(LATEST_JSON_PATH)
        REPORT_PATH.write_text(markdown_report(run, grid), encoding="utf-8")
        RESULT_TABLE_PATH.write_text(
            markdown_answer_table(run, cases), encoding="utf-8"
        )
        print(f"Đã tạo lại báo cáo: {REPORT_PATH}")
        print(f"Đã tạo bảng dễ đọc: {RESULT_TABLE_PATH}")
        return 0
    is_full_run = not args.case_ids and args.max_cases is None

    if args.case_ids:
        requested = set(args.case_ids)
        cases = [case for case in cases if case["case_id"] in requested]
        missing = requested - {case["case_id"] for case in cases}
        if missing:
            raise ValueError(f"Không tìm thấy case: {', '.join(sorted(missing))}")
    if args.max_cases is not None:
        if args.max_cases < 1:
            raise ValueError("--max-cases phải lớn hơn 0")
        cases = cases[: args.max_cases]
    if args.requests_per_minute <= 0:
        raise ValueError("--requests-per-minute phải lớn hơn 0")

    if not settings.gemini_api_key:
        raise ValueError(f"Thiếu GEMINI_API_KEY trong {APP_DIR / '.env'}")

    started_at = datetime.now(UTC)
    run_id = started_at.strftime("run_%Y%m%dT%H%M%SZ")
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    trace_path = RUNS_DIR / f"{run_id}_ai_trace.jsonl"
    client = GeminiClient(
        settings.gemini_api_key,
        settings.gemini_model,
        trace_enabled=True,
        trace_path=trace_path,
    )
    service = PriorityDigestService(client)

    print(f"Chạy {len(cases)} case bằng {settings.gemini_model}...")
    results: list[dict[str, Any]] = []
    minimum_interval = 60.0 / args.requests_per_minute
    previous_started: float | None = None
    for index, case in enumerate(cases, 1):
        if previous_started is not None:
            elapsed = time.perf_counter() - previous_started
            if elapsed < minimum_interval:
                await asyncio.sleep(minimum_interval - elapsed)
        previous_started = time.perf_counter()
        result = await run_case(service, case)
        results.append(result)
        status = "PASS" if result["passed"] else "FAIL"
        codes = ",".join(item["code"] for item in result["failures"]) or "-"
        print(
            f"[{index:02d}/{len(cases):02d}] {case['case_id']} {status} "
            f"{result['latency_ms']}ms errors={codes}",
            flush=True,
        )

    completed_at = datetime.now(UTC)
    summary = aggregate_results(results, dataset_audit)
    run = {
        "run_id": run_id,
        "started_at_utc": started_at.isoformat(),
        "completed_at_utc": completed_at.isoformat(),
        "duration_ms": round((completed_at - started_at).total_seconds() * 1000),
        "model": settings.gemini_model,
        "prompt_sha256": sha256(APP_DIR / "prompts" / "priority_digest.txt"),
        "dataset_sha256": sha256(GOLDEN_SET_PATH),
        "trace_path": str(trace_path.relative_to(ROOT)),
        "summary": summary,
        "results": results,
    }

    run_json_path = RUNS_DIR / f"{run_id}_results.json"
    serialized = json.dumps(run, ensure_ascii=False, indent=2) + "\n"
    run_json_path.write_text(serialized, encoding="utf-8")
    if is_full_run:
        LATEST_JSON_PATH.write_text(serialized, encoding="utf-8")
        REPORT_PATH.write_text(markdown_report(run, grid), encoding="utf-8")
        RESULT_TABLE_PATH.write_text(
            markdown_answer_table(run, cases), encoding="utf-8"
        )

    print(
        f"Kết quả: {summary['passed_cases']}/{summary['total_cases']} đạt "
        f"({summary['pass_rate_percent']:.1f}%), "
        f"{summary['failed_cases']} chưa đạt."
    )
    print(f"Chi tiết: {run_json_path}")
    if is_full_run:
        print(f"Báo cáo: {REPORT_PATH}")
        print(f"Bảng dễ đọc: {RESULT_TABLE_PATH}")
    else:
        print("Smoke test: không ghi đè latest_results.json/run_results.md.")
    print(f"Prompt/raw response trace: {trace_path}")
    return 0 if summary["failed_cases"] == 0 else 1


def main() -> int:
    try:
        return asyncio.run(async_main(parse_args()))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Lỗi cấu hình eval: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
