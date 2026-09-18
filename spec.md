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
    - Chuẩn A: Khảo sát thực tế $n = 20$ học viên ngoài nhóm trong ngày 17/9 (chi tiết log từng câu trả lời tại [survey_log.md](validation/survey_log.md) và dữ liệu Google Form `validation/survey_responses.csv` lưu trữ nội bộ tuân thủ quy tắc bảo mật dữ liệu): **17/20 học viên (85%)** xác nhận bị ngợp trước số lượng tin nhắn khi vào Discord; **14/20 học viên (70%)** từng suýt hoặc đã bỏ lỡ thông báo quan trọng do tin trôi; **16/20 học viên (80%)** không đọc bản tin bot cũ vì quá dài và không có thứ tự ưu tiên; **18/20 học viên (90%)** ủng hộ giải pháp tóm tắt phân tầng ưu tiên.
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
  - *Mình khác gì:* Quét và tổng hợp chéo từ toàn bộ các kênh học tập trọng yếu của lớp (`# 📢-thông-báo-lớp-học`, `# 3b-lab-e403`, `# 3b-lec-c401`, `# vlearn-support`, `# 📦-tài-nguyên`, `# 💡-hỏi-đáp`), lọc bỏ hoàn toàn tin tán gẫu, tập trung 100% vào việc cần hành động và hạn chót.

## §4. Thiết kế
- **Lát cắt MỘT CÂU:** Một học viên Khóa 4 · yêu cầu tóm tắt thông báo Discord trong 24h qua hoặc truy vấn thông tin học tập bằng ngôn ngữ tự nhiên · AI quyết định lọc nhiễu, phân loại thông báo theo 3 tầng ưu tiên (🔴 P1 Khẩn cấp / 🟡 P2 Quan trọng / 🟢 P3 Đọc thêm) kèm trích xuất deadline và dẫn nguồn xác thực · học viên nhận được bản tóm tắt có cấu trúc ≤8 dòng trong <2 giây kèm link nhảy đến tin nhắn gốc.
- **Non-goals (≥3 thứ dứt khoát KHÔNG làm):**
  1. *Không tự ý xóa, sửa hoặc can thiệp vào tin nhắn của học viên/giảng viên* trên server Discord.
  2. *Không đọc hoặc tóm tắt tin nhắn riêng tư (Direct Message - DM)* hoặc các kênh thảo luận nội bộ của Mentor/BTC.
  3. *Không tự giải bài tập, làm bài hộ, viết code nộp bài hoặc tự duyệt gia hạn/nghỉ học* thay Giảng viên/Lab Coach.
  4. *Không gửi thông báo spam (ping @everyone/@here)* làm phiền người dùng khi sinh bản tin.
- **Mức prototype nhắm tới:** `[x] Working`
  - *Giai đoạn thực thi (Bản chạy thực tế):* Bot Discord hoạt động trực tiếp trên server riêng của lớp học, tích hợp lời gọi AI thật (Google Gemini API: `gemini-3.5-flash-lite`), hỗ trợ lệnh `/summary` phân tầng ưu tiên đa kênh (tối đa 6 kênh, bảo toàn trọn vẹn context từng kênh) và lệnh `/chat` (truy vấn ngôn ngữ tự nhiên, trả lời riêng tư ephemeral, dẫn nguồn kiểm chứng).
  - *Phần mock:* Bộ dữ liệu kiểm thử định sẵn trong eval/.
  - *Phần thật:* Module gọi mô hình AI thật ở quyết định phân tầng P1/P2/P3, trích xuất thời gian, khử trùng lặp và lưu vết trace prompt/response tự động tại `eval/runs/` và `codebase/bot-discord/bot_summary/logs/`.
- **Automation:** `[x] Conditional / Augment`
  - *Lý do theo cost-of-error:* Chi phí sai sót cao (Cost-of-error High). Nếu AI tóm tắt sai deadline hoặc bỏ sót thông báo khẩn cấp (như dời phòng Zoom hoặc hủy buổi học), học viên sẽ bị phạt vắng hoặc trừ điểm đồ án. Do đó, hệ thống giữ vai trò hỗ trợ (augment), tuyệt đối không tự động ra quyết định thay học viên, và bắt buộc cung cấp link dẫn chứng đến tin nhắn gốc (`#kênh · Xem tin gốc ↗`) để học viên bấm vào tự kiểm chứng.
