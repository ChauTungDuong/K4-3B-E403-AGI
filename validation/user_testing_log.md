# 📋 NHẬT KÝ THỬ NGHIỆM NGƯỜI DÙNG THỰC TẾ (USER TESTING LOG — KHỐI R6)

> **Dự án:** Trợ lý Tóm tắt Thông báo Discord Theo Thứ Tự Ưu Tiên (Discord Priority Digest)  
> **Nhóm:** AGI · **Lớp:** 3B · **Phòng:** E403 · **Track:** Track B — Trợ lý Học viên Discord  
> **Người thực hiện:** Nguyễn Đình Tuấn Anh (MSSV: `2A202602735` — Vai trò: Data & Evidence)  
> **Phương pháp tiếp cận:** Mom Test (Giao nhiệm vụ, giữ im lặng quan sát, ghi chép điểm nghẽn và trích dẫn nguyên văn)  
> **Môi trường thử nghiệm:** Server Discord lớp 3B phòng E403, kết nối mô hình Google Gemini API thật (`gemini-3.5-flash-lite`).

---

## 1. Bảng Ghi Nhận Thử Nghiệm 5 Người Dùng Ngoài Nhóm (Mom Test)

| STT | Người thử | Nhiệm vụ giao | Điểm tắc nghẽn (Friction Point) | Trích dẫn nguyên văn (Verbatim Quote) | Quyết định xử lý của nhóm |
|:---:|---|---|---|---|---|
| **1** | **Hoàng Phong**<br>`2A202602943`<br>*(Cụm C5 · Willing User CP1)* | Thao tác lệnh `/summary` 24h trên kênh `# 📢-thông-báo-lớp-học` để tìm deadline nộp bài trong ngày. | Lúc đầu tìm nút bấm trong giao diện web, sau khi được hướng dẫn dùng slash command `/summary` trên Discord thì thao tác rất nhanh. | *"Dễ dùng dễ hiểu, nhìn phát biết ngay deadline nào khẩn màu đỏ cần nộp trước."* | **Giữ nguyên:** Giữ nguyên quy ước màu sắc 🔴 P1 / 🟡 P2 / 🟢 P3 vì người dùng nắm bắt thông tin trực quan rất tốt. |
| **2** | **Trần Nam Anh**<br>`2A202602901`<br>*(Cụm C6 · Willing User CP1)* | Giả lập sau 24h bận rộn, vào Discord tìm thông báo đổi phòng học và kiểm tra nguồn gốc tin nhắn. | Muốn biết tin đổi phòng học có đáng tin không vì sợ tin đồn của học viên khác trong kênh chat. | *"Đáp ứng được nhu cầu, có link dẫn về đúng tin nhắn của Coach nên không sợ bị lừa."* | **Cải tiến:** Tối ưu hóa nút `[Xem tin gốc ↗]` to rõ hơn và đặt trực tiếp dưới mỗi thẻ P1/P2 để tiện bấm trên điện thoại. |
| **3** | **Hoàng Anh Minh**<br>`2A202602566`<br>*(Cụm C4 · Willing User CP1)* | Dùng lệnh `/summary` quét đa kênh và kiểm tra độ trễ phản hồi của hệ thống. | Chờ khoảng 1 giây để bot phân tích, tò mò không biết bot có đang chạy hay bị treo. | *"Sản phẩm tốt, phản hồi khoảng hơn 1 giây là rất nhanh so với phải lội 300 tin."* | **Cải tiến:** Bổ sung trạng thái `bot is thinking...` và hiển thị `độ trễ: 1.1s` ở chân bản tin để người dùng an tâm. |
| **4** | **Lê Trung Kiên**<br>`2A202602748`<br>*(Cụm C3 · Willing User CP1)* | Đặt câu hỏi tìm link Zoom Webinar VTV buổi tối trong kênh hỏi đáp. | Lo ngại bản tin dài làm tràn màn hình điện thoại như bản tin bot cũ của khóa học. | *"Sản phẩm đáng tin cậy, nén ngắn gọn trong mấy dòng đọc lướt 10 giây là xong."* | **Giữ nguyên:** Khóa cứng tiêu chí Conciseness $\le 8$ dòng trong Quality Bar, loại bỏ hoàn toàn các câu văn rườm rà. |
| **5** | **Vũ Quốc Huy**<br>`2A202602929`<br>*(Học viên K4 · Phòng E403)* | Thử nghiệm tình huống hỏi ngoài phạm vi (nhờ bot giải bài tập lab và xin nghỉ học). | Ban đầu tưởng bot có thể làm bài tập hộ như ChatGPT thông thường. | *"Tiết kiệm thời gian, bot từ chối khéo việc giải bài và chỉ hướng dẫn liên hệ Coach."* | **Giữ nguyên:** Duy trì 100% tỷ lệ an toàn từ chối ngoài thẩm quyền (Safety/Scope), tuân thủ nghiêm ngặt quy chế đào tạo. |

---

## 2. Tổng Hợp Đánh Giá Nghiệm Thu (Khối R6)

- **Số lượng người thử nghiệm:** $5 / 5$ người ngoài nhóm (100%), trong đó có **4 người dùng thuộc danh sách Willing Users** đã cam kết tại mốc CP1.
- **Tỷ lệ thành công:** $5 / 5$ người dùng hoàn thành xuất sắc nhiệm vụ mà không gặp bất kỳ lỗi kỹ thuật nghẽn mạng nào.
- **Phản hồi định tính:** $100\%$ nhận xét tích cực về tính thực tiễn (*"Dễ dùng dễ hiểu"*, *"Đáp ứng được nhu cầu"*, *"Tiết kiệm thời gian"*).
- **Điều chỉnh sản phẩm:** Nhóm đã ghi nhận 2 cải tiến UX (nút jump link to rõ hơn và thêm chỉ báo độ trễ thực tế) vào mục §9 Changelog của `spec.md`.
