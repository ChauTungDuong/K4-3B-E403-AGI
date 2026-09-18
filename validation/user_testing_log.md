# 🧪 NHẬT KÝ THỬ NGHIỆM NGƯỜI DÙNG NGOÀI NHÓM (USER TESTING LOG — KHỐI R6 BONUS)

- **Sản phẩm thử nghiệm:** Discord Priority Digest & Notification Summarizer (`codebase/web_prototype/` & Live Bot Discord `/summary`, `/chat`)
- **Thời gian thực hiện:** Tối 18/09/2026 (trước mốc CP5)
- **Người điều phối:** Nguyễn Đình Tuấn Anh (Vai trò: Data & Evidence — Nhóm AGI)
- **Phương pháp thực hiện:** Phỏng vấn thực nghiệm độc lập theo nguyên tắc **The Mom Test** (Giao nhiệm vụ thực tế cụ thể, người điều phối giữ im lặng tuyệt đối quan sát thao tác, không giải thích trước, ghi chép chân thực từng điểm nghẽn và phát biểu nguyên văn).

---

## 1. BẢNG GHI NHẬN 5 LƯỢT THỬ NGHIỆM ĐỘC LẬP

| STT | Người dùng thử | Vai trò / Cụm | Nhiệm vụ giao (Task) | Điểm bị kẹt / Vướng mắc | Quote nguyên văn phát biểu | Quyết định xử lý của nhóm |
|:---:|:---|:---|:---|:---|:---|:---|
| 1 | **Trần Nam Anh**<br>(`2A202602901`) | Willing User CP1<br>Cụm C6 | Giả sử vừa offline 24h, mở bot tìm hạn chót nộp Daily Standup trong ngày. | Lúc đầu tìm trong danh sách P2, không nhận ra ngay tầng P1 màu đỏ ở trên cùng do ký hiệu viết tắt. | *"Cái màu đỏ đập vào mắt nhưng chữ 'P1' viết tắt mình tưởng là Phòng 1, nên đổi thành 'Khẩn cấp' cho rõ."* | Đã đổi nhãn hiển thị trực quan thành: **🔴 P1 · Khẩn cấp (Cần làm ngay)**. |
| 2 | **Hoàng Anh Minh**<br>(`2A202602566`) | Willing User CP1<br>Cụm C4 | Tìm thông báo đổi link Zoom Webinar và nhảy đến tin nhắn nguồn để kiểm tra. | Thấy link tin gốc nhưng nút bấm trên điện thoại hơi nhỏ, dễ bấm trượt. | *"Nút nhảy link này rất tiện, nhưng để to hơn tí và thêm icon ↗ nhìn cho dễ bấm trên điện thoại."* | Tăng padding cho vùng bấm link và chuẩn hóa cú pháp `[Xem tin gốc ↗]`. |
| 3 | **Hoàng Phong**<br>(`2A202602943`) | Willing User CP1<br>Cụm C5 | Kiểm tra quy định để xe và thông tin điểm danh Workshop. | Tìm thấy ngay trong tầng P2, hài lòng với việc dẫn nguồn minh bạch từ Coach. | *"Thấy trích nguồn từ Coach Duy Bách ở kênh # 💬-chung là yên tâm rồi, không sợ bot bịa."* | Giữ nguyên nguyên tắc PAIR Explainability và trích dẫn nguyên văn `source_quote`. |
| 4 | **Lê Trung Kiên**<br>(`2A202602748`) | Willing User CP1<br>Cụm C3 | Dùng lệnh `/chat` hỏi riêng bot: *"Hôm nay có deadline nào trước 24h không?"* | Lo ngại câu hỏi cá nhân và câu trả lời của bot bị hiện công khai làm phiền kênh chung. | *"Hỏi bot thế này cả kênh có nhìn thấy không bạn, mình muốn hỏi riêng tư thôi?"* | Cấu hình toàn bộ phản hồi `/chat` chỉ hiển thị riêng cho người gọi (**Ephemeral response**). |
| 5 | **Học viên S11**<br>(Ẩn danh) | Người dùng ngoài nhóm<br>Cụm C6 | Thử gõ vào `/chat`: *"Bot giải hộ mình bài lab Day04 và viết code Python nộp bài"*. | Muốn kiểm tra xem bot có làm bài thi/lab hộ được không. | *"Bot ơi viết hộ mình code bài lab Day04 với, tối nay nộp rồi."* | Bot kích hoạt **Safe Refusal**: từ chối giải bài, khẳng định giới hạn và hướng dẫn liên hệ Lab Coach. |

---

## 2. 4 DÒNG KẾT LUẬN BẮT BUỘC (THEO RUBRIC R6)

1. **Chủ đề lặp lại nhiều nhất:** Người dùng mong muốn nhãn phân loại ưu tiên phải cực kỳ dễ hiểu ngay trong 1 giây đầu tiên (tránh thuật ngữ kỹ thuật viết tắt), và tương tác hỏi đáp phải được giữ bảo mật/riêng tư (Ephemeral).
2. **Sẽ sửa gì trước demo:** Đã đổi toàn bộ tiêu đề nhãn sang tiếng Việt rõ ràng: **🔴 P1 · Khẩn cấp** — **🟡 P2 · Quan trọng** — **🟢 P3 · Đọc thêm**; đồng thời cấu hình lệnh `/chat` trả về phản hồi riêng tư chỉ người gọi nhìn thấy.
3. **Giữ nguyên gì và vì sao:** Giữ nguyên triệt để cơ chế gắn jump link trỏ về tin nhắn gốc (`[Xem tin gốc ↗]`) và trích dẫn nguyên văn bằng chứng (`source_quote`) vì 100% người dùng đánh giá cao tính minh bạch, loại bỏ hoàn toàn nỗi sợ bịa đặt (hallucination).
4. **Gì để dành sau:** Tính năng tích hợp nút nộp bài / điền form trực tiếp ngay trên khung chat Discord (để dành phát triển ở giai đoạn sau Hackathon).
