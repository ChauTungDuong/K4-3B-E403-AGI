# 📁 BỘ 10 CA KIỂM THỬ TRÍCH XUẤT TỪ CHATLOG THẬT (`k4_messages.csv`)
**Phụ trách:** Nguyễn Đình Tuấn Anh (Data & Evidence)  
**Chuyển giao cho:** Đỗ Mạnh Nghĩa (AI & Evaluation) để tích hợp vào Golden Set $\ge 20$ case (Khối R4 · Phục vụ mốc CP3 lúc 16:00)

---

## 🎯 TỔNG QUAN CƠ CẤU 10 CASE

- **Nguồn dữ liệu:** File nhật ký Discord Khóa 4 thật `data/discord-pack/k4_messages.csv` (1.092 tin nhắn).
- **Phân bổ 3 tầng ưu tiên:**
  - **🔴 P1 (Khẩn cấp & Bắt buộc hành động):** 4 case (Deadline Daily Standup, Ghép đội, Hạn Lab, Link Zoom).
  - **🟡 P2 (Quan trọng / Vận hành & Điểm danh / Low-conf):** 5 case (Quy chế XP, Điểm danh WS, Hướng dẫn Daily, Tin mơ hồ thiếu ảnh).
  - **🟢 P3 (Tham khảo / Đọc thêm):** 1 case (Slide tài liệu bài giảng).
- **Độ phủ 4 lớp chỗ khó (PAIR / HAX taxonomy):**
  - Lớp ① Nguồn sự thật (Grounding): 3 case
  - Lớp ② Mơ hồ / Thiếu dữ kiện (Low-confidence): 3 case
  - Lớp ③ Thẩm quyền / Ngoài phạm vi: 1 case
  - Lớp ④ Đặc thù domain học tập (Deadlines / Phạt XP): 3 case

---

## 📋 BẢNG CHI TIẾT 10 CA KIỂM THỬ

### Case 1: Hạn chót nộp Daily Standup bị khóa (TC-CHAT-01)
- **Mã tin nhắn (`msg_id`):** `M98666`
- **Kênh xuất phát:** `channel_10` | **Tác giả:** `D7506`
- **Nội dung nguyên văn:**
  > `"[@BOT] thời gian mở daily standup và kết thúc là khi nào vậy? hôm qua mình gửi sớm daily standup thì không được, chiều nay quá deadline thì nó lại blocked mình."`
- **Tầng ưu tiên chuẩn (Ground Truth):** **🔴 P1 - KHẨN CẤP**
- **Lớp chỗ khó:** **Lớp ④ (Đặc thù domain)** — Sai deadline khiến học viên bị trừ 10 XP và tính vắng mặt.
- **Hành vi mong muốn của AI:** Trích xuất mốc giờ mở/đóng Daily Standup (23:59), cảnh báo nguy cơ bị block/trừ điểm nếu nộp muộn, dẫn link trực tiếp đến thread Daily.
- **Tiêu chí Đạt (Pass):** Xếp đúng P1 + trích xuất đúng hạn 23:59 + link tin gốc.

---

### Case 2: Đóng cổng ghép đội tự do (TC-CHAT-02)
- **Mã tin nhắn (`msg_id`):** `M19124`
- **Kênh xuất phát:** `channel_02` | **Tác giả:** `D9616`
- **Nội dung nguyên văn:**
  > `"a oi sao deadline ghép đội tự do end sớm vậy a?"`
- **Tầng ưu tiên chuẩn (Ground Truth):** **🔴 P1 - KHẨN CẤP**
- **Lớp chỗ khó:** **Lớp ④ (Đặc thù domain)** — Ghép đội ảnh hưởng trực tiếp đến tư cách làm đồ án Hackathon/Build phase.
- **Hành vi mong muốn của AI:** Nhận diện đây là thắc mắc deadline khẩn cấp, trích xuất thời hạn chốt đội (18:00), dẫn link đến kênh `#ghép-đội-tự-do`.
- **Tiêu chí Đạt (Pass):** Xếp đúng P1 + có cảnh báo thời hạn ghép đội.

---

### Case 3: Quy định hạn chót nộp bài Lab trong ngày (TC-CHAT-03)
- **Mã tin nhắn (`msg_id`):** `M57630`
- **Kênh xuất phát:** `channel_10` | **Tác giả:** `BOT`
- **Nội dung nguyên văn:**
  > `"Bài Lab trên lớp sẽ được chấm sau khi hết deadline thường là 23:59 cùng ngày nhé"`
