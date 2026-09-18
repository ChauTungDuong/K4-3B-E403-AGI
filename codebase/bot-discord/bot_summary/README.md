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
/add-source channel:#thông-báo
/add-source channel:#backend
/add-source channel:#thảo-luận
/setup-output channel:#ai-report
/group-set name:du-an-a channel:#thông-báo channel_2:#backend channel_3:#thảo-luận
/set-interval hours:6
/config
```

Thành viên có quyền đọc kênh nguồn có thể dùng:

```text
/summary channel:#thông-báo channel_2:#backend channel_3:#thảo-luận hours:24
/summary group:du-an-a hours:24 end_hours_ago:12
/summary group:du-an-a start_at:"2026-09-20 08:30" end_at:"2026-09-20 17:15"
/chat input:"Chỉ liệt kê deadline dạng checklist" channel:#thông-báo hours:24
/trends group:du-an-a current_hours:24 baseline_days:7
/help
```

`/group-set` tạo mới hoặc thay toàn bộ danh sách của một nhóm, tối đa 6 kênh,
theo đúng thứ tự ưu tiên đã chọn. Các kênh phải được cho phép trước bằng
`/add-source`. Dùng `/groups` để xem nhóm và
`/group-remove` để xóa. `/summary`, `/chat` và `/trends` đều nhận tham số
`group`; không dùng `group` cùng lúc với các tham số `channel`.

`/summary` nhận tối đa 6 kênh. `channel` có ưu tiên cao nhất, sau đó lần lượt
đến `channel_6`. Mỗi kênh được hiển thị thành một phần riêng với tiêu đề
`Ưu tiên N · #tên-kênh`.

Bot chỉ đưa một kênh vào bản tóm tắt khi đã lấy được **toàn bộ** tin hợp lệ
trong cửa sổ thời gian. Nếu context còn lại chỉ chứa được một phần của kênh kế
tiếp, bot bỏ nguyên kênh đó và mọi kênh ưu tiên thấp hơn, chỉ tóm tắt các kênh
đã lấy trọn vẹn, rồi báo rõ danh sách bị bỏ cho người gọi. Báo cáo định kỳ dùng
thứ tự các kênh đã được thêm bằng `/add-source`; xóa rồi thêm lại một kênh sẽ
đưa kênh đó xuống cuối thứ tự ưu tiên.

`/chat` nhận yêu cầu tự nhiên trong tham số `input`. Có thể bỏ `channel` để
dùng toàn bộ kênh nguồn đã cấu hình, hoặc chọn tối đa 6 kênh theo cùng thứ tự
ưu tiên như `/summary`. Ví dụ:

```text
/chat input:"Tóm tắt các thay đổi lịch học thành bullet"
/chat input:"Only show confirmed deadlines in English" channel:#thông-báo
/chat input:"Có thông tin review cuối tuần không?" hours:48
```

Câu trả lời `/chat` chỉ hiện riêng cho người gọi, có link về message nguồn và
vẫn áp dụng quy tắc lấy trọn từng kênh. Yêu cầu làm hộ bài, cấp quyền, duyệt
nghỉ/gia hạn, tiết lộ danh tính/secret hoặc bỏ qua kiểm chứng sẽ bị từ chối.

Các lệnh phân tích mặc định đọc từ 24 giờ trước đến hiện tại. `hours` của
`/summary` và `/chat` (hoặc `current_hours` của `/trends`) là mốc bắt đầu;
`end_hours_ago` là mốc kết thúc. Ví dụ `hours:24 end_hours_ago:12` đọc từ
24 giờ trước đến 12 giờ trước. Mốc kết thúc phải nhỏ hơn mốc bắt đầu.

Để chọn chính xác ngày, giờ và phút, truyền đồng thời `start_at` và `end_at`
theo dạng `YYYY-MM-DD HH:mm`. Mốc không ghi múi giờ được hiểu là giờ Việt Nam
(UTC+7); cũng có thể dùng ISO 8601 kèm múi giờ, ví dụ
`2026-09-20T01:30+00:00`. Khi có đủ hai mốc tuyệt đối, bot bỏ qua
`hours`/`current_hours` và `end_hours_ago`. Nếu không truyền hai mốc này, hành
vi mặc định theo số giờ vẫn giữ nguyên. `/trends` dùng khoảng tuyệt đối làm cửa
sổ hiện tại và vẫn lấy `baseline_days` ngay trước `start_at`. Khoảng được chọn
không dài quá 168 giờ, giống giới hạn của cách nhập theo số giờ.

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
