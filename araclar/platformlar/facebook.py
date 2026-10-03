"""Facebook Sayfası (Graph API) istemcisi.

Gerekenler: pages_manage_posts + pages_read_engagement izinli sayfa erişim tokenı.
"""

from __future__ import annotations

import json

from . import meta
from .ortak import istek, ortam


def _sayfa() -> str:
    return ortam("META_SAYFA_ID")


def _gonder(uc: str, **alanlar) -> dict:
    return istek("POST", f"{meta.taban()}/{_sayfa()}/{uc}",
                 data={**alanlar, "access_token": meta.token()})


def yayinla(g) -> dict:
    if g.tur == "video":
        s = _gonder("videos", file_url=g.medya[0], description=g.metin,
                    title=str(g.veri.get("baslik", "")))
        return {"platform_id": s["id"], "url": f"https://www.facebook.com/{s['id']}"}
    if g.tur == "gorsel" and len(g.medya) == 1:
        s = _gonder("photos", url=g.medya[0], caption=g.metin)
        pid = s.get("post_id", s["id"])
    elif g.tur == "gorsel":
        fotolar = [_gonder("photos", url=u, published="false")["id"] for u in g.medya]
        ekler = json.dumps([{"media_fbid": f} for f in fotolar])
        pid = _gonder("feed", message=g.metin, attached_media=ekler)["id"]
    elif g.tur == "baglanti":
        pid = _gonder("feed", message=g.metin, link=g.veri["baglanti"])["id"]
    else:
        pid = _gonder("feed", message=g.metin)["id"]
    return {"platform_id": pid, "url": f"https://www.facebook.com/{pid}"}


def metrikler(sonuc: dict) -> dict:
    s = istek("GET", f"{meta.taban()}/{sonuc['platform_id']}", params={
        "fields": "shares,reactions.summary(true).limit(0),comments.summary(true).limit(0)",
        "access_token": meta.token(),
    })
    return {
        "tepki": s.get("reactions", {}).get("summary", {}).get("total_count"),
        "yorum": s.get("comments", {}).get("summary", {}).get("total_count"),
        "paylasim": s.get("shares", {}).get("count", 0),
    }