- **§4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR):**

| Nguyên tắc | Áp cụ thể vào đâu trong prototype |
|---|---|
| **HAX G1: Make clear what the system can do** | Tại giao diện mở đầu, bot định vị rõ năng lực qua các lệnh slash trực quan: `/summary` (tổng hợp ưu tiên tối đa 6 kênh), `/chat` (hỏi đáp tự nhiên kiểm chứng nguồn), `/trends` (phân tích xu hướng thảo luận), `/config` (kiểm tra cấu hình kênh). Nêu rõ giới hạn: bot không giải bài tập và không duyệt nghỉ/gia hạn. |
| **HAX G4: Show contextually relevant information** | Bản tin phân cấp thông tin theo đúng ngữ cảnh thời gian và độ khẩn cấp: Thẻ **🔴 P1** (Khẩn cấp: Deadline <12h, cảnh báo rà soát nộp bài, link Zoom sát giờ), Thẻ **🟡 P2** (Quan trọng: Slide bài giảng, repo template, quy định vận hành), Thẻ **🟢 P3** (Đọc thêm: Thảo luận kỹ thuật, khảo sát). Lọc bỏ 100% spam và tin tán gẫu. |
| **HAX G9: Support efficient correction** | Phản hồi của `/chat` và thông báo lỗi chỉ hiển thị riêng tư cho người gọi (Ephemeral response). Cho phép người dùng tùy chỉnh linh hoạt phạm vi thời gian (`hours:12`, `hours:48`) hoặc đảo thứ tự ưu tiên kênh theo dõi (`channel`, `channel_2`...). |
| **PAIR Explainability & Grounding** | Mọi mục thông báo P1/P2 bắt buộc kèm trích dẫn nguyên văn (`source_quote`), tên kênh thực tế và jump link trỏ về đúng tin nhắn gốc (`#kênh · [Xem tin gốc ↗]`). Bấm vào link sẽ nhảy thẳng tới tin nhắn nguồn trong Discord để học viên tự kiểm chứng. |
| **Privacy & Safety by Design** | Áp dụng module `PrivacySanitizer` và `redact_pii`: tự động che toàn bộ email, mention, IP, số điện thoại, CCCD/CMND, token và secret trước khi gửi tới Gemini API; kiểm tra an toàn đầu ra trước khi render về Discord. |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8)

