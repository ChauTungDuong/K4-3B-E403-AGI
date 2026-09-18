const channelData = {
  assistant: {
    title: "trợ-lý-tổng-hợp",
    description: "Hỏi nhanh, nhận tóm tắt có nguồn từ toàn bộ server",
    icon: "✦",
    placeholder: "Nhắn #trợ-lý-tổng-hợp"
  },
  general: {
    title: "chung",
    description: "Trao đổi chung của cộng đồng VinAI Campus",
    icon: "#",
    placeholder: "Nhắn #chung"
  },
  announcements: { title: "thông-báo", description: "Thông tin chính thức từ giảng viên", icon: "#" },
  assignments: { title: "bài-tập", description: "Đề bài, deadline và hướng dẫn nộp", icon: "#" },
  schedule: { title: "lịch-học", description: "Lịch học, workshop và thay đổi mới nhất", icon: "#" },
  discussion: { title: "thảo-luận", description: "Chia sẻ tài liệu và trao đổi chuyên môn", icon: "#" },
  support: { title: "hỗ-trợ", description: "Đặt câu hỏi và nhận hỗ trợ từ mentor", icon: "#" }
};

let currentChannel = "assistant";
let toastTimer;

const appShell = document.querySelector(".app-shell");
const channelSidebar = document.getElementById("channelSidebar");
const memberSidebar = document.getElementById("memberSidebar");
const assistantView = document.getElementById("assistantView");
const generalView = document.getElementById("generalView");
const placeholderView = document.getElementById("placeholderView");
const messageScroll = document.getElementById("messageScroll");
const messageInput = document.getElementById("messageInput");
const chatForm = document.getElementById("chatForm");
const dynamicMessages = document.getElementById("dynamicMessages");
const mobileScrim = document.getElementById("mobileScrim");
const searchInput = document.getElementById("searchInput");

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function nowLabel() {
  return new Intl.DateTimeFormat("vi-VN", {
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date());
}

function showToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.classList.add("show");
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => toast.classList.remove("show"), 2200);
}

function closeMobileSidebar() {
  channelSidebar.classList.remove("open");
  mobileScrim.classList.remove("show");
}

function switchChannel(channelName, options = {}) {
  const channel = channelData[channelName] || channelData.general;
  currentChannel = channelName;

  document.querySelectorAll(".channel-item[data-channel]").forEach((item) => {
    item.classList.toggle("active", item.dataset.channel === channelName);
  });

  assistantView.classList.toggle("active", channelName === "assistant");
  generalView.classList.toggle("active", channelName === "general");
  placeholderView.classList.toggle("active", !["assistant", "general"].includes(channelName));

  document.getElementById("channelTitle").textContent = channel.title;
  document.getElementById("channelDescription").textContent = channel.description;
  document.getElementById("headingIcon").textContent = channel.icon;
  messageInput.placeholder = channel.placeholder || `Nhắn #${channel.title}`;

  if (!["assistant", "general"].includes(channelName)) {
    document.getElementById("placeholderTitle").textContent = `Chào mừng đến với #${channel.title}!`;
    document.getElementById("placeholderText").textContent = channel.description;
  }

  searchInput.value = "";
  clearSearch();
  closeMobileSidebar();

  window.requestAnimationFrame(() => {
    if (options.toSource && channelName === "general") {
      const source = generalView.querySelector(".source-message");
      source.scrollIntoView({ behavior: "smooth", block: "center" });
      source.classList.add("source-highlight");
      window.setTimeout(() => source.classList.remove("source-highlight"), 1500);
      showToast("Đã mở tin nhắn nguồn trong #chung");
    } else if (options.atTop) {
      messageScroll.scrollTop = 0;
    } else {
      messageScroll.scrollTop = channelName === "assistant" ? messageScroll.scrollHeight : 0;
    }
  });
}

function clearSearch() {
  document.querySelectorAll(".message.is-search-hidden").forEach((message) => {
    message.classList.remove("is-search-hidden");
  });
}

