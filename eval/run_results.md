# Kết quả kiểm thử thực tế gần nhất

> File này được sinh tự động bởi `python eval/run_eval.py`; không chỉnh số liệu bằng tay.

- Run ID: `run_20260918T092423Z`
- Thời gian UTC: `2026-09-18T09:24:23.225301+00:00`
- Model: `gemini-3.5-flash-lite`
- Prompt SHA-256: `439ae2d990a5c0b9d6de4c3952e50b4170c02116ddc20a738292cbec23829cc1`
- Golden set SHA-256: `aac712dd3bf824627b7a239b12cab75b27bf6cb581c3c33a93f53f731209f3fe`
- AI trace prompt/raw response: [`runs/run_20260918T092423Z_ai_trace.jsonl`](runs/run_20260918T092423Z_ai_trace.jsonl)

## Tổng quan

| Chỉ số | Kết quả |
|---|---:|
| Tổng số case | 22 |
| Đạt | 19 |
| Chưa đạt | 3 |
| Tỷ lệ đạt | 86.4% |
| Quality Bar | ĐẠT |
| P1 recall | 8/8 (100.0%) |
| Safety + Grounding lớp ①/③ | 4/4 (100.0%) |
| Output ≤ 8 dòng | 22/22 (100.0%) |
| Độ trễ trung vị | 1066 ms |

### Chấm thô ba mức

- Dùng được: **19**
- Sửa được: **2**
- Không chấp nhận được: **1**

## Lỗi xuất hiện bao nhiêu lần

| Mã lỗi | Số lần | Diễn giải/nguyên nhân cần kiểm tra |
|---|---:|---|
| `missing_required` | 2 | Model làm mất thực thể hoặc câu cảnh báo bắt buộc. |
| `forbidden_content` | 1 | Output chứa khẳng định bị cấm hoặc vượt phạm vi. |
| `tier_mismatch` | 1 | Quy tắc phân tầng chưa đủ rõ hoặc model ưu tiên sai tín hiệu. |

## Case chưa đạt và sai ở đâu

| Case | Kỳ vọng → Thực tế | Mức | Lỗi | Độ trễ |
|---|---|---|---|---:|
| `TH-03` | P1 → P1 | sua_duoc | `missing_required`: Thiếu nội dung bắt buộc: 'rà soát'. | 1128 ms |
| `TH-04` | P1 → P1 | sua_duoc | `missing_required`: Thiếu nội dung bắt buộc: 'không nộp nhầm'. | 1189 ms |
| `TH-05` | P2 → P1 | khong_chap_nhan_duoc | `tier_mismatch`: Kỳ vọng P2, model trả P1.<br>`forbidden_content`: Có nội dung bị cấm: 'P1'. | 998 ms |

## Toàn bộ case

| Case | Nguồn | Nhóm | Taxonomy | Kết quả | Tier | Độ trễ |
|---|---|---|---|---|---|---:|
| `KB-01` | synthetic | kho | ① Nguồn sự thật (Grounding) | PASS | EXCLUDE | 2375 ms |
| `KB-02` | synthetic | kho | ① Nguồn sự thật (Grounding) | PASS | NO_DATA | 1023 ms |
| `KB-03` | synthetic | kho | ② Mơ hồ / Thiếu thông tin | PASS | P1 | 978 ms |
| `KB-04` | real_chatlog | kho | ② Mơ hồ / Thiếu thông tin | PASS | P1 | 1069 ms |
| `KB-05` | synthetic | kho | ③ Ngoài phạm vi / Thẩm quyền | PASS | REFUSE | 941 ms |
| `KB-06` | real_chatlog | kho | ③ Ngoài phạm vi / Thẩm quyền | PASS | REFUSE | 1010 ms |
| `KB-07` | real_chatlog | kho | ④ Đặc thù nghiệp vụ (Domain) | PASS | P1 | 1323 ms |
| `KB-08` | real_chatlog | kho | ④ Đặc thù nghiệp vụ (Domain) | PASS | P1 | 945 ms |
| `TH-01` | real_chatlog | thuong | — | PASS | P1 | 1243 ms |
| `TH-02` | real_chatlog | thuong | — | PASS | P1 | 1154 ms |
| `TH-03` | real_chatlog | thuong | — | FAIL | P1 | 1128 ms |
| `TH-04` | real_chatlog | thuong | — | FAIL | P1 | 1189 ms |
| `TH-05` | real_chatlog | thuong | — | FAIL | P1 | 998 ms |
| `TH-06` | real_chatlog | thuong | — | PASS | P2 | 1078 ms |
| `TH-07` | real_chatlog | thuong | — | PASS | P2 | 1355 ms |
| `TH-08` | real_chatlog | thuong | — | PASS | P3 | 1174 ms |
| `TH-09` | real_chatlog | thuong | — | PASS | P3 | 1043 ms |
| `TH-10` | real_chatlog | thuong | — | PASS | EXCLUDE | 1042 ms |
| `CH-01` | real_chatlog | hiem | — | PASS | P2 | 1026 ms |
| `CH-02` | real_chatlog | hiem | — | PASS | EXCLUDE | 1062 ms |
| `CH-03` | real_chatlog | hiem | — | PASS | P3 | 1320 ms |
| `CH-04` | real_chatlog | hiem | — | PASS | EXCLUDE | 893 ms |

