# Sơ đồ luồng dữ liệu

Tài liệu này mô tả dữ liệu đi từ Discord đến báo cáo cuối cùng, trường nào được giữ lại, trường nào bị thay thế và dữ liệu nào được lưu.

## 1. Toàn cảnh

```mermaid
flowchart TD
    A["Discord API<br/>Tin nhắn gốc + danh tính thật"]
    B{"Collector<br/>Lọc theo kênh và thời gian"}
    DROP["Bị loại<br/>• Ngoài time window<br/>• Content rỗng<br/>• Tin của Bot Summary<br/>• Bot/app khác nếu cấu hình tắt"]
    RAW["Message — chỉ trong RAM<br/>message_id, channel_id/name<br/>author_id/name, time, content<br/>reaction, reply"]
    P["PrivacySanitizer<br/>Ẩn danh + che PII"]
    SAFE["SafeMessage<br/>MSG_xxx, CHANNEL_xx, USER_xx<br/>time, content đã che<br/>reaction, reply"]
    S{"Chọn pipeline"}
    SUM["SUMMARY<br/>Trích task/decision/question"]
    TREND["TRENDS<br/>Current + Baseline"]
    SV["Kiểm chứng bằng code<br/>evidence, priority, deadline<br/>confidence, deduplicate"]
    TV["Tính metric bằng code<br/>growth, velocity, engagement<br/>participant, hot, novelty"]
    SR["SummaryResult"]
    TR["TrendResult"]
    DB[("SQLite<br/>Chỉ lưu TrendResult đã ẩn danh<br/>+ guild/channel metadata")]
    OG["Output Guard<br/>Quét PII lần cuối"]
    OUT["Discord<br/>Tổng quan công khai + nút chi tiết<br/>Chi tiết ephemeral cho người bấm"]
    BLOCK["Chặn gửi<br/>nếu còn dấu hiệu PII"]

    A --> B
    B --> DROP
    B --> RAW
    RAW --> P
    P --> SAFE
    SAFE --> S
    S --> SUM
    S --> TREND
    SUM --> SV --> SR --> OG
    TREND --> TV --> TR
    TR --> DB
    TR --> OG
    OG -->|An toàn| OUT
    OG -->|Phát hiện PII| BLOCK

    classDef danger fill:#ffe2e2,stroke:#d33,color:#600;
    classDef safe fill:#e1f5e8,stroke:#25834b,color:#123;
    classDef process fill:#e7efff,stroke:#3765b0,color:#123;
    class DROP,BLOCK danger;
    class SAFE,SR,TR,OUT safe;
    class B,P,S,SUM,TREND,SV,TV,OG process;
```

## 2. Dữ liệu thay đổi như thế nào

| Giai đoạn | Dữ liệu đang có | Bị loại hoặc thay thế | Đi tiếp đến đâu |
|---|---|---|---|
| Discord API | ID thật, tên kênh, tên/ID tác giả, thời gian, content, reaction, reply | Chưa thay đổi | `collector.py` |
| Collector | Tạo đối tượng `Message` | Bỏ tin ngoài thời gian, content rỗng, tin của chính Bot Summary; bot/app khác phụ thuộc `INCLUDE_BOT_MESSAGES` | RAM |
| Privacy | Nhận `Message` còn thông tin thật | `message_id → MSG_001`, `author → USER_01`, `channel → CHANNEL_01`; che email, phone, IP, địa chỉ, URL, secret | `SafeMessage` |
| Gemini input | Chỉ nhận `SafeMessage` | Không nhận ID thật, username/display name hoặc tên kênh thật | Summary hoặc Trends |
| Validation | Nhận bản nháp từ Gemini | Loại ID nguồn bịa, kết luận thiếu nguồn, task hoàn thành/hủy và dữ liệu không đủ tin cậy | Kết quả cuối |
| Output guard | Nhận JSON kết quả đã ẩn danh | Chặn toàn bộ report nếu vẫn phát hiện mẫu PII | Discord Embed |

### Ví dụ trước và sau Privacy