function createUserMessage(text) {
  return `
    <article class="message user-message">
      <div class="avatar avatar-user">T</div>
      <div class="message-body">
        <div class="message-meta"><strong>tuienn</strong><time>Hôm nay lúc ${nowLabel()}</time></div>
        <p>${escapeHtml(text)}</p>
      </div>
    </article>`;
}

function createTypingMessage() {
  return `
    <article class="message bot-message typing-message" id="typingMessage">
      <div class="avatar avatar-bot">✦</div>
      <div class="message-body">
        <div class="message-meta"><strong>Trợ Lý Tổng Hợp</strong><span class="app-tag">ỨNG DỤNG</span></div>
        <div class="typing-bubbles" aria-label="Trợ lý đang xử lý"><span></span><span></span><span></span></div>
      </div>
    </article>`;
}

function responseShell(content, responseClass = "") {
  return `
    <article class="message bot-message">
      <div class="avatar avatar-bot">✦</div>
      <div class="message-body">
        <div class="message-meta"><strong>Trợ Lý Tổng Hợp</strong><span class="app-tag">ỨNG DỤNG</span><time>Hôm nay lúc ${nowLabel()}</time><span class="latency">1,4 giây</span></div>
        <div class="response-card ${responseClass}">${content}</div>
      </div>
    </article>`;
}

function digestResponse() {
  return responseShell(`
    <div class="response-head">
      <div><span class="response-kicker">BẢN TIN ƯU TIÊN · 24 GIỜ</span><h2>3 việc bạn cần biết</h2></div>
      <span class="verified-badge">✓ Đã kiểm tra nguồn</span>
    </div>
    <ol class="digest-list">
      <li class="priority-item p1"><span class="priority-badge">P1</span><div><strong>Nộp Assignment 03 trước 23:59 hôm nay</strong><p>PDF tối đa 10 trang. Deadline được giảng viên xác nhận lại lúc 08:27.</p><button class="source-link" data-jump="general">#chung · Xem tin gốc ↗</button></div><time>Còn 8 giờ</time></li>
      <li class="priority-item p1"><span class="priority-badge">P1</span><div><strong>Workshop AI Agent chuyển sang 20:00</strong><p>Tham gia ở Voice · Workshop, link cũ vẫn dùng được.</p><button class="source-link" data-jump="general">#chung · Xem tin gốc ↗</button></div><time>20:00</time></li>
      <li class="priority-item p2"><span class="priority-badge">P2</span><div><strong>Bộ tài liệu MCP Server đã sẵn sàng</strong><p>Gồm slide và code mẫu trong thread MCP resources.</p><button class="source-link" data-jump="discussion">#thảo-luận · Mở thread ↗</button></div><time>09:12</time></li>
    </ol>
    <div class="response-foot"><span>362 tin · 6 kênh · 3 sự kiện được xếp hạng</span><div class="feedback"><span>Kết quả này hữu ích?</span><button aria-label="Hữu ích">👍</button><button aria-label="Chưa đúng">👎</button></div></div>
  `, "digest-card");
}

function insightResponse() {
  return responseShell(`
    <div class="response-head">
      <div><span class="response-kicker">PHÂN TÍCH #CHUNG · 24 GIỜ</span><h2>Hoạt động cao, hội thoại lành mạnh</h2></div>
      <span class="verified-badge">✓ 427 tin đã phân tích</span>
    </div>
    <div class="metric-grid">
      <div class="metric"><span>TIN NHẮN</span><strong>427</strong><small>↑ 18% so với hôm qua</small></div>
      <div class="metric"><span>NGƯỜI THAM GIA</span><strong>63</strong><small>14 người mới hoạt động</small></div>
      <div class="metric"><span>SỨC KHỎE</span><strong>92</strong><small>3/427 tin cần lưu ý</small></div>
    </div>
    <div class="topic-list">
      <div class="topic-row"><span>01</span><div><b>LangGraph & agent workflow</b><small>84 tin · 31 người · đang tăng 54%</small></div><span class="score">87 hot</span></div>
      <div class="topic-row"><span>02</span><div><b>MCP Server</b><small>62 tin · 24 người · đang tăng 32%</small></div><span class="score">73 hot</span></div>
      <div class="topic-row"><span>03</span><div><b>Assignment 03</b><small>48 tin · 29 người · ổn định</small></div><span class="score">68 hot</span></div>
    </div>
    <div class="response-foot"><span>Không phát hiện công kích cá nhân · 2 tin spam đã loại</span><div class="feedback"><span>Kết quả này hữu ích?</span><button aria-label="Hữu ích">👍</button><button aria-label="Chưa đúng">👎</button></div></div>
  `, "insight-card");
}

