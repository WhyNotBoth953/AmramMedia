import asyncio
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.services.radarr import RadarrClient
from bot.services.sonarr import SonarrClient
from bot.utils.auth import restricted
from bot.utils.formatters import format_movie_result, format_series_result, truncate

logger = logging.getLogger(__name__)

radarr = RadarrClient()
sonarr = SonarrClient()


@restricted
async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /search <query> - search both movies and series."""
    if not context.args:
        await update.message.reply_text("Usage: /search <query>\nExample: /search Breaking Bad")
        return

    query = " ".join(context.args)
    await update.message.reply_text(f"🔍 Searching for '{query}'...")

    movies, series = await asyncio.gather(
        radarr.search(query),
        sonarr.search(query),
        return_exceptions=True,
    )

    parts = []
    buttons = []

    # Movies
    if isinstance(movies, list) and movies:
        parts.append("🎬 *Movies:*\n")
        for i, movie in enumerate(movies[:5], 1):
            parts.append(format_movie_result(movie, i))
            tmdb_id = movie.get("tmdbId", 0)
            title = movie.get("title", "Unknown")
            year = movie.get("year", "")
            buttons.append(
                [InlineKeyboardButton(
                    f"🎬 {title} ({year})",
                    callback_data=f"add_movie:{tmdb_id}",
                )]
            )
        parts.append("")
    elif isinstance(movies, Exception):
        parts.append(f"⚠️ Radarr error: {movies}\n")

    # Series
    if isinstance(series, list) and series:
        parts.append("📺 *Series:*\n")
        for i, show in enumerate(series[:5], 1):
            parts.append(format_series_result(show, i))
            tvdb_id = show.get("tvdbId", 0)
            title = show.get("title", "Unknown")
            year = show.get("year", "")
            buttons.append(
                [InlineKeyboardButton(
                    f"📺 {title} ({year})",
                    callback_data=f"add_series:{tvdb_id}",
                )]
            )
    elif isinstance(series, Exception):
        parts.append(f"⚠️ Sonarr error: {series}\n")

    if not parts:
        await update.message.reply_text(f"No results found for '{query}'.")
        return

    text = truncate("\n".join(parts))
    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)
