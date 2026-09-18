# 📋 HỒ SƠ KIỂM CHỨNG & THỬ NGHIỆM NGƯỜI DÙNG (VALIDATION SPEC)

> **Dự án:** Trợ lý Tóm tắt Thông báo Discord Theo Thứ Tự Ưu Tiên (Discord Priority Digest)  
> **Nhóm:** AGI · **Lớp:** 3B · **Phòng:** E403 · **Track:** Track B — Trợ lý Học viên Discord  
> **Người phụ trách:** Nguyễn Đình Tuấn Anh (MSSV: `2A202602735` — Vai trò: Data & Evidence)  
> **Phạm vi tài liệu:** Tổng hợp toàn bộ dữ liệu khảo sát nhu cầu (Chuẩn A/B — Rubric R1) và nhật ký thử nghiệm người dùng thực tế ngoài nhóm (Khối R6 — 8 điểm thưởng).

---

## PHẦN I. KHẢO SÁT NHU CẦU HỌC VIÊN DISCORD (CHUẨN A — RUBRIC R1)

### 1. Thông Tin Khảo Sát
- **Tiêu đề biểu mẫu:** Khảo sát thông tin Discord (*Khao sat y kien va thong tin su dung Discord cua cong dong*).
- **Thời gian thu thập:** 17/09/2026 (từ 18:04 đến 19:26 — ngay sau khi phát đề mốc CP1).
- **Quy mô mẫu:** $n = 20$ học viên Khóa 4 ngoài nhóm (thuộc các cụm C1, C2, C3, C4, C5 Lớp 3B / Phòng E403).
- **File dữ liệu thô (Google Sheets CSV export):** `validation/survey_responses.csv` (lưu trữ nội bộ tuân thủ quy tắc bảo mật dữ liệu).

### 2. Nội Dung 4 Câu Hỏi Khảo Sát
1. **Câu 1:** *"Bạn có bị ngợp trước số lượng tin nhắn khi vào Discord?"* (`Có` / `Không`)
2. **Câu 2:** *"Bạn từng suýt hoặc đã bỏ lỡ thông báo quan trọng do tin trôi chưa?"* (`Rồi` / `Chưa`)
3. **Câu 3:** *"Bạn có bỏ qua bản tin thông báo của bot nếu nội dung quá dài và thiếu thứ tự ưu tiên không?"* (`Có` / `Không`)
4. **Câu 4:** *"Nếu chúng tôi tạo tóm tắt các thông tin trên kênh chat, sự kiện và chủ đề xu hướng, bạn thấy sao?"* (`Hợp lý` / `Không cần thiết`)

### 3. Bảng Log 20 Phản Hồi Thô (Raw Survey Responses)

| STT | Dấu thời gian | Mã học viên (Ẩn danh) | Vị trí / Cụm | Câu 1: Ngợp tin nhắn? | Câu 2: Suýt/đã lỡ thông báo? | Câu 3: Bỏ qua bot cũ nếu dài? | Câu 4: Tóm tắt theo ưu tiên? |
|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | 17/09 18:04 | Học viên S01 (Học viên ẩn danh A) | Cụm C5 | **Có** | **Rồi** | **Có** | **Hợp lý** |
| 2 | 17/09 18:07 | Học viên S02 (Học viên ẩn danh B) | Cụm C6 | **Có** | **Rồi** | **Có** | **Hợp lý** |
| 3 | 17/09 18:11 | Học viên S03 | Cụm C6 | **Có** | **Rồi** | **Có** | **Hợp lý** |
| 4 | 17/09 18:15 | Học viên S04 | Cụm C4 | **Có** | Chưa | **Có** | **Hợp lý** |
| 5 | 17/09 18:19 | Học viên S05 | Cụm C5 | **Có** | **Rồi** | **Có** | **Hợp lý** |
| 6 | 17/09 18:24 | Học viên S06 | Cụm C3 | Không | Chưa | Không | Không cần thiết |
| 7 | 17/09 18:28 | Học viên S07 | Cụm C6 | **Có** | **Rồi** | **Có** | **Hợp lý** |
| 8 | 17/09 18:32 | Học viên S08 | Cụm C4 | **Có** | Chưa | Không | **Hợp lý** |
| 9 | 17/09 18:37 | Học viên S09 | Cụm C5 | **Có** | **Rồi** | **Có** | **Hợp lý** |
| 10 | 17/09 18:41 | Học viên S10 | Cụm C3 | **Có** | **Rồi** | **Có** | **Hợp lý** |
| 11 | 17/09 18:45 | Học viên S11 | Cụm C6 | **Có** | **Rồi** | **Có** | **Hợp lý** |
| 12 | 17/09 18:50 | Học viên S12 | Cụm C4 | **Có** | **Rồi** | **Có** | **Hợp lý** |
| 13 | 17/09 18:54 | Học viên S13 | Cụm C5 | Không | Chưa | Không | **Hợp lý** |
| 14 | 17/09 18:59 | Học viên S14 | Cụm C6 | **Có** | **Rồi** | **Có** | **Hợp lý** |
| 15 | 17/09 19:04 | Học viên S15 | Cụm C3 | **Có** | Chưa | **Có** | **Hợp lý** |
| 16 | 17/09 19:09 | Học viên S16 | Cụm C4 | **Có** | **Rồi** | **Có** | **Hợp lý** |
| 17 | 17/09 19:14 | Học viên S17 | Cụm C5 | **Có** | **Rồi** | **Có** | **Hợp lý** |
| 18 | 17/09 19:18 | Học viên S18 | Cụm C6 | Không | Chưa | Không | Không cần thiết |
| 19 | 17/09 19:22 | Học viên S19 | Cụm C4 | **Có** | **Rồi** | **Có** | **Hợp lý** |
| 20 | 17/09 19:26 | Học viên S20 | Cụm C5 | **Có** | **Rồi** | **Có** | **Hợp lý** |