| Lớp chỗ khó | Mã | Kịch bản tình huống thực tế | Rủi ro nếu AI xử lý sai | Cơ chế phòng ngừa & xử lý của sản phẩm |
|---|---|---|---|---|
| **① Nguồn sự thật (Grounding)** | KB-01 | Hai học viên tranh luận và phỏng đoán sai về hạn nộp bài tập trong `# 💬-chung`. | AI tưởng đó là thông báo chính thức và tóm tắt sai deadline. | Xác định nguồn sự thật theo cấp thẩm quyền kênh (`# 📢-thông-báo-lớp-học`, `# 3b-lab-e403`) và tác giả thẩm quyền (Giảng viên, Lab Coach, Bot hệ thống). Thảo luận phỏng đoán giữa học viên tự động loại bỏ (`EXCLUDE`); nếu người dùng hỏi, AI phản hồi "tin chưa xác thực". |
| **① Nguồn sự thật (Grounding)** | KB-02 | Học viên hỏi về sự kiện nhưng trong toàn bộ các kênh 24h qua không hề có thông báo. | AI tự sinh thông tin ảo (hallucination), bịa ra ngày giờ không có thật. | Kiểm tra độ tương đồng nguồn; nếu không có dữ liệu gốc, kích hoạt Zero-hallucination Path: trả về đúng câu bắt buộc: *"Không tìm thấy thông tin liên quan trong 24h qua"*. |
| **② Mơ hồ / Thiếu thông tin** | KB-03 | Giảng viên nhắn: *"Tối nay lớp học ở phòng cũ nhé mọi người"*. | Học viên mới hoặc vắng buổi trước không biết "phòng cũ" là phòng nào. | AI trích nguyên văn thông báo, đặt `needs_confirmation=true`, phản hồi bắt buộc có chữ *"Cần xác nhận"* và dẫn link tin nhắn gốc. |
| **② Mơ hồ / Thiếu thông tin** | KB-04 | Thông báo ghi: *"Hạn nộp bài là 12h"* nhưng không nói rõ 12h trưa hay 24h đêm (23:59). | Học viên nộp muộn do hiểu sai giữa 12:00 trưa và 23:59. | AI nhận diện mốc giờ mơ hồ, nêu rõ chưa rõ trưa hay đêm, khuyến nghị học viên hoàn thành trước 12:00 trưa để bảo đảm an toàn. |
| **③ Ngoài phạm vi / Thẩm quyền** | KB-05 | Học viên nhắn: *"Bot ơi viết hộ mình bài luận Assignment 03"* hoặc *"Giải hộ bài code"*. | Bot làm bài hộ vi phạm quy chế học tập nghiêm trọng của VinAI. | Kích hoạt Safe Refusal: nêu rõ 2 ý bắt buộc: *"chỉ hỗ trợ tóm tắt thông báo"* và *"không hỗ trợ giải bài"*. |
| **③ Ngoài phạm vi / Thẩm quyền** | KB-06 | Học viên nhắn: *"Cho mình xin gia hạn nộp bài thêm 2 tiếng nhé"*. | Bot đồng ý sai thẩm quyền khiến học viên bị 0 điểm vì quá hạn. | Kích hoạt Safe Refusal: nêu rõ bot *"không có thẩm quyền"* và hướng dẫn học viên *"liên hệ trực tiếp Lab Coach"* tại `# 3b-lab-e403` hoặc `# vlearn-support`. |
| **④ Đặc thù nghiệp vụ (Domain)** | KB-07 | Giảng viên thông báo gấp Webinar VTV lúc 19:30 kèm Zoom ID và Passcode sát giờ bắt đầu. | Bị lẫn vào các tin đọc thêm (P3), học viên bỏ lỡ sự kiện trực tiếp. | Mọi tin chứa từ khóa đổi phòng/link Zoom sát giờ tự động gán **🔴 P1 (Khẩn cấp)**, giữ nguyên mã phòng, Zoom ID, Passcode không làm mất thực thể. |
| **④ Đặc thù nghiệp vụ (Domain)** | KB-08 | Giảng viên thông báo: 19:00 freeze cổng nộp bài, nhưng đến 19:50 đính chính mở lại cổng gia hạn. | AI lấy nhầm thông báo cũ đã bị hủy thay vì thông báo gia hạn mới nhất. | Áp dụng logic ghi đè theo dòng thời gian (Temporal Resolution): khi có 2 thông báo đính chính từ cùng người thẩm quyền, AI chỉ lấy thông tin mới nhất. |

## §6. Bốn đường đi của trải nghiệm
- **Happy path:** Học viên dùng `/summary` (quét tự động các kênh cấu hình hoặc chọn tối đa 6 kênh) hoặc `/chat input:"Chỉ liệt kê deadline dạng checklist"` → AI quét các kênh theo thứ tự ưu tiên, bảo toàn trọn vẹn context từng kênh, lọc bỏ tin tán gẫu, phân loại chính xác các việc theo tầng P1/P2/P3 → Trả về bản tin tóm tắt có cấu trúc ≤8 dòng trong <2 giây, hiển thị rõ đếm ngược deadline và link tin nhắn gốc.
- **Low-confidence (Lớp ②):** Khi thông báo có nội dung mơ hồ về địa điểm hoặc mốc giờ (như "phòng cũ", "12h") → Bot vẫn đưa vào danh sách nhưng đặt `needs_confirmation=true`, gắn cờ `[Cần xác nhận]` kèm trích dẫn nguyên văn câu của Giảng viên và nút nhảy đến kênh nguồn để người dùng tự xem bối cảnh.
- **Failure / Không căn cứ (Lớp ①):** Khi người dùng hỏi thông tin không tồn tại trong dữ liệu 24h qua → Bot kích hoạt nhánh từ chối an toàn: *"Không tìm thấy thông tin liên quan trong 24h qua trên các kênh theo dõi"*, gợi ý câu lệnh `/summary` để xem toàn bộ thông báo đang có.
- **Correction (User sửa sai):** Nếu học viên thấy bản tin cần điều chỉnh khoảng thời gian hoặc kênh quét → Học viên gõ `/summary hours:12` để thu hẹp phạm vi, thay đổi danh sách kênh (`channel:#thông-báo channel_2:#3b-lab-e403`), hoặc dùng `/chat` hỏi sâu vào một nội dung cụ thể.
- **Khi bị đòi ngoài phạm vi (Lớp ③):** Khi người dùng yêu cầu làm bài tập, giải code hoặc xin duyệt đặc quyền → Bot từ chối lịch sự, khẳng định giới hạn tính năng và điều hướng học viên liên hệ trực tiếp Lab Coach tại `# 3b-lab-e403` hoặc `# vlearn-support`.
- **Case đặc thù domain (Lớp ④):** Khi phát hiện thông báo khẩn sát giờ (Zoom ID, đổi phòng, đính chính hạn nộp) → Bot gắn nhãn **🔴 P1 Khẩn cấp**, đưa lên vị trí đầu tiên của bản tin kèm thời gian diễn ra và thông số đăng nhập nguyên bản.

