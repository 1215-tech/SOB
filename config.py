import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TOKEN = os.getenv("TOKEN")

# Your Telegram User ID (for admin commands)
MY_TELEGRAM_ID = int(os.getenv("MY_TELEGRAM_ID", 0))

# Channel/Chat ID for logging
LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID", 0))

# Channel/Chat ID for logging additional applications
ADDITIONAL_APPLICATION_LOG_CHAT_ID = int(os.getenv("ADDITIONAL_APPLICATION_LOG_CHAT_ID", 0))

# Cooldown in seconds for the broadcast command
BROADCAST_COOLDOWN_SECONDS = 60

