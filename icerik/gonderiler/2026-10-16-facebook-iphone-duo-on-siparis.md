---
id: 2026-10-16-facebook-iphone-duo-on-siparis
platform: facebook
tur: baglanti
durum: ertelendi
planlanan_tarih: 2026-10-16T17:30:00+03:00
konu: "iPhone Duo ön sipariş: Apple resmî sayfasından kısa özet"
kampanya: iphone-duo
baglanti: "[APPLE-RESMI-BAGLANTI: yayın günü Apple'ın resmî iPhone Duo ürün/haber sayfası eklenecek]"
metin: |
  iPhone Duo ön siparişe açıldı: Apple'ın resmî sayfasından 3 maddelik özet, bağlantı aşağıda.

  1) [MADDE 1: Apple resmî sayfasından]
  2) [MADDE 2: Apple resmî sayfasından]
  3) [MADDE 3: Apple resmî sayfasından]

  Türkiye'deki satış durumu ve fiyat için Apple Türkiye sayfasına bakmak en doğrusu. Fiyat ve tarih bilgisi resmî sayfada göründüğünde "16 Ekim 2026 itibarıyla" notuyla paylaşılır 📱

  Ön siparişle mi alırsın, yoksa ilk incelemeleri mi beklersin? Yorumlara yaz 👇

  #ilkeruzunx #iphone
medya: []
---
## Kanca
Seçilen (hook-yazari, 2. alternatif): "iPhone Duo ön siparişe açıldı: Apple'ın resmî sayfasından 3 maddelik özet, bağlantı aşağıda." — [rakam/somutluk]. Değiştirilmedi.

**Yedek ilk satır (Apple'da ön sipariş yayın anında doğrulanmazsa kullanılacak, 1. alternatif):** "iPhone Duo için ön sipariş vermeyi düşünüyorsan önce Apple'ın resmî sayfasında yazanlara bak." Bu durumda metindeki "ön siparişe açıldı" ifadesi de kaldırılır; madde 1-3 "bilinen resmî bilgiler" olarak yazılır.

**Doğrulama kuralı:** "Açıldı" yalnızca Apple resmî sayfasında ön sipariş açık görüldüğünde kullanılır. Tarih, saat ve fiyat resmî olarak doğrulanmadı; metinde kesin tarih ve fiyat yok. Teslimat tarihi (iddia: 23 Ekim) resmî doğrulama olmadan yazılmaz.

## Metin akışı
Bağlantı gönderisi: tek görsel yok, önizleme Apple sayfasından gelir. Metin: 1 satır kanca, 3 madde (resmî sayfadan alınacak, uydurulmaz), 1 satır Türkiye durumu notu, 1 soru. Hashtag en fazla 2.

## Kaynaklar
- Birincil: Apple resmî iPhone Duo ürün/haber sayfası (bağlantı yayın günü eklenecek, henüz doğrulanmadı).
- İddia düzeyinde, resmî değil: ön siparişin 16 Ekim 15:00 TSİ'de açılacağı ve teslimatın 23 Ekim'de başlayacağı haberi (MacRumors: https://www.macrumors.com/2026/09/28/iphone-duo-preorders-and-release-date/). Metinde kullanılmaz.

## Açık konular
- `baglanti` alanı yer tutucu; Apple'ın gerçek URL'si yayın öncesi insan tarafından girilecek (URL uydurulmadı). Alan, ajan tarafından doğrulanamayan bir yer tutucu olduğu için yayınlama öncesi mutlaka değiştirilmeli.
- Madde 1-3 resmî sayfadan doldurulacak.

## Medya ihtiyacı
Yok; bağlantı önizlemesi Apple sayfasından gelir. Ek görsel konulmaz.

## Editör notları
- **Karar: taslak kalır.** `baglanti` alanı yer tutucu (`[APPLE-RESMI-BAGLANTI: ...]`) ve `metin`de üç madde yer tutucu (`[MADDE 1-3 ...]`). İkisi de yayın günü Apple resmî sayfasından doldurulmadan onaya gidemez.
- Not: `python -m araclar.dogrula` bu dosyayı geçerli sayıyor çünkü yalnızca `baglanti` alanının dolu olup olmadığına bakıyor; köşeli parantezli yer tutucuyu yakalamıyor. teknik-uzman için öneri: `baglanti` için `https://` zorunluluğu ve `metin`/`baslik` içinde `[` ... `]` yer tutucu kontrolü eklenmeli.
- "ön siparişe açıldı" ifadesi yalnızca Apple'da açık görülürse kalır; görülmezse `## Kanca` altındaki yedek ilk satır uygulanır.
- `metin`deki "Fiyat ve tarih bilgisi resmî sayfada göründüğünde "16 Ekim 2026 itibarıyla" notuyla paylaşılır" cümlesi okura değil ekibe yönelik bir iç not gibi okunuyor. Yayın günü ya fiyat/tarih tarihli olarak yazılmalı ya da cümle "Fiyat ve tarih için Apple Türkiye sayfasına bak." gibi okura dönük hâle getirilmeli.
- Hashtag 2 adet, emoji 2 adet: uygun. Takvimle uyumlu (2026-10-16 17:30, facebook, baglanti).
