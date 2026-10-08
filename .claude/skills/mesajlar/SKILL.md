---
name: mesajlar
description: Gelen kutusu — Instagram/Facebook DM'leri ile Instagram/Facebook/YouTube yorumlarını çeker, yanıt taslaklarını hazırlatır ve onaylananları gönderir.
argument-hint: "[gün, varsayılan 7]"
disable-model-invocation: true
---

1. `python -m araclar.mesajlar cek --gun <$ARGUMENTS, boşsa 7>` çalıştır. Kimlik bilgisi/izni eksik kaynakları belirt (hata değil, atlanır).
2. `durum: yeni` kayıt varsa `musteri-iliskileri` alt ajanını çağır.
3. `python -m araclar.mesajlar liste` çıktısını kullanıcıya üç tablo halinde göster:
   - **DM'ler** (önce, kalan süreye göre): no · platform · @yazar · mesaj (kısaltılmış) · önerilen yanıt · ⏰ kalan süre. 3 saatten az kalanları vurgula.
   - **Yorumlar**: no · platform · @yazar · yorum · önerilen yanıt
   - **Size bırakılanlar**: no · tür · platform · @yazar · içerik · neden — bunları kullanıcı uygulamadan yanıtlar, gizler ya da sana yazdırır.
4. Kullanıcıya sor: "Hangileri gönderilsin? (ör. hepsi / 1,3,5 · düzeltme: '3 → yeni metin' · atla: 'atla 4')"
5. Kullanıcının cevabına göre:
   - Düzeltmeler: `python -m araclar.mesajlar taslak <no> --kategori <aynı> --yanit "<kullanıcının metni>"`
   - Atlananlar: `python -m araclar.mesajlar atla <no...>`
   - Gönderilecekler: önce `python -m araclar.mesajlar gonder <no...> --ad "<git config user.name>"` (kuru) ile son hali göster, kullanıcı açıkça onaylarsa aynı komutu `--gercek` ile çalıştır.
6. Sonucu özetle. Hata alanlarda `teknik-uzman` alt ajanını çağır. Süresi dolan DM'ler için uygulamadan yanıtlanması gerektiğini söyle.

Kullanıcı açıkça onaylamadan `--gercek` çalıştırma. Mesaj içeriklerini commit'leme veya başka yere kopyalama; `yerel/` git dışındadır.
