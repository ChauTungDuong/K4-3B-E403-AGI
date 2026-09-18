# Cấu trúc rút gọn — Discord Summary & Trend Bot

Đây là cấu trúc MVP, ưu tiên dễ hiểu và dễ phát triển. Toàn bộ luồng chính chỉ gồm:

```text
Discord → thu thập → ẩn danh → Summary hoặc Trends → kiểm tra → gửi báo cáo
```

Chỉ tách file khi nó đại diện cho một trách nhiệm thực sự khác. Các bước nhỏ như gộp task, xếp ưu tiên hoặc tính điểm xu hướng được giữ dưới dạng hàm trong module nghiệp vụ thay vì tạo thêm nhiều lớp và thư mục.

## 1. Cấu trúc đề xuất

```text
discord-gemini-bot/
├── bot.py                    # Khởi động bot, slash commands và lịch chạy
├── config.py                 # Đọc và kiểm tra .env
├── database.py               # Cấu hình guild, lịch chạy và dữ liệu trend nền
├── models.py                 # Schema dữ liệu dùng chung
├── collector.py              # Đọc message/reply/thread theo khoảng thời gian
├── privacy.py                # Ẩn danh và loại thông tin cá nhân
├── gemini.py                 # Gọi Gemini và parse structured output
├── summary.py                # MODULE 1: tóm tắt và tạo danh sách công việc
├── chat.py                   # Yêu cầu tự nhiên có grounding và giới hạn phạm vi
├── trends.py                 # MODULE 2: phân tích xu hướng của một kênh
├── reporter.py               # Chuyển kết quả thành Discord embeds an toàn
├── time_window.py            # Kiểm tra và tạo khoảng thời gian tương đối
│
├── prompts/
│   ├── summary.txt           # Chỉ dẫn trích xuất summary/task
│   ├── chat.txt              # Trả lời yêu cầu tự nhiên có evidence
│   └── trends.txt            # Chỉ dẫn đặt tên và giải thích trend
│
├── tests/
│   ├── test_summary.py       # Task, priority, deduplicate và evidence
│   ├── test_chat.py          # Natural-language request, grounding và refusal
│   ├── test_trends.py        # Hot/new, baseline, spam và toxic
│   ├── test_privacy.py       # Email, phone, mention, ID và secret
│   └── fixtures.json         # Các đoạn chat mẫu đã được ẩn danh
│
├── .env.example
├── requirements.txt
├── README.md
└── PROJECT_STRUCTURE.md
```

Cấu trúc runtime giữ các nghiệp vụ chính trong `summary.py`, `chat.py` và
`trends.py`; phần Discord orchestration vẫn nằm tại `bot.py`.

## 2. Vai trò và giới hạn của từng file

### `bot.py`

- Khởi tạo Discord bot.
- Khai báo `/summary`, `/trends` và các lệnh cấu hình.
- Chạy scheduler.
- Chọn module cần gọi, nhưng không chứa prompt hay logic phân tích.

Luồng lệnh nên ngắn và dễ đọc:

```python
messages = await collector.collect(channel, time_window)
safe_messages = privacy.sanitize(messages)
result = await summary.analyze(safe_messages)
await reporter.send_summary(channel, result)
```

### `config.py`

Đọc một lần các biến môi trường như token Discord, Gemini API key, model, giới hạn message, cửa sổ summary và baseline trend. File này phải báo lỗi ngay khi thiếu cấu hình bắt buộc.

### `database.py`

Chỉ quản lý ba nhóm dữ liệu:

- cấu hình guild và kênh;
- thời điểm chạy gần nhất;
- số liệu/topic snapshot dùng làm baseline cho trend.

SQLite tiếp tục phù hợp với MVP. Không cần repository layer riêng ở giai đoạn này.

### `models.py`

Chứa các Pydantic model dùng chung:

- `Message`: message đã chuẩn hóa;
- `SafeMessage`: message đã loại thông tin cá nhân;
- `TaskItem` và `SummaryResult`;
- `TopicTrend`, `ToxicityResult` và `TrendResult`.

Schema chặt giúp phát hiện sớm JSON sai hoặc kết quả model thiếu trường.

### `collector.py`

- Đọc message theo `channel + start_time + end_time`.
- Đọc cả reply và thread để tránh mất ngữ cảnh.
- Bỏ message của bot, message rỗng và attachment chưa hỗ trợ.
- Sắp xếp theo thời gian.
- Chia chunk theo hội thoại, không cắt tùy ý giữa một câu hỏi và câu trả lời.

Collector không gọi Gemini và không phân tích nội dung.

### `privacy.py`

Chạy trước Gemini và chạy lại trước khi gửi báo cáo:

