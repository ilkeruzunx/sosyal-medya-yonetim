"""Gelen kutusu: yorumları ve DM'leri çeker, yanıt taslaklarını saklar, onaylananları gönderir.

Kişisel veri içerir: depo dışında, git'e girmeyen `yerel/mesajlar.json` dosyasında tutulur;
sonuçlanmış kayıtlar 30 gün sonra silinir.

Kullanım:
    python -m araclar.mesajlar cek [--gun 7]               # yeni yorum ve DM'leri getir
    python -m araclar.mesajlar liste [--json] [--hepsi]    # bekleyenleri göster
    python -m araclar.mesajlar taslak <no> --kategori soru --yanit "..."
    python -m araclar.mesajlar insana <no> --kategori sikayet --neden "..."
    python -m araclar.mesajlar gonder <no> [<no> ...] --ad "Ad Soyad" [--gercek]
    python -m araclar.mesajlar atla <no> [<no> ...]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

from . import ortam
from .icerik import KOK
from .platformlar import istemci, mesajlasma

DEPO = KOK / "yerel" / "mesajlar.json"
YORUM_PLATFORMLARI = ["instagram", "facebook", "youtube"]
DM_PLATFORMLARI = ["instagram", "facebook"]
KATEGORILER = ["soru", "siparis", "ovgu", "oneri", "sikayet", "spam", "diger"]
SONUCLANMIS = {"gonderildi", "atlandi", "suresi_doldu"}
SAKLAMA_GUN = 30


def yukle() -> dict:
    if DEPO.exists():
        return json.loads(DEPO.read_text(encoding="utf-8"))
    return {"sayac": 0, "kayitlar": []}


def kaydet(veri: dict) -> None:
    DEPO.parent.mkdir(exist_ok=True)
    DEPO.write_text(json.dumps(veri, ensure_ascii=False, indent=2), encoding="utf-8")


def _simdi() -> dt.datetime:
    return dt.datetime.now().astimezone()


def _bul(veri: dict, no: int) -> dict:
    for k in veri["kayitlar"]:
        if k["no"] == no:
            return k
    raise SystemExit(f"✗ {no} numaralı kayıt yok")


def _kalan(k: dict) -> dt.timedelta | None:
    if k["tur"] != "dm":
        return None
    return dt.datetime.fromisoformat(k["son_yanit"]) - _simdi()


def _ekle(veri: dict, tur: str, platform: str, gelen: dict) -> bool:
    """Yeni kaydı ekler; aynı DM konuşmasında bekleyen kayıt varsa onu günceller."""
    for k in veri["kayitlar"]:
        if k["platform"] != platform or k["tur"] != tur:
            continue
        if k["platform_id"] == gelen["platform_id"]:
            return False
        if tur == "dm" and k["konusma_id"] == gelen["konusma_id"] and k["durum"] not in SONUCLANMIS:
            k.update(gelen, durum="yeni", cekilme=_simdi().isoformat(timespec="seconds"))
            k.pop("yanit", None)
            k.pop("neden", None)
            return True
    veri["sayac"] += 1
    veri["kayitlar"].append({"no": veri["sayac"], "tur": tur, "platform": platform, "durum": "yeni",
                             "cekilme": _simdi().isoformat(timespec="seconds"), **gelen})
    return True


def cek(veri: dict, gun: int) -> int:
    sinir = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=gun)
    kaynaklar = [("yorum", p, lambda p=p: istemci(p).yorumlari_getir(sinir)) for p in YORUM_PLATFORMLARI]
    # DM'lerde 24 saatten eski mesaj yanıtlanamaz; daha eskisini çekmeye gerek yok
    dm_siniri = max(sinir, dt.datetime.now(dt.timezone.utc) - mesajlasma.YANIT_PENCERESI)
    kaynaklar += [("dm", p, lambda p=p: mesajlasma.dmleri_getir(p, dm_siniri)) for p in DM_PLATFORMLARI]
    yeni = 0
    for tur, p, getir in kaynaklar:
        try:
            gelenler = getir()
        except Exception as e:  # noqa: BLE001 — bir kaynak hatası diğerlerini durdurmasın
            print(f"✗ {p} {tur}: {e}")
            continue
        yeni += sum(_ekle(veri, tur, p, g) for g in gelenler)
        print(f"✓ {p} {tur}: {len(gelenler)} yanıt bekliyor")
    for k in veri["kayitlar"]:  # yanıt penceresi kapanmış DM'ler
        kalan = _kalan(k)
        if k["durum"] not in SONUCLANMIS and kalan is not None and kalan <= dt.timedelta(0):
            k["durum"] = "suresi_doldu"
    esik = _simdi() - dt.timedelta(days=SAKLAMA_GUN)  # kişisel veri saklama süresi
    veri["kayitlar"] = [k for k in veri["kayitlar"] if not (
        k["durum"] in SONUCLANMIS and dt.datetime.fromisoformat(k["cekilme"]) < esik)]
    return yeni


def _gonder(k: dict) -> dict:
    if k["tur"] == "dm":
        return mesajlasma.dm_gonder(k["alici_id"], k["yanit"])
    return istemci(k["platform"]).yorum_yanitla(k["platform_id"], k["yanit"])


def _sure(k: dict) -> str:
    kalan = _kalan(k)
    if kalan is None:
        return ""
    if kalan <= dt.timedelta(0):
        return " · ⏰ süre doldu"
    return f" · ⏰ {int(kalan.total_seconds() // 3600)} sa {int(kalan.total_seconds() % 3600 // 60)} dk kaldı"


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
        print(f"\n{yeni} yeni/güncellenen kayıt. Bekleyen: "
              f"{sum(k['durum'] not in SONUCLANMIS for k in veri['kayitlar'])}")
        return 0

    if a.komut == "liste":
        secili = [k for k in veri["kayitlar"] if a.hepsi or k["durum"] not in SONUCLANMIS]
        # DM'ler süresi en az kalandan başlayarak önce
        secili.sort(key=lambda k: (k["tur"] != "dm", k.get("son_yanit", ""), k["no"]))
        if a.json:
            print(json.dumps(secili, ensure_ascii=False, indent=2))
            return 0
        for k in secili:
            print(f"[{k['no']}] {k['platform']} {k['tur'].upper()} · {k['durum']} · "
                  f"{k.get('kategori', '-')} · @{k['yazar']}{_sure(k)}")
            print(f"    Gelen: {k['metin']}")
            if k.get("yanit"):
                print(f"    Yanıt: {k['yanit']}")
            if k.get("neden"):
                print(f"    Size bırakıldı: {k['neden']}")
        print(f"\n{len(secili)} kayıt")
        return 0

    if a.komut in {"taslak", "insana"}:
        k = _bul(veri, a.no)
        if k["durum"] in SONUCLANMIS:
            raise SystemExit(f"✗ {a.no}: zaten {k['durum']}")
        k["kategori"] = a.kategori
        if a.komut == "taslak":
            k.update(durum="taslak", yanit=a.yanit.strip())
            k.pop("neden", None)
        else:
            k.update(durum="insana", neden=a.neden)
            k.pop("yanit", None)
        kaydet(veri)
        print(f"✓ {a.no} → {k['durum']}")
        return 0

    if a.komut == "atla":
        for no in a.nolar:
            _bul(veri, no).update(durum="atlandi", sonuc_tarihi=_simdi().isoformat(timespec="seconds"))
        kaydet(veri)
        print(f"✓ {len(a.nolar)} kayıt atlandı")
        return 0

    # gonder
    hata = 0
    for no in a.nolar:
        k = _bul(veri, no)
        if k["durum"] not in {"taslak", "hata"} or not k.get("yanit"):
            print(f"✗ {no}: gönderilecek yanıt taslağı yok (durum: {k['durum']})")
            hata += 1
            continue
        kalan = _kalan(k)
        if kalan is not None and kalan <= dt.timedelta(0):
            k["durum"] = "suresi_doldu"
            print(f"✗ {no}: 24 saatlik DM yanıt süresi doldu; uygulamadan yanıtlayın")
            hata += 1
            continue
        if not a.gercek:
            print(f"• [KURU] {k['platform']} {k['tur']} @{k['yazar']}{_sure(k)} ← {k['yanit']!r}")
            continue
        try:
            sonuc = _gonder(k)
        except Exception as e:  # noqa: BLE001
            k.update(durum="hata", hata=str(e))
            print(f"✗ {no}: {e}")
            hata += 1
            continue
        k.update(durum="gonderildi", onaylayan=a.ad,
                 sonuc_tarihi=_simdi().isoformat(timespec="seconds"), **sonuc)
        k.pop("hata", None)
        print(f"✓ {no} yanıtlandı ({k['platform']} {k['tur']} @{k['yazar']})")
    kaydet(veri)
    if not a.gercek:
        print("\nKuru çalışma: hiçbir şey gönderilmedi. Göndermek için --gercek ekleyin.")
    return 1 if hata else 0


if __name__ == "__main__":
    sys.exit(main())
