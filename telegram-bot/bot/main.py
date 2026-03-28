import asyncio
import logging

from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers.callbacks import callback_handler
from bot.handlers.delete import delete_handler
from bot.handlers.disk import disk_handler
from bot.handlers.library import library_handler
from bot.handlers.movie import movie_handler
from bot.handlers.restart import restart_handler
from bot.handlers.search import search_handler
from bot.handlers.series import series_handler
from bot.handlers.status import status_handler
from bot.handlers.upcoming import upcoming_handler
from bot.notifications.poller import poll_completed_downloads

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start_handler(update, context):
    """Handle /start command."""
    await update.message.reply_text(
        "🎬 *AmramMedia Bot*\n\n"
        "Available commands:\n"
        "/search <query> - Search movies & series\n"
        "/movie <title> - Add a movie\n"
        "/series <title> - Add a series\n"
        "/status - Active downloads\n"
        "/library - Library stats\n"
        "/upcoming - Upcoming episodes\n"
        "/delete <title> - Remove from library\n"
        "/disk - Disk usage\n"
        "/restart <service> - Restart a service",
        parse_mode="Markdown",
    )


async def post_init(app) -> None:
    """Start background tasks after the application initializes."""
    asyncio.create_task(poll_completed_downloads(app))
    logger.info("Download notification poller started")


def main() -> None:
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Command handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", start_handler))
    app.add_handler(CommandHandler("search", search_handler))
    app.add_handler(CommandHandler("movie", movie_handler))
    app.add_handler(CommandHandler("series", series_handler))
    app.add_handler(CommandHandler("status", status_handler))
    app.add_handler(CommandHandler("library", library_handler))
    app.add_handler(CommandHandler("upcoming", upcoming_handler))
    app.add_handler(CommandHandler("delete", delete_handler))
    app.add_handler(CommandHandler("disk", disk_handler))
    app.add_handler(CommandHandler("restart", restart_handler))

    # Inline keyboard callbacks
    app.add_handler(CallbackQueryHandler(callback_handler))

    logger.info("AmramMedia Bot starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
