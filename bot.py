import asyncio
import logging
from datetime import datetime
import requests
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# --------------------- CẤU HÌNH ---------------------
BOT_TOKEN = "123456:ABC-DEF..."          # ← Thay bằng token thật của bạn
CHAT_ID = 123456789                      # ← Thay bằng chat_id thật (int hoặc str nếu là channel)

# ----------------------------------------------------

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def get_top_10_negative_funding() -> str:
    """Lấy top 10 coin funding âm mạnh nhất từ Binance Futures"""
    url = 'https://fapi.binance.com/fapi/v1/premiumIndex'
    
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        # Lọc funding âm
        negative = [
            item for item in data 
            if 'lastFundingRate' in item and float(item['lastFundingRate']) < 0
        ]
        
        if not negative:
            return "Hiện tại không có coin nào có funding rate âm."
        
        # Sắp xếp: âm mạnh nhất → âm nhẹ nhất
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
        return f"Lỗi khi lấy dữ liệu từ Binance: {str(e)}"


async def send_funding_report(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Job gửi báo cáo mỗi giờ"""
    message = await get_top_10_negative_funding()
    
    try:
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        logger.info("Đã gửi funding report thành công")
    except Exception as e:
        logger.error(f"Lỗi gửi tin nhắn: {e}")


async def start(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command /start - test bot & hiện chat_id nếu cần debug"""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"Bot đang chạy!\n"
        f"Chat ID của bạn: `{chat_id}`\n"
        f"Dùng chat_id này để cấu hình gửi thông báo tự động.\n\n"
        "Bot sẽ gửi top 10 funding âm mỗi 1 giờ."
    )


async def manual(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command /manual - gửi báo cáo ngay lập tức"""
    message = await get_top_10_negative_funding()
    await context.bot.send_message(
        chat_id=context._chat_id,  # hoặc update.effective_chat.id nếu từ handler
        text=message,
        parse_mode="Markdown"
    )


def main():
    """Chạy bot"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Thêm các command
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("manual", manual))

    # Lên lịch gửi mỗi 1 giờ (3600 giây)
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_repeating(
            send_funding_report,
            interval=3600,          # 1 giờ
            first=10               # bắt đầu sau 10 giây khi bot chạy
        )
        logger.info("Đã lên lịch gửi funding report mỗi 1 giờ")
    else:
        logger.warning("JobQueue không khả dụng! Kiểm tra cài đặt python-telegram-bot[job-queue]")

    # Chạy bot (polling)
    application.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()