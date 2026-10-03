#!/usr/bin/env python3
"""PreToolUse kancası: ajanların gönderi dosyalarında onay alanlarını elle değiştirmesini engeller.

Onay yalnızca `python -m araclar.onayla` (insanın /onayla komutu) ile verilir.
"""

import json
import re
import sys

YASAK = re.compile(r"^(durum:\s*['\"]?(onaylandi|yayinlandi)|onaylayan:|onay_tarihi:|yayin:)", re.M)

olay = json.load(sys.stdin)
girdi = olay.get("tool_input", {})
yol = girdi.get("file_path", "")
if "icerik/gonderiler/" not in yol:
    sys.exit(0)

yeni = girdi.get("content") or girdi.get("new_string") or ""
eski = girdi.get("old_string") or ""
eklenen = set(YASAK.findall(yeni)) - set(YASAK.findall(eski))
if eklenen:
    print("Gönderi dosyalarında durum 'onaylandi'/'yayinlandi', onaylayan, onay_tarihi veya "
          "yayin alanları elle yazılamaz. Onay için kullanıcı /onayla komutunu kullanmalı.",
          file=sys.stderr)
    sys.exit(2)