function hotResponse() {
  return responseShell(`
    <div class="response-head"><div><span class="response-kicker">CHỦ ĐỀ ĐANG NÓNG · #CHUNG</span><h2>LangGraph dẫn đầu thảo luận</h2></div><span class="verified-badge">↗ Xu hướng 24 giờ</span></div>
    <div class="topic-list">
      <div class="topic-row"><span>01</span><div><b>LangGraph & agent workflow</b><small>20 tin/giờ · 31 người tham gia</small></div><span class="score">87 hot</span></div>
      <div class="topic-row"><span>02</span><div><b>MCP Server</b><small>13 tin/giờ · 24 người tham gia</small></div><span class="score">73 hot</span></div>
      <div class="topic-row"><span>03</span><div><b>Assignment 03</b><small>9 tin/giờ · 29 người tham gia</small></div><span class="score">68 hot</span></div>
    </div>
    <div class="response-foot"><span>Xếp hạng từ tin nhắn, người tham gia, reply, reaction và tốc độ tăng</span><div class="feedback"><button aria-label="Hữu ích">👍</button><button aria-label="Chưa đúng">👎</button></div></div>
  `, "insight-card");
}

function healthResponse() {
  return responseShell(`
    <div class="response-head"><div><span class="response-kicker">SỨC KHỎE HỘI THOẠI · #CHUNG</span><h2>92/100 — Lành mạnh</h2></div><span class="verified-badge">✓ Không có cảnh báo nghiêm trọng</span></div>
    <div class="metric-grid">
      <div class="metric"><span>TIN BÌNH THƯỜNG</span><strong>424</strong><small>99,3% tổng số tin</small></div>
      <div class="metric"><span>CẦN LƯU Ý</span><strong>3</strong><small>Giọng điệu gay gắt nhẹ</small></div>
      <div class="metric"><span>SPAM ĐÃ LỌC</span><strong>2</strong><small>Không đưa vào phân tích</small></div>
    </div>
    <div class="response-foot"><span>Không phát hiện quấy rối hoặc công kích cá nhân</span><div class="feedback"><span>Đánh giá chính xác?</span><button aria-label="Hữu ích">👍</button><button aria-label="Chưa đúng">👎</button></div></div>
  `, "insight-card");
}

function defaultResponse(text) {
  const shortQuestion = escapeHtml(text.length > 80 ? `${text.slice(0, 77)}...` : text);
  return responseShell(`
    <div class="response-head"><div><span class="response-kicker">KẾT QUẢ TỔNG HỢP</span><h2>Mình hiểu câu hỏi của bạn</h2></div><span class="verified-badge">✓ Phạm vi: kênh được phép xem</span></div>
    <div class="topic-list">
      <div class="topic-row"><span>→</span><div><b>“${shortQuestion}”</b><small>Mình tìm thấy 3 thông tin liên quan trong 24 giờ qua.</small></div><span class="score">3 nguồn</span></div>
    </div>
    <div class="response-foot"><span>Thử hỏi “Có gì quan trọng?” hoặc dùng /insight #chung 24h</span><div class="feedback"><button aria-label="Hữu ích">👍</button><button aria-label="Chưa đúng">👎</button></div></div>
  `, "insight-card");
}

