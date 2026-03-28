import aiohttp

from app.config import QBITTORRENT_PASSWORD, QBITTORRENT_URL, QBITTORRENT_USERNAME


class QBittorrentClient:
    def __init__(self):
        self.base_url = QBITTORRENT_URL.rstrip("/")
        self._cookie_jar = aiohttp.CookieJar()

    async def login(self) -> None:
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
        return await self._get("torrents/info", params={"filter": filter})

    async def get_transfer_info(self) -> dict:
        return await self._get("transfer/info")


qbt = QBittorrentClient()
