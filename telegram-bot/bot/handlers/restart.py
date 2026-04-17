import logging

import docker
from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.auth import restricted

logger = logging.getLogger(__name__)

ALLOWED_CONTAINERS = {
    "plex", "sonarr", "radarr", "qbittorrent",
    "bazarr", "prowlarr", "telegram-bot", "web-dashboard",
}


@restricted
async def restart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /restart <service> - restart a Docker container."""
    if not context.args:
        services = ", ".join(sorted(ALLOWED_CONTAINERS))
        await update.message.reply_text(
            f"Usage: /restart <service>\nAvailable: {services}"
        )
        return

    service = context.args[0].lower()
    if service not in ALLOWED_CONTAINERS:
        services = ", ".join(sorted(ALLOWED_CONTAINERS))
        await update.message.reply_text(
            f"❌ Unknown service '{service}'.\nAvailable: {services}"
        )
        return

    await update.message.reply_text(f"🔄 Restarting {service}...")

    try:
        client = docker.from_env()
        container = client.containers.get(service)
        container.restart(timeout=30)
        await update.message.reply_text(f"✅ {service} restarted successfully.")
    except docker.errors.NotFound:
        await update.message.reply_text(f"❌ Container '{service}' not found.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to restart {service}: {e}")
