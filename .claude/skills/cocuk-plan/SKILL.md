---
name: cocuk-plan
description: Okul öncesi YouTube çocuk kanalı (kanal: cocuk) için bir haftalık takvim, senaryo ve üretim paketlerini hazırlar (strateji → hook → senarist → YZ üretim/tasarım → editör). Kullanıcı çocuk kanalı, çocuk videosu veya "çocuk planı" istediğinde kullanın.
argument-hint: "[hafta, ör. 2026-W43] [ek notlar]"
---

Çocuk kanalının haftalık üretim hattını yönet. Argümanlar: $ARGUMENTS
(Hafta verilmediyse bir sonraki ISO haftayı kullan.) Her ajana **"kanal: cocuk — `marka/cocuk-rehberi.md` geçerli"** bilgisini açıkça ver.

1. **Strateji** — `strateji-planlayici`: `icerik/takvim/<hafta>-cocuk.md` (rehberdeki sıklık: 2 uzun video + 2 Shorts; son rapor ve önceki çocuk takvimlerini ver, konu tekrarından kaçınsın).
2. **Kancalar** — `hook-yazari`: `icerik/kancalar/<hafta>-cocuk.md`.
3. **Senaryo** — `senarist`: tüm gönderiler (`icerik/ornek-cocuk-gonderi.md` biçiminde; `kanal: cocuk`, `yz_icerik`, `## Çocuk güvenliği`).
4. **Üretim** — **paralel**: `yz-icerik-ureticisi` (tüm videolar için sahne sahne üretim paketi) ∥ `tasarimci` (her uzun video için kapak brief'i).
5. **İnceleme** — `marka-editoru`: tüm dosyalar, çocuk güvenliği listesiyle.
6. `python -m araclar.dogrula --ozet` çalıştır.
7. Kullanıcıya özet:
   - Takvim yolu; kaç gönderi `incelendi` / `taslak` (neden).
   - **Üretim listesi**: her video için kimlik, süre, biçim (16:9 / 9:16), dosya adı `medya/cocuk/<kimlik>.mp4`.
   - Sonraki adımlar: videoları üretip `medya/cocuk/` altına koyun → `medya` alanı doğru mu kontrol → `/onayla <kimlik...>` → `/yayinla --zamanla` (haftanın tüm videoları bir kerede yüklenir, YouTube planlanan saatlerde kendisi yayına açar).

Hiçbir gönderiyi onaylama veya yayınlama.
