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

    async def delete_torrents_by_name(self, name: str) -> int:
        """Delete torrents whose name contains the given string. Returns count deleted."""
        torrents = await self.get_torrents()
        name_lower = name.lower()
        hashes = [t["hash"] for t in torrents if name_lower in t.get("name", "").lower()]
        if hashes:
            await self._post(
                "torrents/delete",
                data={"hashes": "|".join(hashes), "deleteFiles": "true"},
            )
        return len(hashes)

    async def _post(self, endpoint: str, data: dict) -> None:
        async with aiohttp.ClientSession(cookie_jar=self._cookie_jar) as session:
            async with session.post(
                f"{self.base_url}/api/v2/{endpoint}",
                data=data,
            ) as resp:
                if resp.status == 403:
                    await self.login()
                    return await self._post(endpoint, data)
                resp.raise_for_status()


qbt = QBittorrentClient()