- **Tầng ưu tiên chuẩn (Ground Truth):** **🔴 P1 - KHẨN CẤP**
- **Lớp chỗ khó:** **Lớp ① (Nguồn sự thật)** — Thông báo từ bot hệ thống/trợ lý chính thức.
- **Hành vi mong muốn của AI:** Trích xuất mốc 23:59 là hạn nộp bài Lab bắt buộc trong ngày, không bị nhầm sang ngày hôm sau.
- **Tiêu chí Đạt (Pass):** Xếp đúng P1 + trích xuất "23:59 cùng ngày".

---

### Case 4: Thông báo mở phòng Zoom trực tiếp sát giờ (TC-CHAT-04)
- **Mã tin nhắn (`msg_id`):** `M31445`
- **Kênh xuất phát:** `channel_03` | **Tác giả:** `D3694`
- **Nội dung nguyên văn:**
  > `"Các bạn đừng quên Lịch sáng nay nhé, zoom đã mở nha [@role]"`
- **Tầng ưu tiên chuẩn (Ground Truth):** **🔴 P1 - KHẨN CẤP**
- **Lớp chỗ khó:** **Lớp ④ (Đặc thù domain)** — Sự kiện diễn ra ngay tại thời điểm hiện tại, có điểm danh.
- **Hành vi mong muốn của AI:** Đưa lên đầu bản tin với nhãn hành động [Vào Zoom ngay], đính kèm link Zoom từ thông báo gốc.
- **Tiêu chí Đạt (Pass):** Xếp đúng P1 + gắn nhãn sự kiện đang diễn ra.

---

### Case 5: Hướng dẫn địa điểm và cách nộp Daily Standup (TC-CHAT-05)
- **Mã tin nhắn (`msg_id`):** `M60122`
- **Kênh xuất phát:** `channel_02` | **Tác giả:** `D3154`
- **Nội dung nguyên văn:**
  > `"cho mình hỏi cái daily-standup này làm ở đâu vậy nhỉ, làm thế nào"`
- **Tầng ưu tiên chuẩn (Ground Truth):** **🟡 P2 - QUAN TRỌNG**
- **Lớp chỗ khó:** **Lớp ② (Mơ hồ / Câu hỏi vận hành)**.
- **Hành vi mong muốn của AI:** Tóm tắt ngắn gọn quy trình nộp Daily (nộp trong thread nhóm, dùng lệnh `/daily-standup`), dẫn link hướng dẫn chính thức.
- **Tiêu chí Đạt (Pass):** Xếp đúng P2 + nêu rõ nơi nộp (thread nhóm).

---

### Case 6: Mốc thời gian bắt đầu tính điểm thưởng XP (TC-CHAT-06)
- **Mã tin nhắn (`msg_id`):** `M22827`
- **Kênh xuất phát:** `channel_11` | **Tác giả:** `D9617` (Mentor/Coach)
- **Nội dung nguyên văn:**
  > `"Bình thường nhé [HV], ngày bắt đầu ghi nhận XP daily standup là 14/9 nhé"`
- **Tầng ưu tiên chuẩn (Ground Truth):** **🟡 P2 - QUAN TRỌNG**
- **Lớp chỗ khó:** **Lớp ① (Nguồn sự thật)** — Xác nhận chính sách tính điểm XP từ Coach.
- **Hành vi mong muốn của AI:** Trích xuất mốc 14/9 là ngày bắt đầu tính XP Daily Standup để học viên theo dõi bảng xếp hạng.
- **Tiêu chí Đạt (Pass):** Xếp đúng P2 + không làm tròn sai mốc ngày 14/9.

---

### Case 7: Thắc mắc về việc điểm danh Workshop (TC-CHAT-07)
- **Mã tin nhắn (`msg_id`):** `M69081`
- **Kênh xuất phát:** `channel_02` | **Tác giả:** `D2313`
- **Nội dung nguyên văn:**
  > `"có điểm danh ws không ạ"`
- **Tầng ưu tiên chuẩn (Ground Truth):** **🟡 P2 - QUAN TRỌNG**
- **Lớp chỗ khó:** **Lớp ② (Mơ hồ)** — Câu hỏi cụt lủn không nói rõ Workshop nào.
- **Hành vi mong muốn của AI:** Khẳng định quy định chung có điểm danh Workshop qua mã QR / Coach, dẫn link đến kênh thông báo Workshop gần nhất.
- **Tiêu chí Đạt (Pass):** Xếp đúng P2 + xác nhận có điểm danh.

---

### Case 8: Quy chế vào phòng và điểm danh bổ sung (TC-CHAT-08)
- **Mã tin nhắn (`msg_id`):** `M17046`
- **Kênh xuất phát:** `channel_02` | **Tác giả:** `D7688`
- **Nội dung nguyên văn:**
  > `"vào trước 30p là được nhé, b liên hệ labcoach hôm đó để điểm danh sau"`
