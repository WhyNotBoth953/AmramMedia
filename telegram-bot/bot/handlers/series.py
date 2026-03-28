import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.services.sonarr import SonarrClient
from bot.utils.auth import restricted
from bot.utils.formatters import format_series_result, truncate

logger = logging.getLogger(__name__)

sonarr = SonarrClient()


@restricted
async def series_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /series <title> - search and add a series."""
    if not context.args:
        await update.message.reply_text("Usage: /series <title>\nExample: /series Breaking Bad")
        return

    query = " ".join(context.args)
    await update.message.reply_text(f"📺 Searching series for '{query}'...")

    try:
        results = await sonarr.search(query)
    except Exception as e:
        await update.message.reply_text(f"❌ Sonarr error: {e}")
        return

    if not results:
        await update.message.reply_text(f"No series found for '{query}'.")
        return

    parts = []
    buttons = []
    for i, show in enumerate(results[:5], 1):
        parts.append(format_series_result(show, i))
        tvdb_id = show.get("tvdbId", 0)
        title = show.get("title", "Unknown")
        year = show.get("year", "")
        buttons.append(
            [InlineKeyboardButton(
                f"➕ {title} ({year})",
                callback_data=f"add_series:{tvdb_id}",
            )]
        )

    text = truncate("\n\n".join(parts))
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
