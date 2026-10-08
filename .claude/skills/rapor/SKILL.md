---
name: rapor
description: Yayınlanmış gönderilerin metriklerini çekip haftalık performans raporu hazırlar. Kullanıcı performans, istatistik, analiz veya rapor istediğinde kullanın.
argument-hint: "[gün sayısı, varsayılan 7]"
---

`analist` alt ajanını çağır; süre: $ARGUMENTS gün (boşsa 7).
Raporun yolunu, 3 cümlelik özetini ve önerileri kullanıcıya aktar. Önerilerin bir sonraki `/haftalik-plan` çalıştırmasında otomatik kullanılacağını hatırlat.
