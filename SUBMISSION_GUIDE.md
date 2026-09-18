# HƯỚNG DẪN CẤU TRÚC REPOSITORY & CHECKLIST NỘP BÀI HACKATHON
> **Dành cho Nhóm AGI · Track B — Trợ lý Học viên Discord · Lớp 3B · Phòng E403**  
> *Căn cứ theo tài liệu hướng dẫn chính thức Lab 05–06 AI Product Hackathon (`huongdan.txt` & `01-challenge-brief.md`)*

---

## I. SƠ ĐỒ CẤU TRÚC TỔNG THỂ REPOSITORY

Repository của nhóm phải đảm bảo đúng cấu trúc thư mục tiêu chuẩn dưới đây để Ban Giám Khảo và Trợ Giảng đối chiếu từng hạng mục điểm số:

```text
K4-3B-E403-AGI/
├── README.md             # Bản sao README đề bài kèm bảng phân công vai trò hoàn chỉnh
├── TEAMMATES.md          # Danh sách 4 thành viên kèm MSSV, vai trò và nhiệm vụ
├── canvas.md             # Canvas 7 dòng hoàn thiện tại mốc CP1
├── spec.md               # Tài liệu AI Spec 9 phần (chiếm 45/67 điểm chấm repo)
├── demo-slides.pdf       # Bộ slide báo cáo đúng 6 trang PDF (nộp tại CP5)
├── SUBMISSION_GUIDE.md   # Hướng dẫn chi tiết cấu trúc nộp bài các mốc (tài liệu này)
├── codebase/             # Toàn bộ mã nguồn sản phẩm (Web Prototype & Bot Discord AI thật)
│   ├── web_prototype/    # Giao diện web mô phỏng Discord (phục vụ CP2)
│   └── discord_bot/      # Bot Discord chạy trên server riêng có gọi LLM thật (phục vụ CP3)
├── eval/                 # Bộ kiểm thử Golden Set (≥20 case) và nhật ký chạy thử nghiệm
│   ├── golden_set.json   # 20 ca kiểm thử phân loại theo taxonomy 4 lớp chỗ khó
│   └── run_results.md    # Báo cáo kết quả chạy thử các lượt kèm phân tích lỗi
├── validation/           # Nhật ký thử nghiệm người dùng ngoài nhóm (Khối R6 - 8 điểm cộng)
│   └── user_testing_log.md # Nhật ký phỏng vấn tối thiểu 5 người dùng (Mom Test)
└── reflection/           # Bài thu hoạch cá nhân của từng thành viên (chấm điểm cá nhân CP6)
    ├── 2A202602822_ChauTungDuong.md
    ├── 2A202602735_NguyenDinhTuanAnh.md
    ├── 2A202602971_DoManhNghia.md
    └── 2A202603010_NguyenNgocTuyen.md
```

---

## II. CHI TIẾT TỪNG THƯ MỤC & TỆP TIN: CẦN NỘP GÌ?

### 1. Các tệp ở thư mục gốc (Root Files)

| Tệp tin | Mốc nộp | Yêu cầu nội dung chi tiết |
|---|---|---|
| **`README.md`** | CP1 → CP6 | Chứa **bảng thành viên đầy đủ** ở đầu tệp: Họ tên, Mã học viên, Vai trò chính và Phần việc cụ thể. Đây là căn cứ đối chiếu điểm của BTC. Giữ nguyên các phần quy chế, luật hackathon và cam kết bảo mật dữ liệu ở phía dưới. |
| **`TEAMMATES.md`** | CP1 | Danh sách chi tiết 4 thành viên trong nhóm, phân định rõ 4 mảng: Product Lead, Data & Evidence, AI & Evaluation, UX & Prototype. |
| **`canvas.md`** | CP1 | Canvas 7 dòng chuẩn: Track & đề, Job executor, Pain một câu, Bằng chứng số liệu, Lát cắt 1 câu, Mức tự động hóa & danh sách willing users, Phân công công việc. |
| **`spec.md`** | CP1 → CP4 | **Tài liệu trung tâm chiếm 45/67 điểm.** Gồm 9 phần (§1–§9):<br>• **§1 & §2:** Bài toán, người dùng, minh chứng số liệu (chuẩn A/B), bảng so sánh 3 phương án.<br>• **§3 & §4:** Phân tích 2 giải pháp tương tự, lát cắt 1 câu, non-goals, mức prototype (Working), mức tự động hóa (Augment/Conditional), bảng 4 nguyên tắc HAX/PAIR.<br>• **§5 & §6:** 8 kịch bản thuộc 4 lớp chỗ khó, 4 nhánh trải nghiệm UX.<br>• **§7 (Khóa tại CP4):** **Quality Bar** định lượng khóa cứng trước hạn chốt, kết quả đo đếm.<br>• **§8 & §9:** Phân công, willing users, Changelog. |
| **`demo-slides.pdf`** | CP5 | Đúng **6 trang chuẩn định dạng PDF** lưu tại thư mục gốc:<br>• *Trang 1:* Bối cảnh, bài toán & bằng chứng thực tế (chuẩn A/B).<br>• *Trang 2:* Lát cắt giải pháp một câu & kiến trúc tổng quan.<br>• *Trang 3:* 4 lớp chỗ khó & cách xử lý trong trải nghiệm người dùng.<br>• *Trang 4:* Bảng đo lường kết quả thực tế đối chiếu Quality Bar CP4.<br>• *Trang 5:* Bài học rút ra từ các ca lỗi & phản hồi người dùng (R6).<br>• *Trang 6:* Kế hoạch mở rộng & đóng góp của từng thành viên. |

