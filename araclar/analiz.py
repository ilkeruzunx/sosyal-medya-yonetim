"""Yayınlanmış gönderilerin metriklerini çekip raporlar/veri/ altına JSON yazar.

Kullanım:
    python -m araclar.analiz              # son 30 gün
    python -m araclar.analiz --gun 7
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

from . import ortam
from .icerik import KOK, tumunu_oku
from .platformlar import istemci


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gun", type=int, default=30, help="kaç günlük yayınlar (varsayılan 30)")
    a = ap.parse_args(argv)
    ortam.yukle()

    simdi = dt.datetime.now(dt.timezone.utc)
    sinir = simdi - dt.timedelta(days=a.gun)
    kayitlar = []
    for g in tumunu_oku():
        yayin = g.veri.get("yayin") or {}
        if g.durum != "yayinlandi" or not yayin.get("platform_id"):
            continue
        if dt.datetime.fromisoformat(yayin["tarih"]) < sinir:
            continue
        kayit = {"id": g.kimlik, "platform": g.platform, "tur": g.tur,
                 "yayin_tarihi": yayin["tarih"], "url": yayin.get("url"),
                 "kampanya": g.veri.get("kampanya"), "konu": g.veri.get("konu")}
        try:
            kayit["metrikler"] = istemci(g.platform).metrikler(yayin)
        except Exception as e:  # noqa: BLE001
            kayit["hata"] = str(e)
        kayitlar.append(kayit)
        print(f"{'✗' if 'hata' in kayit else '✓'} {g.platform:9} {g.kimlik}")

    hedef = KOK / "raporlar" / "veri" / f"{simdi.date().isoformat()}.json"
    hedef.write_text(json.dumps({"cekilme": simdi.isoformat(timespec="seconds"),
                                 "gun": a.gun, "gonderiler": kayitlar},
                                ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{len(kayitlar)} gönderi → {hedef.relative_to(KOK)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
