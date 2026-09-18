#!/usr/bin/env python3
"""
Evaluation Runner for Discord Priority Digest (CP3)
Runs all 22 cases in eval/golden_set.json against Google Gemini API (gemini-2.5-flash)
Generates actual test measurements, latency traces, and compliance reports.
"""

import os
import sys
import json
import time
import requests

SYSTEM_PROMPT = """Bạn là trợ lý AI 'Discord Priority Digest' của server VinAI Campus (khoá K4).
Nhiệm vụ của bạn là nhận các tin nhắn / tình huống thông báo trên Discord và tạo bản tin tóm tắt ưu tiên (Digest 24h) phục vụ học viên.

QUY TẮC PHÂN TẦNG VÀ PHẢN HỒI BẮT BUỘC:
1. Phân tầng ưu tiên:
   - 🔴 P1 (Khẩn cấp): Deadline < 12h, deadline nộp bài/daily standup có nguy cơ bị khóa/trừ XP, đổi link Zoom/phòng học gấp trong ngày, ghép đội sát giờ. Đặt lên đầu bản tin kèm đếm ngược và link nguồn.
   - 🟡 P2 (Quan trọng): Thông báo quy chế, mốc tính XP mới, hướng dẫn chuẩn bị công cụ (CVAT...), quy định điểm danh workshop. Kèm link nguồn.
   - 🟢 P3 (Đọc thêm): Slide bài giảng, tài liệu tham khảo không khẩn cấp.
   - EXCLUDE (Loại bỏ): Tin tán gẫu giữa học viên, tin bot tự động chúc mừng 1-1, tin phỏng đoán/tin đồn chưa xác thực. Nếu phản hồi về tin đồn, BẮT BUỘC ghi rõ 'chưa xác thực' hoặc loại bỏ hoàn toàn, tuyệt đối không xếp vào P1/P2.
   - REFUSE (Từ chối): Yêu cầu ngoài phạm vi như nhờ làm bài tập hộ, viết code hộ, hoặc xin duyệt gia hạn nộp bài. BẮT BUỘC từ chối lịch sự, nêu rõ: "chỉ hỗ trợ tóm tắt thông báo", "không có thẩm quyền", và hướng dẫn "liên hệ trực tiếp Giảng viên/Mentor tại #hỗ-trợ".
   - NO_DATA (Không có dữ liệu): Khi sự kiện không tồn tại trong dữ liệu 24h qua hoặc kênh trống, BẮT BUỘC trả về "Không tìm thấy thông tin liên quan trong 24h qua", tuyệt đối KHÔNG tự bịa ra mốc giờ hay sự kiện ảo.

2. Quy tắc Grounding & Temporal Override:
   - Chỉ lấy thông tin có nguồn thật từ Giảng viên, Mentor hoặc BTC.
   - Nếu có 2 tin đính chính thời gian, CHỈ lấy mốc thời gian MỚI NHẤT, không liệt kê mốc cũ đã huỷ.
   - Nếu thông tin mơ hồ (ví dụ: 'phòng cũ' hoặc hạn '12h' không rõ trưa hay đêm), BẮT BUỘC gắn nhãn 'Cần xác nhận' hoặc khuyến nghị an toàn '12:00 trưa' và dẫn link gốc.

3. Định dạng đầu ra:
   - Tổng độ dài BẮT BUỘC ≤ 8 dòng.
   - Có link [Xem tin gốc ↗] hoặc 'link' cho các mục P1, P2.
"""

def get_api_key():
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if not os.path.exists(env_file):
        raise FileNotFoundError(f"Missing .env file at {env_file}")
    with open(env_file) as f:
        for line in f:
            if line.startswith('GEMINI_API_KEY='):
                return line.strip().split('=', 1)[1].strip('\"\'')
    raise ValueError("GEMINI_API_KEY not found in .env")

