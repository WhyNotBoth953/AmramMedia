import logging

import docker
import docker.errors
from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.auth import restricted

logger = logging.getLogger(__name__)

MANAGED_SERVICES = [
    "plex", "sonarr", "radarr", "qbittorrent",
    "bazarr", "prowlarr", "telegram-bot", "web-dashboard",
]

STATUS_ICON = {
    "running": "🟢",
    "restarting": "🟡",
    "exited": "🔴",
    "paused": "🟡",
    "not_found": "⚫",
}


@restricted
async def services_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /services - show status of all managed containers."""
    try:
        client = docker.from_env()
    except Exception as e:
        await update.message.reply_text(f"❌ Docker unavailable: {e}")
        return

    lines = ["⚙️ *Service Status:*\n"]
    for name in MANAGED_SERVICES:
        try:
            container = client.containers.get(name)
            status = container.status
        except docker.errors.NotFound:
            status = "not_found"
        icon = STATUS_ICON.get(status, "⚪")
        lines.append(f"{icon} `{name}`: {status}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
