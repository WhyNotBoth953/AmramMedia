import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.services.radarr import RadarrClient
from bot.services.sonarr import SonarrClient
from bot.utils.auth import restricted

logger = logging.getLogger(__name__)

radarr = RadarrClient()
sonarr = SonarrClient()


@restricted
async def delete_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /delete <title> - search library and delete a movie/series."""
    if not context.args:
        await update.message.reply_text(
            "Usage: /delete <title>\nSearches your library for matching movies/series to remove."
        )
        return

    query = " ".join(context.args).lower()
    buttons = []

    try:
        movies = await radarr.get_movies()
        for m in movies:
            if query in m.get("title", "").lower():
                mid = m["id"]
                title = m["title"]
                year = m.get("year", "")
                buttons.append(
                    [InlineKeyboardButton(
                        f"🎬 {title} ({year})",
                        callback_data=f"del_movie:{mid}",
                    )]
                )
    except Exception as e:
        logger.error("Radarr search for delete failed: %s", e)

    try:
        series = await sonarr.get_series()
        for s in series:
            if query in s.get("title", "").lower():
                sid = s["id"]
                title = s["title"]
                year = s.get("year", "")
                buttons.append(
                    [InlineKeyboardButton(
                        f"📺 {title} ({year})",
                        callback_data=f"del_series:{sid}",
                    )]
                )
    except Exception as e:
        logger.error("Sonarr search for delete failed: %s", e)

    if not buttons:
        await update.message.reply_text(f"No items matching '{query}' found in your library.")
        return

    await update.message.reply_text(
        f"⚠️ Select item to *delete* (files will be removed):",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons[:10]),
    )