function getBotResponse(text) {
  const normalized = text.toLowerCase();
  if (normalized.includes("insight") || normalized.includes("phân tích")) return insightResponse();
  if (normalized.includes("health") || normalized.includes("sức khỏe") || normalized.includes("toxic")) return healthResponse();
  if (normalized.includes("hot") || normalized.includes("chủ đề") || normalized.includes("đang nóng")) return hotResponse();
  if (normalized.includes("digest") || normalized.includes("quan trọng") || normalized.includes("cần làm") || normalized.includes("bỏ lỡ")) return digestResponse();
  return defaultResponse(text);
}

function submitMessage(text) {
  const cleaned = text.trim();
  if (!cleaned) return;

  if (currentChannel !== "assistant") {
    switchChannel("assistant");
  }

  dynamicMessages.insertAdjacentHTML("beforeend", createUserMessage(cleaned));
  dynamicMessages.insertAdjacentHTML("beforeend", createTypingMessage());
  messageScroll.scrollTo({ top: messageScroll.scrollHeight, behavior: "smooth" });

  window.setTimeout(() => {
    document.getElementById("typingMessage")?.remove();
    dynamicMessages.insertAdjacentHTML("beforeend", getBotResponse(cleaned));
    messageScroll.scrollTo({ top: messageScroll.scrollHeight, behavior: "smooth" });
  }, 650);
}

document.querySelectorAll(".channel-item[data-channel]").forEach((item) => {
  item.addEventListener("click", () => switchChannel(item.dataset.channel));
});

document.querySelectorAll(".command-card").forEach((button) => {
  button.addEventListener("click", () => submitMessage(button.dataset.command));
});

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const value = messageInput.value;
  messageInput.value = "";
  messageInput.style.height = "auto";
  chatForm.classList.remove("has-content");
  submitMessage(value);
});

messageInput.addEventListener("input", () => {
  chatForm.classList.toggle("has-content", messageInput.value.trim().length > 0);
  messageInput.style.height = "auto";
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 110)}px`;
});

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

document.addEventListener("click", (event) => {
  const sourceLink = event.target.closest(".source-link");
  if (sourceLink) {
    const target = sourceLink.dataset.jump;
    if (target === "general") {
      switchChannel("general", { toSource: true });
    } else {
      switchChannel(target);
      showToast(`Đã mở #${channelData[target]?.title || target}`);
    }
    return;
  }

  const feedbackButton = event.target.closest(".feedback button");
  if (feedbackButton) {
    const group = feedbackButton.closest(".feedback");
    group.querySelectorAll("button").forEach((button) => button.classList.remove("selected"));
    feedbackButton.classList.add("selected");
    showToast(feedbackButton.textContent.includes("👍") ? "Đã ghi nhận: kết quả hữu ích" : "Đã ghi nhận để cải thiện kết quả");
  }
});

document.getElementById("memberToggle").addEventListener("click", () => {
  memberSidebar.classList.toggle("hidden");
  appShell.classList.toggle("members-hidden");
});

document.getElementById("mobileMenu").addEventListener("click", () => {
  channelSidebar.classList.add("open");
  mobileScrim.classList.add("show");
});

mobileScrim.addEventListener("click", closeMobileSidebar);

document.getElementById("micButton").addEventListener("click", (event) => {
  const button = event.currentTarget;
  button.classList.toggle("muted");
  button.setAttribute("aria-label", button.classList.contains("muted") ? "Bật mic" : "Tắt mic");
  showToast(button.classList.contains("muted") ? "Đã tắt mic" : "Đã bật mic");
});

searchInput.addEventListener("input", () => {
  const query = searchInput.value.trim().toLowerCase();
  const activeView = document.querySelector(".channel-view.active");
  activeView.querySelectorAll(".message").forEach((message) => {
    const haystack = `${message.textContent} ${message.dataset.search || ""}`.toLowerCase();
    message.classList.toggle("is-search-hidden", Boolean(query) && !haystack.includes(query));
  });
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeMobileSidebar();
});

switchChannel("assistant", { atTop: true });
