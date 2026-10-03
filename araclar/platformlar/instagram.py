"""Instagram Graph API (İçerik Yayınlama) istemcisi.

Gerekenler: Instagram Business/Creator hesabı, bağlı Facebook sayfası ve
instagram_content_publish + instagram_manage_insights izinli uzun ömürlü token.
"""

from __future__ import annotations

from . import meta
from .ortak import PlatformHatasi, bekle, istek, ortam

_VIDEO_UZANTILARI = (".mp4", ".mov")


def _kullanici() -> str:
    return ortam("META_IG_KULLANICI_ID")


def _kapsayici(**alanlar) -> str:
    sonuc = istek("POST", f"{meta.taban()}/{_kullanici()}/media",
                  data={**alanlar, "access_token": meta.token()})
    return sonuc["id"]


def _hazir_olunca(kapsayici_id: str) -> None:
    def kontrol():
        s = istek("GET", f"{meta.taban()}/{kapsayici_id}",
                  params={"fields": "status_code", "access_token": meta.token()})
        if s.get("status_code") == "ERROR":
            raise PlatformHatasi(f"Instagram medya işleme hatası: {s}")
        return s.get("status_code") == "FINISHED"
    bekle(kontrol, f"Instagram kapsayıcısı {kapsayici_id}")


def _ogeyi_hazirla(url: str, carousel_ogesi: bool = False) -> str:
    video = url.lower().split("?")[0].endswith(_VIDEO_UZANTILARI)
    alanlar = {"video_url": url, "media_type": "VIDEO"} if video else {"image_url": url}
    if carousel_ogesi:
        alanlar["is_carousel_item"] = "true"
    return _kapsayici(**alanlar)


def yayinla(g) -> dict:
    if g.tur == "reels":
        kid = _kapsayici(media_type="REELS", video_url=g.medya[0], caption=g.metin,
                         share_to_feed="true")
    elif g.tur == "carousel":
        cocuklar = [_ogeyi_hazirla(u, carousel_ogesi=True) for u in g.medya]
        for c in cocuklar:
            _hazir_olunca(c)
        kid = _kapsayici(media_type="CAROUSEL", children=",".join(cocuklar), caption=g.metin)
    else:
        kid = _kapsayici(image_url=g.medya[0], caption=g.metin)
    _hazir_olunca(kid)

    medya = istek("POST", f"{meta.taban()}/{_kullanici()}/media_publish",
                  data={"creation_id": kid, "access_token": meta.token()})
    bilgi = istek("GET", f"{meta.taban()}/{medya['id']}",
                  params={"fields": "permalink", "access_token": meta.token()})
    return {"platform_id": medya["id"], "url": bilgi.get("permalink")}


def metrikler(sonuc: dict) -> dict:
    mid = sonuc["platform_id"]
    temel = istek("GET", f"{meta.taban()}/{mid}",
                  params={"fields": "like_count,comments_count", "access_token": meta.token()})
    veri = {"begeni": temel.get("like_count"), "yorum": temel.get("comments_count")}
    try:
        ic = istek("GET", f"{meta.taban()}/{mid}/insights",
                   params={"metric": "reach,views,saved,shares", "access_token": meta.token()})
        adlar = {"reach": "erisim", "views": "goruntulenme", "saved": "kaydetme", "shares": "paylasim"}
        for m in ic.get("data", []):
            veri[adlar.get(m["name"], m["name"])] = m["values"][0]["value"]
    except PlatformHatasi as e:  # bazı medya türleri tüm metrikleri desteklemez
        veri["not"] = f"içgörüler alınamadı: {e}"
    return veri
