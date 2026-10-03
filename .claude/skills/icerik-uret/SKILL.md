---
name: icerik-uret
description: Tek bir fikir veya takvim satırından bir ya da birden çok platform için gönderi taslağı üretip editörden geçirir. Kullanıcı belirli bir gönderi, Reels, Shorts, TikTok veya YouTube içeriği istediğinde kullanın.
argument-hint: "<fikir veya kimlik> [platformlar] [tarih]"
---

İstek: $ARGUMENTS

1. İstek bir takvim kimliğiyse takvimden satırı bul; serbest fikirse platform, tür ve tarih belirt (belirtilmemişse makul öneri yap, en yakın uygun boş saati seç).
2. `icerik-yazari` alt ajanını çağırarak taslak(lar)ı yazdır.
3. `marka-editoru` alt ajanını aynı dosyalarla çağır.
4. Dosya yollarını, durumlarını, editör notlarını ve medya ihtiyacını özetle. Sonraki adım olarak `/onayla <kimlik>` hatırlat.

Onaylama veya yayınlama yapma.
