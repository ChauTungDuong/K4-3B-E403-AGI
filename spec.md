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
- **Giải pháp 1: Bản tin tóm tắt bot Discord hiện tại (`k4_daily_reports.md`):**
  - *Flow:* Bot tự động quét tin nhắn toàn server mỗi ngày một lần và đăng bản tin tổng hợp vào kênh chung.
  - *Đáng học:* Tự động định kỳ gom thông tin mà học viên không cần phải chủ động bấm gọi.
  - *Đáng né:* Trình bày dạng một khối văn bản đặc quánh (>500 từ), gom lẫn lộn thông báo chính thức với thảo luận linh tinh, không phân loại khẩn cấp (P1/P2/P3), không trích xuất deadline dạng bullet point, dính lỗi kỹ thuật nối chuỗi và câu kết thúc bị cắt cụt.
  - *Mình khác gì:* Phân loại 3 tầng ưu tiên trực quan (P1 Khẩn cấp / P2 Quan trọng / P3 Đọc thêm) kèm đếm ngược deadline, độ dài tối đa ≤8 dòng, gắn link nhảy thẳng về tin nhắn gốc trong kênh nguồn để học viên tự xác thực.
- **Giải pháp 2: Slack AI Recap / Discord Auto-Summarize:**
  - *Flow:* Người dùng vắng mặt mở kênh lên sẽ thấy nút "Catch up / Recap" tóm tắt nội dung các tin chưa đọc trong kênh đó.
  - *Đáng học:* Giao diện tích hợp mượt mà, tóm tắt nhanh dạng danh sách đầu dòng (bullet points).
  - *Đáng né:* Chỉ tóm tắt cục bộ từng kênh đơn lẻ (single-channel), không hỗ trợ quét tổng hợp chéo nhiều kênh (cross-channel digest), không lọc được tin nhắn tán gẫu ngoài lề, không nhận diện được các sự kiện học tập đặc thù (đổi phòng Zoom, nộp assignment).
  - *Mình khác gì:* Quét và tổng hợp chéo từ toàn bộ 6 kênh thông tin học tập (`#thông-báo`, `#bài-tập`, `#lịch-học`, `#chung`, `#thảo-luận`, `#hỗ-trợ`), lọc bỏ hoàn toàn tin tán gẫu, tập trung 100% vào việc cần hành động và hạn chót.

## §4. Thiết kế
- **Lát cắt MỘT CÂU:** Một học viên Khóa 4 · yêu cầu tóm tắt thông báo Discord trong 24h qua · AI quyết định lọc nhiễu và phân loại thông báo theo 3 tầng ưu tiên (P1 Khẩn cấp / P2 Quan trọng / P3 Đọc thêm) kèm trích xuất deadline · học viên nhận được bản tóm tắt có cấu trúc ≤8 dòng trong 3 giây kèm link nhảy đến tin nhắn gốc.
- **Non-goals (≥3 thứ dứt khoát KHÔNG làm):**
  1. *Không tự ý xóa, sửa hoặc can thiệp vào tin nhắn của học viên/giảng viên* trên server Discord.
  2. *Không đọc hoặc tóm tắt tin nhắn riêng tư (Direct Message - DM)* hoặc các kênh thảo luận nội bộ của Mentor/BTC.
  3. *Không tự giải bài tập, làm bài hộ hoặc trả lời thay Giảng viên/Mentor* về kiến thức chuyên môn ngoài phạm vi thông báo khóa học.
  4. *Không gửi thông báo spam (ping @everyone/@here)* làm phiền người dùng khi sinh bản tin.
- **Mức prototype nhắm tới:** `[x] Working`
  - *Giai đoạn CP2 (Bản mẫu tương tác):* Bản web prototype tương tác hoàn chỉnh mô phỏng Discord UI đặt tại `codebase/web_prototype/index.html` (demo click luồng `/digest 24h`, lọc kênh, nhảy tin gốc).
  - *Giai đoạn CP3 (Bản chạy thực tế):* Bot Discord hoạt động trực tiếp trên server riêng có tích hợp lời gọi AI thật (Google Gemini API / OpenAI) để phân loại 3 tầng ưu tiên và trích xuất hạn chót từ tin nhắn Discord thật.
  - *Phần mock:* Danh sách tin nhắn giả lập trong giao diện web prototype ở CP2; bộ dữ liệu kiểm thử định sẵn trong eval/.
  - *Phần thật:* Module gọi mô hình AI thật ở quyết định phân tầng P1/P2/P3, trích xuất thời gian và lưu trace log tại CP3.