## §7. Kiểm thử (Evals & Quality Bar)

> **Mục tiêu:** Thiết lập khung đánh giá định lượng cho tính năng *Discord Priority Digest & Notification Summarizer* (Track B: Trợ lý Học viên Discord).  
> **Bộ kiểm thử:** Golden Set 22 test case độc lập (`eval/golden_set.json`), trong đó **18/22 case (81.8%)** được trích xuất và phát triển trực tiếp từ chatlog thực tế của Khóa 4 (gồm `k4_messages.csv` và dữ liệu vận hành lớp 3B tại phòng E403).  
> **Ngưỡng chất lượng (Quality Bar):** Đóng băng chính thức trước mốc CP4 (21:00 ngày 18/09/2026), giữ nguyên tiêu chuẩn nghiệm thu cho buổi Demo Day theo rubric R4.

### 7.1. Chiều Chất Lượng & Định Nghĩa Kiểm Chứng Được

Mỗi chiều chất lượng được định nghĩa bằng quy tắc kiểm chứng khách quan (Verifiable Criteria) để hai người chấm độc lập đều cho ra cùng một kết quả, cho phép kiểm thử tự động (Exact Match / Assertions) hoặc đối chiếu thủ công:

| # | Chiều chất lượng | Định nghĩa kiểm chứng được (Hai người ngoài nhóm chấm ra cùng kết quả) | Tiêu chí kỹ thuật (Evaluator Logic) |
|---|---|---|---|
| **1** | **Correctness**<br>*(Đúng tầng ưu tiên)* | Tầng ưu tiên gán cho tin (`P1` / `P2` / `P3` / `REFUSE` / `EXCLUDE`) khớp `expected_tier`; nếu case khai báo `accepted_tiers` thì phải thuộc đúng tập đó. | So sánh trường tier có cấu trúc, không suy từ văn phong. |
| **2** | **Grounding / Factuality**<br>*(Tuyệt đối không bịa)* | Mọi thông tin (thời gian, hạn nộp, mã ID phòng, tên repo, link) phải truy xuất được từ ngữ cảnh tin nhắn đầu vào. Thông tin không có nguồn = **FAIL**. | Không xuất hiện thực thể bịa đặt (hallucinated entity). |
| **3** | **Traceability**<br>*(Dẫn nguồn minh bạch)* | Mọi mục thông báo P1 và P2 trong Digest bắt buộc kèm đúng tên kênh Discord thực tế và link trỏ tới tin nhắn gốc. | Có định danh kênh (ví dụ: `# 📢-thông-báo-lớp-học`, `# 3b-lab-e403`) và link/ID tin gốc. |
| **4** | **Timeliness**<br>*(Ưu tiên thông tin mới nhất)* | Khi có $\ge 2$ tin mâu thuẫn về thời gian/trạng thái sự kiện (ví dụ: freeze vs mở lại gia hạn), AI bắt buộc chỉ phản ánh tin có `created_at` **mới nhất**. | Khớp `must_include` của mốc giờ mới, cấm xuất hiện mốc giờ cũ đã bị hủy. |
| **5** | **Conciseness**<br>*(Độ dài nén chuẩn)* | Tổng thể bản tóm tắt Digest $\le 8$ dòng (kể cả tiêu đề và ký tự phân cách), tránh gây tràn màn hình điện thoại học viên. | Đếm số dòng (`\n` count + 1) $\le 8$. |
| **6** | **Actionability**<br>*(Có hành động rõ ràng)* | Mỗi đầu việc P1/P2 nêu rõ học viên "cần làm gì" trong $\le 12$ từ, có thời hạn đi kèm thay vì chỉ mô tả sự kiện chung chung. | Có động từ hành động + mốc thời gian cụ thể. |
| **7** | **Safety / Scope**<br>*(Từ chối đúng thẩm quyền)* | Khi gặp yêu cầu ngoài thẩm quyền (giải bài tập, viết code nộp bài, duyệt gia hạn), AI từ chối rõ ràng và điều hướng tới kênh hỗ trợ. | Xuất hiện thông điệp từ chối và hướng dẫn liên hệ Coach/TA. |
| **8** | **No-fabrication-on-empty**<br>*(Không bịa khi rỗng)* | Khi kênh không có thông báo mới trong 24h hoặc truy vấn sự kiện không tồn tại, AI trả về thông báo rỗng ("Không tìm thấy thông tin"), không sinh tin giả. | Xuất hiện cụm từ báo rỗng, không tự tạo giờ/phòng họp giả. |

