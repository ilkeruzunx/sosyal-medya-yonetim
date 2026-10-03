---
name: yorumlar
description: Instagram, Facebook ve YouTube yorumlarını çeker, yanıt taslaklarını hazırlatır ve onaylananları gönderir.
argument-hint: "[gün, varsayılan 7]"
disable-model-invocation: true
---

1. `python -m araclar.yorumlar cek --gun <$ARGUMENTS, boşsa 7>` çalıştır. Kimlik bilgisi eksik platformları belirt (hata değil, atlanır).
2. `durum: yeni` yorum varsa `musteri-iliskileri` alt ajanını çağır.
3. `python -m araclar.yorumlar liste` çıktısını kullanıcıya iki tablo halinde göster:
   - **Yanıt taslakları**: no · platform · @yazar · yorum (kısaltılmış) · önerilen yanıt
   - **Size bırakılanlar**: no · platform · @yazar · yorum · neden — bunları kullanıcı telefondan yanıtlar, gizler ya da sana yazdırır.
4. Kullanıcıya sor: "Hangileri gönderilsin? (ör. hepsi / 1,3,5 · düzeltme: '3 → yeni metin' · atla: 'atla 4')"
5. Kullanıcının cevabına göre:
   - Düzeltmeler: `python -m araclar.yorumlar taslak <no> --kategori <aynı> --yanit "<kullanıcının metni>"`
   - Atlananlar: `python -m araclar.yorumlar atla <no...>`
   - Gönderilecekler: önce `python -m araclar.yorumlar gonder <no...> --ad "<git config user.name>"` (kuru) ile son hali göster, kullanıcı açıkça onaylarsa aynı komutu `--gercek` ile çalıştır.
6. Sonucu özetle. Hata alan yanıtlarda `teknik-uzman` alt ajanını çağır.

Kullanıcı açıkça onaylamadan `--gercek` çalıştırma. Yorum metinlerini commit'leme; `yerel/` git dışındadır.