- **Automation:** `[x] Conditional / Augment`
  - *Lý do theo cost-of-error:* Chi phí sai sót cao (Cost-of-error High). Nếu AI tóm tắt sai deadline hoặc bỏ sót thông báo khẩn cấp (như dời phòng Zoom hoặc hủy buổi học), học viên sẽ bị phạt vắng hoặc trừ điểm đồ án. Do đó, hệ thống giữ vai trò hỗ trợ (augment), tuyệt đối không tự động ra quyết định thay học viên, và bắt buộc cung cấp link dẫn chứng đến tin nhắn gốc (`#kênh · Xem tin gốc ↗`) để học viên bấm vào tự kiểm chứng.
- **§4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR):**

| Nguyên tắc | Áp cụ thể vào đâu trong prototype |
|---|---|
| **HAX G1: Make clear what the system can do** | Tại giao diện mở đầu của `#trợ-lý-tổng-hợp`, bot hiển thị thông điệp định vị rõ ràng: *"Không cần đọc ngược 362 tin nhắn. Mình tổng hợp theo độ ưu tiên, kiểm tra nguồn và dẫn bạn về đúng tin nhắn gốc"*, cùng số kênh theo dõi (6 kênh) và các nút lệnh gợi ý (`/digest 24h`, `/insight`, `/hot`, `/health`). |
| **HAX G4: Show contextually relevant information** | Bản tin phân cấp thông tin theo đúng ngữ cảnh thời gian và độ khẩn cấp: Thẻ **P1** (Đỏ rực - Deadline <12h hoặc đổi lịch học sát giờ kèm thời gian đếm ngược "Còn 8 giờ"), Thẻ **P2** (Vàng cam - Tài liệu/thông báo quan trọng), Thẻ **P3** (Xanh - Đọc thêm). Lọc bỏ hoàn toàn các tin tán gẫu. |
| **HAX G9: Support efficient correction** | Dưới mỗi bản tin tóm tắt luôn có cụm phản hồi 👍/👎 ("Kết quả này hữu ích?") và cho phép người dùng sửa đổi truy vấn nhanh (như gõ `/digest 12h` để thu hẹp khoảng thời gian, hoặc yêu cầu kiểm tra riêng một kênh). |
| **PAIR Explainability & Grounding** | Mọi mục thông báo trong bản tin đều có nhãn "✓ Đã kiểm tra nguồn" và nút bấm dẫn nguồn trực tiếp `#kênh · Xem tin gốc ↗`. Bấm vào sẽ tự chuyển view sang kênh đó và highlight tin nhắn gốc. |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8)

| Lớp chỗ khó | Mã | Kịch bản tình huống thực tế | Rủi ro nếu AI xử lý sai | Cơ chế phòng ngừa & xử lý của sản phẩm |
|---|---|---|---|---|
| **① Nguồn sự thật (Grounding)** | KB-01 | Hai học viên tranh luận và phỏng đoán sai về hạn nộp bài tập trong `#chung`. | AI tưởng đó là thông báo chính thức và tóm tắt sai deadline. | Chỉ trích xuất thông tin có nguồn từ Giảng viên, Mentor hoặc bot hệ thống; gắn link trỏ về đúng tin nhắn gốc. |
| **① Nguồn sự thật (Grounding)** | KB-02 | Học viên hỏi về sự kiện nhưng trong toàn bộ các kênh 24h qua không hề có thông báo. | AI tự sinh thông tin ảo (hallucination), bịa ra ngày giờ không có thật. | Kiểm tra độ tương đồng nguồn; nếu không có dữ liệu gốc, trả về phản hồi "Không tìm thấy căn cứ thông báo". |
| **② Mơ hồ / Thiếu thông tin** | KB-03 | Giảng viên nhắn: *"Tối nay lớp học ở phòng cũ nhé mọi người"*. | Học viên mới hoặc vắng buổi trước không biết "phòng cũ" là phòng nào. | AI trích nguyên văn thông báo, gắn cờ cảnh báo `[Cần xác nhận lại]` và dẫn link tin nhắn gốc. |
| **② Mơ hồ / Thiếu thông tin** | KB-04 | Thông báo ghi: *"Hạn nộp bài là 12h"* nhưng không nói rõ 12h trưa hay 24h đêm (23:59). | Học viên nộp muộn do hiểu sai giữa 12:00 trưa và 23:59. | AI cảnh báo mốc giờ chưa rõ ràng, mặc định nhắc học viên chuẩn bị trước mốc 12:00 trưa để an toàn. |
| **③ Ngoài phạm vi / Thẩm quyền** | KB-05 | Học viên nhắn: *"Bot ơi viết hộ mình bài luận Assignment 03"* hoặc *"Giải hộ bài code"*. | Bot làm bài hộ vi phạm quy chế học tập nghiêm trọng của VinAI. | Nhận diện intent yêu cầu giải bài, từ chối an toàn: *"Mình chỉ hỗ trợ tóm tắt thông báo học tập, không hỗ trợ giải bài tập"*. |
| **③ Ngoài phạm vi / Thẩm quyền** | KB-06 | Học viên nhắn: *"Cho mình xin gia hạn nộp bài thêm 2 tiếng nhé"*. | Bot đồng ý sai thẩm quyền khiến học viên bị 0 điểm vì quá hạn. | Từ chối khẳng định quyền hạn, hướng dẫn học viên liên hệ trực tiếp Giảng viên/Mentor tại kênh `#hỗ-trợ`. |
| **④ Đặc thù nghiệp vụ (Domain)** | KB-07 | Giảng viên thông báo đổi link Zoom hoặc đổi phòng học trước giờ học 15 phút. | Bị lẫn vào các tin đọc thêm (P3), học viên vào nhầm phòng Zoom. | Bất kể độ dài tin nhắn ngắn hay dài, mọi tin chứa từ khóa đổi link/phòng trong vòng 2h trước sự kiện đều tự động gán **P1 (Khẩn cấp)**. |
| **④ Đặc thù nghiệp vụ (Domain)** | KB-08 | Giảng viên thông báo deadline mới đính chính cho thông báo 2 tiếng trước đó. | AI lấy nhầm deadline cũ đã bị hủy thay vì deadline mới nhất. | Áp dụng logic ghi đè theo dòng thời gian (temporal resolution): thông báo sau của cùng người thẩm quyền sẽ cập nhật thông báo trước. |

