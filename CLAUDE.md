# Çiftlik İletişim — Sosyal Medya Yönetimi

Bu depo, Instagram, Facebook, YouTube ve TikTok hesaplarını bir Claude Code ajan ekibiyle yönetir.
Akış: **plan → taslak → editör incelemesi → insan onayı → yayın → rapor**.

## Ajan ekibi (`.claude/agents/`)
| Ajan | Görev | Yazdığı yer |
|---|---|---|
| `strateji-planlayici` | Haftalık takvim | `icerik/takvim/YYYY-Www.md` |
| `icerik-yazari` | Gönderi taslakları, senaryolar | `icerik/gonderiler/<kimlik>.md` |
| `marka-editoru` | Marka/dil/hukuk incelemesi | aynı dosyalar (`durum: incelendi`) |
| `analist` | Metrik çekme ve rapor | `raporlar/YYYY-Www-rapor.md` |

## Komutlar (`.claude/skills/`)
- `/haftalik-plan [hafta] [notlar]` — tüm hattı çalıştırır.
- `/icerik-uret <fikir>` — tek içerik için yazar + editör.
- `/onayla <kimlik...>` — yalnızca insan çağırabilir.
- `/yayinla [--id kimlik]` — yalnızca insan çağırabilir; önce kuru çalışma, sonra onay.
- `/rapor [gün]` — analist.

## Gönderi durumu
`taslak → incelendi → onaylandi → yayinlandi` (veya `hata`).
- Ajanlar en fazla `incelendi` yapabilir. `onaylandi`, `onaylayan`, `onay_tarihi`, `yayin` alanlarını
  yalnızca `araclar.onayla` / `araclar.yayinla` yazar; `.claude/hooks/onay_korumasi.py` elle yazmayı engeller.
- Biçim örneği: `icerik/ornek-gonderi.md`. Kurallar: `araclar/icerik.py` → `dogrula`.

## Geliştirme
- `pip install -r requirements.txt`, testler: `python -m pytest -q`
- Doğrulama: `python -m araclar.dogrula [--ozet]`
- `.env` dosyasını asla okuma, yazdırma veya commit'leme; kimlik bilgileri `.env.example`'da listelenir.
- Tüm metinler ve kod tanımlayıcıları Türkçe (ASCII dosya/kimlik adları).
