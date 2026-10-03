"""TikTok Content Posting API istemcisi.

Gerekenler: video.publish + video.list kapsamlı TikTok geliştirici uygulaması.
Not: TikTok denetiminden geçmemiş uygulamalar yalnızca SELF_ONLY (gizli)
paylaşım yapabilir; bu durumda gönderi gizli yüklenir, siz uygulamadan açarsınız.
Video URL'si TikTok'ta doğrulanmış bir alan adında olmalıdır (PULL_FROM_URL).
"""

from __future__ import annotations

from .ortak import PlatformHatasi, bekle, istek, ortam

TABAN = "https://open.tiktokapis.com/v2"
_token: str | None = None


def _erisim_tokeni() -> str:
    """Yenileme tokenından kısa ömürlü (24 saat) erişim tokenı alır."""
    global _token
    if _token is None:
        s = istek("POST", f"{TABAN}/oauth/token/", data={
            "client_key": ortam("TIKTOK_ISTEMCI_ANAHTARI"),
            "client_secret": ortam("TIKTOK_ISTEMCI_SIRRI"),
            "grant_type": "refresh_token",
            "refresh_token": ortam("TIKTOK_YENILEME_TOKENI"),
        })
        if "access_token" not in s:
            raise PlatformHatasi(f"TikTok token yenilenemedi: {s}")
        if s.get("refresh_token") and s["refresh_token"] != ortam("TIKTOK_YENILEME_TOKENI"):
            print("UYARI: TikTok yeni bir yenileme tokenı verdi; TIKTOK_YENILEME_TOKENI'ni güncelleyin.")
        _token = s["access_token"]
    return _token


def _api(yol: str, govde: dict | None = None, params: dict | None = None) -> dict:
    s = istek("POST", f"{TABAN}/{yol}", json=govde or {}, params=params, headers={
        "Authorization": f"Bearer {_erisim_tokeni()}",
        "Content-Type": "application/json; charset=UTF-8",
    })
    hata = s.get("error", {})
    if hata.get("code") not in (None, "ok"):
        raise PlatformHatasi(f"TikTok {yol}: {hata}")
    return s.get("data", {})


def yayinla(g) -> dict:
    yaratici = _api("post/publish/creator_info/query/")
    secenekler = yaratici.get("privacy_level_options") or ["SELF_ONLY"]
    istenen = g.veri.get("gizlilik", "PUBLIC_TO_EVERYONE")
    gizlilik = istenen if istenen in secenekler else secenekler[-1]
    if gizlilik != istenen:
        print(f"UYARI: TikTok '{istenen}' izin vermedi; '{gizlilik}' kullanılıyor.")

    baslat = _api("post/publish/video/init/", {
        "post_info": {
            "title": g.metin,
            "privacy_level": gizlilik,
            "disable_comment": False,
            "disable_duet": False,
            "disable_stitch": False,
        },
        "source_info": {"source": "PULL_FROM_URL", "video_url": g.medya[0]},
    })
    yid = baslat["publish_id"]

    def kontrol():
        d = _api("post/publish/status/fetch/", {"publish_id": yid})
        if d.get("status") == "FAILED":
            raise PlatformHatasi(f"TikTok yayın hatası: {d.get('fail_reason')}")
        return d if d.get("status") == "PUBLISH_COMPLETE" else None

    durum = bekle(kontrol, f"TikTok yayını {yid}", deneme=120)
    ids = durum.get("publicaly_available_post_id") or []  # API'deki yazım böyle
    vid = str(ids[0]) if ids else None
    return {
        "platform_id": vid or yid,
        "yayin_id": yid,
        "gizlilik": gizlilik,
        "url": f"https://www.tiktok.com/@{yaratici.get('creator_username', '')}/video/{vid}" if vid else None,
    }


def metrikler(sonuc: dict) -> dict:
    d = _api("video/query/", {"filters": {"video_ids": [sonuc["platform_id"]]}},
             params={"fields": "id,view_count,like_count,comment_count,share_count"})
    videolar = d.get("videos") or []
    if not videolar:
        return {"not": "video bulunamadı (gizli olabilir)"}
    v = videolar[0]
    return {
        "goruntulenme": v.get("view_count"),
        "begeni": v.get("like_count"),
        "yorum": v.get("comment_count"),
        "paylasim": v.get("share_count"),
    }
