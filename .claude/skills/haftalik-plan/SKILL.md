---
name: haftalik-plan
description: Ajan ekibiyle bir haftalık içerik planı ve taslakları üretir (strateji → hook → senaryo → tasarım/YZ üretim → editör). Kullanıcı haftalık plan, içerik takvimi veya "gelecek haftanın içerikleri" istediğinde kullanın.
argument-hint: "[hafta, ör. 2026-W41] [ek notlar]"
---

Bir haftalık içerik üretim hattını yönet. Argümanlar: $ARGUMENTS
(Hafta verilmediyse bir sonraki ISO haftayı kullan.)

1. **Strateji** — `strateji-planlayici`: `icerik/takvim/<hafta>.md` oluştursun (son rapor yolunu ve kullanıcı notlarını ver).
2. **Kancalar** — `hook-yazari`: takvimdeki tüm gönderiler için `icerik/kancalar/<hafta>.md`.
3. **Senaryo/metin** — Gönderileri platforma göre 2-4 gruba böl; her grup için `senarist`i **paralel** çağır (takvim, kanca dosyası, kimlikler).
4. **Görsel üretim** — Oluşan dosyaları türe göre ayır ve **paralel** çağır:
   - `gorsel`/`carousel` → `tasarimci`
   - video türleri (`reels`, `shorts`, `video`) → `yz-icerik-ureticisi`
   - Facebook `metin`/`baglanti` → atla
5. **İnceleme** — `marka-editoru`: tüm dosyalar.
6. `python -m araclar.dogrula --ozet` çalıştır.
7. Kullanıcıya özet: takvim yolu; kaç gönderi `incelendi` / `taslak` (neden); üretilmesi/çekilmesi gereken medya listesi (her biri için kimlik + kısa tarif); sonraki adım: medya URL'lerini `medya` alanına ekleyip `/onayla <kimlik...>`.

Hiçbir gönderiyi onaylama veya yayınlama.
