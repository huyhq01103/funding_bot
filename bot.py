import asyncio
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
    url = 'https://fapi.binance.com/fapi/v1/premiumIndex'
    
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        negative = [item for item in data if 'lastFundingRate' in item and float(item['lastFundingRate']) < 0]
        
        if not negative:
            return "Hiện tại không có coin nào có funding rate âm."
        
        sorted_neg = sorted(negative, key=lambda x: float(x['lastFundingRate']))
        top10 = sorted_neg[:10]
        
        lines = ["**Top 10 coin funding rate ÂM mạnh nhất** (Binance Futures)"]
        lines.append(f"**Cập nhật lúc:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        
        for i, item in enumerate(top10, 1):
            symbol = item['symbol']
            rate_pct = float(item['lastFundingRate']) * 100
            mark_price = float(item.get('markPrice', 0))
            sign = "▼" if rate_pct < -0.05 else ""
            lines.append(
                f"{i:2d}. **{symbol}** : `{rate_pct:7.4f}%`  {sign}  "
                f"(mark: {mark_price:,.2f})"
            )
        
        return "\n".join(lines)
    
    except Exception as e:
        logger.error(f"Lỗi lấy funding data: {e}")
        return f"Lỗi khi lấy dữ liệu: {str(e)}"


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
    main()        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())
            result = await resp.json()

    data = result.get("data", [])

    # Funding âm trên Binance
    binance_negative = [
        x for x in data
        if x.get("exchangeName") == "Binance"
        and float(x.get("fundingRate", 0)) < 0
    ]

    if not binance_negative:
        return "Hiện tại không có coin funding âm trên Binance."

    # sort âm sâu nhất
    binance_negative.sort(key=lambda x: float(x["fundingRate"]))

    # -------- ALERT FUNDING SÂU --------
    alert_lines = []
    for x in binance_negative:
        rate_pct = float(x["fundingRate"]) * 100
        if rate_pct <= ALERT_FUNDING_2:
            alert_lines.append(f"🔥 *{x['symbol']}* : `{rate_pct:.3f}%`")
        elif rate_pct <= ALERT_FUNDING_1:
            alert_lines.append(f"⚠️ *{x['symbol']}* : `{rate_pct:.3f}%`")

    # -------- TOP 10 --------
    top10 = binance_negative[:10]
    lines = [
        "*Top 10 coin funding rate ÂM mạnh nhất* (Binance – CoinGlass)",
        f"_Cập nhật: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}_\n"
    ]

    for i, x in enumerate(top10, 1):
        rate = float(x["fundingRate"]) * 100
        price = float(x.get("price", 0))
        lines.append(
            f"{i}. *{x['symbol']}* : `{rate:.4f}%`  (price: {price:,.2f})"
        )

    # -------- GHÉP ALERT --------
    if alert_lines:
        lines.append("\n*🚨 ALERT FUNDING SÂU*")
        lines.extend(alert_lines)

    return "\n".join(lines)

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