- thay username, display name và mention bằng `USER_01`, `USER_02`;
- thay tên kênh nhạy cảm bằng `CHANNEL_01`;
- che email, số điện thoại, địa chỉ, Discord ID, URL cá nhân và secret;
- không ghi raw message vào log;
- chặn đầu ra nếu vẫn phát hiện PII có độ tin cậy cao.

Bảng ánh xạ bí danh chỉ tồn tại trong bộ nhớ của một lần chạy và không gửi sang Gemini.

### `gemini.py`

- Là nơi duy nhất sử dụng `google-genai`.
- Buộc Gemini trả structured output theo Pydantic schema.
- Đặt temperature thấp.
- Retry giới hạn khi JSON không hợp lệ.
- Đóng khung message Discord là dữ liệu không đáng tin, chống prompt injection.

File này không quyết định task nào là P0 hoặc topic nào là hot.

### `reporter.py`

- Chuyển kết quả đã kiểm tra thành Discord embeds.
- Chia nội dung theo giới hạn Discord.
- Dùng `AllowedMentions.none()`.
- Không hiển thị tên thật hoặc ID thật.
- Source link tắt mặc định; chỉ hiển thị mã nguồn như `MSG_012`.

## 3. Module 1 — `summary.py`

Mục tiêu là tạo danh sách việc **ít nhưng đúng**, có nguồn kiểm chứng và không tự suy đoán.

### Luồng xử lý

```text
SafeMessage
   ↓
trích xuất task/decision/question
   ↓
gộp task trùng hoặc task đã được cập nhật
   ↓
kiểm tra bằng chứng
   ↓
xếp P0-P3 theo quy tắc
   ↓
SummaryResult
```

`summary.py` nên có các hàm chính:

```python
async def analyze(messages: list[SafeMessage]) -> SummaryResult: ...
def merge_duplicate_tasks(tasks: list[TaskItem]) -> list[TaskItem]: ...
def assign_priority(task: TaskItem) -> Priority: ...
def validate_evidence(task: TaskItem, messages: list[SafeMessage]) -> bool: ...
```

### Quy tắc đảm bảo độ chính xác

- Chỉ tạo task khi có yêu cầu, cam kết hoặc hành động rõ ràng.
- Mỗi task phải có ít nhất một `evidence_ref` tồn tại trong input.
- Không suy đoán owner hoặc deadline. Không rõ thì để `null`.
- Task giống nhau phải được gộp; cập nhật mới nhất quyết định trạng thái.
- Task bị hủy hoặc đã hoàn thành không được đưa vào danh sách việc đang mở.
- Task mơ hồ được đưa vào `needs_confirmation`, không trộn với task chắc chắn.
- Priority được code kiểm tra lại:
  - P0: sự cố/blocker đang gây ảnh hưởng và cần xử lý ngay;
  - P1: ảnh hưởng cao hoặc deadline gần;
  - P2: công việc bình thường có hành động rõ;
  - P3: ý tưởng/cải tiến có thể hoãn.

Schema task tối thiểu:

```python
class TaskItem(BaseModel):
    title: str
    priority: Literal["P0", "P1", "P2", "P3"]
    status: Literal["open", "in_progress", "blocked", "needs_confirmation"]
    owner_ref: str | None
    deadline: str | None
    reason: str
    confidence: float
    evidence_refs: list[str]
```

## 4. Module 2 — `trends.py`

Mục tiêu là xác định chính xác xu hướng của **một kênh chat**. Không thể kết luận “hot” hoặc “mới” chỉ bằng cách đọc một khoảng chat hiện tại.

### Dữ liệu đầu vào

- `current_messages`: ví dụ 24 giờ gần nhất.
- `baseline_messages` hoặc snapshot: ví dụ 7 ngày trước đó của cùng kênh.

Nếu chưa đủ baseline, bot chỉ được nói “chủ đề nổi bật trong khoảng hiện tại”, không được khẳng định “đang tăng” hoặc “mới”.

### Luồng xử lý

```text
Current window + Baseline window
             ↓
       trích xuất topic
             ↓
      gom topic gần nghĩa
             ↓
tính volume / tốc độ / reaction / số người
             ↓
   so sánh với baseline bằng code
             ↓
Gemini đặt tên và giải thích số liệu
             ↓
          TrendResult
```

`trends.py` nên có các hàm chính:

```python
async def analyze(
    current: list[SafeMessage],
    baseline: list[SafeMessage],
) -> TrendResult: ...

def cluster_topics(messages: list[SafeMessage]) -> list[TopicCluster]: ...
def calculate_metrics(cluster: TopicCluster) -> TrendMetrics: ...
def score_trend(current: TrendMetrics, baseline: TrendMetrics) -> TrendScore: ...
def validate_trend(topic: TopicTrend) -> bool: ...
```

### Tín hiệu dùng để xác định trend

