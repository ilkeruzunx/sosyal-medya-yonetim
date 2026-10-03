---
name: onayla
description: İncelenmiş gönderileri insan onayıyla onaylar ve isteğe bağlı olarak hemen paylaşır.
argument-hint: "<kimlik> [<kimlik> ...]"
disable-model-invocation: true
---

Kullanıcı şu gönderileri onaylıyor: $ARGUMENTS

1. Her kimlik için `icerik/gonderiler/<kimlik>.md` dosyasını oku ve kullanıcıya platform, tarih, metnin ilk 2 satırı ve medya listesini tek satırda göster.
2. Onaylayanın adını `git config user.name` ile al (boşsa kullanıcıya sor).
3. `python -m araclar.onayla <kimlikler> --ad "<ad>"` çalıştır ve sonucu aktar. Başarısız olanların nedenini (ör. medya eksik, henüz incelenmemiş) açıkla.
4. **Hemen paylaşım (test dönemi varsayılanı):** Onaylanan gönderiler için kuru çalışma yap:
   `python -m araclar.yayinla --id <k1> --id <k2> ...`
   Listeyi gösterip sor: "Bu N gönderi şimdi paylaşılsın mı? (Hayır derseniz onaylı kalır, sonra `/yayinla --id <kimlik>` ile paylaşabilirsiniz.)"
5. Kullanıcı açıkça evet derse: `python -m araclar.yayinla --id <k1> --id <k2> ... --gercek`. Sonuçları (URL'ler) aktar; hata varsa `teknik-uzman` alt ajanını o dosyalarla çağır ve çözümü aktar. Değişen dosyaları commit'le: `git add icerik/gonderiler && git commit -m "Yayın: <kimlikler>"`.

Dosyalardaki `durum`/`onaylayan` alanlarını elle düzenleme; yalnızca bu komutları kullan. Kullanıcı evet demeden `--gercek` çalıştırma.
