---
name: yayinla
description: Onaylanmış ve zamanı gelmiş gönderileri sosyal medya hesaplarında yayınlar.
argument-hint: "[--id <kimlik>]"
disable-model-invocation: true
---

1. Önce kuru çalışma yap: `python -m araclar.yayinla $ARGUMENTS`
2. Listeyi kullanıcıya göster ve **açıkça onay iste** ("Bu N gönderi şimdi paylaşılsın mı?"). Kullanıcı evet demeden devam etme.
3. Onay gelirse: `python -m araclar.yayinla --gercek $ARGUMENTS`
4. Sonuçları (URL'ler, hatalar) özetle. Hata alan gönderilerde dosyadaki `hata` alanını okuyup olası çözümü (token süresi, medya URL'si, izin) açıkla.
5. Değişen gönderi dosyalarını commit'le: `git add icerik/gonderiler && git commit -m "Yayın: <kimlikler>"`.
