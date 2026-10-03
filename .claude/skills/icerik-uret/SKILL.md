---
name: icerik-uret
description: Tek bir fikir veya takvim satırından bir ya da birden çok platform için gönderi taslağı üretir (hook → senaryo → tasarım/YZ üretim → editör). Kullanıcı belirli bir gönderi, Reels, Shorts, TikTok, carousel veya YouTube içeriği istediğinde kullanın.
argument-hint: "<fikir veya kimlik> [platformlar] [tarih]"
---

İstek: $ARGUMENTS

1. İstek bir takvim kimliğiyse takvimden satırı bul; serbest fikirse platform, tür, tarih ve kimlik belirle (belirtilmemişse makul öneri yap, en yakın uygun boş saati seç) ve bunları kısa bir takvim satırı olarak `icerik/kancalar/<hafta>.md` girdisine bağlam olarak ver.
2. `hook-yazari` → `senarist` (sıralı).
3. Türüne göre `tasarimci` veya `yz-icerik-ureticisi` (birden çok dosya varsa paralel).
4. `marka-editoru`.
5. Dosya yollarını, durumlarını, seçilen kancayı, editör notlarını ve medya ihtiyacını özetle; sonraki adım `/onayla <kimlik>`.

Onaylama veya yayınlama yapma.
