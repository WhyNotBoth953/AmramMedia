import asyncio
import logging

from telegram.ext import Application

from bot.config import POLL_INTERVAL, TELEGRAM_ALLOWED_CHAT_IDS
from bot.services.qbittorrent import QBittorrentClient

logger = logging.getLogger(__name__)

qbt = QBittorrentClient()


async def poll_completed_downloads(app: Application) -> None:
    """Background task that polls qBittorrent for completed downloads
    and sends notifications to all allowed chat IDs."""
    seen_hashes: set[str] = set()

    # Initialize with current completed torrents to avoid notifying on startup
    try:
        await qbt.login()
        seen_hashes = await qbt.get_completed_hashes()
        logger.info("Initialized poller with %d existing completed torrents", len(seen_hashes))
    except Exception as e:
        logger.warning("Failed to initialize poller: %s", e)

    while True:
        await asyncio.sleep(POLL_INTERVAL)
        try:
            current = await qbt.get_completed_hashes()
            new_hashes = current - seen_hashes

            if new_hashes:
                torrents = await qbt.get_torrents(filter="completed")
                for torrent in torrents:
                    if torrent["hash"] in new_hashes:
                        name = torrent.get("name", "Unknown")
                        size = torrent.get("total_size", 0)
                        size_str = f"{size / (1024**3):.1f} GB" if size > 0 else "unknown size"

                        message = (
                            f"✅ *Download Complete!*\n\n"
                            f"📦 {name}\n"
                            f"💾 {size_str}"
                        )

                        for chat_id in TELEGRAM_ALLOWED_CHAT_IDS:
                            try:
                                await app.bot.send_message(
                                    chat_id=chat_id,
                                    text=message,
                                    parse_mode="Markdown",
                                )
                            except Exception as e:
                                logger.error("Failed to notify chat %s: %s", chat_id, e)

                seen_hashes = current

        except Exception as e:
            logger.error("Poller error: %s", e)
