from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
import database
from config import ADDITIONAL_APPLICATION_LOG_CHAT_ID
import logging
from constants import (
    ADDITIONAL_APPLICATION_Q1, ADDITIONAL_APPLICATION_Q2, ADDITIONAL_APPLICATION_Q3, ADDITIONAL_APPLICATION_Q4, ADDITIONAL_APPLICATION_Q5
)

logger = logging.getLogger(__name__)

def increment_additional_application_counter():
    try:
        with open("additional_application_counter.txt", "r+") as f:
            count = int(f.read().strip())
            count += 1
            f.seek(0)
            f.write(str(count))
            f.truncate()
        return count
    except FileNotFoundError:
        with open("additional_application_counter.txt", "w") as f:
            f.write("1")
        return 1
    except Exception as e:
        logger.error(f"Counter error: {e}")
        return None

async def start_additional_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    increment_additional_application_counter()
    await query.message.reply_text("<b>Question 1:</b> What is your name?", parse_mode=ParseMode.HTML)
    return ADDITIONAL_APPLICATION_Q1

async def additional_application_q2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["w_q1"] = update.message.text
    await update.message.reply_text("<b>Question 2:</b> What is your age?", parse_mode=ParseMode.HTML)
    return ADDITIONAL_APPLICATION_Q2

async def additional_application_q3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["w_q2"] = update.message.text
    await update.message.reply_text("<b>Question 3:</b> Please provide some photos.", parse_mode=ParseMode.HTML)
    return ADDITIONAL_APPLICATION_Q3

async def additional_application_q4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["w_q3"] = update.message.text
    await update.message.reply_text("<b>Question 4:</b> What is your favorite color?", parse_mode=ParseMode.HTML)
    context.user_data["w_q4"] = []
    return ADDITIONAL_APPLICATION_Q4

async def additional_application_q5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        if len(context.user_data.get('w_q4', [])) < 10:
            context.user_data["w_q4"].append({"file_id": update.message.photo[-1].file_id, "caption": update.message.caption or ""})
        else:
            await update.message.reply_text("<b>You can upload a maximum of 10 photos.</b>", parse_mode=ParseMode.HTML)
    elif update.message.text and update.message.text != '/done':
        context.user_data["w_q4"].append(update.message.text)
    
    if update.message.text == '/done':
        await update.message.reply_text("<b>Question 5:</b> What is your quest?", parse_mode=ParseMode.HTML)
        return ADDITIONAL_APPLICATION_Q5
    else:
        return ADDITIONAL_APPLICATION_Q4

async def finish_additional_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["w_q5"] = update.message.text
    user = update.effective_user
    context.bot_data.setdefault("additional_application_contacts", {})[str(user.id)] = context.user_data["w_q5"]

    database.add_user(user.id, update.message.chat_id)

    msg_lines = [
        f"New additional application from {user.full_name} (@{user.username})",
        f"1. Name: {context.user_data.get('w_q1', '—')}",
        f"2. Age: {context.user_data.get('w_q2', '—')}",
        f"3. Favorite Color: {context.user_data.get('w_q3', '—')}",
    ]

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Approve", callback_data=f"additional_application_approve_{user.id}")
        ]
    ])

    q4 = context.user_data.get("w_q4")
    if q4:
        msg_lines.insert(4, "4. Photos and additional info:")
        full_msg = "\n".join(msg_lines)
        media_group = []
        for item in q4:
            if isinstance(item, dict):
                media_group.append(InputMediaPhoto(media=item["file_id"]))
            else:
                full_msg += f"\n\n{item}"
        
        if media_group:
            await context.bot.send_media_group(chat_id=ADDITIONAL_APPLICATION_LOG_CHAT_ID, media=media_group)

        await context.bot.send_message(ADDITIONAL_APPLICATION_LOG_CHAT_ID, full_msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        msg_lines.insert(4, "4. Photos: —")
        await context.bot.send_message(ADDITIONAL_APPLICATION_LOG_CHAT_ID, "\n".join(msg_lines), reply_markup=keyboard, parse_mode=ParseMode.HTML)

    await update.message.reply_text("<b>Thank you for your application!</b> We will review it shortly.", parse_mode=ParseMode.HTML)
    logger.info(f"New additional application from {user.full_name} (@{user.username}, {user.id}) submitted.")
    return ConversationHandler.END
