from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
import database
from config import LOG_CHAT_ID
from handlers.additional_application import start_additional_application
import logging
from constants import (
    ASK_Q1, ASK_Q2, ASK_Q3, ASK_Q4, ASK_Q5, ASK_Q6
)

logger = logging.getLogger(__name__)

def get_welcome_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Let's get started!", callback_data="start_intro")]
    ])

def get_intro_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("I'm ready to answer the questions", callback_data="start_questions")]
    ])

def get_application_keyboard(user_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("Reject", callback_data=f"reject_{user_id}")
        ]
    ])

def get_cn_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Manual", callback_data="cn_manual"), InlineKeyboardButton("Domains", callback_data="cn_domains")],
        [InlineKeyboardButton("Additional Application", callback_data="cn_additional_application"), InlineKeyboardButton("Bot", callback_data="cn_bot")],
        [InlineKeyboardButton("Close", callback_data="cn_close")]
    ])

def get_eu_na_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Manual", callback_data="eu_na_manual"), InlineKeyboardButton("Domains", callback_data="eu_na_domains")],
        [InlineKeyboardButton("Bot", callback_data="eu_na_bot")],
        [InlineKeyboardButton("Close", callback_data="eu_na_close")]
    ])

def get_back_close_keyboard(back_callback):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data=back_callback), InlineKeyboardButton("Close", callback_data="close_message")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()
    database.add_user(user.id, update.message.chat_id)
    logger.info(f"New user started the bot: {user.full_name} (@{user.username}, {user.id})")

    welcome_text = "<b>Welcome to the bot!</b>\n\nThis bot will help you to get started with our community."
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_welcome_keyboard()
    )
    return ConversationHandler.END

async def intro_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "<b>Introduction</b>\n\nPlease read the following information carefully."
    await query.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_intro_keyboard()
    )

async def start_application_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "<b>Question 1:</b> What is your name?",
        parse_mode=ParseMode.HTML
    )
    return ASK_Q1

async def ask_q2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['q1'] = update.message.text
    await update.message.reply_text(
        "<b>Question 2:</b> What is your age?",
        parse_mode=ParseMode.HTML
    )
    return ASK_Q2

async def ask_q3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['q2'] = update.message.text
    await update.message.reply_text(
        "<b>Question 3:</b> Please provide some photos.",
        parse_mode=ParseMode.HTML
    )
    context.user_data['q3'] = []
    return ASK_Q3

async def ask_q4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        if len(context.user_data.get('q3', [])) < 10:
            context.user_data['q3'].append({
                "file_id": update.message.photo[-1].file_id,
                "caption": update.message.caption or ""
            })
        else:
            await update.message.reply_text("<b>You can upload a maximum of 10 photos.</b>")
    elif update.message.text and update.message.text != '/done':
        context.user_data['q3'].append(update.message.text)
    
    if update.message.text == '/done':
        await update.message.reply_text(
            "<b>Question 4:</b> What is your favorite color?",
            parse_mode=ParseMode.HTML
        )
        return ASK_Q4
    else:
        return ASK_Q3

async def ask_q5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['q4'] = update.message.text
    await update.message.reply_text(
        "<b>Question 5:</b> What is your quest?",
        parse_mode=ParseMode.HTML
    )
    return ASK_Q6