- **Tầng ưu tiên chuẩn (Ground Truth):** **🟡 P2 - QUAN TRỌNG**
- **Lớp chỗ khó:** **Lớp ① (Nguồn sự thật)** — Quy trình giải quyết khi gặp sự cố điểm danh.
- **Hành vi mong muốn của AI:** Tóm tắt giải pháp khi đến muộn: cần liên hệ trực tiếp Lab Coach phụ trách để điểm danh bổ sung.
- **Tiêu chí Đạt (Pass):** Xếp đúng P2 + trích xuất đúng người thẩm quyền (Lab Coach).

---

### Case 9: Nơi nhận slide bài học và tài liệu kỹ thuật (TC-CHAT-09)
- **Mã tin nhắn (`msg_id`):** `M81490`
- **Kênh xuất phát:** `channel_02` | **Tác giả:** `D7688`
- **Nội dung nguyên văn:**
  > `"bạn hỏi labcoach tại phòng nhé, vì slide/bài học thì giảng viên từng buổi sẽ up"`
- **Tầng ưu tiên chuẩn (Ground Truth):** **🟢 P3 - THAM KHẢO (Đọc thêm / FYI)**
- **Lớp chỗ khó:** **Lớp ③ (Tài liệu học tập thường quy)** — Không chứa áp lực thời gian hay chế tài phạt.
- **Hành vi mong muốn của AI:** Xếp vào tầng P3 Đọc thêm, nêu rõ slide bài giảng do Giảng viên từng buổi đăng tải.
- **Tiêu chí Đạt (Pass):** Xếp đúng P3 + không bị đẩy nhầm lên P1/P2 gây loãng tin.

---

### Case 10: Tin nhắn mơ hồ đính kèm ảnh lỗi (TC-CHAT-10)
- **Mã tin nhắn (`msg_id`):** `M55571`
- **Kênh xuất phát:** `channel_11` | **Tác giả:** `D5195`
- **Nội dung nguyên văn:**
  > `"em có test thử nộp daily thì nó hiện như vậy là bình thường hay có lỗi ạa"`
- **Tầng ưu tiên chuẩn (Ground Truth):** **🟡 P2 - CẢNH BÁO (Low-confidence)**
- **Lớp chỗ khó:** **Lớp ② (Thiếu thông tin ngữ cảnh)** — Học viên hỏi về ảnh chụp màn hình nhưng không nêu mã lỗi.
- **Hành vi mong muốn của AI:** Nhận diện tin nhắn thiếu dữ liệu để kết luận lỗi, gắn cờ `[Cần xác minh]` và tạo nút `[Nhảy đến tin gốc ↗]` để người dùng tự xem ảnh.
- **Tiêu chí Đạt (Pass):** Kích hoạt cơ chế Low-confidence theo PAIR (không bịa đặt kết luận có lỗi hay không lỗi).

---

## 📊 BẢNG TỔNG HỢP KIỂM TRA (CHECKLIST CHO NGHĨA)

| Case ID | Msg ID | Kênh | Priority | Chỗ khó | Trích xuất chính |
|---|---|---|:---:|:---:|---|
| TC-CHAT-01 | `M98666` | channel_10 | 🔴 P1 | ④ Domain | Deadline Daily Standup 23:59 |
| TC-CHAT-02 | `M19124` | channel_02 | 🔴 P1 | ④ Domain | Hạn chót ghép đội 18:00 |
| TC-CHAT-03 | `M57630` | channel_10 | 🔴 P1 | ① Grounding | Deadline nộp Lab 23:59 |
| TC-CHAT-04 | `M31445` | channel_03 | 🔴 P1 | ④ Domain | Link Zoom mở trực tiếp |
| TC-CHAT-05 | `M60122` | channel_02 | 🟡 P2 | ② Ambiguity | Hướng dẫn lệnh /daily |
| TC-CHAT-06 | `M22827` | channel_11 | 🟡 P2 | ① Grounding | Ngày tính XP 14/9 |
| TC-CHAT-07 | `M69081` | channel_02 | 🟡 P2 | ② Ambiguity | Điểm danh Workshop |
| TC-CHAT-08 | `M17046` | channel_02 | 🟡 P2 | ① Grounding | Điểm danh bù qua Coach |
| TC-CHAT-09 | `M81490` | channel_02 | 🟢 P3 | ③ Scope | Slide tài liệu học tập |
| TC-CHAT-10 | `M55571` | channel_11 | 🟡 P2 | ② Low-conf | Thiếu ảnh → Cần xác minh |
