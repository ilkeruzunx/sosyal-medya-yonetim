# sosyal-medya-yonetim

@ilkeruzunx — telefon ve teknoloji içerikleri için sosyal medya yönetim projesi. Claude Code ajan ekibiyle
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
 +       musteri-iliskileri ──── yorum ve DM yanıt taslakları (/mesajlar, onayınızla gönderilir)

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
| Instagram + Facebook | Instagram **Business/Creator** hesabı, bağlı Facebook Sayfası, Meta for Developers uygulaması, uzun ömürlü **sayfa** erişim tokenı | Medya herkese açık `https://` URL olmalı (ör. S3, Cloudinary, kendi CDN'iniz). Hikâyelerde API anket/soru/bağlantı çıkartması desteklemez; bunları telefondan paylaşın. Hikâye metrikleri yalnızca ilk 24 saat alınabilir |
| YouTube | Google Cloud projesi, YouTube Data API v3, OAuth istemcisi | Yenileme tokenı: `python -m araclar.youtube_yetkilendir istemci_sirri.json` (kendi bilgisayarınızda). Medya yerel dosya yolu veya URL olabilir |
| TikTok | developers.tiktok.com uygulaması, Content Posting API (`video.publish`, `video.list`) | Denetimden geçmemiş uygulamalar yalnızca **gizli** paylaşım yapabilir. Video URL'si TikTok'ta doğrulanmış alan adında olmalı |

### Bulut oturumlarında
Claude Code'u web/mobil üzerinden kullanıyorsanız `.env` yerine ortam (environment) ayarlarındaki
gizli değişkenleri kullanın ve ağ politikasının `graph.facebook.com`, `*.googleapis.com`,
`open.tiktokapis.com` alan adlarına izin verdiğinden emin olun.

## Çocuk kanalı (YouTube, okul öncesi 3-6 yaş)

Ayrı bir YouTube kanalı aynı ajan ekibiyle yönetilir; haftada bir onay vermeniz yeterli.

```
 /cocuk-plan → takvim + senaryo + sahne sahne üretim paketi + kapak brief'i + editör   (durum: incelendi)
 siz: videoları üretin (CapCut vb.) → medya/cocuk/<kimlik>.mp4                         (git dışı)
 /onayla <kimlikler>  →  /yayinla --zamanla                                           (haftanın videoları bir kerede
                                                                                       yüklenir, YouTube saatinde açar)
 /rapor                                                                               (iki kanalı birlikte raporlar)
```

Bir kerelik kurulum:
1. YouTube Studio'da çocuk kanalını ayrı bir **marka hesabı** olarak açın; ayarlarda kitleyi "Evet, çocuklar için yapıldı" yapın.
2. Token: `python -m araclar.youtube_yetkilendir istemci_sirri.json cocuk` (tarayıcıda çocuk kanalını seçin) →
   çıktıdaki `YOUTUBE_COCUK_YENILEME_TOKENI` satırını `.env`'e ekleyin.
3. Google Cloud projeniz YouTube API denetiminden (audit) geçmediyse API ile yüklenen videolar **özel** kalır;
   herkese açık yayın için "YouTube API Services – Audit and Quota Extension" formunu doldurun.
4. `marka/cocuk-rehberi.md` içindeki `[DOLDURUN]` alanlarını (kanal adı, maskot, renkler) tamamlayın.

Kod tarafından zorlananlar: "Çocuklar için yapıldı" beyanı, YZ içerik bildirimi (`yz_icerik`), yoruma/dış bağlantıya
çağrı yasağı ve editörün işaretlediği `## Çocuk güvenliği` listesi.

## Yorum ve DM yanıtları
`/mesajlar` Instagram ve Facebook DM'lerini, Instagram, Facebook ve YouTube'daki yanıtlanmamış yorumları çeker;
`musteri-iliskileri` ajanı taslak yazar, şikâyet/fiyat/sipariş/kişisel veri gibi hassas olanları size bırakır.
Siz seçtiklerinizi onaylayınca gönderilir.

- **24 saat kuralı:** Meta, DM'lere yalnızca kişinin son mesajından sonraki 24 saat içinde yanıt verilmesine izin verir.
  Liste DM'leri kalan süreye göre sıralar; `/mesajlar`ı en az günde 1-2 kez çalıştırın. Süresi dolanları uygulamadan yanıtlayın.
- **İzinler:** `pages_messaging`, `instagram_manage_messages` (DM) ve `instagram_manage_comments`,
  `pages_read_user_content`, `pages_manage_engagement` (yorum). Gerçek müşterilere mesaj göndermek için Meta uygulama
  incelemesi gerekebilir; o zamana kadar uygulamaya rolü olan test hesaplarıyla deneyin. Instagram ayarlarında
  "Mesajlara bağlı araçlara erişime izin ver" seçeneği açık olmalı.
- TikTok yorum ve DM'leri desteklenmiyor.
- Mesajlar kişisel veri içerdiği için git'e girmeyen `yerel/` klasöründe tutulur, Claude bu dosyayı doğrudan okuyamaz
  ve sonuçlananlar 30 gün sonra silinir. Önce marka rehberindeki "Sık sorulan sorular" bölümünü doldurun.

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
