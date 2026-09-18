import asyncio
import os
import discord
from google import genai
from dotenv import load_dotenv

load_dotenv()

# ================= CẤU HÌNH =================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

TOKEN_BOT_A = os.getenv("TOKEN_BOT_A")
TOKEN_BOT_B = os.getenv("TOKEN_BOT_B")

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Thay bằng ID kênh Discord bạn muốn 2 bot nói chuyện
MODEL_NAME = os.getenv("MODEL_NAME")   # Hoặc mã model Gemini bạn muốn sử dụng

# Khởi tạo Gemini Client
ai_client = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot_a = discord.Client(intents=intents)
bot_b = discord.Client(intents=intents)

# Persona / Tính cách của từng bot
SYSTEM_PROMPT_A = (
    "Bạn là Triết gia lạc quan. Bạn thích nhìn nhận các vấn đề qua góc độ hy vọng, "
    "tương lai tươi sáng và vẻ đẹp cuộc sống. Hãy trả lời ngắn gọn (dưới 3 câu)."
)

SYSTEM_PROMPT_B = (
    "Bạn là Nhà khoa học thực tế, hơi hoài nghi. Bạn đòi hỏi dẫn chứng logic, "
    "phản biện sắc sảo nhưng lịch sự. Hãy trả lời ngắn gọn (dưới 3 câu)."
)

def get_gemini_reply(system_prompt: str, user_message: str) -> str:
    """Gọi Gemini API để lấy câu trả lời"""
    try:
        response = ai_client.models.generate_content(
            model=MODEL_NAME,
            contents=user_message,
            config={"system_instruction": system_prompt}
        )
        return response.text.strip()
    except Exception as e:
        print(f"Lỗi Gemini: {e}")
        return "Tôi đang suy nghĩ thêm một chút..."

@bot_a.event
async def on_ready():
    print(f"Bot A đã online: {bot_a.user}")

@bot_b.event
async def on_ready():
    print(f"Bot B đã online: {bot_b.user}")

# Bot A phản hồi khi Bot B nói (hoặc khi có lệnh bắt đầu từ bạn)
@bot_a.event
async def on_message(message: discord.Message):
    if message.channel.id != CHANNEL_ID:
        return
    if message.author.id == bot_a.user.id:
        return

    # Kích hoạt cuộc trò chuyện nếu bạn gõ !start
    if message.content.startswith("!start"):
        topic = message.content.replace("!start", "").strip() or "Trí tuệ nhân tạo sẽ thay đổi con người thế nào?"
        async with message.channel.typing():
            reply = get_gemini_reply(SYSTEM_PROMPT_A, f"Hãy mở đầu cuộc trò chuyện về chủ đề: {topic}")
            await asyncio.sleep(2)
            await message.channel.send(reply)
        return

    # Chỉ phản hồi nếu người gửi là Bot B
    if message.author.id == bot_b.user.id:
        async with message.channel.typing():
            await asyncio.sleep(3)  # Delay tránh spam
            reply = get_gemini_reply(SYSTEM_PROMPT_A, message.content)
            await message.channel.send(reply)

# Bot B phản hồi khi Bot A nói
@bot_b.event
async def on_message(message: discord.Message):
    if message.channel.id != CHANNEL_ID:
        return
    if message.author.id == bot_b.user.id:
        return

    # Chỉ phản hồi nếu người gửi là Bot A
    if message.author.id == bot_a.user.id:
        async with message.channel.typing():
            await asyncio.sleep(3)  # Delay tránh spam
            reply = get_gemini_reply(SYSTEM_PROMPT_B, message.content)
            await message.channel.send(reply)

# Chạy cả 2 bot song song
async def main():
    await asyncio.gather(
        bot_a.start(TOKEN_BOT_A),
        bot_b.start(TOKEN_BOT_B)
    )

if __name__ == "__main__":
    asyncio.run(main())

# chạy !start [Tương lai của việc con người sống trên Sao Hỏa] trong kênh để bắt đầu