## §6. Bốn đường đi của trải nghiệm
- **Happy path:** Học viên gõ `/digest 24h` → AI quét 6 kênh thông báo, lọc bỏ tin tán gẫu, phân loại chính xác các việc theo tầng P1/P2/P3 → Trả về bản tin tóm tắt có cấu trúc ≤8 dòng trong 1,8 giây, hiển thị rõ đếm ngược deadline và link tin nhắn gốc.
- **Low-confidence (Lớp ②):** Khi thông báo có nội dung mơ hồ hoặc thiếu mốc giờ cụ thể → Bot vẫn đưa vào danh sách nhưng gắn huy hiệu `[Cần xác nhận]` kèm trích dẫn nguyên văn câu của Giảng viên và nút nhảy đến kênh nguồn để người dùng tự xem bối cảnh.
- **Failure / Không căn cứ (Lớp ①):** Khi người dùng hỏi thông tin không tồn tại trong dữ liệu 24h qua → Bot kích hoạt nhánh từ chối an toàn: *"Không tìm thấy thông tin liên quan đến [...] trong 6 kênh thông báo 24h qua"*, gợi ý câu lệnh `/digest 24h` để xem toàn bộ việc đang có.
- **Correction (User sửa sai):** Nếu học viên thấy bản tin phân loại chưa chuẩn hoặc muốn kiểm tra kỹ hơn → Học viên bấm nút 👎 hoặc nhập lệnh `/digest 12h` hay `/insight #chung` → Hệ thống thu hẹp phạm vi quét và cập nhật lại bản tin tức thì.
- **Khi bị đòi ngoài phạm vi (Lớp ③):** Khi người dùng yêu cầu làm bài tập, giải code hoặc xin đặc quyền → Bot từ chối lịch sự, nêu rõ giới hạn chức năng và dẫn link đến kênh `#hỗ-trợ` để gặp nhân sự hỗ trợ.
- **Case đặc thù domain (Lớp ④):** Khi phát hiện tin khẩn sát giờ học (đổi link Zoom, đổi phòng, dời lịch thi) → Bot gắn nhãn **P1 Khẩn cấp**, tô đỏ nổi bật và đưa lên vị trí đầu tiên của bản tin kèm thời gian diễn ra sự kiện.

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
| 18/9 10:00 | Hoàn thiện §3, §4, §5, §6 (phân tích đối thủ, thiết kế, 4 nguyên tắc HAX/PAIR, 8 kịch bản 4 lớp chỗ khó, 4 nhánh UX) và đóng gói web prototype | Hoàn thành đầy đủ hồ sơ thiết kế trải nghiệm và bản mẫu tương tác mốc CP2 |
