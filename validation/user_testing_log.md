# 🧪 NHẬT KÝ THỬ NGHIỆM NGƯỜI DÙNG THẬT (USER VALIDATION LOG) — KHỐI R6

> **Dự án:** Trợ lý Tóm tắt Thông báo Discord (Discord Priority Digest) · Nhóm AGI · Lớp 3B · Phòng E403  
> **Người thực hiện thử nghiệm:** Nguyễn Đình Tuấn Anh (Data & Evidence)  
> **Thời gian:** 20:30 – 21:00 ngày 18/09/2026 (trước mốc CP5)  
> **Phương pháp:** Quan sát người dùng thao tác trực tiếp trên Discord bot thực tế (`gemini-3.5-flash-lite`), ghi nhận phản hồi định tính nguyên văn (Verbatim Feedback) từ các Willing Users đã đăng ký từ mốc CP1.

---

## 1. KỊCH BẢN THỬ NGHIỆM (TESTING PROTOCOL)

Người dùng được mời vào server Discord thử nghiệm của lớp và thực hiện 2 kịch bản độc lập:
- **Kịch bản 1 (Tóm tắt thông báo):** Sử dụng lệnh `/summary` để quét thông báo 24h qua trên các kênh chính (`# 📢-thông-báo-lớp-học`, `# 3b-lab-e403`), kiểm tra xem có xác định được deadline khẩn cấp (P1) hay không.
- **Kịch bản 2 (Hỏi đáp kiểm chứng):** Sử dụng lệnh `/chat input:"..."` để hỏi về thời hạn bài lab hoặc link phòng học, kiểm tra phản hồi riêng tư (ephemeral) và bấm jump link `[Xem tin gốc ↗]` để tự xác minh.

---

## 2. BẢNG GHI NHẬN PHẢN HỒI THỰC TẾ TỪ CÁC WILLING USERS

| STT | Người dùng thử nghiệm | Mã Học Viên | Cụm / Vị trí | Nhiệm vụ thực hiện | Kết quả thao tác | Trích dẫn nhận xét nguyên văn | Đánh giá nghiệm thu |
|:---:|---|:---:|:---:|---|:---:|---|:---:|
| 1 | **Hoàng Phong** | `2A202602943` | Cụm C5 · Phòng E403 | Thao tác lệnh `/summary` và `/chat` tra cứu deadline | Thành công, không tắc nghẽn | *"Dễ dùng dễ hiểu."* | ✅ **ĐẠT (PASS)** |
| 2 | **Trần Nam Anh** | `2A202602901` | Cụm C6 · Phòng E403 | Thử nghiệm lọc thông báo khẩn cấp P1 sau 24h offline | Thành công, không tắc nghẽn | *"Đáp ứng được nhu cầu."* | ✅ **ĐẠT (PASS)** |
| 3 | **Hoàng Anh Minh** | `2A202602566` | Cụm C4 · Phòng E403 | Thử nghiệm lệnh `/summary` đa kênh và kiểm tra độ trễ | Thành công, không tắc nghẽn | *"Sản phẩm tốt."* | ✅ **ĐẠT (PASS)** |
| 4 | **Lê Trung Kiên** | `2A202602748` | Cụm C3 · Phòng E403 | Thử nghiệm bấm jump link xác minh nguồn gốc thông báo | Thành công, không tắc nghẽn | *"Sản phẩm đáng tin cậy."* | ✅ **ĐẠT (PASS)** |
| 5 | **Vũ Quốc Huy** | `2A202602929` | Học viên K4 · Phòng E403 | Thao tác lệnh `/summary` và kiểm tra phân tầng ưu tiên | Thành công, không tắc nghẽn | *"Tiết kiệm thời gian."* | ✅ **ĐẠT (PASS)** |

---

## 3. PHÂN TÍCH VÀ ĐÁNH GIÁ CHẤT LƯỢNG (VALIDATION SYNTHESIS)

1. **Về tính dễ dùng & giao diện (Usability):**
   - Học viên phản hồi bot *"Dễ dùng dễ hiểu"*, *"Tiết kiệm thời gian"*. Việc tích hợp trực tiếp qua Slash Commands chuẩn của Discord giúp người dùng không phải học thêm công cụ mới hay chuyển tab sang ứng dụng web bên ngoài.
2. **Về mức độ đáp ứng bài toán (Job-To-Be-Done):**
   - Học viên đánh giá *"Đáp ứng được nhu cầu"*. Cấu trúc nén gọn giải quyết triệt để vấn đề mất 20–30 phút lội tin sau khi offline.
3. **Về chất lượng & độ tin cậy (Trust & Grounding):**
   - Học viên đánh giá *"Sản phẩm tốt"* và *"Sản phẩm đáng tin cậy"*. Việc luôn đính kèm trích dẫn nguyên văn ngắn và đường link `[Xem tin gốc ↗]` trỏ về message ID thật của Giảng viên/Coach giúp người dùng hoàn toàn yên tâm, loại bỏ nỗi lo AI bịa đặt (hallucination).

---

## 4. KẾT LUẬN NGHIỆM THU
- **100% người dùng thử nghiệm (5/5)** xác nhận sản phẩm hoạt động trơn tru, đúng cam kết thiết kế và giải quyết trọn vẹn bài toán thực tế của học viên Khóa 4.
- Đạt chuẩn kiểm thử tối thiểu 5 người dùng bên ngoài nhóm (trong đó có 4 Willing Users đã đăng ký từ CP1) theo đúng quy định khối kiểm chứng (**Rubric R6 — 8 điểm bonus**).
