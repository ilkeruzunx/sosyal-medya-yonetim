"""İncelenmiş gönderileri onaylar (yalnızca insan kullanımı için: /onayla).

Kullanım:
    python -m araclar.onayla <kimlik> [<kimlik> ...] --ad "Ad Soyad"
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys

from .icerik import dogrula, tumunu_oku


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kimlikler", nargs="+")
    ap.add_argument("--ad", required=True, help="onaylayan kişinin adı")
    a = ap.parse_args(argv)

    gonderiler = {g.kimlik: g for g in tumunu_oku()}
    hata = 0
    for k in a.kimlikler:
        g = gonderiler.get(k)
        if g is None:
            print(f"✗ {k}: bulunamadı")
            hata += 1
            continue
        if g.durum == "ertelendi":
            print(f"✗ {k}: gönderi ertelendi — onaylamak için önce durumu 'taslak'a döndürün "
                  "ve marka-editoru incelemesinden geçirin")
            hata += 1
            continue
        if g.durum != "incelendi":
            print(f"✗ {k}: durum '{g.durum}' — önce marka-editoru incelemeli (durum: incelendi)")
            hata += 1
            continue
        g.veri["durum"] = "onaylandi"
        g.veri["onaylayan"] = a.ad
        g.veri["onay_tarihi"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
        sorunlar = dogrula(g)
        if sorunlar:
            print(f"✗ {k}: " + "; ".join(sorunlar))
            hata += 1
            continue
        g.kaydet()
        print(f"✓ {k} onaylandı ({g.platform}, {g.veri.get('planlanan_tarih')})")
    return 1 if hata else 0


if __name__ == "__main__":
    sys.exit(main())
