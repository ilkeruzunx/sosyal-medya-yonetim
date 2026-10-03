---
name: haftalik-plan
description: Ajan ekibiyle bir haftalık içerik planı ve taslakları üretir (strateji → yazım → editör incelemesi). Kullanıcı haftalık plan, içerik takvimi veya "gelecek haftanın içerikleri" istediğinde kullanın.
argument-hint: "[hafta, ör. 2026-W41] [ek notlar]"
---

Bir haftalık içerik üretim hattını çalıştır. Argümanlar: $ARGUMENTS
(Hafta verilmediyse bir sonraki ISO haftayı kullan.)

1. **Strateji** — `strateji-planlayici` alt ajanını çağır: hafta, kullanıcı notları ve varsa son rapor yolu ile `icerik/takvim/<hafta>.md` oluştursun.
2. **Yazım** — Takvimdeki gönderileri platforma göre 2-4 gruba böl ve her grup için `icerik-yazari` alt ajanını **paralel** çağır. Her birine takvim dosyasını ve yazacağı kimlikleri ver.
3. **İnceleme** — Tüm dosyalar yazılınca `marka-editoru` alt ajanını oluşturulan dosya listesiyle çağır.
4. `python -m araclar.dogrula --ozet` çalıştır.
5. Kullanıcıya kısa özet ver:
   - Takvim dosyası yolu, kaç gönderi, kaçı `incelendi` / kaçı `taslak`ta kaldı ve neden.
   - Medya ihtiyacı olan gönderilerin listesi (medya URL'si eklenmeden onaylanamaz).
   - Sonraki adım: dosyaları inceleyip `/onayla <kimlik...>`.

Hiçbir gönderiyi onaylama veya yayınlama.
