# Canvas 7 Dòng — CP1

1. **Track + đề:** Track B — Trợ lý Học viên Discord (B2): Tóm tắt thông báo trên các kênh theo thứ tự ưu tiên trong 24h/khoảng thời gian tùy chọn (Discord Priority Digest).
2. **Job executor:** Học viên Khóa 4 vừa đăng nhập vào Discord sau thời gian bận/offline, cần cập nhật nhanh các thông báo quan trọng.
3. **Pain một câu:** Học viên mở Discord sau 24h offline thì bị ngợp trước hàng chục kênh và hàng trăm tin nhắn mới, bản tin bot cũ dài dòng không phân loại khẩn cấp, dẫn đến mất 20–30 phút lội tin hoặc bỏ lỡ deadline/link Zoom bị trừ điểm.
4. **1–2 bằng chứng đầu:**
   - Mining dữ liệu: Trong discord-pack có 1.092 tin/3 ngày; bản tin hiện tại của bot (k4_daily_reports.md) là văn bản đặc quánh >500 từ, không xếp thứ tự ưu tiên và dính lỗi cắt cụt câu.
   - Khảo sát thực tế: 17/20 học viên ngoài nhóm (85%) xác nhận bị quá tải thông báo Discord và từng bỏ sót tin nhắn quan trọng.
5. **Lát cắt MỘT CÂU:** Một học viên · yêu cầu tóm tắt thông báo Discord trong 24h qua · AI quyết định phân loại và xếp hạng thông báo theo 3 tầng ưu tiên (P1 Khẩn cấp / P2 Quan trọng / P3 Đọc thêm) kèm trích xuất deadline · học viên nhận được bản tóm tắt có cấu trúc ≤8 dòng trong 3 giây kèm link nhảy đến tin nhắn gốc.
6. **Automation & Willing users:**
   - Automation: Augment / Conditional — AI tóm tắt và phân loại hỗ trợ học viên, bắt buộc dẫn link tin nhắn gốc để tự xác minh; không tự ý xóa tin nhắn.
   - Willing users:
     1. Trần Nam Anh — MSSV: 2A202602901
     2. Hoàng Anh Minh — MSSV: 2A202602566
     3. Hoàng Phong — MSSV: 2A202602943
     4. Lê Trung Kiên — MSSV: 2A202602748
7. **Phân công có tên:**
   - Châu Tùng Dương: Product Lead — Chốt Canvas CP1, viết spec.md, nộp form checkpoint.
   - Nguyễn Đình Tuấn Anh: Data & Evidence — Khai thác lỗi bản tin cũ trong data pack, khảo sát, quản lý willing users.
   - Đỗ Mạnh Nghĩa: AI & Evaluation — Thiết kế prompt phân loại ưu tiên, 4 lớp chỗ khó, xây dựng 20 ca kiểm thử trong eval/.
   - Nguyễn Ngọc Tuyền: UX & Prototype — Thiết kế giao diện tin nhắn tóm tắt phân cấp P1/P2/P3, lập trình prototype.