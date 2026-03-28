import logging
import shutil

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import SSD_MOUNT_PATH
from bot.utils.auth import restricted
from bot.utils.formatters import format_size, progress_bar

logger = logging.getLogger(__name__)


@restricted
async def disk_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /disk - show SSD disk usage."""
    try:
        usage = shutil.disk_usage(SSD_MOUNT_PATH)
    except Exception as e:
        await update.message.reply_text(f"❌ Cannot read disk: {e}")
        return

    total = format_size(usage.total)
    used = format_size(usage.used)
    free = format_size(usage.free)
    percent = usage.used / usage.total * 100
    bar = progress_bar(percent, length=20)

    await update.message.reply_text(
        f"💾 *Disk Usage:*\n\n"
        f"{bar} {percent:.1f}%\n\n"
        f"Used: {used}\n"
        f"Free: {free}\n"
        f"Total: {total}",
        parse_mode="Markdown",
    )
