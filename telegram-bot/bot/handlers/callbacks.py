import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.services.radarr import RadarrClient
from bot.services.sonarr import SonarrClient
from bot.utils.auth import restricted

logger = logging.getLogger(__name__)

radarr = RadarrClient()
sonarr = SonarrClient()


@restricted
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data:
        return

    if data.startswith("add_movie:"):
        await _add_movie(query, data)
    elif data.startswith("add_series:"):
        await _add_series(query, data)
    elif data.startswith("del_movie:"):
        await _delete_movie(query, data)
    elif data.startswith("del_series:"):
        await _delete_series(query, data)
    else:
        await query.edit_message_text(f"❓ Unknown action: {data}")


async def _add_movie(query, data: str) -> None:
    tmdb_id = int(data.split(":")[1])
    try:
        results = await radarr.search(f"tmdb:{tmdb_id}")
        movie = next(
            (m for m in results if m.get("tmdbId") == tmdb_id),
            None,
        )
        if not movie:
            await query.edit_message_text("❌ Movie not found in search results.")
            return

        await radarr.add_movie(movie)
        title = movie.get("title", "Unknown")
        year = movie.get("year", "")
        await query.edit_message_text(
            f"✅ Added *{title} ({year})* to Radarr.\n"
            f"Download will start when available.",
            parse_mode="Markdown",
        )
    except Exception as e:
        error_msg = str(e)
        if "already" in error_msg.lower() or "exists" in error_msg.lower():
            await query.edit_message_text("ℹ️ This movie is already in your library.")
        else:
            await query.edit_message_text(f"❌ Failed to add movie: {error_msg}")


async def _add_series(query, data: str) -> None:
    tvdb_id = int(data.split(":")[1])
    try:
        results = await sonarr.search(f"tvdb:{tvdb_id}")
        series = next(
            (s for s in results if s.get("tvdbId") == tvdb_id),
            None,
        )
        if not series:
            await query.edit_message_text("❌ Series not found in search results.")
            return

        await sonarr.add_series(series)
        title = series.get("title", "Unknown")
        year = series.get("year", "")
        await query.edit_message_text(
            f"✅ Added *{title} ({year})* to Sonarr.\n"
            f"Missing episodes will be searched.",
            parse_mode="Markdown",
        )
    except Exception as e:
        error_msg = str(e)
        if "already" in error_msg.lower() or "exists" in error_msg.lower():
            await query.edit_message_text("ℹ️ This series is already in your library.")
        else:
            await query.edit_message_text(f"❌ Failed to add series: {error_msg}")


async def _delete_movie(query, data: str) -> None:
    movie_id = int(data.split(":")[1])
    try:
        await radarr.delete_movie(movie_id, delete_files=True)
        await query.edit_message_text("🗑️ Movie deleted (files removed).")
    except Exception as e:
        await query.edit_message_text(f"❌ Failed to delete movie: {e}")


async def _delete_series(query, data: str) -> None:
    series_id = int(data.split(":")[1])
    try:
        await sonarr.delete_series(series_id, delete_files=True)
        await query.edit_message_text("🗑️ Series deleted (files removed).")
    except Exception as e:
        await query.edit_message_text(f"❌ Failed to delete series: {e}")
