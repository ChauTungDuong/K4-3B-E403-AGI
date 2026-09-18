# Bảng kết quả AI theo từng test case

> Đây là bảng được sinh từ `latest_results.json`. PASS nghĩa là câu trả lời vượt qua toàn bộ tiêu chí của case; FAIL xem lý do ở cột cuối.

- Run: `run_20260918T092423Z`
- Model: `gemini-3.5-flash-lite`
- Tổng kết: **19/22 PASS (86.4%)**, **3 FAIL**
- Quality Bar: **ĐẠT**

| STT | Case | Nhóm / nguồn | Nhãn mong đợi | Nhãn AI | Câu trả lời do AI sinh | Kết quả | Sai ở đâu |
|---:|---|---|---|---|---|:---:|---|
| 1 | `KB-01` | Khó<br>synthetic | **EXCLUDE** | **EXCLUDE** | Tin đồn dời hạn nộp mini hackathon CP3 chưa xác thực tại #💬-chung. | **PASS** | — |
| 2 | `KB-02` | Khó<br>synthetic | **NO_DATA** | **NO_DATA** | Không tìm thấy thông tin liên quan trong 24h qua về buổi review đồ án trực tiếp với TS Phạm Hy Hiếu trong kênh #📢-thông-báo-lớp-học. | **PASS** | — |
| 3 | `KB-03` | Khó<br>synthetic | **P1** | **P1** | Tại kênh #📢-thông-báo-lớp-học: Chiều nay ca lab lớp 3B chuyển sang học ở phòng cũ. Cần xác nhận phòng cụ thể. | **PASS** | — |
| 4 | `KB-04` | Khó<br>M38917 | **P1** | **P1** | Tại kênh #3b-lab-e403, Coach thông báo hạn chót cập nhật repo GitHub là 12h ngày mai. Mốc 12h hiện chưa rõ trưa hay đêm, cần xác nhận lại. Khuyến nghị hoàn thành trước 12:00 trưa để đảm bảo an toàn. | **PASS** | — |
| 5 | `KB-05` | Khó<br>synthetic | **REFUSE** | **REFUSE** | Bot chỉ hỗ trợ tóm tắt thông báo và không hỗ trợ giải bài. | **PASS** | — |
| 6 | `KB-06` | Khó<br>T014-trichxuat | **REFUSE** | **REFUSE** | Bot không có thẩm quyền duyệt nghỉ hay gia hạn. Vui lòng liên hệ trực tiếp Lab Coach để được hỗ trợ. | **PASS** | — |
| 7 | `KB-07` | Khó<br>M31445, HB-0910-trichxuat | **P1** | **P1** | Tại kênh #📢-thông-báo-lớp-học: Lớp học thông báo WEBINAR AI THỰC CHIẾN 2026 - ĐƯỜNG ĐẾN GIẢI THƯỞNG TRIỆU ĐÔ do thầy Thạnh gửi. Thời gian: 19:30 tối nay. Zoom ID: 916 1573 9756, Passcode: 753006, Link: https://zoom.us/j/91615739756. | **PASS** | — |
| 8 | `KB-08` | Khó<br>HB-0916-trichxuat | **P1** | **P1** | Tại kênh #📢-thông-báo-lớp-học, Coach Hoàng Blue's thông báo cập nhật liveboard sau khi freeze và mở lại form cho các team. Hạn cuối đóng cổng chính thức là 19:50. | **PASS** | — |
| 9 | `TH-01` | Thường<br>HB-0913-trichxuat | **P1** | **P1** | Tại kênh #📢-thông-báo-lớp-học, Lab Coach - Hoàng Blue's thông báo gia hạn deadline nộp bài lab của day01 và day02 đến 23h59p00s tối nay. Điểm số bài lab ảnh hưởng đến kết quả phase1,2 nên học viên cần nhớ nộp đầy đủ. | **PASS** | — |
| 10 | `TH-02` | Thường<br>VLEARN-0915-trichxuat | **P1** | **P1** | Tại # 📢-thông-báo-lớp-học: 🔥 📢 Còn 3 giờ để nộp lab Day04-Prompt-Engineering-Tool-Calling-Labs (Buổi 4 · DAY04). Hạn cuối: 12:00 15/09 · đã có 201 bài nộp | **PASS** | — |
| 11 | `TH-03` | Thường<br>HB-0916-CP2-trichxuat | **P1** | **P1** | Tại kênh #📢-thông-báo-lớp-học, Lab Coach - Hoàng Blue's thông báo Live board đã cập nhật trạng thái CP2. Các team cần kiểm tra trạng thái nộp trên Live board, xem ghi chú bên cạnh và sửa lại form cho hợp lệ (tránh lệch MSSV, lệch tên team, lệch tên trưởng nhóm hoặc sai chính tả) vì các CP này đều tính điểm vào kết quả cuối cùng. | **FAIL** | `missing_required`: Thiếu nội dung bắt buộc: 'rà soát'. |
| 12 | `TH-04` | Thường<br>TT-0916-3B-trichxuat | **P1** | **P1** | Tại kênh #3b-lab-e403, Lab Coach Tai Thanh lưu ý lớp 3B coi và nộp bài trên Vlearn là K4-L3B-DAY05-06-MINI-HACKATHON. Chú ý đừng nộp nhầm k4-3a-d05-06-ai-product-hackathon của lớp khác. | **FAIL** | `missing_required`: Thiếu nội dung bắt buộc: 'không nộp nhầm'. |
| 13 | `TH-05` | Thường<br>TB-0913-trichxuat | **P2** | **P1** | Tại kênh #3b-lec-c401, Lab Coach Thanh Bình đã gửi slide Day 03: Chatbot vs ReAct Agent, link repo bài mini lab template và yêu cầu nộp bài qua Codelab Completion Form. | **FAIL** | `tier_mismatch`: Kỳ vọng P2, model trả P1.<br>`forbidden_content`: Có nội dung bị cấm: 'P1'. |
| 14 | `TH-06` | Thường<br>RES-0910-trichxuat | **P2** | **P2** | Tại kênh #📦-tài-nguyên, đã có Slide và Recording WS01: Kick-off kèm Passcode AI20K_K4. Lưu ý: Tài liệu lưu hành nội bộ chương trình AI20K Build Phase. | **PASS** | — |
| 15 | `TH-07` | Thường<br>DB-0917-trichxuat | **P2** | **P2** | Tại kênh #💬-chung, Lab Coach - Duy Bách [INI] lưu ý quy định không gian và gửi xe: chỉ để xe tại khu vực học viên AI (thẳng rẽ trái, gần toà E), không để ở cạnh toà C và D. Chỉ sử dụng Thư viện VinUni và JC101 đến ngày 20/09, tuyệt đối không dùng tiện ích khác khi chưa cho phép. | **PASS** | — |
| 16 | `TH-08` | Thường<br>SURVEYS-0917-trichxuat | **P3** | **P3** | Tại kênh venture-arena: Các học viên T062, T083, T136, T066, T019 và T052 đã gửi các khảo sát (Kailabs, bản tin TA, bot Discord, review kịch bản, VLearn Tutor kèm link Google Forms). Nội dung này có thể trì hoãn. | **PASS** | — |
| 17 | `TH-09` | Thường<br>M51326, M03651, M44947, M80794, M42604, M50526 | **P3** | **P3** | Tại kênh 💡-hỏi-đáp, học viên trao đổi kỹ thuật về cách sửa lỗi không khởi động được Docker WSL trên Windows với các bước hướng dẫn mở Docker Desktop -> Settings -> Resources -> Enable WSL 2 Engine. | **PASS** | — |
| 18 | `TH-10` | Thường<br>LOST-FOUND-trichxuat | **P3/EXCLUDE** | **EXCLUDE** | Tin nhắn trong kênh #3b-lab-e403 thông báo về đồ thất lạc (sạc và dây type C), không thuộc nội dung cần đưa vào tóm tắt ưu tiên. | **PASS** | — |
| 19 | `CH-01` | Hiếm<br>M47011, M12505 | **P2** | **P2** | Tại kênh # 📢-thông-báo-lớp-học và # 📢-thông-báo: Yêu cầu đổi tên hiển thị theo cú pháp 'Mã Nhóm - Họ và tên - 5 số cuối mã sinh viên'. | **PASS** | — |
| 20 | `CH-02` | Hiếm<br>M41569, KUTE-trichxuat | **EXCLUDE** | **EXCLUDE** | Tin nhắn trong #vlearn-support là trao đổi giữa học viên và bot khác, không thuộc nội dung digest. | **PASS** | — |
| 21 | `CH-03` | Hiếm<br>IMG-ONLY-trichxuat | **P3** | **P3** | Tại kênh #3b-lab-e403, học viên trao đổi kỹ thuật về lỗi cài đặt thư viện pip install chưa rõ nguyên nhân. | **PASS** | — |
| 22 | `CH-04` | Hiếm<br>FLOOD-0915-trichxuat | **P3/EXCLUDE** | **EXCLUDE** | Tin nhắn rác, tán gẫu, không thuộc nội dung cần đưa vào digest tại kênh #💬-chung. | **PASS** | — |

## Cách đọc nhanh

- Nếu **nhãn mong đợi** và **nhãn AI** khác nhau: AI phân loại sai tầng ưu tiên.
- Nếu hai nhãn giống nhau nhưng vẫn FAIL: đọc cột **Sai ở đâu**; thường là thiếu chi tiết bắt buộc, chứa nội dung bị cấm hoặc thiếu nguồn.
- Muốn xem prompt và JSON thô của model, mở file trace được liên kết trong `run_results.md`.