```text
TRƯỚC — Message, chỉ tồn tại trong RAM
{
  message_id: 1550123456789012345,
  channel_id: 1550987654321098765,
  channel_name: "thông-báo-lớp-học",
  author_id: 1550111122223333444,
  author_name: "Nguyễn Văn A",
  created_at: "2026-09-18T05:46:00Z",
  content: "A gửi file cho B, email a@example.com",
  reaction_count: 3,
  reply_count: 1,
  reply_to_id: null
}

SAU — SafeMessage, được phép gửi Gemini
{
  ref: "MSG_001",
  channel_ref: "CHANNEL_01",
  author_ref: "USER_01",
  created_at: "2026-09-18T05:46:00Z",
  content: "USER_01 gửi file cho USER_02, email [EMAIL]",
  reaction_count: 3,
  reply_count: 1,
  reply_to_ref: null
}
```

Bảng ánh xạ giữa ID thật và `USER_xx`/`MSG_xxx` chỉ tồn tại trong bộ nhớ của lần chạy. Nó không được gửi sang Gemini và không được lưu vào SQLite.

## 3. Luồng `/summary`

```mermaid
flowchart LR
    A["SafeMessage[]"] --> B["Gemini<br/>SummaryDraft"]
    B --> C["TaskCandidate[]<br/>Decision[]<br/>OpenQuestion[]"]
    C --> D{"Evidence hợp lệ?"}
    D -->|Không| X["Loại"]
    D -->|Có| E{"Trạng thái"}
    E -->|done / cancelled| X
    E -->|đang mở| F["Kiểm tra owner/deadline"]
    F --> G{"Confidence"}
    G -->|dưới 0.5| X
    G -->|0.5 đến dưới ngưỡng| H["needs_confirmation"]
    G -->|đủ ngưỡng| I["Giữ trạng thái"]
    H --> J["Kiểm tra P0-P3<br/>Gộp task trùng"]
    I --> J
    J --> K["SummaryResult"]
    K --> L["Output guard"]
    L --> M["Discord Embed"]

    classDef danger fill:#ffe2e2,stroke:#d33,color:#600;
    classDef safe fill:#e1f5e8,stroke:#25834b,color:#123;
    class X danger;
    class K,M safe;
```

### SummaryDraft do Gemini trả về

```text
executive_summary
tasks[]
  ├─ title
  ├─ priority: P0 | P1 | P2 | P3
  ├─ status
  ├─ owner_ref
  ├─ deadline
  ├─ reason
  ├─ confidence
  └─ evidence_refs[]
decisions[]
open_questions[]
```

### SummaryResult còn lại sau kiểm chứng

- Task có ít nhất một `evidence_ref` tồn tại.
- Task `done` hoặc `cancelled` đã bị loại.
- Owner không xuất hiện trong nguồn bị đổi thành `null`.
- Deadline không có nguyên văn trong nguồn bị đổi thành `null`.
- Confidence dưới `0.5` bị loại; chưa đạt ngưỡng chính được đưa vào `needs_confirmation`.
- Task gần giống nhau được gộp và sắp theo P0 → P3.
- Chỉ giữ tối đa 16 task, 5 decision và 5 open question.

`SummaryResult` không được lưu vào database; nó chỉ tồn tại trong RAM cho đến khi gửi Discord.

## 4. Luồng `/trends`

```mermaid
flowchart TD
    A["Tin cùng một kênh"]
    A --> C["Current window<br/>Ví dụ: 24 giờ"]
    A --> B["Baseline window<br/>Ví dụ: 7 ngày trước đó"]
    C --> P["Ẩn danh chung<br/>để alias nhất quán"]
    B --> P
    P --> G["Gemini gom topic<br/>và trả message refs"]
    G --> V["Loại ref không tồn tại"]
    V --> M["Python tính metric"]
    M --> M1["message_count"]
    M --> M2["participant_count"]
    M --> M3["growth_rate"]
    M --> M4["velocity + engagement"]
    M --> M5["hot_score + novelty_score"]
    M --> S{"Đủ sample + baseline?"}
    S -->|Không| N["insufficient_data"]
    S -->|Có| CL["new / hot / rising<br/>stable / declining"]
    N --> R["TrendResult"]
    CL --> R
    R --> DB[("trend_snapshots")]
    R --> O["Output guard"]
    O --> D["Discord Embed"]

    classDef safe fill:#e1f5e8,stroke:#25834b,color:#123;
    classDef store fill:#fff2cc,stroke:#b18a00,color:#543;
    class R,D safe;
    class DB store;
```

