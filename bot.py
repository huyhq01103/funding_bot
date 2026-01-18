import asyncio
import aiohttp
import logging
import os
from datetime import datetime
import requests
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# --------------------- CẤU HÌNH ---------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("BOT_TOKEN hoặc CHAT_ID chưa được set trong biến môi trường!")

CHAT_ID = int(CHAT_ID)  # đảm bảo là số nguyên

# ----------------------------------------------------

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def get_top_10_negative_funding() -> str:
    url = "https://fapi.binance.com/fapi/v1/premiumIndex"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"HTTP {resp.status}: {text}")

                data = await resp.json()

        negative = [
            item for item in data
            if float(item.get("lastFundingRate", 0)) < 0
        ]

        if not negative:
            return "Hiện tại không có coin nào có funding rate âm."

        negative.sort(key=lambda x: float(x["lastFundingRate"]))
        top10 = negative[:10]

        lines = [
            "*Top 10 coin funding rate ÂM mạnh nhất* (Binance Futures)",
            f"_Cập nhật: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}_\n"
        ]

        for i, item in enumerate(top10, 1):
            symbol = item["symbol"]
            rate = float(item["lastFundingRate"]) * 100
            mark = float(item.get("markPrice", 0))
            sign = " 🔻" if rate < -0.05 else ""

            lines.append(
                f"{i}. *{symbol}* : `{rate:.4f}%`{sign}  (mark: {mark:,.2f})"
            )

        return "\n".join(lines)

    except Exception as e:
        logger.exception("Lỗi lấy funding")
        return f"❌ Lỗi khi lấy dữ liệu funding:\n`{e}`"

async def send_funding_report(context: ContextTypes.DEFAULT_TYPE) -> None:
    message = await get_top_10_negative_funding()
    try:
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        logger.info("Đã gửi funding report")
    except Exception as e:
        logger.error(f"Lỗi gửi tin: {e}")


async def start(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"Bot đang chạy!\nChat ID: `{update.effective_chat.id}`\n"
        "Sử dụng chat_id này nếu cần cấu hình."
    )


async def manual(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = await get_top_10_negative_funding()
    await update.message.reply_text(message, parse_mode="Markdown")


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("manual", manual))

    job_queue = application.job_queue
    if job_queue:
        job_queue.run_repeating(send_funding_report, interval=3600, first=10)
        logger.info("Đã lên lịch gửi mỗi 1 giờ")

    application.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
