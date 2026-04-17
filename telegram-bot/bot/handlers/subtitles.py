import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.services.bazarr import BazarrClient
from bot.utils.auth import restricted

logger = logging.getLogger(__name__)

bazarr = BazarrClient()


@restricted
async def subtitles_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /subtitles - show missing subtitle counts."""
    try:
        counts = await bazarr.get_wanted_counts()
        movies = counts["movies"]
        episodes = counts["episodes"]
        total = movies + episodes
        if total == 0:
            await update.message.reply_text("✅ No missing subtitles.")
        else:
            await update.message.reply_text(
                f"💬 *Missing Subtitles:*\n\n"
                f"🎬 Movies: {movies}\n"
                f"📺 Episodes: {episodes}\n"
                f"Total: {total}",
                parse_mode="Markdown",
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Could not reach Bazarr: {e}")
