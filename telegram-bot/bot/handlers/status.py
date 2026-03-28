import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.services.qbittorrent import QBittorrentClient
from bot.utils.auth import restricted
from bot.utils.formatters import (
    format_eta,
    format_size,
    format_speed,
    progress_bar,
    truncate,
)

logger = logging.getLogger(__name__)

qbt = QBittorrentClient()


@restricted
async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status - show active downloads."""
    try:
        torrents = await qbt.get_torrents(filter="downloading")
        transfer = await qbt.get_transfer_info()
    except Exception as e:
        await update.message.reply_text(f"❌ qBittorrent error: {e}")
        return

    if not torrents:
        dl_speed = format_speed(transfer.get("dl_info_speed", 0))
        up_speed = format_speed(transfer.get("up_info_speed", 0))
        await update.message.reply_text(
            f"✅ No active downloads.\n\n"
            f"⬇️ {dl_speed} | ⬆️ {up_speed}"
        )
        return

    parts = [f"📥 *Active Downloads ({len(torrents)}):*\n"]
    for t in torrents[:10]:
        name = t.get("name", "Unknown")
        percent = t.get("progress", 0) * 100
        dl_speed = format_speed(t.get("dlspeed", 0))
        size = format_size(t.get("total_size", 0))
        eta = format_eta(t.get("eta", 0))
        bar = progress_bar(percent)

        parts.append(
            f"*{name}*\n"
            f"{bar} {percent:.1f}%\n"
            f"⬇️ {dl_speed} | 📦 {size} | ⏱ {eta}\n"
        )

    global_dl = format_speed(transfer.get("dl_info_speed", 0))
    global_up = format_speed(transfer.get("up_info_speed", 0))
    parts.append(f"\n🌐 Total: ⬇️ {global_dl} | ⬆️ {global_up}")

    await update.message.reply_text(truncate("\n".join(parts)), parse_mode="Markdown")
