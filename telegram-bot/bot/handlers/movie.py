import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.services.radarr import RadarrClient
from bot.utils.auth import restricted
from bot.utils.formatters import format_movie_result, truncate

logger = logging.getLogger(__name__)

radarr = RadarrClient()


@restricted
async def movie_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /movie <title> - search and add a movie."""
    if not context.args:
        await update.message.reply_text("Usage: /movie <title>\nExample: /movie The Matrix")
        return

    query = " ".join(context.args)
    await update.message.reply_text(f"🎬 Searching movies for '{query}'...")

    try:
        results = await radarr.search(query)
    except Exception as e:
        await update.message.reply_text(f"❌ Radarr error: {e}")
        return

    if not results:
        await update.message.reply_text(f"No movies found for '{query}'.")
        return

    parts = []
    buttons = []
    for i, movie in enumerate(results[:5], 1):
        parts.append(format_movie_result(movie, i))
        tmdb_id = movie.get("tmdbId", 0)
        title = movie.get("title", "Unknown")
        year = movie.get("year", "")
        buttons.append(
            [InlineKeyboardButton(
                f"➕ {title} ({year})",
                callback_data=f"add_movie:{tmdb_id}",
            )]
        )

    text = truncate("\n\n".join(parts))
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
