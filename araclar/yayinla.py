"""Onaylanmış ve zamanı gelmiş gönderileri yayınlar.

Varsayılan olarak KURU ÇALIŞMA yapar (hiçbir şey paylaşılmaz).
Gerçekten paylaşmak için --gercek verin.

Kullanım:
    python -m araclar.yayinla                    # zamanı gelenleri listele (kuru)
    python -m araclar.yayinla --gercek           # zamanı gelenleri yayınla
    python -m araclar.yayinla --id <k1> --id <k2> --gercek   # zamanı beklemeden seçilenler
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from zoneinfo import ZoneInfo

from . import ortam
from .icerik import dogrula, tumunu_oku
from .platformlar import istemci

YEREL_SAAT = ZoneInfo("Europe/Istanbul")


def _yerel(t: dt.datetime) -> dt.datetime:
    return t if t.tzinfo else t.replace(tzinfo=YEREL_SAAT)


def secilenler(kimlikler: list[str] | None, simdi: dt.datetime):
    for g in tumunu_oku():
        if g.durum != "onaylandi":
            continue
        if kimlikler:
            if g.kimlik in kimlikler:
                yield g
        elif g.planlanan and _yerel(g.planlanan) <= simdi:
            yield g


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gercek", action="store_true", help="gerçekten paylaş (yoksa kuru çalışma)")
    ap.add_argument("--id", action="append",
                    help="yalnızca bu kimlikli onaylı gönderi(ler); planlanan zamanı beklemez, tekrarlanabilir")
    a = ap.parse_args(argv)
    ortam.yukle()

    simdi = dt.datetime.now(YEREL_SAAT)
    liste = list(secilenler(a.id, simdi))
    if not liste:
        print("Yayınlanacak onaylı gönderi yok." + (f" (id={', '.join(a.id)})" if a.id else ""))
        return 1 if a.id else 0

    basarisiz = 0
    if a.id:
        eksik = set(a.id) - {g.kimlik for g in liste}
        for k in sorted(eksik):
            print(f"✗ {k}: onaylı gönderi bulunamadı")
        basarisiz += len(eksik)
    for g in liste:
        hatalar = dogrula(g)
        if hatalar:
            print(f"✗ ATLANDI {g.kimlik}: " + "; ".join(hatalar))
            basarisiz += 1
            continue
        if not a.gercek:
            print(f"• [KURU] {g.platform}/{g.tur} {g.kimlik} — {g.metin[:60]!r}")
            continue
        try:
            sonuc = istemci(g.platform).yayinla(g)
        except Exception as e:  # noqa: BLE001 — hatayı dosyaya yazıp devam et
            g.veri["durum"] = "hata"
            g.veri["hata"] = str(e)
            g.kaydet()
            print(f"✗ HATA {g.kimlik}: {e}")
            basarisiz += 1
            continue
        g.veri["durum"] = "yayinlandi"
        g.veri.pop("hata", None)
        g.veri["yayin"] = {**sonuc, "tarih": simdi.isoformat(timespec="seconds")}
        g.kaydet()
        print(f"✓ YAYINLANDI {g.kimlik} → {sonuc.get('url')}")

    if not a.gercek:
        print("\nKuru çalışma: hiçbir şey paylaşılmadı. Paylaşmak için --gercek ekleyin.")
    return 1 if basarisiz else 0


if __name__ == "__main__":
    sys.exit(main())
