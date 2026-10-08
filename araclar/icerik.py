"""İçerik dosyalarını (YAML ön bilgili Markdown) okuma, yazma ve doğrulama."""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

import yaml

KOK = Path(__file__).resolve().parent.parent
GONDERI_KLASORU = KOK / "icerik" / "gonderiler"

PLATFORMLAR = {"instagram", "facebook", "youtube", "tiktok"}
TURLER = {
    "instagram": {"gorsel", "carousel", "reels", "hikaye"},
    "facebook": {"metin", "gorsel", "video", "baglanti", "hikaye"},
    "youtube": {"video", "shorts"},
    "tiktok": {"video"},
}
DURUMLAR = ["taslak", "incelendi", "onaylandi", "yayinlandi", "hata", "ertelendi"]
# Bu durumdaki gönderiler bekletilir; içerik kontrolleri atlanır, onaylanamaz ve yayınlanmaz.
ERTELENDI = "ertelendi"

# Platform sınırları (karakter / adet)
METIN_SINIRI = {"instagram": 2200, "facebook": 63206, "youtube": 5000, "tiktok": 2200}
BASLIK_SINIRI = {"youtube": 100}
HASHTAG_SINIRI = {"instagram": 30, "tiktok": 30, "youtube": 15}

VIDEO_UZANTILARI = (".mp4", ".mov")

_ON_BILGI = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)
# Köşeli parantezli yer tutucu: [MODEL], [PİL %], [stok cihaz görünürse ...]
# Markdown bağlantısı ([yazı](url)) hariç tutulur.
_YER_TUTUCU = re.compile(r"\[[^\]\n]+\](?!\()")


def yer_tutucular(yazi: str) -> list[str]:
    """Metindeki köşeli parantezli yer tutucuları sırayla döndürür."""
    return _YER_TUTUCU.findall(yazi or "")


def gecerli_url_mi(deger: str) -> bool:
    """http:// veya https:// ile başlayan, alan adı içeren ve boşluk/köşeli parantez içermeyen URL."""
    if not deger or any(c.isspace() for c in deger) or "[" in deger or "]" in deger:
        return False
    parca = urlparse(deger)
    return parca.scheme in {"http", "https"} and bool(parca.netloc)


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

    def video_mu(self, url: str) -> bool:
        return url.lower().split("?")[0].endswith(VIDEO_UZANTILARI)

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
    if g.durum == ERTELENDI:
        # Ertelenen gönderi bekletiliyor: yalnızca kimlik kontrol edilir, içerik kontrolleri atlanır.
        if not g.veri.get("id"):
            h.append("'id' alanı eksik")
        return h
    zorunlu = ["id", "platform", "tur", "durum", "planlanan_tarih"]
    if g.tur != "hikaye":  # hikâyelerde paylaşım metni yoktur
        zorunlu.append("metin")
    for alan in zorunlu:
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
    if g.tur == "hikaye":
        if g.metin:
            h.append("hikâyelerde 'metin' paylaşılmaz; boş bırakın, yazıyı görselin/videonun içine koyun")
        if len(g.medya) > 1:
            h.append("hikâye tek medya içerir; her kare için ayrı gönderi dosyası açın")
        if any(not m.startswith("https://") for m in g.medya):
            h.append("hikâye medyası herkese açık https:// URL olmalı")
    if g.platform == "instagram" and g.medya:
        if any(not m.startswith("https://") for m in g.medya):
            h.append("Instagram medyası herkese açık https:// URL olmalı")
        if g.tur == "carousel" and not 2 <= len(g.medya) <= 10:
            h.append("carousel 2-10 medya içermeli")
    if g.platform == "tiktok" and g.medya and not g.medya[0].startswith("https://"):
        h.append("TikTok videosu doğrulanmış alan adında https:// URL olmalı")
    if g.platform == "facebook" and g.tur == "baglanti" and not g.veri.get("baglanti"):
        h.append("'baglanti' türü için 'baglanti' alanı zorunlu")

    for alan, deger in (("metin", g.metin), ("baslik", baslik)):
        for yt in yer_tutucular(deger):
            h.append(f"'{alan}' alanında doldurulmamış yer tutucu var: {yt}")
    baglanti = str(g.veri.get("baglanti", "") or "").strip()
    if baglanti and not gecerli_url_mi(baglanti):
        bulunan = yer_tutucular(baglanti)
        ek = f" (yer tutucu: {bulunan[0]})" if bulunan else ""
        h.append(f"'baglanti' geçerli bir http:// veya https:// URL olmalı{ek}: {baglanti}")

    if g.durum in {"onaylandi", "yayinlandi"} and not g.veri.get("onaylayan"):
        h.append("onaylı gönderide 'onaylayan' alanı olmalı (yalnızca /onayla ile ekleyin)")
    return h
