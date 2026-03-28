from telegram.constants import MessageLimit


def truncate(text: str, max_len: int = MessageLimit.MAX_TEXT_LENGTH) -> str:
    """Truncate text to fit Telegram's message length limit."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def progress_bar(percent: float, length: int = 10) -> str:
    """Create a text progress bar."""
    filled = int(length * percent / 100)
    return "█" * filled + "░" * (length - filled)


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable size."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def format_speed(bytes_per_sec: int) -> str:
    """Format download speed."""
    return f"{format_size(bytes_per_sec)}/s"


def format_eta(seconds: int) -> str:
    """Format ETA from seconds."""
    if seconds <= 0 or seconds == 8640000:  # qBittorrent uses 8640000 for unknown
        return "unknown"
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m"
    if minutes > 0:
        return f"{int(minutes)}m {int(secs)}s"
    return f"{int(secs)}s"


def format_movie_result(movie: dict, index: int) -> str:
    """Format a single movie search result."""
    title = movie.get("title", "Unknown")
    year = movie.get("year", "N/A")
    overview = movie.get("overview", "No description available.")
    if len(overview) > 150:
        overview = overview[:147] + "..."
    return f"*{index}. {title} ({year})*\n{overview}"


def format_series_result(series: dict, index: int) -> str:
    """Format a single series search result."""
    title = series.get("title", "Unknown")
    year = series.get("year", "N/A")
    seasons = series.get("seasonCount", "?")
    overview = series.get("overview", "No description available.")
    if len(overview) > 150:
        overview = overview[:147] + "..."
    return f"*{index}. {title} ({year})* - {seasons} seasons\n{overview}"
