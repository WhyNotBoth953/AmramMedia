import logging

import aiohttp

from app.config import PLEX_TOKEN, PLEX_URL

logger = logging.getLogger(__name__)


class PlexClient:
    def __init__(self):
        self.base_url = PLEX_URL.rstrip("/")
        self.token = PLEX_TOKEN

    async def scan_library(self, section_id: int | None = None) -> None:
        """Trigger a Plex library scan. If section_id is None, scan all sections."""
        try:
            sections = [section_id] if section_id else await self._get_section_ids()
            async with aiohttp.ClientSession() as session:
                for sid in sections:
                    async with session.get(
                        f"{self.base_url}/library/sections/{sid}/refresh",
                        params={"X-Plex-Token": self.token},
                    ) as resp:
                        if resp.status < 400:
                            logger.info("Plex scan triggered for section %s", sid)
                        else:
                            logger.warning("Plex scan failed for section %s: %s", sid, resp.status)
        except Exception as e:
            logger.warning("Could not trigger Plex scan: %s", e)

    async def _get_section_ids(self) -> list[int]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/library/sections",
                params={"X-Plex-Token": self.token},
                headers={"Accept": "application/json"},
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return [
                    d["key"]
                    for d in data.get("MediaContainer", {}).get("Directory", [])
                ]


plex = PlexClient()
