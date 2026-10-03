"""YouTube Data API v3 istemcisi (video ve Shorts).

Gerekenler: OAuth istemcisi ve youtube.upload + youtube.readonly kapsamlı
yenileme tokenı (`python -m araclar.youtube_yetkilendir` ile alınır).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import requests

from ..icerik import KOK
from .ortak import ortam

KAPSAMLAR = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def _servis():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    kimlik = Credentials(
        token=None,
        refresh_token=ortam("YOUTUBE_YENILEME_TOKENI"),
        client_id=ortam("YOUTUBE_ISTEMCI_ID"),
        client_secret=ortam("YOUTUBE_ISTEMCI_SIRRI"),
        token_uri="https://oauth2.googleapis.com/token",
        scopes=KAPSAMLAR,
    )
    return build("youtube", "v3", credentials=kimlik, cache_discovery=False)


def _yerel_dosya(kaynak: str, gecici: Path) -> Path:
    if kaynak.startswith(("http://", "https://")):
        hedef = gecici / "video.mp4"
        with requests.get(kaynak, stream=True, timeout=300) as y:
            y.raise_for_status()
            with hedef.open("wb") as f:
                for parca in y.iter_content(1 << 20):
                    f.write(parca)
        return hedef
    yol = Path(kaynak)
    return yol if yol.is_absolute() else KOK / yol


def yayinla(g) -> dict:
    from googleapiclient.http import MediaFileUpload

    aciklama = g.metin
    if g.tur == "shorts" and "#shorts" not in aciklama.lower():
        aciklama += "\n\n#Shorts"
    govde = {
        "snippet": {
            "title": g.veri["baslik"],
            "description": aciklama,
            "tags": list(g.veri.get("etiketler") or []),
            "categoryId": str(g.veri.get("kategori_id", "22")),
            "defaultLanguage": "tr",
        },
        "status": {
            "privacyStatus": g.veri.get("gizlilik", "public"),
            "selfDeclaredMadeForKids": False,
        },
    }
    with tempfile.TemporaryDirectory() as d:
        dosya = _yerel_dosya(g.medya[0], Path(d))
        istek = _servis().videos().insert(
            part="snippet,status", body=govde,
            media_body=MediaFileUpload(str(dosya), chunksize=-1, resumable=True),
        )
        yanit = None
        while yanit is None:
            _, yanit = istek.next_chunk()
    vid = yanit["id"]
    url = (f"https://www.youtube.com/shorts/{vid}" if g.tur == "shorts"
           else f"https://www.youtube.com/watch?v={vid}")
    return {"platform_id": vid, "url": url}


def metrikler(sonuc: dict) -> dict:
    yanit = _servis().videos().list(part="statistics", id=sonuc["platform_id"]).execute()
    if not yanit.get("items"):
        return {"not": "video bulunamadı"}
    s = yanit["items"][0]["statistics"]
    return {
        "goruntulenme": int(s.get("viewCount", 0)),
        "begeni": int(s.get("likeCount", 0)),
        "yorum": int(s.get("commentCount", 0)),
    }
