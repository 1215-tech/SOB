import asyncio
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import TOKEN, LOG_CHAT_ID
from conversations import conv_handler
from handlers.application import handle_main_menu, handle_cn_callback, close_callback, handle_eu_na_callback
from handlers.admin import handle_approval, broadcast, force_update, handle_additional_application_approval
from telegram import Bot

import database

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__) 


class TelegramBotLogHandler(logging.Handler):
    def __init__(self, bot: Bot, chat_id: int):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        try:
            log_entry = self.format(record)
            asyncio.create_task(self.bot.send_message(chat_id=self.chat_id, text=f"📋 Log:\n{log_entry}"))
        except Exception:
            self.handleError(record)


def main() -> None:
    """Start the bot."""
    database.init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    log_handler = TelegramBotLogHandler(bot=app.bot, chat_id=LOG_CHAT_ID)
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger.addHandler(log_handler)

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(handle_approval, pattern="^(approve_|reject_).*"))
    app.add_handler(CallbackQueryHandler(handle_additional_application_approval, pattern="^additional_application_approve_.*" ))
    app.add_handler(CallbackQueryHandler(handle_cn_callback, pattern="^cn_.*" ))
    app.add_handler(CallbackQueryHandler(handle_eu_na_callback, pattern="^eu_na_.*" ))
    app.add_handler(CallbackQueryHandler(close_callback, pattern="^close_message$"))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("force_update", force_update))
    app.add_handler(MessageHandler(filters.TEXT, handle_main_menu))

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical("Bot crashed with exception:", exc_info=e)
