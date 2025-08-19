from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from handlers.application import (
    start, intro_callback, start_application_callback,
    ask_q2, ask_q3, ask_q4, ask_q5, handle_application
)
from handlers.additional_application import (
    start_additional_application, additional_application_q2, additional_application_q3, additional_application_q4, additional_application_q5, finish_additional_application
)
from constants import (
    ASK_Q1, ASK_Q2, ASK_Q3, ASK_Q4, ASK_Q5, ASK_Q6,
    ADDITIONAL_APPLICATION_Q1, ADDITIONAL_APPLICATION_Q2, ADDITIONAL_APPLICATION_Q3, ADDITIONAL_APPLICATION_Q4, ADDITIONAL_APPLICATION_Q5
)

def cancel(update, context):
    update.message.reply_text("<b>[CANCEL_MESSAGE]</b>", parse_mode=ParseMode.HTML)
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("start", start),
        CallbackQueryHandler(intro_callback, pattern="^start_intro$"),
        CallbackQueryHandler(start_application_callback, pattern="^start_questions$"),
        CallbackQueryHandler(start_additional_application, pattern="^cn_start_additional_application$"),
    ],
    states={
        ASK_Q1: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_q2)],
        ASK_Q2: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_q3)],
        ASK_Q3: [MessageHandler(filters.TEXT | filters.PHOTO, ask_q4), CommandHandler('done', ask_q4)],
        ASK_Q4: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_q5)],
        ASK_Q5: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_q5)],
        ASK_Q6: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_application)],
        ADDITIONAL_APPLICATION_Q1: [MessageHandler(filters.TEXT & ~filters.COMMAND, additional_application_q2)],
        ADDITIONAL_APPLICATION_Q2: [MessageHandler(filters.TEXT & ~filters.COMMAND, additional_application_q3)],
        ADDITIONAL_APPLICATION_Q3: [MessageHandler(filters.TEXT & ~filters.COMMAND, additional_application_q4)],
        ADDITIONAL_APPLICATION_Q4: [MessageHandler(filters.TEXT | filters.PHOTO, additional_application_q5), CommandHandler('done', additional_application_q5)],
        ADDITIONAL_APPLICATION_Q5: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish_additional_application)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)