async def handle_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['q5'] = update.message.text
    user = update.message.from_user
    user_info = f"{user.full_name} (@{user.username})" if user.username else user.full_name

    keyboard = get_application_keyboard(user.id)

    msg_lines = [
        f"New application from {user_info}",
        f"1. Name: {context.user_data.get('q1', '—')}",
        f"2. Age: {context.user_data.get('q2', '—')}",
        f"4. Favorite Color: {context.user_data.get('q4', '—')}",
        f"5. Quest: {context.user_data.get('q5', '—')}",
    ]

    q3_data = context.user_data.get("q3")
    if q3_data:
        msg_lines.insert(3, "3. Photos and additional info:")
        full_msg = "\n".join(msg_lines)
        media_group = []
        for item in q3_data:
            if isinstance(item, dict):
                media_group.append(InputMediaPhoto(media=item["file_id"]))
            else:
                full_msg += f"\n\n{item}"
        
        if media_group:
            await context.bot.send_media_group(chat_id=LOG_CHAT_ID, media=media_group)

        await context.bot.send_message(
            chat_id=LOG_CHAT_ID,
            text=full_msg,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        msg_lines.insert(3, "3. Photos: —")
        full_msg = "\n".join(msg_lines)
        await context.bot.send_message(
            chat_id=LOG_CHAT_ID,
            text=full_msg,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )

    await update.message.reply_text("<b>Thank you for your application!</b> We will review it shortly.", parse_mode=ParseMode.HTML)
    logger.info(f"New application from {user.full_name} (@{user.username}, {user.id}) submitted.")
    return ConversationHandler.END

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if not database.is_approved(user_id):
        await update.message.reply_text("<b>You are not yet approved to use this bot.</b>", parse_mode=ParseMode.HTML)
        return

    if text == "CN Menu":
        await update.message.reply_text("<b>CN Menu</b>", reply_markup=get_cn_keyboard(), parse_mode=ParseMode.HTML)
    elif text == "EU/NA Menu":
        await update.message.reply_text("<b>EU/NA Menu</b>", reply_markup=get_eu_na_keyboard(), parse_mode=ParseMode.HTML)
    elif text == "Telegram":
        await update.message.reply_text("<b>Telegram</b>", reply_markup=get_back_close_keyboard("main_menu"), parse_mode=ParseMode.HTML)
    elif text == "Discord":
        await update.message.reply_text("<b>Discord</b>", reply_markup=get_back_close_keyboard("main_menu"), parse_mode=ParseMode.HTML)
    elif text == "Admin":
        await update.message.reply_text("<b>Admin</b>", reply_markup=get_back_close_keyboard("main_menu"), parse_mode=ParseMode.HTML)

async def handle_eu_na_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()    
    if query.data == "eu_na_close":
        await query.message.delete()
    elif query.data == "eu_na_domains":
        await query.edit_message_text("<b>EU/NA Domains</b>", reply_markup=get_back_close_keyboard("eu_na_back"), parse_mode=ParseMode.HTML)
    elif query.data == "eu_na_manual":
        await query.edit_message_text("<b>EU/NA Manual</b>", reply_markup=get_back_close_keyboard("eu_na_back"), parse_mode=ParseMode.HTML)
    elif query.data == "eu_na_bot":
        await query.edit_message_text("<b>EU/NA Bot</b>", reply_markup=get_back_close_keyboard("eu_na_back"), parse_mode=ParseMode.HTML)
    elif query.data == "eu_na_back":
        await query.edit_message_text("<b>EU/NA Menu</b>", reply_markup=get_eu_na_keyboard(), parse_mode=ParseMode.HTML)

async def handle_cn_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()    
    if query.data == "cn_close":
        await query.message.delete()
    elif query.data == "cn_domains":
        await query.edit_message_text("<b>CN Domains</b>", reply_markup=get_back_close_keyboard("cn_back"), parse_mode=ParseMode.HTML)
    elif query.data == "cn_manual":
        await query.edit_message_text("<b>CN Manual</b>", reply_markup=get_back_close_keyboard("cn_back"), parse_mode=ParseMode.HTML)
    elif query.data == "cn_bot":
        await query.edit_message_text("<b>CN Bot</b>", reply_markup=get_back_close_keyboard("cn_back"), parse_mode=ParseMode.HTML)
    elif query.data == "cn_additional_application":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Start Additional Application", callback_data="cn_start_additional_application")],
            [InlineKeyboardButton("Back", callback_data="cn_back"), InlineKeyboardButton("Close", callback_data="cn_close")]
        ])
        await query.edit_message_text("<b>Additional Application</b>", reply_markup=keyboard, parse_mode=ParseMode.HTML)
    elif query.data == "cn_back":
        await query.edit_message_text("<b>CN Menu</b>", reply_markup=get_cn_keyboard(), parse_mode=ParseMode.HTML)


async def close_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()