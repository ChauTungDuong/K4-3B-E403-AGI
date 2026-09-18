# AI SPEC — Trợ Lý Tóm Tắt Thông Báo Discord Theo Thứ Tự Ưu Tiên (Discord Priority Digest) · Nhóm AGI · Zone C6 - E403

Hướng: [ ] A — VLearn  [x] B — Trợ lý Học viên  [ ] C — Làn mở  
Loại: [x] Tối ưu tính năng có sẵn (Cải tiến bản tin bot) / Tính năng mới

## §1. User & Job
- **Job executor + workflow (đính kèm worksheet JTBD / ảnh sơ đồ):** Học viên Khóa 4 vừa đăng nhập vào Discord sau thời gian bận (sau 24h hoặc sau nhiều giờ offline); quy trình gồm: Mở Discord → Nhìn danh sách kênh thông báo có tin chưa đọc → Cần xác định ngay các thông tin khẩn cấp (deadline, đổi phòng/link Zoom, nhiệm vụ học tập) → Thực hiện các hành động cần thiết đúng hạn.
- **Core JTBD (không tên sản phẩm/AI trong câu):** Cập nhật đầy đủ và kịp thời các thông báo học tập quan trọng sau mỗi khoảng thời gian vắng mặt để không bị trễ nợ bài tập hoặc bỏ lỡ sự kiện bắt buộc.
- **Problem statement (KHÔNG chữ AI):** Học viên gặp tình trạng quá tải thông tin khi đăng nhập vào Discord do thông báo bị phân tán trên nhiều kênh và trôi nhanh giữa các tin thảo luận; họ mất nhiều thời gian lội đọc từng kênh hoặc đọc các bản tin tổng hợp dạng khối chữ dài không phân cấp, dẫn đến việc bỏ sót thông báo khẩn cấp và bị phạt điểm hoặc phạt vắng.
- **Evidence (chuẩn A và/hoặc B — log đầy đủ trong repo):**
  - **Số liệu mining / kết quả khảo sát (n = ?, % xác nhận):**
    - Chuẩn B: Mining dữ liệu từ `data/discord-pack/k4_messages.csv` (1.092 tin nhắn / 24 kênh và luồng trong 3 ngày) và `data/discord-pack/k4_daily_reports.md` (bản tin bot hiện tại là khối chữ dài >500 từ, không phân cấp khẩn cấp, dính lỗi câu bị cắt cụt và thiếu trích xuất deadline).
    - Chuẩn A: Khảo sát thực tế $n = 20$ học viên ngoài nhóm trong ngày 17/9: **17/20 học viên (85%)** xác nhận bị ngợp trước số lượng tin nhắn khi vào Discord; **14/20 học viên (70%)** từng suýt hoặc đã bỏ lỡ thông báo quan trọng do tin trôi; **16/20 học viên (80%)** không đọc bản tin bot cũ vì quá dài và không có thứ tự ưu tiên.
  - **≥5 quote/ví dụ nguyên văn + nguồn:**
    1. `k4_daily_reports.md` (Bản tin bot ngày 14/09): *"Học viên thắc mắc về việc deadline ghép đội tự do kết thúc sớm hơn dự kiến..."*
    2. `[M98666]` (`k4_messages.csv`): *"[@BOT] thời gian mở daily standup và kết thúc là khi nào vậy? hôm qua mình gửi sớm daily standup thì không được, chiều nay quá deadline thì nó lại blocked mình."*
    3. `[M19124]` (`k4_messages.csv`): *"a oi sao deadline ghép đội tự do end sớm vậy a?"*
    4. Quote khảo sát 1 (Học viên ẩn danh A): *"Nhiều kênh quá, đi làm về mở Discord lên thấy chấm đỏ tùm lum, mình chỉ muốn biết hôm nay có deadline gì hay có link Zoom mới không thôi."*
    5. Quote khảo sát 2 (Học viên ẩn danh B): *"Bản tin của bot hiện tại viết một cục dài ngoằng, đọc xong chả đọng lại được việc gì phải làm trước việc gì phải làm sau."*

## §2. Impact & quyết định chọn
- **Bảng impact ≥3 ứng viên (bao nhiêu người · tần suất · tốn gì mỗi lần · khả thi):**