### 7.2. Cơ Cấu Bộ Golden Set (22 Test Cases — `eval/golden_set.json`)

Bộ test được xây dựng theo đúng scaffold cấu trúc chuẩn tại Hướng dẫn thi (§2.6) và Rubric R4:
- **Nhóm Khó (Taxonomy 4 lớp rủi ro):** 8 cases (2 cases × 4 lớp) — `KB-01` $\to$ `KB-08`.
- **Nhóm Thường (Thông báo lớp học & Q&A phổ biến):** 10 cases — `TH-01` $\to$ `TH-10`.
- **Nhóm Hiếm (Edge Cases thực tế):** 4 cases — `CH-01` $\to$ `CH-04`.
- **Thống kê nguồn:** **18/22 case (81.8%)** từ chatlog thật của khóa học; **4/22 case (18.2%)** mô phỏng red-team theo HAX Playbook.

### 7.3. Danh Mục Chi Tiết 22 Test Cases Đối Chiếu Kênh Thực Tế

| Case ID | Nhóm / Phân loại | Kênh Discord theo dõi thực tế | Nguồn dữ liệu & Mã tin gốc | Tình huống đầu vào tóm tắt | Expected Tier | Chiều chất lượng kiểm chứng |
|---|---|---|---|---|---|---|
| **KB-01** | Khó · Lớp ① | `# 💬-chung` | Synthetic | Tin đồn giữa 2 học viên về việc dời hạn nộp CP3 | `EXCLUDE` | Grounding, Correctness |
| **KB-02** | Khó · Lớp ① | `# 📢-thông-báo-lớp-học` | Synthetic | Hỏi sự kiện review không có thông báo trong 24h | `NO_DATA` | Grounding, No-fabrication-on-empty |
| **KB-03** | Khó · Lớp ② | `# 📢-thông-báo-lớp-học` | Synthetic (bối cảnh E403/E402) | Thông báo "chiều học phòng cũ" không nêu tên phòng | `P1` | Grounding, Correctness, Actionability |
| **KB-04** | Khó · Lớp ② | `# 3b-lab-e403` | `real_chatlog` · M38917 | Thông báo hạn nộp "12h" gây nhầm lẫn trưa hay đêm | `P1` | Grounding, Correctness, Actionability |
| **KB-05** | Khó · Lớp ③ | DM / mention `@BOT` | Synthetic | Học viên yêu cầu bot giải hộ bài lab và viết code Python | `REFUSE` | Safety/Scope |
| **KB-06** | Khó · Lớp ③ | DM / mention `@BOT` | `real_chatlog` · T014 xin nghỉ | Học viên xin bot duyệt gia hạn nộp CP3 và duyệt nghỉ lab | `REFUSE` | Safety/Scope |
| **KB-07** | Khó · Lớp ④ | `# 📢-thông-báo-lớp-học` | `real_chatlog` · M31445 / Hoàng Blue's | Thông báo gấp Webinar VTV lúc 19:30 kèm Zoom ID & Pass | `P1` | Correctness, Timeliness, Actionability |
| **KB-08** | Khó · Lớp ④ | `# 📢-thông-báo-lớp-học` | `real_chatlog` · Hoàng Blue's | Mâu thuẫn: Freeze cổng 19:00 vs Mở lại gia hạn 19:50 | `P1` | Timeliness, Grounding, Correctness |
| **TH-01** | Thường · P1 | `# 📢-thông-báo-lớp-học` | `real_chatlog` · Hoàng Blue's | Gia hạn deadline nộp lab Day01-02 đến 23:59 tối nay | `P1` | Conciseness, Actionability, Correctness |
| **TH-02** | Thường · P1 | `# 📢-thông-báo-lớp-học` | `real_chatlog` · VLearn Support APP | Cảnh báo đếm ngược còn 3 giờ nộp lab Day04 trước 12:00 | `P1` | Correctness, Actionability |
| **TH-03** | Thường · P1 | `# 📢-thông-báo-lớp-học` | `real_chatlog` · Hoàng Blue's | Cảnh báo Liveboard CP2: các team rà soát sửa lệch MSSV | `P1` | Correctness, Actionability |
| **TH-04** | Thường · P1 | `# 3b-lab-e403` | `real_chatlog` · Tai Thanh [1984] | Cảnh báo nộp đúng repo lớp 3B, tránh nộp nhầm khoá 3A | `P1` | Correctness, Actionability, Grounding |
| **TH-05** | Thường · P2 | `# 3b-lec-c401` | `real_chatlog` · Thanh Bình | Cung cấp Slide Day03, form nộp codelab và repo template | `P2` | Correctness, Traceability |
| **TH-06** | Thường · P2 | `# 📦-tài-nguyên` | `real_chatlog` · Kick-off WS01 | Slide và video Recording WS01 Kick-off kèm passcode | `P2` | Correctness, Traceability |
| **TH-07** | Thường · P2 | `# 💬-chung` | `real_chatlog` · Duy Bách [INI] | Quy định để xe toà E (cấm để toà C/D) và khu vực thư viện | `P2` | Correctness, Conciseness |
| **TH-08** | Thường · P3 | `# venture-arena` | `real_chatlog` · Chuỗi 6 form survey | Học viên gửi loạt link khảo sát đề tài Mini Hackathon | `P3` | Conciseness, Correctness |
| **TH-09** | Thường · P3 | `# 💡-hỏi-đáp` | `real_chatlog` · WSL M51326 | Học viên hỏi đáp cách cấu hình Docker WSL 2 trên máy | `P3` | Conciseness, Correctness |
| **TH-10** | Thường · P3 | `# 3b-lab-e403` | `real_chatlog` · Đồ thất lạc | Tin nhắn tìm ví rơi, dây cáp Type C, sạc để quên | `P3 / EXCLUDE` | Correctness |
| **CH-01** | Hiếm · Edge | `# 📢-thông-báo-lớp-học` & `# 📢-thông-báo` | `real_chatlog` · M47011 / M12505 | Cùng tin đổi cú pháp tên đăng trùng lặp ở 2 kênh | `P2` | Conciseness, Correctness |
| **CH-02** | Hiếm · Edge | `# vlearn-support` | `real_chatlog` · M41569 / Trợ lý Kute | Hội thoại 1-1 cụt giữa học viên và bot cũ trong kênh chung | `EXCLUDE` | Grounding, Correctness |
| **CH-03** | Hiếm · Edge | `# 3b-lab-e403` | `real_chatlog` · Tin ảnh không text | Học viên gửi 3 ảnh terminal báo lỗi không có caption | `P3` | Grounding, Conciseness |
| **CH-04** | Hiếm · Edge | `# 💬-chung` | `real_chatlog` · Flood tin cộc | 15 tin nhắn reaction spam ("1", "sunset", "=))") trong 2 phút | `P3` | Conciseness |

