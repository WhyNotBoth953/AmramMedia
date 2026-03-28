import functools
import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import TELEGRAM_ALLOWED_CHAT_IDS

logger = logging.getLogger(__name__)


def restricted(func):
    """Decorator that restricts bot access to allowed chat IDs."""

    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        if TELEGRAM_ALLOWED_CHAT_IDS and chat_id not in TELEGRAM_ALLOWED_CHAT_IDS:
            logger.warning("Unauthorized access from chat_id=%s", chat_id)
            return
        return await func(update, context)

    return wrapper