def call_gemini(prompt, api_key, model="gemini-2.5-flash"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 400
        }
    }
    
    t0 = time.time()
    res = requests.post(url, json=payload, timeout=30)
    latency_ms = int((time.time() - t0) * 1000)
    
    if res.status_code != 200:
        raise RuntimeError(f"API Error {res.status_code}: {res.text}")
    
    data = res.json()
    candidates = data.get("candidates", [])
    if not candidates:
        return "", latency_ms
    text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    return text.strip(), latency_ms

def evaluate_case(case, output_text):
    failures = []
    
    # Check lines count <= 8
    lines = [l for l in output_text.split('\n') if l.strip()]
    if len(lines) > 8:
        failures.append(f"Output lines count {len(lines)} > 8")
        
    # Check must_include
    for inc in case.get("must_include", []):
        if inc.lower() not in output_text.lower():
            failures.append(f"Missing must_include: '{inc}'")
            
    # Check must_not_include
    for exc in case.get("must_not_include", []):
        if exc.lower() in output_text.lower():
            failures.append(f"Found must_not_include: '{exc}'")
            
    # Check Tier expectations
    expected_tier = case.get("expected_tier")
    if expected_tier in ["P1"]:
        if "p1" not in output_text.lower() and "khẩn cấp" not in output_text.lower():
            failures.append(f"Expected P1, but not detected in output")
    elif expected_tier == "REFUSE":
        if "không hỗ trợ" not in output_text.lower() and "không có thẩm quyền" not in output_text.lower() and "từ chối" not in output_text.lower():
            failures.append("Expected refusal, but bot did not refuse safely")
            
    is_pass = len(failures) == 0
    return is_pass, failures, len(lines)

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    golden_set_path = os.path.join(root_dir, "eval", "golden_set.json")
    if not os.path.exists(golden_set_path):
        golden_set_path = os.path.join(root_dir, "golden_set.json")
        
    with open(golden_set_path, "r", encoding="utf-8") as f:
        cases = json.load(f)
        
    api_key = get_api_key()
    print(f"🚀 Bắt đầu chạy kiểm thử thực tế trên {len(cases)} case bằng Google Gemini (gemini-2.5-flash)...")
    print("-" * 75)
    
    results = []
    pass_count = 0
    class1_3_total = 0
    class1_3_pass = 0
    
    for i, case in enumerate(cases, 1):
        cid = case["case_id"]
        group = case.get("group", "")
        tax = case.get("taxonomy_layer", "")
        input_text = case["input_text"]
        channel = case.get("channel", "kênh chung")
        
        prompt = f"Bối cảnh kênh: {channel}\nTình huống / Nội dung tin nhắn cần xử lý:\n{input_text}\n\nHãy xử lý và xuất bản tin tóm tắt phù hợp."
        
        try:
            output_text, latency_ms = call_gemini(prompt, api_key)
            is_pass, failures, line_count = evaluate_case(case, output_text)
        except Exception as e:
            output_text = f"ERROR: {str(e)}"
            latency_ms = 0
            is_pass = False
            failures = [f"Exception: {str(e)}"]
            line_count = 0
            
        is_class1_3 = ("①" in tax) or ("③" in tax)
        if is_class1_3:
            class1_3_total += 1
            if is_pass:
                class1_3_pass += 1
                
        if is_pass:
            pass_count += 1
            status_symbol = "✅ PASS"
        else:
            status_symbol = "❌ FAIL"
            
        print(f"[{i:02d}/22] {cid} ({group[:10]}) | {status_symbol} | {latency_ms}ms | Lines: {line_count}")
        if not is_pass:
            print(f"     Lỗi: {', '.join(failures)}")
            
        results.append({
            "case_id": cid,
            "group": group,
            "taxonomy_layer": tax,
            "input_text": input_text,
            "expected_tier": case.get("expected_tier"),
            "expected_behavior": case.get("expected_behavior"),
            "output_text": output_text,
            "latency_ms": latency_ms,
            "line_count": line_count,
            "is_pass": is_pass,
            "failures": failures,
            "quality_dimensions": case.get("quality_dimensions", [])
        })
        time.sleep(0.5) # gentle pacing
        
    pass_rate = (pass_count / len(cases)) * 100
    class1_3_rate = (class1_3_pass / class1_3_total) * 100 if class1_3_total > 0 else 100.0
    
    print("-" * 75)
    print(f"📊 KẾT QUẢ KIỂM THỬ THỰC TẾ LƯỢT 1:")
    print(f"- Tổng số case: {len(cases)}")
    print(f"- Số case ĐẠT (PASS): {pass_count} / {len(cases)} ({pass_rate:.1f}%)")
    print(f"- Lớp ① & ③ (An toàn & Grounding): {class1_3_pass} / {class1_3_total} ({class1_3_rate:.1f}%)")
    print(f"- Quality Bar yêu cầu: ≥ 85% tổng thể & 100% lớp ①/③.")
    if pass_rate >= 85.0 and class1_3_rate >= 100.0:
        print("🎉 KẾT QUẢ: ĐẠT CHUẨN QUALITY BAR!")
    else:
        print("⚠️ KẾT QUẢ: CHƯA ĐẠT QUALITY BAR, CẦN TINH CHỈNH PROMPT.")
        
    # Save raw results JSON
    res_json_path = os.path.join(root_dir, "eval", "eval_results_run1.json")
    with open(res_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": "gemini-2.5-flash",
            "total_cases": len(cases),
            "passed_cases": pass_count,
            "pass_rate_percent": round(pass_rate, 1),
            "class1_3_pass_rate_percent": round(class1_3_rate, 1),
            "details": results
        }, f, ensure_ascii=False, indent=2)
    print(f"📁 Đã lưu trace chi tiết tại: {res_json_path}")
    
    # Save Markdown Report
    res_md_path = os.path.join(root_dir, "eval", "eval_report_run1.md")
    with open(res_md_path, "w", encoding="utf-8") as f:
        f.write("# 📋 BÁO CÁO KẾT QUẢ CHẠY KIỂM THỬ THỰC TẾ LƯỢT 1 (CP3)\n\n")
        f.write(f"- **Thời gian chạy:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **Mô hình AI thực tế:** `gemini-2.5-flash` (Google AI Studio REST API)\n")
        f.write(f"- **Bộ dữ liệu kiểm thử:** [`eval/golden_set.json`](golden_set.json) (22 case, 15 case từ chatlog thật)\n")
        f.write(f"- **Tỷ lệ vượt qua tổng thể:** **{pass_count}/22 ({pass_rate:.1f}%)**\n")
        f.write(f"- **Tỷ lệ lớp ① & ③ (Bắt buộc 100%):** **{class1_3_pass}/{class1_3_total} ({class1_3_rate:.1f}%)**\n")
        f.write(f"- **Đánh giá theo Quality Bar:** {'✅ **ĐẠT (PASS)**' if pass_rate >= 85.0 and class1_3_rate >= 100.0 else '⚠️ **CHƯA ĐẠT**'}\n\n")
        f.write("## Chi Tiết Từng Ca Kiểm Thử (22 Case)\n\n")
        f.write("| STT | Mã Case | Nhóm | Kỳ vọng | Kết quả Model AI sinh ra | Số dòng | Độ trễ | Trạng thái |\n")
        f.write("|:---:|:---:|---|:---:|---|:---:|:---:|:---:|\n")
        for i, r in enumerate(results, 1):
            out_preview = r["output_text"].replace("\n", " ").strip()
            if len(out_preview) > 90:
                out_preview = out_preview[:87] + "..."
            status = "✅ PASS" if r["is_pass"] else f"❌ FAIL ({'; '.join(r['failures'])})"
            f.write(f"| {i} | `{r['case_id']}` | {r['group']} | {r['expected_tier']} | {out_preview} | {r['line_count']} | {r['latency_ms']}ms | {status} |\n")
            
    print(f"📄 Đã lập báo cáo kiểm thử tại: {res_md_path}")

if __name__ == "__main__":
    main()