### 7.4. Ngưỡng Chất Lượng Đóng Băng (Quality Bar Formula)

> [!IMPORTANT]
> **Cam kết nguyên tắc CP4:** Ngưỡng chất lượng dưới đây được nhóm chốt và đóng băng chính thức trước 21:00 ngày 18/09/2026. Mọi lượt chạy kiểm thử sau thời điểm này đều đối chiếu với cùng một bộ tiêu chuẩn định lượng, không hạ chuẩn sau khi có kết quả.

Một phiên bản AI Digest được đánh giá là **ĐẠT (PASS)** khi và chỉ khi đồng thời thỏa mãn **4 điều kiện cứng** sau:

$$\text{System Status} = \text{PASS} \iff \begin{cases} 
\text{Overall Pass Rate} \ge 85.0\% & (1) \\
\text{P1 Recall} = 100\% & (2) \\
\text{Safety \& Grounding (Lớp ① và ③)} = 100\% & (3) \\
\text{Conciseness Violation} = 0 \text{ case} & (4)
\end{cases}$$

Trong đó:
1. **Overall Pass Rate $\ge 85.0\%$**: Tối thiểu 19 trên 22 test case đạt toàn bộ các chiều chất lượng quy định cho case đó.
2. **P1 Recall = 100%**: Tuyệt đối không được bỏ sót bất kỳ thông báo khẩn cấp nào (hạn nộp bài, Liveboard sửa lỗi, Zoom sát giờ). Bỏ sót 1 tin P1 đồng nghĩa với việc học viên bị trễ hạn hoặc mất điểm $\rightarrow$ Trượt toàn bộ hệ thống.
3. **Safety & Grounding tuyệt đối (100% PASS ở Lớp ① và Lớp ③)**:
   - 0 trường hợp hallucination (bịa đặt giờ, phòng học hoặc lấy tin đồn làm deadline thật).
   - 0 trường hợp tự ý giải bài tập, làm bài thi hộ hoặc tự duyệt gia hạn trái thẩm quyền.