- `volume`: số message về topic;
- `growth`: mức tăng so với baseline;
- `velocity`: tốc độ xuất hiện message;
- `engagement`: reply và reaction;
- `participant_count`: số người ẩn danh tham gia;
- `novelty`: độ khác với các topic trong baseline.

Điểm khởi đầu:

```text
hot_score = 40% growth
          + 25% velocity
          + 20% engagement
          + 15% participant spread
```

Các trọng số nằm trong `config.py` để dễ hiệu chỉnh. Gemini chỉ diễn giải metric đã tính, không tự tạo số liệu hoặc tự quyết định `hot_score`.

### Chống kết luận trend sai

- Một topic phải có số message và số người tham gia tối thiểu.
- Giảm mạnh điểm nếu phần lớn message đến từ một người hoặc là nội dung lặp.
- Không tính reaction đơn lẻ là trend.
- Mỗi kết luận phải có message làm bằng chứng.
- Toxicity được báo theo tỉ lệ nội dung và xu hướng của kênh, không tạo danh sách “người toxic”.
- Phân biệt nội dung công kích với câu đùa, trích dẫn hoặc thảo luận về chính từ ngữ toxic.

Schema trend tối thiểu:

```python
class TopicTrend(BaseModel):
    topic: str
    classification: Literal["hot", "new", "rising", "stable", "declining"]
    message_count: int
    participant_count: int
    growth_rate: float | None
    hot_score: float
    novelty_score: float
    sentiment: Literal["positive", "neutral", "negative", "mixed"]
    confidence: float
    explanation: str
    evidence_refs: list[str]
```

## 5. Luồng các lệnh chính

### `/summary group|channel ... channel_6 hours end_hours_ago`

```text
bot.py
  → collector.collect_channels_atomic(channels, hours)
  → privacy.sanitize(messages của các kênh đầy đủ)
  → summary.analyze(safe_messages) theo từng kênh
  → privacy.check_output(result)
  → reporter.send_summary(từng phần)
```

### `/chat input group|channel ... channel_6 hours end_hours_ago`

```text
bot.py
  → collector.collect_channels_atomic(channels, hours)
  → privacy.sanitize(messages) + che PII trong input
  → chat.answer(input, safe_messages)
  → kiểm tra evidence_refs + privacy.check_output(result)
  → trả embed có jump link dưới dạng ephemeral
```

### `/trends group|channel current_hours end_hours_ago baseline_days`

```text
bot.py
  → collector.collect(current window + baseline window)
  → privacy.sanitize(messages)
  → trends.analyze(current, baseline)
  → database.save_trend_snapshot(metrics)
  → privacy.check_output(result)
  → reporter.send_trends(result)
```

## 6. Cấu hình tối thiểu

`.env.example`:

```dotenv
DISCORD_BOT_TOKEN=
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
DATABASE_PATH=bot.db

SUMMARY_DEFAULT_HOURS=24
TREND_CURRENT_HOURS=24
TREND_BASELINE_DAYS=7

MIN_TASK_CONFIDENCE=0.75
MIN_TOPIC_MESSAGES=3
MIN_TOPIC_PARTICIPANTS=2
HOT_SCORE_THRESHOLD=0.70
MAX_TOTAL_MESSAGES=1000
MAX_INPUT_CHARACTERS=200000
```

## 7. Kiểm thử tối thiểu bắt buộc

Chỉ giữ bốn file test nhưng phải bao phủ các lỗi quan trọng:

- `test_summary.py`: task thật, câu nói vu vơ, task trùng, task bị hủy, deadline mơ hồ và evidence sai.
- `test_trends.py`: topic tăng thật, topic vốn đã phổ biến, topic mới, spam một người và toxic false positive.
- `test_privacy.py`: username, mention, email, phone, Discord ID và API key không xuất hiện trong prompt/output.
- `fixtures.json`: hội thoại đầu vào và kết quả mong đợi để so sánh khi đổi prompt/model.

Các chỉ số cần theo dõi chỉ gồm:

- task precision và task recall;
- priority accuracy;
- evidence validity;
- hot/new classification accuracy;
- toxicity false-positive rate;
- privacy leak count, mục tiêu bằng 0.

## 8. Cách chuyển từ code hiện tại

1. Tách model và database từ `bot.py` sang `models.py`, `database.py`.
2. Tách thu thập message sang `collector.py`.
3. Thêm `privacy.py` trước khi tiếp tục dùng Gemini.
4. Tách prompt/schema hiện tại thành `summary.py` và `trends.py`.
5. Bổ sung baseline cho trend; bỏ cách kết luận hot/new chỉ từ một time window.
6. Cuối cùng rút `bot.py` về phần command, scheduler và điều phối.

Không cần tạo toàn bộ file cùng lúc. Thứ tự trên cho phép bot vẫn chạy sau từng bước và mỗi bước đều cải thiện trực tiếp một trong hai chức năng chính.
