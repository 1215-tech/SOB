import time
import asyncio
import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.error import BadRequest
import database
from config import MY_TELEGRAM_ID, BROADCAST_COOLDOWN_SECONDS
from handlers.buttons import get_main_menu_keyboard

logger = logging.getLogger(__name__)

last_broadcast_time = 0


async def handle_approval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles user approval and rejection."""
    query = update.callback_query
    await query.answer()
    data = query.data

    action, user_id_str = data.split("_")[0], data.split("_")[1]
    user_id = int(user_id_str)

    if not database.is_pending(user_id):
        await query.edit_message_text("This user has already been processed.")
        return

    if action == "approve":
        database.approve_user(user_id)
        chat_id = database.get_chat_id(user_id)
        reply_markup = get_main_menu_keyboard(user_id)

        await context.bot.send_message(
            chat_id=chat_id,
            text="""<b>✅ Your application has been approved!</b>""",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
        )
        await query.message.reply_text(
            "User approved.", reply_to_message_id=query.message.message_id
        )
        logger.info(f"User {user_id} approved by {query.from_user.id}.")

    elif action == "reject":
        chat_id = database.get_chat_id(user_id)
        database.reject_user(user_id)
        await context.bot.send_message(
            chat_id=chat_id, text="<b>❌ Your application has been rejected.</b>", parse_mode=ParseMode.HTML
        )
        try:
            await query.edit_message_text("User rejected. ❌")
        except BadRequest:
            await query.edit_message_caption("User rejected. ❌")
        logger.info(f"User {user_id} rejected by {query.from_user.id}.")

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            raise


async def handle_additional_application_approval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the approval of additional applications."""
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id_str = data.split("_")[3]
    user_id = int(user_id_str)

    additional_application_contacts = context.bot_data.get(
        "additional_application_contacts", {}
    )
    if user_id_str not in additional_application_contacts:
        await query.edit_message_text("This application has already been processed.")
        return

    contact_info = additional_application_contacts[user_id_str]

    await query.message.reply_text(
        "📨 The user has been sent the contact information.",
        reply_to_message_id=query.message.message_id,
    )

    try:
        user_chat = await context.bot.get_chat(user_id)
        user_username = f"@{user_chat.username}" if user_chat.username else "Not available"
    except Exception:
        user_username = "Not available"

    try:
        with open("additional_application_counter.txt", "r") as f:
            counter_value = int(f.read().strip())
    except Exception:
        counter_value = "?"

    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=f"""📞 New contact information № {counter_value}

{contact_info}

<b>User:</b> {user_username}
<b>Telegram ID:</b> <code>{user_id}</code>""",
        parse_mode=ParseMode.HTML,
    )

    approver = query.from_user
    worker_username = f"@{approver.username}" if approver.username else "Not available"
    worker_id = approver.id
    worker_info_msg = (
        f"🛠 A new worker has been assigned to you! № {counter_value}\n"
        f"<b>Username:</b> {worker_username}\n"
        f"<b>Telegram ID:</b> <code>{worker_id}</code>"
    )

    if database.is_pending(user_id):
        chat_id = database.get_chat_id(user_id)
        await context.bot.send_message(
            chat_id=chat_id, text=worker_info_msg, parse_mode=ParseMode.HTML
        )
        database.reject_user(user_id)

    del additional_application_contacts[user_id_str]

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            raise


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message to all approved users."""
    global last_broadcast_time

    if update.effective_user.id != MY_TELEGRAM_ID:
        await update.message.reply_text("⛔ You are not authorized to use this command.")
        return

    now = time.time()
    remaining = BROADCAST_COOLDOWN_SECONDS - (now - last_broadcast_time)

    if remaining > 0:
        await update.message.reply_text(
            f"⏳ Please wait {int(remaining)} seconds before broadcasting again."
        )
        return

    if not context.args:
        await update.message.reply_text("⚠️ Please provide a message to broadcast.")
        return

    message = " ".join(context.args)
    user_ids = database.get_all_users()

    sent, failed = 0, 0
    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=message, parse_mode=ParseMode.HTML)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            failed += 1
            logger.error(f"[Broadcast Error] {uid}: {e}")

    last_broadcast_time = now

    await update.message.reply_text(
        f"✅ Broadcast sent to {sent} users.\n❌ Failed to send to {failed} users."
    )


async def force_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Forces a keyboard update for all users."""
    if update.effective_user.id != MY_TELEGRAM_ID:
        await update.message.reply_text("⛔ You are not authorized to use this command.")
        return

    user_ids = database.get_all_users()
    updated, failed = 0, 0

    for uid in user_ids:
        try:
            await context.bot.send_message(
                chat_id=uid, text="Updating keyboard...", reply_markup=ReplyKeyboardRemove()
            )
            reply_markup = get_main_menu_keyboard(uid)
            await context.bot.send_message(
                chat_id=uid, text="New keyboard:", reply_markup=reply_markup
            )
            updated += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            failed += 1
            logger.error(f"[Force Update Error] {uid}: {e}")

    await update.message.reply_text(
        f"✅ Keyboard updated for {updated} users.\n❌ Failed to update for {failed} users."
    )
