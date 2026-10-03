---
name: onayla
description: İncelenmiş gönderileri insan onayıyla yayına hazır hale getirir.
argument-hint: "<kimlik> [<kimlik> ...]"
disable-model-invocation: true
---

Kullanıcı şu gönderileri onaylıyor: $ARGUMENTS

1. Her kimlik için `icerik/gonderiler/<kimlik>.md` dosyasını oku ve kullanıcıya platform, tarih, metnin ilk 2 satırı ve medya listesini tek satırda göster.
2. Onaylayanın adını `git config user.name` ile al (boşsa kullanıcıya sor).
3. `python -m araclar.onayla <kimlikler> --ad "<ad>"` çalıştır ve sonucu aktar. Başarısız olanların nedenini (ör. medya eksik, henüz incelenmemiş) açıkla.

Dosyalardaki `durum`/`onaylayan` alanlarını elle düzenleme; yalnızca bu komutu kullan.
