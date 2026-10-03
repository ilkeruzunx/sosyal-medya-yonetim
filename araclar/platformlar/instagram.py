"""Instagram Graph API (İçerik Yayınlama) istemcisi.

Gerekenler: Instagram Business/Creator hesabı, bağlı Facebook sayfası ve
instagram_content_publish + instagram_manage_insights izinli uzun ömürlü token.
"""

from __future__ import annotations

from ..icerik import VIDEO_UZANTILARI
from . import meta
from .ortak import PlatformHatasi, bekle, istek, ortam


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
    video = url.lower().split("?")[0].endswith(VIDEO_UZANTILARI)
    alanlar = {"video_url": url, "media_type": "VIDEO"} if video else {"image_url": url}
    if carousel_ogesi:
        alanlar["is_carousel_item"] = "true"
    return _kapsayici(**alanlar)


def yayinla(g) -> dict:
    if g.tur == "hikaye":
        url = g.medya[0]
        alan = "video_url" if g.video_mu(url) else "image_url"
        kid = _kapsayici(media_type="STORIES", **{alan: url})
    elif g.tur == "reels":
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
    sonuc = {"platform_id": medya["id"], "url": bilgi.get("permalink")}
    if g.tur == "hikaye":
        sonuc["tur"] = "hikaye"  # metrikler yalnızca 24 saat alınabilir
    return sonuc


def _hikaye_metrikleri(mid: str) -> dict:
    ic = istek("GET", f"{meta.taban()}/{mid}/insights",
               params={"metric": "reach,views,replies,shares", "access_token": meta.token()})
    adlar = {"reach": "erisim", "views": "goruntulenme", "replies": "yanit", "shares": "paylasim"}
    return {adlar.get(m["name"], m["name"]): m["values"][0]["value"] for m in ic.get("data", [])}


def metrikler(sonuc: dict) -> dict:
    mid = sonuc["platform_id"]
    if sonuc.get("tur") == "hikaye":
        try:
            return _hikaye_metrikleri(mid)
        except PlatformHatasi as e:
            return {"not": f"hikâye metrikleri alınamadı (yalnızca ilk 24 saat açıktır): {e}"}
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


# --- Yorumlar (instagram_manage_comments izni gerekir) ---

def yorumlari_getir(sinir) -> list[dict]:
    """`sinir` (aware datetime) sonrasındaki, henüz yanıtlanmamış yorumlar."""
    import datetime as dt

    tok = meta.token()
    kendi = istek("GET", f"{meta.taban()}/{_kullanici()}",
                  params={"fields": "username", "access_token": tok})["username"]
    medyalar = istek("GET", f"{meta.taban()}/{_kullanici()}/media", params={
        "fields": "id,caption,permalink,comments_count", "limit": 25, "access_token": tok,
    }).get("data", [])
    sonuc = []
    for m in medyalar:
        if not m.get("comments_count"):
            continue
        yorumlar = istek("GET", f"{meta.taban()}/{m['id']}/comments", params={
            "fields": "id,text,username,timestamp,replies{username}", "limit": 50, "access_token": tok,
        }).get("data", [])
        for y in yorumlar:
            tarih = dt.datetime.strptime(y["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
            yanitlayanlar = {r.get("username") for r in (y.get("replies") or {}).get("data", [])}
            if tarih < sinir or y.get("username") == kendi or kendi in yanitlayanlar:
                continue
            sonuc.append({
                "platform_id": y["id"], "gonderi_id": m["id"],
                "gonderi_ozeti": (m.get("caption") or "")[:80], "gonderi_url": m.get("permalink"),
                "yazar": y.get("username"), "metin": y.get("text", ""),
                "tarih": tarih.isoformat(),
            })
    return sonuc


def yorum_yanitla(yorum_id: str, metin: str) -> dict:
    s = istek("POST", f"{meta.taban()}/{yorum_id}/replies",
              data={"message": metin, "access_token": meta.token()})
    return {"yanit_id": s["id"]}
