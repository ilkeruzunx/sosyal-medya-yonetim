"""Platform istemcilerinin ortak yardımcıları."""

from __future__ import annotations

import os
import time

import requests

ZAMAN_ASIMI = 60


class PlatformHatasi(RuntimeError):
    pass


def ortam(ad: str, varsayilan: str | None = None) -> str:
    deger = os.environ.get(ad, varsayilan)
    if not deger:
        raise PlatformHatasi(f"{ad} ortam değişkeni tanımlı değil (.env.example dosyasına bakın)")
    return deger


def istek(yontem: str, url: str, **kw) -> dict:
    yanit = requests.request(yontem, url, timeout=ZAMAN_ASIMI, **kw)
    try:
        govde = yanit.json()
    except ValueError:
        govde = {"ham": yanit.text}
    if yanit.status_code >= 400:
        raise PlatformHatasi(f"{yontem} {url.split('?')[0]} → {yanit.status_code}: {govde}")
    return govde


def bekle(kontrol, aciklama: str, deneme: int = 60, aralik: float = 5.0):
    """`kontrol()` doğru bir değer döndürene kadar bekler; o değeri döndürür."""
    for _ in range(deneme):
        sonuc = kontrol()
        if sonuc:
            return sonuc
        time.sleep(aralik)
    raise PlatformHatasi(f"zaman aşımı: {aciklama}")
