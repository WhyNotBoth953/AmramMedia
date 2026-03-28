import logging
import shutil

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import SSD_MOUNT_PATH
from bot.services.radarr import RadarrClient
from bot.services.sonarr import SonarrClient
from bot.utils.auth import restricted
from bot.utils.formatters import format_size

logger = logging.getLogger(__name__)

radarr = RadarrClient()
sonarr = SonarrClient()


@restricted
async def library_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /library - show library stats."""
    parts = ["📚 *Library Stats:*\n"]

    try:
        movies = await radarr.get_movies()
        downloaded = sum(1 for m in movies if m.get("hasFile", False))
        parts.append(f"🎬 Movies: {downloaded}/{len(movies)} downloaded")
    except Exception as e:
        parts.append(f"🎬 Movies: ❌ {e}")

    try:
        series = await sonarr.get_series()
        total_episodes = sum(s.get("statistics", {}).get("totalEpisodeCount", 0) for s in series)
        have_episodes = sum(s.get("statistics", {}).get("episodeFileCount", 0) for s in series)
        parts.append(f"📺 Series: {len(series)} shows, {have_episodes}/{total_episodes} episodes")
    except Exception as e:
        parts.append(f"📺 Series: ❌ {e}")

    try:
        usage = shutil.disk_usage(SSD_MOUNT_PATH)
        total = format_size(usage.total)
        used = format_size(usage.used)
        free = format_size(usage.free)
        percent = usage.used / usage.total * 100
        parts.append(f"\n💾 Disk: {used} / {total} ({percent:.1f}% used, {free} free)")
    except Exception:
        parts.append("\n💾 Disk: unavailable")

    await update.message.reply_text("\n".join(parts), parse_mode="Markdown")
