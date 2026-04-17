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

    if data.startswith("wl_movie:"):
        await _wishlist_movie(query, data)
    elif data.startswith("wl_series:"):
        await _wishlist_series(query, data)
    elif data.startswith("dl_movie:"):
        await _download_movie(query, data)
    elif data.startswith("dl_series:"):
        await _download_series(query, data)
    elif data.startswith("wldl_movie:"):
        await _activate_movie(query, data)
    elif data.startswith("wldl_series:"):
        await _activate_series(query, data)
    elif data.startswith("wlrm_movie:"):
        await _remove_movie(query, data)
    elif data.startswith("wlrm_series:"):
        await _remove_series(query, data)
    # Legacy callbacks kept for backward compatibility
    elif data.startswith("add_movie:"):
        await _download_movie(query, "dl_movie:" + data.split(":", 1)[1])
    elif data.startswith("add_series:"):
        await _download_series(query, "dl_series:" + data.split(":", 1)[1])
    elif data.startswith("del_movie:"):
        await _delete_movie(query, data)
    elif data.startswith("del_series:"):
        await _delete_series(query, data)
    else:
        await query.edit_message_text(f"Unknown action: {data}")


async def _wishlist_movie(query, data: str) -> None:
    tmdb_id = int(data.split(":")[1])
    try:
        results = await radarr.search(f"tmdb:{tmdb_id}")
        movie = next((m for m in results if m.get("tmdbId") == tmdb_id), None)
        if not movie:
            await query.edit_message_text("Movie not found.")
            return
        await radarr.add_movie(movie, monitored=False)
        title = movie.get("title", "Unknown")
        year = movie.get("year", "")
        await query.edit_message_text(
            f"📋 *{title} ({year})* added to wishlist.\nUse /wishlist to download it later.",
            parse_mode="Markdown",
        )
    except Exception as e:
        if "already" in str(e).lower() or "exists" in str(e).lower():
            await query.edit_message_text("ℹ️ Already in your library or wishlist.")
        else:
            await query.edit_message_text(f"Failed to add to wishlist: {e}")


async def _wishlist_series(query, data: str) -> None:
    tvdb_id = int(data.split(":")[1])
    try:
        results = await sonarr.search(f"tvdb:{tvdb_id}")
        series = next((s for s in results if s.get("tvdbId") == tvdb_id), None)
        if not series:
            await query.edit_message_text("Series not found.")
            return
        await sonarr.add_series(series, monitored=False)
        title = series.get("title", "Unknown")
        year = series.get("year", "")
        await query.edit_message_text(
            f"📋 *{title} ({year})* added to wishlist.\nUse /wishlist to download it later.",
            parse_mode="Markdown",
        )
    except Exception as e:
        if "already" in str(e).lower() or "exists" in str(e).lower():
            await query.edit_message_text("ℹ️ Already in your library or wishlist.")
        else:
            await query.edit_message_text(f"Failed to add to wishlist: {e}")


async def _download_movie(query, data: str) -> None:
    tmdb_id = int(data.split(":")[1])
    try:
        results = await radarr.search(f"tmdb:{tmdb_id}")
        movie = next((m for m in results if m.get("tmdbId") == tmdb_id), None)
        if not movie:
            await query.edit_message_text("Movie not found.")
            return
        await radarr.add_movie(movie, monitored=True)
        title = movie.get("title", "Unknown")
        year = movie.get("year", "")
        await query.edit_message_text(
            f"✅ *{title} ({year})* added. Download will start when available.",
            parse_mode="Markdown",
        )
    except Exception as e:
        if "already" in str(e).lower() or "exists" in str(e).lower():
            await query.edit_message_text("ℹ️ Already in your library.")
        else:
            await query.edit_message_text(f"Failed to add movie: {e}")


async def _download_series(query, data: str) -> None:
    tvdb_id = int(data.split(":")[1])
    try:
        results = await sonarr.search(f"tvdb:{tvdb_id}")
        series = next((s for s in results if s.get("tvdbId") == tvdb_id), None)
        if not series:
            await query.edit_message_text("Series not found.")
            return
        await sonarr.add_series(series, monitored=True)
        title = series.get("title", "Unknown")
        year = series.get("year", "")
        await query.edit_message_text(
            f"✅ *{title} ({year})* added. Missing episodes will be searched.",
            parse_mode="Markdown",
        )
    except Exception as e:
        if "already" in str(e).lower() or "exists" in str(e).lower():
            await query.edit_message_text("ℹ️ Already in your library.")
        else:
            await query.edit_message_text(f"Failed to add series: {e}")


async def _activate_movie(query, data: str) -> None:
    movie_id = int(data.split(":")[1])
    try:
        await radarr.activate_movie(movie_id)
        await query.edit_message_text("✅ Downloading — search started.")
    except Exception as e:
        await query.edit_message_text(f"Failed: {e}")


async def _activate_series(query, data: str) -> None:
    series_id = int(data.split(":")[1])
    try:
        await sonarr.activate_series(series_id)
        await query.edit_message_text("✅ Downloading — missing episodes search started.")
    except Exception as e:
        await query.edit_message_text(f"Failed: {e}")


async def _remove_movie(query, data: str) -> None:
    movie_id = int(data.split(":")[1])
    try:
        await radarr.delete_movie(movie_id)
        await query.edit_message_text("🗑 Removed from wishlist.")
    except Exception as e:
        await query.edit_message_text(f"Failed to remove: {e}")


async def _remove_series(query, data: str) -> None:
    series_id = int(data.split(":")[1])
    try:
        await sonarr.delete_series(series_id)
        await query.edit_message_text("🗑 Removed from wishlist.")
    except Exception as e:
        await query.edit_message_text(f"Failed to remove: {e}")


async def _delete_movie(query, data: str) -> None:
    movie_id = int(data.split(":")[1])
    try:
        await radarr.delete_movie(movie_id)
        await query.edit_message_text("🗑️ Movie deleted (files removed).")
    except Exception as e:
        await query.edit_message_text(f"Failed to delete movie: {e}")


async def _delete_series(query, data: str) -> None:
    series_id = int(data.split(":")[1])
    try:
        await sonarr.delete_series(series_id)
        await query.edit_message_text("🗑️ Series deleted (files removed).")
    except Exception as e:
        await query.edit_message_text(f"Failed to delete series: {e}")
