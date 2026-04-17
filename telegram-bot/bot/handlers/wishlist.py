import asyncio
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
async def wishlist_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /wishlist - show unmonitored movies and series."""
    movies_data, series_data = await asyncio.gather(
        radarr.get_movies(),
        sonarr.get_series(),
        return_exceptions=True,
    )

    items = []
    if isinstance(movies_data, list):
        for m in movies_data:
            if not m.get("monitored"):
                items.append(("movie", m["id"], m.get("title", "?"), m.get("year", "")))
    if isinstance(series_data, list):
        for s in series_data:
            if not s.get("monitored"):
                items.append(("series", s["id"], s.get("title", "?"), s.get("year", "")))

    if not items:
        await update.message.reply_text("📋 Wishlist is empty.")
        return

    lines = [f"📋 *Wishlist ({len(items)} items):*\n"]
    buttons = []
    for kind, item_id, title, year in items[:10]:
        icon = "🎬" if kind == "movie" else "📺"
        lines.append(f"{icon} {title} ({year})")
        buttons.append([
            InlineKeyboardButton("⬇️ Download", callback_data=f"wldl_{kind}:{item_id}"),
            InlineKeyboardButton("🗑 Remove", callback_data=f"wlrm_{kind}:{item_id}"),
        ])

    if len(items) > 10:
        lines.append(f"\n_...and {len(items) - 10} more_")

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
