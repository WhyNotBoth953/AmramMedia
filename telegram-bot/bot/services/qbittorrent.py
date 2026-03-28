import logging

import aiohttp

from bot.config import QBITTORRENT_PASSWORD, QBITTORRENT_URL, QBITTORRENT_USERNAME

logger = logging.getLogger(__name__)


class QBittorrentClient:
    def __init__(self):
        self.base_url = QBITTORRENT_URL.rstrip("/")
        self._cookie_jar = aiohttp.CookieJar()

    async def login(self) -> None:
        """Authenticate with qBittorrent Web API."""
        async with aiohttp.ClientSession(cookie_jar=self._cookie_jar) as session:
            async with session.post(
                f"{self.base_url}/api/v2/auth/login",
                data={
                    "username": QBITTORRENT_USERNAME,
                    "password": QBITTORRENT_PASSWORD,
                },
            ) as resp:
                text = await resp.text()
                if text.strip() != "Ok.":
                    raise ConnectionError(f"qBittorrent login failed: {text}")
        logger.info("Logged into qBittorrent")

    async def _get(self, endpoint: str, params: dict | None = None) -> list | dict:
        async with aiohttp.ClientSession(cookie_jar=self._cookie_jar) as session:
            async with session.get(
                f"{self.base_url}/api/v2/{endpoint}",
                params=params,
            ) as resp:
                if resp.status == 403:
                    await self.login()
                    return await self._get(endpoint, params)
                resp.raise_for_status()
                return await resp.json()

    async def get_torrents(self, filter: str = "all") -> list[dict]:
        """Get torrent list. Filter: all, downloading, seeding, completed, paused."""
        return await self._get("torrents/info", params={"filter": filter})

    async def get_transfer_info(self) -> dict:
        """Get global transfer info (speeds, etc)."""
        return await self._get("transfer/info")

    async def get_completed_hashes(self) -> set[str]:
        """Get hashes of all completed torrents."""
        torrents = await self.get_torrents(filter="completed")
        return {t["hash"] for t in torrents}
