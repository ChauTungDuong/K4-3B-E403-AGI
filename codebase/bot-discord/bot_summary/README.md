# Discord Gemini Summary Bot

Bot có hai pipeline độc lập:

- Tóm tắt hội thoại và tạo danh sách công việc P0–P3 có nguồn kiểm chứng.
- Phân tích xu hướng của một kênh bằng cách so sánh cửa sổ hiện tại với baseline.

Tên người dùng, mention, email, số điện thoại, Discord ID, URL và secret được che trước khi gửi tới Gemini. Đầu ra được quét lại trước khi gửi về Discord.

## Cài đặt

Yêu cầu Python 3.11 trở lên.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Điền `DISCORD_BOT_TOKEN`, `GEMINI_API_KEY` và tùy chọn `DISCORD_GUILD_ID` trong `.env`. Bot cần bật `Message Content Intent` và có các quyền:

- `View Channel`
- `Read Message History`
- `Send Messages`
- `Embed Links`

Chạy bot:

```powershell
python bot.py
```

## Cấu hình trong Discord

Quản trị viên dùng:

```text
/add-source channel:#backend
/setup-output channel:#ai-report
/set-interval hours:6
/config
```

Thành viên có quyền đọc kênh nguồn có thể dùng:

```text
/summary channel:#thông-báo channel_2:#backend channel_3:#thảo-luận hours:24
/trends channel:#backend current_hours:24 baseline_days:7
```

`/summary` nhận tối đa 6 kênh. `channel` có ưu tiên cao nhất, sau đó lần lượt
đến `channel_6`. Mỗi kênh được hiển thị thành một phần riêng với tiêu đề
`Ưu tiên N · #tên-kênh`.

Bot chỉ đưa một kênh vào bản tóm tắt khi đã lấy được **toàn bộ** tin hợp lệ
trong cửa sổ thời gian. Nếu context còn lại chỉ chứa được một phần của kênh kế
tiếp, bot bỏ nguyên kênh đó và mọi kênh ưu tiên thấp hơn, chỉ tóm tắt các kênh
đã lấy trọn vẹn, rồi báo rõ danh sách bị bỏ cho người gọi. Báo cáo định kỳ dùng
thứ tự các kênh đã được thêm bằng `/add-source`; xóa rồi thêm lại một kênh sẽ
đưa kênh đó xuống cuối thứ tự ưu tiên.

Kết quả được gửi vào kênh output đã cấu hình. Digest dùng khung 🔴/🟡/🟢 tối đa 8 dòng; bản tin trend dùng khung 🔥/💡 tối đa 10 dòng. Mỗi mục có channel mention và jump link tới tin gốc khi có bằng chứng hợp lệ. Trạng thái lệnh và lỗi chỉ hiện với người gọi.

Báo cáo trend ban đầu chỉ hiển thị kết luận chung. Người dùng bấm `📊 Xem chi tiết` để mở topic và số liệu trong phản hồi riêng tư; nút hoạt động trong 60 phút sau khi báo cáo được gửi.

## Cách đảm bảo chất lượng

Summary chỉ giữ task có `evidence_ref` hợp lệ, không tự đoán owner/deadline, loại task đã xong hoặc bị hủy và kiểm tra lại P0 bằng code.

Trends dùng Gemini để gom/đặt tên topic, còn số message, tăng trưởng, tốc độ, engagement, số người tham gia và điểm hot được tính bằng code. Khi không có baseline, bot không khẳng định topic là mới hoặc đang tăng.

## Kiểm thử

```powershell
python -m unittest discover -s tests -v
```

Chi tiết kiến trúc nằm trong [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md). Sơ đồ dữ liệu trước và sau từng bước nằm trong [DATA_FLOW.md](DATA_FLOW.md).