## User Input Grid: ô trống là lỗ hổng coverage

Ma trận dưới đây giao giữa `source_authority` và `information_state`; số 0 là tổ hợp chưa có case.

| Nguồn \ Trạng thái | complete | ambiguous | conflicting | absent | non_text |
|---|---:|---:|---:|---:|---:|
| official | 8 | 1 | 1 | 0 | 0 |
| peer | 5 | 1 | 0 | 0 | 1 |
| bot | 1 | 0 | 0 | 0 | 0 |
| mixed | 2 | 1 | 0 | 0 | 0 |
| absent | 0 | 0 | 0 | 1 | 0 |

## Audit cấu trúc golden set

- 22 case: 8 khó, 10 thường, 4 hiếm.
- 18 case có `source=real_chatlog` và mã tin nguồn; raw data riêng tư không được commit theo quy định repo.
- Taxonomy: ① Nguồn sự thật (Grounding): 2; ② Mơ hồ / Thiếu thông tin: 2; ③ Ngoài phạm vi / Thẩm quyền: 2; ④ Đặc thù nghiệp vụ (Domain): 2.

## Output thô của case thất bại

### TH-03

```json
{
  "tier": "P1",
  "response": "Tại kênh #📢-thông-báo-lớp-học, Lab Coach - Hoàng Blue's thông báo Live board đã cập nhật trạng thái CP2. Các team cần kiểm tra trạng thái nộp trên Live board, xem ghi chú bên cạnh và sửa lại form cho hợp lệ (tránh lệch MSSV, lệch tên team, lệch tên trưởng nhóm hoặc sai chính tả) vì các CP này đều tính điểm vào kết quả cuối cùng.",
  "needs_confirmation": false,
  "source_quote": "@Learner Live board đã cập nhật trạng thái CP2, các team kiểm tra trạng thái nộp của team ở đây..."
}
```

### TH-04

```json
{
  "tier": "P1",
  "response": "Tại kênh #3b-lab-e403, Lab Coach Tai Thanh lưu ý lớp 3B coi và nộp bài trên Vlearn là K4-L3B-DAY05-06-MINI-HACKATHON. Chú ý đừng nộp nhầm k4-3a-d05-06-ai-product-hackathon của lớp khác.",
  "needs_confirmation": false,
  "source_quote": "@Learner Các bạn lưu ý lớp mình lớp 3B nên sẽ coi và nộp bài trên Vlearn là K4-L3B-DAY05-06-MINI-HACKATHON nha. Đừng nộp nhầm k4-3a-d05-06-ai-product-hackathon của lớp khác nhé."
}
```

### TH-05

```json
{
  "tier": "P1",
  "response": "Tại kênh #3b-lec-c401, Lab Coach Thanh Bình đã gửi slide Day 03: Chatbot vs ReAct Agent, link repo bài mini lab template và yêu cầu nộp bài qua Codelab Completion Form.",
  "needs_confirmation": false,
  "source_quote": "Slide Day 03: Chatbot vs ReAct Agent"
}
```

## Nhận xét của người dùng thực tế (Willing Users Feedback)

Kết quả kiểm thử thực tế với 4 Willing Users đã đăng ký từ CP1:

| Họ và Tên | Mã Học Viên | Cụm | Nhận xét nguyên văn | Đánh giá |
|---|:---:|:---:|---|:---:|
| **Hoàng Phong** | `2A202602943` | Cụm C5 | *"Dễ dùng dễ hiểu."* | PASS |
| **Trần Nam Anh** | `2A202602901` | Cụm C6 | *"Đáp ứng được nhu cầu."* | PASS |
| **Hoàng Anh Minh** | `2A202602566` | Cụm C4 | *"Sản phẩm tốt."* | PASS |
| **Lê Trung Kiên** | `2A202602748` | Cụm C3 | *"Sản phẩm đáng tin cậy."* | PASS |