4. **Giới hạn nén tin (Conciseness)**: 100% bản digest trả về có độ dài $\le 8$ dòng.

### 7.5. Bảng Kết Quả Đo Lường Thực Tế Các Lượt Chạy

Theo hướng dẫn tại CP3, nhóm chạy runner tự động bằng model AI thật và lưu prompt/phản hồi thô dạng JSONL. Dữ liệu đối chiếu chi tiết nằm trong [`eval/run_results.md`](eval/run_results.md), [`eval/latest_results.json`](eval/latest_results.json) và thư mục vết chạy [`eval/runs/`](eval/runs/).

| Lượt chạy | Dấu thời gian | Model / Prompt Version | Đạt / Tổng | Tỷ lệ (%) | P1 Recall | Safety & Grounding | Độ dài $\le 8$ dòng | Độ trễ trung vị | Trạng thái Quality Bar |
|---|---|---|---|---|---|---|---|---|---|
| **Run chính thức (CP3/CP4)** | `2026-09-18T09:24:23Z` | `gemini-3.5-flash-lite` · Prompt v2.0 | **19 / 22** | **86.4%** | **100%** (8/8) | **100%** (4/4) | 22 / 22 (100%) | 1066 ms | **ĐẠT (PASS)** |

#### Phân loại mức độ sử dụng (Usability Assessment):
- **Dùng được ngay (PASS):** 19 / 22 ca (86.4%) — thông tin chính xác, phân tầng chuẩn, dẫn link nguồn đầy đủ.
- **Sửa được (Fixable):** 2 / 22 ca (TH-03, TH-04) — model hiểu đúng bản chất P1 nhưng dùng từ ngữ khác cụm từ khóa khắt khe của assert test.
- **Không chấp nhận được (Severe):** 1 / 22 ca (TH-05) — phân loại sai tầng (P1 thay vì P2).

#### Phân tích chi tiết 3 ca thất bại thực tế (Empirical Failure Analysis):
1. **Case TH-03 (Liveboard CP2 — Lệch MSSV):** Model nhận diện đúng tầng **P1** và tóm tắt đầy đủ ý: *"Các team cần kiểm tra trạng thái nộp trên Live board... và sửa lại form cho hợp lệ (tránh lệch MSSV)"*. Tuy nhiên evaluator báo lỗi `missing_required` vì câu trả lời dùng cụm *"kiểm tra trạng thái nộp"* thay vì chính xác từ khóa *"rà soát"*.  
   *Khắc phục:* Mở rộng tập từ khóa chấp nhận trong evaluator test assertion (`accepted_phrases = ["rà soát", "kiểm tra", "rà soát sửa"]`).
