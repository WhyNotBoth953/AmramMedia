from fastapi import APIRouter

from app.services.qbittorrent import qbt

router = APIRouter()


@router.get("/api/downloads")
async def get_downloads():
    torrents = await qbt.get_torrents("downloading")
    transfer = await qbt.get_transfer_info()

    items = []
    for t in torrents:
        items.append({
            "name": t.get("name", "Unknown"),
            "progress": round(t.get("progress", 0) * 100, 1),
            "downloadSpeed": t.get("dlspeed", 0),
            "uploadSpeed": t.get("upspeed", 0),
            "size": t.get("total_size", 0),
            "downloaded": t.get("downloaded", 0),
            "eta": t.get("eta", 0),
            "state": t.get("state", "unknown"),
        })

    return {
        "items": items,
        "globalDownloadSpeed": transfer.get("dl_info_speed", 0),
        "globalUploadSpeed": transfer.get("up_info_speed", 0),
    }
