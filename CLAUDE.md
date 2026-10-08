# @ilkeruzunx — Sosyal Medya Yönetimi (telefon ve teknoloji)

Bu depo, Instagram, Facebook, YouTube ve TikTok hesaplarını bir Claude Code ajan ekibiyle yönetir.
Akış: **plan → taslak → editör incelemesi → insan onayı → yayın → rapor**.

## Ajan ekibi (`.claude/agents/`)
| Kat | Ajan | Görev | Yazdığı yer |
|---|---|---|---|
| 7 | `analist` | Metrik çekme ve rapor | `raporlar/YYYY-Www-rapor.md` |
| 6 | `hook-yazari` | Kanca alternatifleri ve seçim | `icerik/kancalar/YYYY-Www.md` |
| 5 | `senarist` | Gönderi dosyası, metin, senaryo | `icerik/gonderiler/<kimlik>.md` |
| 4 | `yz-icerik-ureticisi` | Video çekim listesi, YZ promptları, seslendirme | gönderi gövdesi `## Üretim paketi` |
| 3 | `tasarimci` | Görsel/carousel/hikâye brief'i, kapak | gönderi gövdesi `## Tasarım brief'i` |
| 2 | ana oturum (`/ekip`) | Yönetici: dağıtım ve sıralama | — |
| 1 | `teknik-uzman` | API, token, yayın hataları, kod | `araclar/` |
| + | `strateji-planlayici` | Haftalık takvim | `icerik/takvim/YYYY-Www.md` |
| + | `marka-editoru` | Marka/dil/hukuk incelemesi | gönderi (`durum: incelendi`) |
| + | `musteri-iliskileri` | Yorum/DM sınıflandırma ve yanıt taslağı | `yerel/mesajlar.json` (CLI ile) |

Alt ajanlar birbirini çağıramaz; koordinasyonu ana oturum yapar.
Sıra: strateji → hook → senarist → (tasarımcı ∥ YZ üretici, türe göre) → editör.

## Komutlar (`.claude/skills/`)
- `/ekip <istek>` — yönetici; serbest isteği doğru ajanlara dağıtır.
- `/haftalik-plan [hafta] [notlar]` — tüm hattı çalıştırır.
- `/icerik-uret <fikir>` — tek içerik için hook → senaryo → tasarım/YZ → editör.
- `/onayla <kimlik...>` — yalnızca insan çağırabilir; onaydan sonra hemen paylaşmayı teklif eder (test dönemi akışı).
- `/yayinla [--id kimlik ...]` — yalnızca insan çağırabilir; onaylı ve zamanı gelmiş (veya `--id` ile seçilen) gönderileri paylaşır. Zamanlanmış otomatik yayın henüz yok.
- `/rapor [gün]` — analist.
- `/mesajlar [gün]` — yalnızca insan çağırabilir; yorum ve DM'leri çeker, taslak hazırlatır, onaylananları gönderir.

## Gönderi durumu
`taslak → incelendi → onaylandi → yayinlandi` (veya `hata`).
- Ajanlar en fazla `incelendi` yapabilir. `onaylandi`, `onaylayan`, `onay_tarihi`, `yayin` alanlarını
  yalnızca `araclar.onayla` / `araclar.yayinla` yazar; `.claude/hooks/onay_korumasi.py` elle yazmayı engeller.
- Hikâyeler (`tur: hikaye`, Instagram/Facebook): `metin` boş, tek medya; diğer türler gibi insan onayından geçer.
- Gelen kutusu (`araclar/mesajlar.py`, yorum + DM): `yeni → taslak | insana → gonderildi | atlandi | suresi_doldu`. DM'ler yalnızca son mesajdan sonraki 24 saat içinde yanıtlanabilir. Kişisel veri içerir; git dışı `yerel/mesajlar.json`'da tutulur, 30 gün sonra silinir. Ajanlar dosyayı okuyamaz/düzenleyemez (yalnızca CLI), yanıt gönderemez.
- Biçim örneği: `icerik/ornek-gonderi.md`. Kurallar: `araclar/icerik.py` → `dogrula`.

## Geliştirme
- `pip install -r requirements.txt`, testler: `python -m pytest -q`
- Doğrulama: `python -m araclar.dogrula [--ozet]`
- `.env` dosyasını asla okuma, yazdırma veya commit'leme; kimlik bilgileri `.env.example`'da listelenir.
- Tüm metinler ve kod tanımlayıcıları Türkçe (ASCII dosya/kimlik adları).
