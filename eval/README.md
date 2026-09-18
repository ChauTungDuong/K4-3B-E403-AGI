# Đánh giá định lượng

`golden_set.json` có 22 case: 8 case khó (2 case cho mỗi lớp taxonomy), 10 case thường và 4 case hiếm. Trong đó 18 case có nhãn `real_chatlog` cùng mã tin nguồn; dữ liệu Discord gốc nằm trong data pack riêng tư và không được commit.

Chạy toàn bộ bằng đúng môi trường của bot:

```powershell
codebase\bot-discord\.venv\Scripts\python.exe eval\run_eval.py
```

Smoke test một hoặc vài case:

```powershell
codebase\bot-discord\.venv\Scripts\python.exe eval\run_eval.py --case KB-01 --case KB-05
```

Mỗi lượt chạy sinh ba loại bằng chứng:

- `runs/run_*_ai_trace.jsonl`: prompt đầu vào, phản hồi thô, retry, latency và token usage từng lời gọi.
- `runs/run_*_results.json` cùng `latest_results.json`: assertion từng case và thống kê lỗi máy đọc được.
- `run_results.md`: số lần chưa đạt, vị trí sai, phân tích nguyên nhân và ma trận User Input Grid.
- `result_table.md`: bảng dễ đọc gồm nhãn mong đợi, nhãn AI, câu trả lời AI và PASS/FAIL của đủ 22 case.

Chỉ tạo lại bảng Markdown từ kết quả gần nhất, không gọi Gemini:

```powershell
codebase\bot-discord\.venv\Scripts\python.exe eval\run_eval.py --render-only
```

Runner trả exit code `0` khi mọi case đạt, `1` khi có case chưa đạt, `2` khi dataset/cấu hình không hợp lệ. Báo cáo ba mức `dung_duoc`, `sua_duoc`, `khong_chap_nhan_duoc` chỉ là lượt chấm thô; hai thành viên vẫn cần chấm độc lập cùng 5 output để kiểm tra độ rõ của định nghĩa đạt.

Hai thành viên điền độc lập `human_review_5.json` bằng một trong ba nhãn trên, sau đó điền `agree=true/false`. Nếu có từ 1/5 case lệch trở lên (≥20%), cần viết lại định nghĩa đạt trước khi dùng chấm tay cho tập lớn hơn. Không điền sẵn tên hoặc kết quả khi chưa có hai người chấm thật.
