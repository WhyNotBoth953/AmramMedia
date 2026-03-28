import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.services.sonarr import SonarrClient
from bot.utils.auth import restricted
from bot.utils.formatters import truncate

logger = logging.getLogger(__name__)

sonarr = SonarrClient()


@restricted
async def upcoming_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /upcoming - show upcoming episodes in the next 7 days."""
    try:
        episodes = await sonarr.get_upcoming(days=7)
    except Exception as e:
        await update.message.reply_text(f"❌ Sonarr error: {e}")
        return

    if not episodes:
        await update.message.reply_text("📅 No upcoming episodes in the next 7 days.")
        return

    parts = ["📅 *Upcoming Episodes (7 days):*\n"]
    for ep in episodes[:15]:
        series_title = ep.get("series", {}).get("title", "Unknown")
        season = ep.get("seasonNumber", 0)
        episode = ep.get("episodeNumber", 0)
        title = ep.get("title", "TBA")
        air_date = ep.get("airDate", "Unknown")

        parts.append(
            f"*{series_title}* S{season:02d}E{episode:02d}\n"
            f"  {title} — {air_date}"
        )

    await update.message.reply_text(truncate("\n\n".join(parts)), parse_mode="Markdown")
