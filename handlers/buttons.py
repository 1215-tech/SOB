from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import database

def get_main_menu_keyboard(user_id):
    """
    Returns the main menu keyboard based on user's approval status.
    """
    if database.is_approved(user_id):
        # Approved user menu
        keyboard = [
            ["CN Menu", "EU/NA Menu"],
            ["Telegram", "Discord"],
            ["Admin"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    else:
        # Default menu for non-approved users
        return ReplyKeyboardRemove()
