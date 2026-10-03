"""İçerik dosyalarını (YAML ön bilgili Markdown) okuma, yazma ve doğrulama."""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

KOK = Path(__file__).resolve().parent.parent
GONDERI_KLASORU = KOK / "icerik" / "gonderiler"

PLATFORMLAR = {"instagram", "facebook", "youtube", "tiktok"}
TURLER = {
    "instagram": {"gorsel", "carousel", "reels"},
    "facebook": {"metin", "gorsel", "video", "baglanti"},
    "youtube": {"video", "shorts"},
    "tiktok": {"video"},
}
DURUMLAR = ["taslak", "incelendi", "onaylandi", "yayinlandi", "hata"]

# Platform sınırları (karakter / adet)
METIN_SINIRI = {"instagram": 2200, "facebook": 63206, "youtube": 5000, "tiktok": 2200}
BASLIK_SINIRI = {"youtube": 100}
HASHTAG_SINIRI = {"instagram": 30, "tiktok": 30, "youtube": 15}

_ON_BILGI = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)


@dataclass
class Gonderi:
    yol: Path
    veri: dict
    govde: str = ""
    hatalar: list[str] = field(default_factory=list)

    @property
    def kimlik(self) -> str:
        return str(self.veri.get("id", self.yol.stem))

    @property
    def platform(self) -> str:
        return str(self.veri.get("platform", ""))

    @property
    def tur(self) -> str:
        return str(self.veri.get("tur", ""))

    @property
    def durum(self) -> str:
        return str(self.veri.get("durum", ""))

    @property
    def metin(self) -> str:
        return str(self.veri.get("metin", "") or "").strip()

    @property
    def medya(self) -> list[str]:
        return [str(m) for m in (self.veri.get("medya") or [])]

    @property
    def planlanan(self) -> dt.datetime | None:
        deger = self.veri.get("planlanan_tarih")
        if deger is None:
            return None
        if isinstance(deger, dt.datetime):
            return deger
        if isinstance(deger, dt.date):
            return dt.datetime.combine(deger, dt.time(0, 0))
        return dt.datetime.fromisoformat(str(deger))

    def hashtagler(self) -> list[str]:
        return re.findall(r"#\w+", self.metin)

    def kaydet(self) -> None:
        on_bilgi = yaml.safe_dump(self.veri, allow_unicode=True, sort_keys=False)
        self.yol.write_text(f"---\n{on_bilgi}---\n{self.govde}", encoding="utf-8")


def oku(yol: Path) -> Gonderi:
    yazi = Path(yol).read_text(encoding="utf-8")
    eslesme = _ON_BILGI.match(yazi)
    if not eslesme:
        raise ValueError(f"{yol}: YAML ön bilgisi (--- ... ---) bulunamadı")
    veri = yaml.safe_load(eslesme.group(1)) or {}
    if not isinstance(veri, dict):
        raise ValueError(f"{yol}: ön bilgi bir sözlük olmalı")
    return Gonderi(yol=Path(yol), veri=veri, govde=eslesme.group(2))


def tumunu_oku(klasor: Path = GONDERI_KLASORU) -> list[Gonderi]:
    return [oku(p) for p in sorted(Path(klasor).rglob("*.md"))]


def dogrula(g: Gonderi) -> list[str]:
    """Gönderiyi kurallara göre kontrol eder; hata mesajlarının listesini döndürür."""
    h: list[str] = []
    for alan in ("id", "platform", "tur", "durum", "planlanan_tarih", "metin"):
        if not g.veri.get(alan):
            h.append(f"'{alan}' alanı eksik")
    if g.platform and g.platform not in PLATFORMLAR:
        h.append(f"bilinmeyen platform: {g.platform}")
    elif g.platform and g.tur and g.tur not in TURLER[g.platform]:
        h.append(f"{g.platform} için geçersiz tür: {g.tur} (geçerli: {sorted(TURLER[g.platform])})")
    if g.durum and g.durum not in DURUMLAR:
        h.append(f"geçersiz durum: {g.durum}")
    try:
        g.planlanan
    except ValueError:
        h.append("planlanan_tarih ISO biçiminde olmalı (ör. 2026-10-07T19:00:00+03:00)")

    sinir = METIN_SINIRI.get(g.platform)
    if sinir and len(g.metin) > sinir:
        h.append(f"metin {len(g.metin)} karakter; {g.platform} sınırı {sinir}")
    hs = HASHTAG_SINIRI.get(g.platform)
    if hs and len(g.hashtagler()) > hs:
        h.append(f"{len(g.hashtagler())} hashtag var; {g.platform} sınırı {hs}")

    baslik = str(g.veri.get("baslik", "") or "")
    if g.platform == "youtube":
        if not baslik:
            h.append("YouTube için 'baslik' zorunlu")
        elif len(baslik) > BASLIK_SINIRI["youtube"]:
            h.append(f"başlık {len(baslik)} karakter; YouTube sınırı 100")

    medya_gerekir = not (g.platform == "facebook" and g.tur in {"metin", "baglanti"})
    if medya_gerekir and not g.medya:
        h.append("'medya' listesi boş; bu tür için en az bir medya gerekir")
    if g.platform == "instagram" and g.medya:
        if any(not m.startswith("https://") for m in g.medya):
            h.append("Instagram medyası herkese açık https:// URL olmalı")
        if g.tur == "carousel" and not 2 <= len(g.medya) <= 10:
            h.append("carousel 2-10 medya içermeli")
    if g.platform == "tiktok" and g.medya and not g.medya[0].startswith("https://"):
        h.append("TikTok videosu doğrulanmış alan adında https:// URL olmalı")
    if g.platform == "facebook" and g.tur == "baglanti" and not g.veri.get("baglanti"):
        h.append("'baglanti' türü için 'baglanti' alanı zorunlu")

    if g.durum in {"onaylandi", "yayinlandi"} and not g.veri.get("onaylayan"):
        h.append("onaylı gönderide 'onaylayan' alanı olmalı (yalnızca /onayla ile ekleyin)")
    return h
