"""İçerik dosyalarını doğrular ve durum özetini yazdırır.

Kullanım:
    python -m araclar.dogrula                 # tüm gönderiler
    python -m araclar.dogrula icerik/gonderiler/x.md
    python -m araclar.dogrula --ozet          # durum tablosu
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from .icerik import GONDERI_KLASORU, dogrula, oku


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dosyalar", nargs="*", type=Path)
    ap.add_argument("--ozet", action="store_true", help="durum ve platform özetini göster")
    a = ap.parse_args(argv)

    yollar = a.dosyalar or sorted(GONDERI_KLASORU.rglob("*.md"))
    hatali = 0
    gonderiler = []
    for yol in yollar:
        try:
            g = oku(yol)
        except ValueError as e:
            print(f"✗ {e}")
            hatali += 1
            continue
        gonderiler.append(g)
        hatalar = dogrula(g)
        if hatalar:
            hatali += 1
            print(f"✗ {yol}")
            for h in hatalar:
                print(f"    - {h}")
        elif not a.ozet:
            print(f"✓ {yol}")

    if a.ozet:
        print("\nPlanlanan  | Platform  | Tür       | Durum      | Kimlik")
        print("-" * 72)
        for g in sorted(gonderiler, key=lambda x: str(x.veri.get("planlanan_tarih", ""))):
            print(f"{str(g.veri.get('planlanan_tarih', ''))[:10]:10} | {g.platform:9} | "
                  f"{g.tur:9} | {g.durum:10} | {g.kimlik}")
        print("\n" + ", ".join(f"{d}: {n}" for d, n in Counter(g.durum for g in gonderiler).items()))

    print(f"\n{len(yollar)} dosya, {hatali} hatalı")
    return 1 if hatali else 0


if __name__ == "__main__":
    sys.exit(main())