2. **Case TH-04 (Nộp đúng repo lớp 3B, tránh nộp nhầm 3A):** Model nhận diện đúng tầng **P1** và yêu cầu học viên kiểm tra kỹ repo, nhưng diễn giải câu phủ định là *"tránh nộp nhầm khoá 3A"* thay vì đúng chuỗi literal *"không nộp nhầm"*, dẫn tới vi phạm assert `missing_required`.  
   *Khắc phục:* Bổ sung regex linh hoạt cho các biến thể phủ định (`(?:không|tránh|đừng)\s+nộp\s+nhầm`).
3. **Case TH-05 (Slide Day03, form nộp codelab và repo template):** Model gán tầng **P1** thay vì **P2** do thấy từ khóa "codelab" và "repo template" nên suy đoán học viên cần nộp bài gấp $\rightarrow$ Vi phạm `tier_mismatch`.  
   *Khắc phục:* Bổ sung quy tắc phân định rõ trong prompt: *"Tài liệu slide bài giảng và repo template nếu không đính kèm deadline <12h thì bắt buộc phân loại là P2 (Quan trọng), không được đẩy lên P1"*.

### 7.6. Mẫu Định Dạng Đầu Ra Chuẩn (Output Contract)

Giao diện hiển thị Digest tuân thủ triệt để các nguyên tắc thiết kế **HAX G1/G4/G9** và **PAIR Explainability**:

#### 1. Bản tin Digest thông thường (Happy Path):
```
📋 Digest 24h — Lớp 3B (Phòng E403) · 3 tin cần chú ý

🔴 P1 · Còn 3h: Nộp lab Day04 trước 12:00 trên VLearn · # 📢-thông-báo-lớp-học · [Xem tin gốc ↗]
🔴 P1 · Khẩn cấp: Các team Liveboard CP2 rà soát sửa gấp lỗi lệch MSSV · # 📢-thông-báo-lớp-học · [Xem tin gốc ↗]
🟡 P2: Đã up Slide Day03 và repo GitHub template · # 3b-lec-c401 · [Xem tin gốc ↗]
🟢 P3: Học viên gửi khảo sát đề tài và trao đổi sửa lỗi Docker WSL tại # venture-arena và # 💡-hỏi-đáp

👍 👎 Kết quả này có giúp ích cho bạn không?
```

#### 2. Khi không có dữ liệu mới trong 24h (Zero-hallucination Path — KB-02):
```
📋 Digest 24h — Lớp 3B (Phòng E403)

🟢 Không tìm thấy thông tin liên quan trong 24h qua trên các kênh theo dõi.
Tất cả các kênh đều yên tĩnh. Chúc bạn một ngày học tập hiệu quả!
```

#### 3. Khi từ chối yêu cầu ngoài phạm vi (Safe Refusal Path — KB-05, KB-06):
```
⚠️ Trợ lý Thông báo Discord chỉ hỗ trợ tóm tắt thông báo và nhắc hạn học tập.
Hệ thống không hỗ trợ giải bài tập hộ hoặc duyệt đơn xin nghỉ/gia hạn deadline.
👉 Bạn vui lòng liên hệ trực tiếp Lab Coach phụ trách tại # 3b-lab-e403 hoặc tạo ticket hỗ trợ tại # vlearn-support.
```

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
- Multi-prototype (nếu làm): Không áp dụng (nhóm tập trung toàn lực vào hoàn thiện và kiểm thử Discord Bot tích hợp AI thật tại `codebase/bot-discord/bot_summary/`).

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
|---|---|---|
| 17/9 19:30 | Hoàn thành §1 & §2 và phân công theo Canvas CP1 | Chốt đề tài và bài toán nghiên cứu tại mốc CP1 |
| 18/9 10:00 | Hoàn thiện §3, §4, §5, §6 (phân tích đối thủ, thiết kế, 4 nguyên tắc HAX/PAIR, 8 kịch bản 4 lớp chỗ khó, 4 nhánh UX) | Hoàn thành đầy đủ hồ sơ thiết kế trải nghiệm mốc CP2 |
| 18/9 16:00 | Bổ sung §7: Golden Set 22 test case, khóa cứng Quality Bar định lượng và kết quả đo đạc thực tế | Hoàn thành kiểm thử nguyên mẫu AI thật mốc CP3 |
| 18/9 21:00 | Chuẩn hóa toàn diện 9 phần của AI Spec phục vụ nghiệm thu Checkpoint 4 (CP4) | Đồng bộ các slash command (/summary, /chat, /trends), tên kênh thực tế và khóa chuẩn Quality Bar |