---

### 2. Thư mục `codebase/` (Mã nguồn Prototype)

Chứa toàn bộ mã nguồn sản phẩm qua các giai đoạn:
1. **Bản mẫu tương tác Web (`codebase/web_prototype/`):**
   - Đã có sẵn: `index.html`, `style.css`, `script.js`.
   - Phục vụ mốc CP2 để chứng minh luồng tương tác UX thông suốt không bị tắc nghẽn.
2. **Chatbot Discord AI thật (`codebase/discord_bot/` hoặc thư mục gốc `codebase/`):**
   - Phục vụ mốc CP3: Phải có **≥1 lời gọi AI thật (Live AI call)** tại quyết định trung tâm (gọi LLM Gemini/OpenAI để phân tầng ưu tiên P1/P2/P3 và trích xuất deadline).
   - Tuyệt đối không gán cứng kết quả (hardcode).
   - Tệp ghi chú `README.md` trong `codebase/` ghi rõ: **phần nào chạy AI thật, phần nào là dữ liệu giả lập (mock)**.
   - **Bắt buộc có cơ chế ghi vết (Trace Log):** Lưu tại `codebase/logs/ai_trace.log` ghi lại `timestamp`, `input_prompt` và `raw_output` của mô hình để giám khảo kiểm tra.
   - Không commit file `.env` chứa API Key thật lên GitHub.

---

### 3. Thư mục `eval/` (Đo lường & Kiểm thử chất lượng)

Đo lường năng lực của giải pháp một cách khách quan bằng số liệu định lượng:
1. **`eval/golden_set.json` (hoặc `.csv`):**
   - Tối thiểu **20 ca kiểm thử độc lập** do nhóm tự xây dựng.
   - Cơ cấu 20 ca:
     - Tối thiểu 2 ca cho mỗi lớp trong **4 lớp chỗ khó** (① Nguồn sự thật, ② Mơ hồ/thiếu thông tin, ③ Ngoài phạm vi/thẩm quyền, ④ Đặc thù nghiệp vụ).
     - 8–10 ca tình huống thông báo phổ biến thường gặp.
     - 2–4 ca hiếm gặp / góc khuất (edge cases).
     - **Ít nhất 10 ca phải trích từ dữ liệu thực tế** (chatlog discord-pack đã ẩn danh).
2. **`eval/run_results.md`:**
   - Bảng kết quả chạy kiểm thử qua các lượt (Lượt 1 ở CP3, Lượt 2/chốt ở CP4).
   - Thống kê: Số ca đạt, số ca hỏng, tỷ lệ % đạt chuẩn.
   - **Phân tích nguyên nhân lỗi:** Bắt buộc giải thích cặn kẽ nguyên nhân vì sao AI phân loại sai ở các ca hỏng (BTC đánh giá cao dữ liệu thực nghiệm trung thực).

---

### 4. Thư mục `validation/` (Kiểm chứng người dùng ngoài nhóm — R6)

Khối điểm cộng mang lại tối đa **8 điểm** (giúp nâng tổng điểm từ 92 lên mức tối đa 100 điểm):
- **`validation/user_testing_log.md`:**
  - Nhật ký thử nghiệm với **ít nhất 5 người dùng bên ngoài nhóm** (trong đó bắt buộc có tối thiểu **2 willing users** đã đăng ký từ mốc CP1).
  - Quy trình thử nghiệm tuân thủ nguyên tắc Mom Test (giao nhiệm vụ cụ thể, giữ im lặng quan sát thao tác, ghi chép điểm nghẽn).
  - Bảng ghi nhận gồm:
    | Người thử (ẩn danh) | Nhiệm vụ giao cho họ | Điểm họ bị tắc nghẽn | Trích dẫn nguyên văn câu nói khi gặp khó | Quyết định xử lý của nhóm |
    |---|---|---|---|---|
  - Dựa trên phản hồi này, nhóm thực hiện ít nhất một điều chỉnh cụ thể trên prototype và cập nhật vào mục **§9 Changelog** của `spec.md`.

