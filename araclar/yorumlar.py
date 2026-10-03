"""Yorumları çeker, yanıt taslaklarını saklar ve onaylanan yanıtları gönderir.

Yorumlar kişisel veri içerebilir: depo dışında, git'e girmeyen `yerel/yorumlar.json`
dosyasında tutulur; sonuçlanmış kayıtlar 30 gün sonra silinir.

Kullanım:
    python -m araclar.yorumlar cek [--gun 7]               # yeni yorumları getir
    python -m araclar.yorumlar liste [--json] [--hepsi]    # bekleyenleri göster
    python -m araclar.yorumlar taslak <no> --kategori soru --yanit "..."
    python -m araclar.yorumlar insana <no> --kategori sikayet --neden "..."
    python -m araclar.yorumlar gonder <no> [<no> ...] --ad "Ad Soyad" [--gercek]
    python -m araclar.yorumlar atla <no> [<no> ...]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

from . import ortam
from .icerik import KOK
from .platformlar import istemci

DEPO = KOK / "yerel" / "yorumlar.json"
PLATFORMLAR = ["instagram", "facebook", "youtube"]
KATEGORILER = ["soru", "siparis", "ovgu", "oneri", "sikayet", "spam", "diger"]
SONUCLANMIS = {"gonderildi", "atlandi"}
SAKLAMA_GUN = 30


def yukle() -> dict:
    if DEPO.exists():
        return json.loads(DEPO.read_text(encoding="utf-8"))
    return {"sayac": 0, "yorumlar": []}


def kaydet(veri: dict) -> None:
    DEPO.parent.mkdir(exist_ok=True)
    DEPO.write_text(json.dumps(veri, ensure_ascii=False, indent=2), encoding="utf-8")


def _simdi() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _bul(veri: dict, no: int) -> dict:
    for y in veri["yorumlar"]:
        if y["no"] == no:
            return y
    raise SystemExit(f"✗ {no} numaralı yorum yok")


def cek(veri: dict, gun: int) -> int:
    sinir = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=gun)
    bilinen = {(y["platform"], y["platform_id"]) for y in veri["yorumlar"]}
    yeni = 0
    for p in PLATFORMLAR:
        try:
            gelenler = istemci(p).yorumlari_getir(sinir)
        except Exception as e:  # noqa: BLE001 — bir platform hatası diğerlerini durdurmasın
            print(f"✗ {p}: {e}")
            continue
        for y in gelenler:
            if (p, y["platform_id"]) in bilinen:
                continue
            veri["sayac"] += 1
            veri["yorumlar"].append({"no": veri["sayac"], "platform": p, "durum": "yeni",
                                     "cekilme": _simdi(), **y})
            yeni += 1
        print(f"✓ {p}: {len(gelenler)} yanıtlanmamış yorum")
    # sonuçlanmış eski kayıtları temizle (kişisel veri saklama süresi)
    esik = dt.datetime.now().astimezone() - dt.timedelta(days=SAKLAMA_GUN)
    veri["yorumlar"] = [y for y in veri["yorumlar"] if not (
        y["durum"] in SONUCLANMIS and dt.datetime.fromisoformat(y["cekilme"]) < esik)]
    return yeni


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    alt = ap.add_subparsers(dest="komut", required=True)
    c = alt.add_parser("cek")
    c.add_argument("--gun", type=int, default=7)
    li = alt.add_parser("liste")
    li.add_argument("--json", action="store_true")
    li.add_argument("--hepsi", action="store_true", help="sonuçlanmışları da göster")
    t = alt.add_parser("taslak")
    t.add_argument("no", type=int)
    t.add_argument("--yanit", required=True)
    t.add_argument("--kategori", choices=KATEGORILER, required=True)
    i = alt.add_parser("insana")
    i.add_argument("no", type=int)
    i.add_argument("--neden", required=True)
    i.add_argument("--kategori", choices=KATEGORILER, required=True)
    g = alt.add_parser("gonder")
    g.add_argument("nolar", type=int, nargs="+")
    g.add_argument("--ad", required=True, help="onaylayan kişinin adı")
    g.add_argument("--gercek", action="store_true", help="gerçekten gönder (yoksa kuru çalışma)")
    at = alt.add_parser("atla")
    at.add_argument("nolar", type=int, nargs="+")
    a = ap.parse_args(argv)

    ortam.yukle()
    veri = yukle()

    if a.komut == "cek":
        yeni = cek(veri, a.gun)
        kaydet(veri)
        print(f"\n{yeni} yeni yorum. Bekleyen: "
              f"{sum(y['durum'] not in SONUCLANMIS for y in veri['yorumlar'])}")
        return 0

    if a.komut == "liste":
        secili = [y for y in veri["yorumlar"] if a.hepsi or y["durum"] not in SONUCLANMIS]
        if a.json:
            print(json.dumps(secili, ensure_ascii=False, indent=2))
            return 0
        for y in secili:
            print(f"[{y['no']}] {y['platform']} · {y['durum']} · {y.get('kategori', '-')} · @{y['yazar']}")
            print(f"    Yorum: {y['metin']}")
            if y.get("yanit"):
                print(f"    Yanıt: {y['yanit']}")
            if y.get("neden"):
                print(f"    Size bırakıldı: {y['neden']}")
        print(f"\n{len(secili)} kayıt")
        return 0

    if a.komut in {"taslak", "insana"}:
        y = _bul(veri, a.no)
        if y["durum"] in SONUCLANMIS:
            raise SystemExit(f"✗ {a.no}: zaten {y['durum']}")
        y["kategori"] = a.kategori
        if a.komut == "taslak":
            y.update(durum="taslak", yanit=a.yanit.strip())
            y.pop("neden", None)
        else:
            y.update(durum="insana", neden=a.neden)
            y.pop("yanit", None)
        kaydet(veri)
        print(f"✓ {a.no} → {y['durum']}")
        return 0

    if a.komut == "atla":
        for no in a.nolar:
            _bul(veri, no).update(durum="atlandi", sonuc_tarihi=_simdi())
        kaydet(veri)
        print(f"✓ {len(a.nolar)} yorum atlandı")
        return 0

    # gonder
    hata = 0
    for no in a.nolar:
        y = _bul(veri, no)
        if y["durum"] not in {"taslak", "hata"} or not y.get("yanit"):
            print(f"✗ {no}: gönderilecek yanıt taslağı yok (durum: {y['durum']})")
            hata += 1
            continue
        if not a.gercek:
            print(f"• [KURU] {y['platform']} @{y['yazar']} ← {y['yanit']!r}")
            continue
        try:
            sonuc = istemci(y["platform"]).yorum_yanitla(y["platform_id"], y["yanit"])
        except Exception as e:  # noqa: BLE001
            y.update(durum="hata", hata=str(e))
            print(f"✗ {no}: {e}")
            hata += 1
            continue
        y.update(durum="gonderildi", onaylayan=a.ad, sonuc_tarihi=_simdi(), **sonuc)
        y.pop("hata", None)
        print(f"✓ {no} yanıtlandı ({y['platform']} @{y['yazar']})")
    kaydet(veri)
    if not a.gercek:
        print("\nKuru çalışma: hiçbir şey gönderilmedi. Göndermek için --gercek ekleyin.")
    return 1 if hata else 0


if __name__ == "__main__":
    sys.exit(main())
