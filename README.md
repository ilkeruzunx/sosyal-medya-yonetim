# sosyal-medya-yonetim

Çiftlik İletişim sosyal medya içerik, planlama ve yönetim projesi — Claude Code ajan ekibiyle
Instagram, Facebook, YouTube ve TikTok için içerik planlar, yazar, denetler, (onayınızla) yayınlar ve raporlar.

```
 7. kat  analist ─────────────── metrikler ve haftalık rapor ──────────────┐
 6. kat  hook-yazari ─────────── kanca alternatifleri, en güçlüsü           │
 5. kat  senarist ────────────── gönderi metni + video senaryosu            │ öneriler
 4. kat  yz-icerik-ureticisi ─── çekim listesi, YZ video/görsel promptları  │
 3. kat  tasarimci ───────────── carousel/görsel brief'i, YouTube kapağı    │
 2. kat  /ekip (yönetici) ────── işi dağıtır, sıralar, özetler              │
 1. kat  teknik-uzman ────────── API, token, yayın hataları                 │
 +       strateji-planlayici ─── haftalık takvim ◄──────────────────────────┘
 +       marka-editoru ───────── onay öncesi son kontrol

 /haftalik-plan → strateji → hook → senarist → tasarımcı ∥ YZ üretici → editör   (durum: incelendi)
 siz: medya URL'lerini ekleyin → /onayla <kimlik>                                (durum: onaylandi)
        └─ "şimdi paylaşılsın mı?" → evet → paylaşım                             (durum: yayinlandi)
 /yayinla: onaylı bekleyenleri sonradan paylaşmak için
```

## Kurulum

1. Bağımlılıklar: `pip install -r requirements.txt`
2. `cp .env.example .env` ve platform bilgilerini doldurun (aşağıya bakın).
3. `marka/marka-rehberi.md` içindeki `[DOLDURUN]` alanlarını tamamlayın.
4. Claude Code'u bu klasörde açıp `/haftalik-plan` veya `/ekip <istek>` yazın.

Yalnızca içerik üretimi için API bilgisi gerekmez; `.env` yalnızca `/yayinla` ve `/rapor` için gereklidir.

### Platform bağlantıları

| Platform | Gerekenler | Not |
|---|---|---|
| Instagram + Facebook | Instagram **Business/Creator** hesabı, bağlı Facebook Sayfası, Meta for Developers uygulaması, uzun ömürlü **sayfa** erişim tokenı | Medya herkese açık `https://` URL olmalı (ör. S3, Cloudinary, kendi CDN'iniz) |
| YouTube | Google Cloud projesi, YouTube Data API v3, OAuth istemcisi | Yenileme tokenı: `python -m araclar.youtube_yetkilendir istemci_sirri.json` (kendi bilgisayarınızda). Medya yerel dosya yolu veya URL olabilir |
| TikTok | developers.tiktok.com uygulaması, Content Posting API (`video.publish`, `video.list`) | Denetimden geçmemiş uygulamalar yalnızca **gizli** paylaşım yapabilir. Video URL'si TikTok'ta doğrulanmış alan adında olmalı |

### Bulut oturumlarında
Claude Code'u web/mobil üzerinden kullanıyorsanız `.env` yerine ortam (environment) ayarlarındaki
gizli değişkenleri kullanın ve ağ politikasının `graph.facebook.com`, `*.googleapis.com`,
`open.tiktokapis.com` alan adlarına izin verdiğinden emin olun.

## Güvenlik önlemleri
- Ajanlar hiçbir gönderiyi onaylayamaz veya yayınlayamaz: `/onayla` ve `/yayinla` yalnızca sizin tarafınızdan çağrılabilir,
  ilgili komutlar her seferinde izin ister ve bir kanca ajanların onay alanlarını elle yazmasını engeller.
- `araclar.yayinla` varsayılan olarak kuru çalışır; paylaşım için `--gercek` gerekir.
- `.env` git'e girmez ve Claude tarafından okunması engellenmiştir.

## Klasörler
```
.claude/agents/     ajan tanımları          icerik/takvim/      haftalık takvimler
                                            icerik/kancalar/    hook alternatifleri
.claude/skills/     /komutlar               icerik/gonderiler/  gönderi dosyaları
.claude/hooks/      onay koruması           raporlar/           performans raporları
araclar/            Python API araçları     marka/              marka rehberi
```
