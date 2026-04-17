import logging

import docker
import docker.errors
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter()

MANAGED_SERVICES = [
    "plex",
    "sonarr",
    "radarr",
    "qbittorrent",
    "bazarr",
    "prowlarr",
    "telegram-bot",
    "web-dashboard",
]


def _get_client():
    return docker.from_env()


@router.get("/api/services")
async def get_services():
    try:
        client = _get_client()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Docker unavailable: {e}")

    result = []
    for name in MANAGED_SERVICES:
        try:
            container = client.containers.get(name)
            result.append({"name": name, "status": container.status})
        except docker.errors.NotFound:
            result.append({"name": name, "status": "not_found"})
    return result


@router.post("/api/services/{name}/restart")
async def restart_service(name: str):
    if name not in MANAGED_SERVICES:
        raise HTTPException(status_code=400, detail="Unknown service")
    try:
        client = _get_client()
        container = client.containers.get(name)
        container.restart(timeout=10)
        logger.info("Restarted container: %s", name)
        return {"status": "restarting"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
