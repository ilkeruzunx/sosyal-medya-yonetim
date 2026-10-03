"""Instagram ve Facebook Sayfası DM'leri (Meta Messenger Platformu).

Gerekenler: sayfa erişim tokenında pages_messaging ve instagram_manage_messages izinleri.
Kural: yalnızca kişinin son mesajından sonraki 24 saat içinde yanıt gönderilebilir.
"""

from __future__ import annotations

import datetime as dt
import json

from . import meta
from .ortak import istek, ortam

YANIT_PENCERESI = dt.timedelta(hours=24)


def _kendi_id(platform: str) -> str:
    return ortam("META_IG_KULLANICI_ID") if platform == "instagram" else ortam("META_SAYFA_ID")


def _tarih(deger: str) -> dt.datetime:
    return dt.datetime.strptime(deger, "%Y-%m-%dT%H:%M:%S%z")


def dmleri_getir(platform: str, sinir: dt.datetime) -> list[dict]:
    """Son mesajı karşı taraftan gelen (yanıt bekleyen) konuşmalar."""
    kendi = _kendi_id(platform)
    konusmalar = istek("GET", f"{meta.taban()}/{ortam('META_SAYFA_ID')}/conversations", params={
        "platform": "messenger" if platform == "facebook" else "instagram",
        "fields": "id,updated_time,messages.limit(10){id,message,from,created_time}",
        "limit": 25, "access_token": meta.token(),
    }).get("data", [])
    sonuc = []
    for k in konusmalar:
        mesajlar = (k.get("messages") or {}).get("data", [])  # en yeni önce
        bekleyen = []
        for m in mesajlar:
            if (m.get("from") or {}).get("id") == kendi:
                break
            bekleyen.append(m)
        if not bekleyen:
            continue
        son = _tarih(bekleyen[0]["created_time"])
        if son < sinir:
            continue
        gonderen = bekleyen[0].get("from") or {}
        sonuc.append({
            "platform_id": bekleyen[0]["id"],
            "konusma_id": k["id"],
            "alici_id": gonderen.get("id"),
            "yazar": gonderen.get("username") or gonderen.get("name") or "(bilinmiyor)",
            "metin": "\n".join(m.get("message") or "[ek/medya]" for m in reversed(bekleyen)),
            "tarih": son.isoformat(),
            "son_yanit": (son + YANIT_PENCERESI).isoformat(),
        })
    return sonuc


def dm_gonder(alici_id: str, metin: str) -> dict:
    s = istek("POST", f"{meta.taban()}/{ortam('META_SAYFA_ID')}/messages", data={
        "recipient": json.dumps({"id": alici_id}),
        "message": json.dumps({"text": metin}, ensure_ascii=False),
        "messaging_type": "RESPONSE",
        "access_token": meta.token(),
    })
    return {"yanit_id": s.get("message_id")}