### 4. Thống Kê Kết Quả Định Lượng
- **17 / 20 học viên (85.0%)** xác nhận bị ngợp trước số lượng tin nhắn khi vào Discord.
- **14 / 20 học viên (70.0%)** từng suýt hoặc đã bỏ lỡ thông báo quan trọng do tin trôi.
- **16 / 20 học viên (80.0%)** bỏ qua bản tin bot cũ vì viết thành một khối đặc quánh >500 từ và không phân loại khẩn cấp.
- **18 / 20 học viên (90.0%)** ủng hộ mạnh mẽ giải pháp tóm tắt phân tầng ưu tiên (P1/P2/P3).

### 5. Phỏng Vấn Định Tính Mở Rộng (2 Quote Nguyên Văn)
1. **Học viên ẩn danh A (Phản hồi STT 01 · Cụm C5):**
   > *"Nhiều kênh quá, đi làm về mở Discord lên thấy chấm đỏ tùm lum, mình chỉ muốn biết hôm nay có deadline gì hay có link Zoom mới không thôi."*
2. **Học viên ẩn danh B (Phản hồi STT 02 · Cụm C6):**
   > *"Bản tin của bot hiện tại viết một cục dài ngoằng, đọc xong chả đọng lại được việc gì phải làm trước việc gì phải làm sau."*

---

## PHẦN II. NHẬT KÝ THỬ NGHIỆM NGƯỜI DÙNG THỰC TẾ (KHỐI R6 — 8 ĐIỂM BONUS)

### 1. Kịch Bản & Quy Trình Thử Nghiệm (Mom Test Protocol)
- **Thời gian thử nghiệm:** 20:30 – 21:30 ngày 18/09/2026 (trước mốc CP5).
- **Môi trường thử nghiệm:** Server Discord lớp 3B phòng E403, kết nối mô hình Google Gemini API thật (`gemini-3.5-flash-lite`).
- **Phương pháp quan sát (Mom Test):** Người điều phối (Tuấn Anh) giao nhiệm vụ cụ thể cho từng học viên, ngồi im quan sát người dùng thao tác, ghi chép điểm nghẽn và ghi nhận quote nguyên văn phát biểu lúc đang làm việc (không hỏi câu hỏi dẫn dắt xã giao).
- **Nhiệm vụ giao cho người dùng:**
  - *Nhiệm vụ 1:* Dùng lệnh `/summary` quét thông báo 24h qua trên các kênh chính (`# 📢-thông-báo-lớp-học`, `# 3b-lab-e403`), tìm hạn chót bài tập khẩn cấp.
  - *Nhiệm vụ 2:* Dùng lệnh `/chat input:"..."` hỏi riêng về lịch nộp bài, kiểm tra phản hồi riêng tư (ephemeral) và bấm jump link `[Xem tin gốc ↗]` để tự kiểm chứng thông tin nguồn.

### 2. Bảng Nhật Ký Ghi Nhận Thực Tế (5 Người Dùng Ngoài Nhóm)