| Ứng viên | Đối tượng | Tần suất | Tổn thất khi gặp lỗi / tốn kém | Khả thi kỹ thuật |
|---|---|---|---|---|
| **Phương án 1 (CHỌN): Trợ lý Tóm tắt Thông báo theo Thứ tự Ưu tiên (Discord Priority Digest)** | Toàn bộ ~1.000 học viên Khóa 4 | 1–2 lần / ngày / học viên (mỗi sáng hoặc tối) | Mất 20–30 phút lội tin mỗi ngày; bỏ lỡ deadline/link Zoom bị trừ điểm | Rất cao (quét kênh thông báo, trích xuất thời gian & phân loại 3 tầng) |
| **Phương án 2: Bot Trả lời Từng Deadline Riêng Lẻ (Single Deadline Q&A)** | Học viên có thắc mắc cụ thể | Bị động (chỉ khi học viên nhớ ra để hỏi) | Nếu không biết có thông báo mới thì học viên không chủ động hỏi bot | Cao |
| **Phương án 3: Bộ Đếm Tin Chưa Đọc Theo Kênh (Unread Counter)** | Học viên | Thường xuyên | Chỉ đếm số lượng, không giải quyết được việc người dùng vẫn phải đọc từng tin | Rất cao (nhưng giá trị AI thấp) |

- **Ứng viên ĐÃ LOẠI + vì sao:**
  - *Loại Phương án 3:* Giải pháp cơ học, không có giá trị quyết định AI và không giải quyết được việc người dùng vẫn phải tự đọc tin.
  - *Loại Phương án 2:* Tính năng mang tính bị động (reactive), chỉ hỗ trợ khi học viên đã biết có bài tập để đi hỏi, không giải quyết được bài toán người dùng "không biết những gì mình đã bỏ lỡ" sau 24h vắng mặt.
- **Ứng viên CHỌN + vì sao (bằng số):**
  - **Chọn Phương án 1:** Mang lại giá trị chủ động (proactive), phục vụ 100% học viên ($n \approx 1.000$). Giúp tiết kiệm từ 15–20 phút xuống còn <30 giây mỗi lần cập nhật. Giải quyết trực tiếp lỗi tồn đọng của bản tin bot cũ trong pack (80% học viên chê bản tin cũ không hiệu quả).

## §3. Giải pháp tương tự đã nghiên cứu
- [Sản phẩm 1]: flow / đáng học / đáng né / mình khác gì
- [Sản phẩm 2]: ...

## §4. Thiết kế
- Lát cắt MỘT CÂU (1 user · 1 việc · 1 quyết định AI · 1 kết quả):
- Non-goals (≥3 thứ KHÔNG build):
- Mức prototype nhắm tới: [ ] Sketch [ ] Mock [ ] Working — phần nào mock, phần nào thật:
- Automation: [ ] augment [ ] conditional [ ] automate — lý do theo cost-of-error:
- §4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR, xem guide):
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8) [bảng theo guide §2.5]

## §6. Bốn đường đi của trải nghiệm
- Happy path: · Low-confidence (②): · Failure/không căn cứ (①): · Correction (user sửa):
- Khi bị đòi ngoài phạm vi (③): · Case đặc thù domain (④):

## §7. Kiểm thử
- Chiều chất lượng + định nghĩa kiểm chứng được:
- Golden set (≥20 case theo cơ cấu trong guide §2.6, file trong eval/):
- Quality bar (chốt từ hạn chốt spec của khoá, giữ nguyên sau đó): "Đạt khi ≥ ___% qua bộ, và ___"
- Kết quả các lượt chạy (bảng % — cập nhật đến trước CP6):

## §8. Phân công & kế hoạch
- **Phân công có tên:**
  - Châu Tùng Dương (Product Lead): Chốt Canvas CP1, viết và chuẩn hóa spec.md, quản lý tiến độ và nộp form checkpoint.
  - Nguyễn Đình Tuấn Anh (Data & Evidence): Khai thác dữ liệu log chat, khảo sát, quản lý willing users.
  - Đỗ Mạnh Nghĩa (AI & Evaluation): Phụ trách Prompting phân loại ưu tiên, thiết kế 4 lớp chỗ khó, xây dựng bộ golden set 20 case trong eval/.
  - Nguyễn Ngọc Tuyền (UX & Prototype): Thiết kế giao diện tóm tắt P1/P2/P3 trên Discord, code prototype trong codebase/.
- **Willing users (≥2 tên) + kế hoạch vòng validation *(bonus, nếu làm)*:**
  1. Trần Nam Anh (MSSV: 2A202602901)
  2. Hoàng Anh Minh (MSSV: 2A202602566)
  3. Hoàng Phong (MSSV: 2A202602943)
  4. Lê Trung Kiên (MSSV: 2A202602748)
- Multi-prototype (nếu làm): trục khác biệt của ≥2 phương án + lý do chọn:

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
|---|---|---|
| 17/9 19:30 | Hoàn thành §1 & §2 và phân công theo Canvas CP1 | Chốt đề tài và bài toán nghiên cứu tại mốc CP1 |
