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
    "https://www.googleapis.com/auth/youtube.force-ssl",  # yorum yanıtlama
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


# --- Yorumlar (youtube.force-ssl kapsamı gerekir) ---

def yorumlari_getir(sinir) -> list[dict]:
    """`sinir` (aware datetime) sonrasındaki, kanalın henüz yanıtlamadığı yorumlar."""
    import datetime as dt

    servis = _servis()
    kanal = servis.channels().list(part="id", mine=True).execute()["items"][0]["id"]
    yanit = servis.commentThreads().list(
        part="snippet,replies", allThreadsRelatedToChannelId=kanal,
        maxResults=50, order="time", textFormat="plainText",
    ).execute()
    sonuc = []
    for t in yanit.get("items", []):
        ust = t["snippet"]["topLevelComment"]["snippet"]
        tarih = dt.datetime.fromisoformat(ust["publishedAt"].replace("Z", "+00:00"))
        yanitlayanlar = {r["snippet"].get("authorChannelId", {}).get("value")
                         for r in (t.get("replies") or {}).get("comments", [])}
        if tarih < sinir or ust.get("authorChannelId", {}).get("value") == kanal or kanal in yanitlayanlar:
            continue
        vid = t["snippet"].get("videoId")
        sonuc.append({
            "platform_id": t["id"], "gonderi_id": vid, "gonderi_ozeti": "",
            "gonderi_url": f"https://www.youtube.com/watch?v={vid}" if vid else None,
            "yazar": ust.get("authorDisplayName"), "metin": ust.get("textDisplay", ""),
            "tarih": tarih.isoformat(),
        })
    return sonuc


def yorum_yanitla(yorum_id: str, metin: str) -> dict:
    s = _servis().comments().insert(
        part="snippet", body={"snippet": {"parentId": yorum_id, "textOriginal": metin}},
    ).execute()
    return {"yanit_id": s["id"]}