---

### 5. Thư mục `reflection/` (Thu hoạch cá nhân — Điểm cá nhân CP6)

Dùng để đánh giá độc lập từng thành viên trong buổi thi đấu và thuyết trình:
- **Mỗi thành viên tự tạo 1 file markdown riêng** đặt tên theo đúng mã học viên:
  - `reflection/2A202602822_ChauTungDuong.md` (Product Lead)
  - `reflection/2A202602735_NguyenDinhTuanAnh.md` (Data & Evidence)
  - `reflection/2A202602971_DoManhNghia.md` (AI & Evaluation)
  - `reflection/2A202603010_NguyenNgocTuyen.md` (UX & Prototype)
- **Nội dung mỗi file reflection bắt buộc trả lời đủ 4 ý:**
  1. Vai trò cá nhân trong dự án.
  2. Phần việc cụ thể trực tiếp đảm nhiệm và hoàn thành.
  3. Cách thức ứng dụng AI/tools trong quá trình xây dựng sản phẩm.
  4. Một bài học thực tế rút ra từ chính các trường hợp thất bại / thử nghiệm hỏng của nhóm.

---

## III. LỘ TRÌNH NỘP BÀI QUA 6 CHECKPOINT (CP1 → CP6)

| Mốc | Tên mốc | Hạn chốt | Sản phẩm cần có trên GitHub | Kênh & Người nộp |
|:---:|---|:---:|---|---|
| **CP1** | Khám phá bài toán & Canvas 7 dòng | 19:30 17/9 | `canvas.md`, `spec.md` (§1, §2, §8) | **Đội trưởng nộp Form CP1** (Kèm Canvas + 4 willing users) |
| **CP2** | Thiết kế luồng & Bản mẫu tương tác | 21:00 16/9 (hoặc ca lớp) | `codebase/web_prototype/`, `spec.md` (§3, §4, §5, §6) | **Đội trưởng nộp Form CP2** (Link Web Prototype Netlify hoặc link GitHub) |
| **CP3** | Prototype AI thật & Đo lường kiểm thử | 16:00 17/9 (hoặc ca lớp) | `codebase/` (bot AI thật + trace log), `eval/golden_set.json` (20 ca), `eval/run_results.md` | **Đội trưởng nộp Form CP3** (Link Video 30s thao tác + Tỷ lệ % test lượt 1) |
| **CP4** | Hoàn thiện Spec & Khóa Quality Bar | 21:00 17/9 | `spec.md` hoàn chỉnh 100% 9 phần; khóa cứng công thức Quality Bar tại §7 | **Đội trưởng nộp Form CP4** (Link trực tiếp đến file `spec.md` trên GitHub) |
| **CP5** | Validation R6, Slide PDF & Video dự phòng | 13:00 18/9 | `demo-slides.pdf` (đúng 6 trang), `validation/user_testing_log.md` (5 users), `spec.md` (§9 Changelog) | **Đội trưởng nộp Form CP5** (Tải file `demo-slides.pdf` + Link video demo dự phòng) |
| **CP6** | Nộp bài tổng kết & Thuyết trình vòng thi | 17:30 18/9 (LAB 6) | Đầy đủ toàn bộ cấu trúc repo kể trên + 4 file trong `reflection/` | **MỌI THÀNH VIÊN** đăng nhập VLearn cá nhân và dán cùng link GitHub repo |

---

## IV. 3 NGUYÊN TẮC SỐNG CÒN CẦN GHI NHỚ

1. **Quy tắc Vibe-Coding:** Được dùng AI hỗ trợ build thoải mái, nhưng bất kỳ thành viên nào không giải thích được phần việc có tên mình thì phần đó nhận **0 điểm** (giám khảo sẽ hỏi ngẫu nhiên khi thuyết trình).
2. **Quy tắc bảo mật dữ liệu:** 
   - Không commit dữ liệu thô trong `data/` vào repo nộp bài.
   - Không commit API Key hay Bot Token lên GitHub.
   - Tuyệt đối ẩn danh hóa, không suy ngược danh tính học viên từ dữ liệu khóa học.
3. **Hai kênh nộp bài song song:**
   - **Kênh 1 (Form CP1–CP5):** Chỉ một mình Đội trưởng nộp, dùng duy nhất một mã học viên của đội trưởng cho cả 5 mốc.
   - **Kênh 2 (VLearn):** Mọi thành viên đều phải tự nộp link repo trên tài khoản VLearn cá nhân. Thiếu ai người đó mất điểm.