### Gemini chỉ tạo bản nháp topic

```text
TopicCandidate
  ├─ topic
  ├─ current_refs[]
  ├─ baseline_refs[]
  ├─ sentiment
  ├─ toxic_refs[]
  └─ explanation
```

### Python tính kết quả định lượng

```text
TopicTrend
  ├─ classification
  ├─ message_count
  ├─ participant_count
  ├─ growth_rate
  ├─ hot_score
  ├─ novelty_score
  ├─ sentiment
  ├─ confidence
  ├─ explanation
  └─ evidence_refs[]
```

Gemini không tự tạo `hot_score` hoặc `growth_rate`. Các giá trị này được tính từ message refs hợp lệ. Nếu phần lớn tin đến từ một tác giả, `hot_score` bị giảm để chống spam tạo trend giả.

## 5. Dữ liệu được gửi, lưu và không lưu

```mermaid
flowchart LR
    RAW["Raw Message<br/>có danh tính thật"] -->|Chỉ RAM| P["Privacy"]
    P --> SAFE["SafeMessage"]
    SAFE -->|Gửi| GEMINI["Gemini API"]
    SAFE -->|Không lưu trực tiếp| END["Hủy sau lần chạy"]
    GEMINI --> RESULT["SummaryResult / TrendResult"]
    RESULT -->|Summary| RAM["Chỉ RAM + Discord"]
    RESULT -->|Trend| DB[("SQLite snapshot")]

    classDef danger fill:#ffe2e2,stroke:#d33,color:#600;
    classDef safe fill:#e1f5e8,stroke:#25834b,color:#123;
    class RAW danger;
    class SAFE,RESULT,RAM safe;
```

| Loại dữ liệu | Gửi Gemini | Lưu SQLite | Trả về Discord |
|---|---:|---:|---:|
| Raw message có ID/tên thật | Không | Không | Không |
| SafeMessage đã ẩn danh | Có | Không | Không trực tiếp |
| SummaryResult | Không gửi lại | Không | Có |
| TrendResult | Không gửi lại | Có | Có |
| Guild ID và channel ID cấu hình | Không | Có | Không hiển thị trong report |
| Bảng ánh xạ ID thật → alias | Không | Không | Không |

## 6. Những nội dung hiện chưa đi qua pipeline

- Attachment và nội dung file chưa được đọc.
- Text chỉ nằm trong Discord embed chưa được đưa vào `content`.
- Hình ảnh chưa OCR.
- Audio/video chưa được chuyển thành text.
- Reaction chỉ dùng số lượng, chưa phân biệt loại emoji.
- Tin có `content` rỗng vẫn bị bỏ qua, kể cả khi nó có attachment hoặc embed.

Điều này có nghĩa `INCLUDE_BOT_MESSAGES=true` cho phép đọc text do bot/app khác gửi, nhưng chưa giúp đọc các app chỉ gửi Discord embed không có `message.content`.

## 7. Ảnh hưởng của cấu hình

```text
INCLUDE_BOT_MESSAGES=false
  └─ Giữ tin người dùng, bỏ mọi bot/app.

INCLUDE_BOT_MESSAGES=true
  ├─ Giữ tin người dùng.
  ├─ Giữ text từ bot/app khác.
  └─ Vẫn bỏ tin của chính Bot Summary.
```

Các giới hạn khác:

- `SUMMARY_DEFAULT_HOURS`: cửa sổ mặc định của summary.
- `TREND_CURRENT_HOURS`: cửa sổ hiện tại của trends.
- `TREND_BASELINE_DAYS`: số ngày baseline.
- `MAX_MESSAGES_PER_CHANNEL`: số tin tối đa mỗi kênh.
- `MAX_TOTAL_MESSAGES`: số tin tối đa toàn lượt chạy.
- `MAX_INPUT_CHARACTERS`: tổng số ký tự tối đa gửi phân tích.