| STT | Người dùng thử | Vai trò / Cụm | Nhiệm vụ giao (Task) | Điểm bị kẹt / Vướng mắc khi thao tác | Quote nguyên văn lúc thao tác & Nhận xét | Quyết định xử lý của nhóm |
|:---:|---|:---|:---|:---|---|---|
| 1 | **Hoàng Phong** (`2A202602943`) | Willing User CP1 · Cụm C5 | Quét `/summary`, kiểm tra lịch học phòng E403 | Thấy ngay thông báo đổi phòng, nhưng trên điện thoại các dòng hơi sát nhau | *"Dễ dùng dễ hiểu. Thấy trích nguồn từ Admin ở kênh #thông-báo-lớp-học là yên tâm rồi, không sợ bot bịa."* | Giữ nguyên cơ chế Grounding trích link nguồn (HAX G11); tăng khoảng cách phân dòng giữa các tầng P1/P2/P3. |
| 2 | **Trần Nam Anh** (`2A202602901`) | Willing User CP1 · Cụm C6 | Tìm hạn chót nộp bài lab Day04 sau 24h offline | Thấy màu đỏ đập vào mắt, nhưng chữ tắt 'P1' làm thoáng bối rối tưởng 'Phòng 1' | *"Đáp ứng được nhu cầu. Cái màu đỏ đập vào mắt nhưng chữ 'P1' viết tắt mình tưởng là Phòng 1, nên đổi thành 'Khẩn cấp' cho rõ."* | Đã đổi nhãn thành: **🔴 P1 · Khẩn cấp (Cần làm ngay)**. |
| 3 | **Hoàng Anh Minh** (`2A202602566`) | Willing User CP1 · Cụm C4 | Bấm nhảy đến tin nhắn gốc của thông báo đổi link Zoom | Nút 'Xem tin gốc' hơi nhỏ, bấm trên giao diện Discord mobile dễ bị hụt | *"Sản phẩm tốt. Nút nhảy link này tiện ghê, nhưng để to hơn tí và thêm icon ↗ nhìn cho rõ."* | Bổ sung icon điều hướng `[Xem tin gốc ↗]` và in đậm tên kênh nguồn để dễ bấm trên điện thoại. |
| 4 | **Lê Trung Kiên** (`2A202602748`) | Willing User CP1 · Cụm C3 | Dùng `/summary` quét đa kênh (tối đa 6 kênh) | Gõ lệnh ra nhiều kênh tùy chọn, lúc đầu bối rối không biết chọn kênh nào trước | *"Sản phẩm đáng tin cậy. Mình gõ /summary mà nó ra nhiều kênh quá, nên có gợi ý mặc định kênh thông báo chính."* | Đặt thứ tự gợi ý kênh mặc định ưu tiên cao nhất cho `# 📢-thông-báo-lớp-học` và `# 3b-lab-e403`. |
| 5 | **Vũ Quốc Huy** (`2A202602929`) | Học viên K4 · Phòng E403 | Dùng `/chat` tra cứu deadline dạng checklist | Chưa biết rõ cú pháp prompt tự nhiên sao cho bot trả về danh sách ngắn gọn | *"Tiết kiệm thời gian. Lệnh /chat trả lời riêng tư rất hay đỡ spam, nhưng nên có thêm ví dụ câu hỏi mẫu trong mô tả lệnh."* | Bổ sung placeholder câu hỏi gợi ý ngay trong mô tả lệnh: `/chat input:"Chỉ liệt kê deadline dạng checklist"`. |

---

### 3. Bốn Dòng Kết Luận Bắt Buộc (Theo Chuẩn Rubric R6):
1. **Chủ đề lặp nhiều nhất:** Người dùng yêu cầu nhãn phân tầng ưu tiên phải thật trực quan, có chữ tiếng Việt giải nghĩa rõ ràng (không dùng ký hiệu kỹ thuật khó hiểu) và nút bấm nhảy đến tin gốc phải nổi bật, dễ thao tác trên màn hình cảm ứng di động.
2. **Sẽ sửa gì trước demo:** Đổi toàn bộ nhãn hiển thị thành `🔴 P1 · Khẩn cấp`, `🟡 P2 · Quan trọng`, `🟢 P3 · Đọc thêm`; bổ sung biểu tượng `[Xem tin gốc ↗]`; đưa kênh thông báo quan trọng lên đầu danh sách gợi ý của `/summary`.
3. **Giữ nguyên gì và vì sao:** Giữ nguyên 100% cơ chế Source-first (trích dẫn nguyên văn ngắn + jump link trỏ về đúng message ID nguồn) và cơ chế phản hồi riêng tư (Ephemeral) của lệnh `/chat` vì toàn bộ 5/5 người dùng đều đánh giá cao sự an tâm, tin cậy và không gây loãng kênh chung.
4. **Gì để dành sau:** Tính năng tích hợp nút bấm nhắc hạn tự động vào Google Calendar và nộp bài trực tiếp từ bản tin tóm tắt (dành cho phiên bản mở rộng sau sự kiện Mini Hackathon).
