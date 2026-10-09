---
name: yayinla
description: Onaylanmış ve zamanı gelmiş gönderileri sosyal medya hesaplarında yayınlar.
argument-hint: "[--id <kimlik> ...] [--zamanla]"
disable-model-invocation: true
---

1. Önce kuru çalışma yap: `python -m araclar.yayinla $ARGUMENTS`
   (`--zamanla`: ileri tarihli onaylı YouTube videoları da şimdi yüklenir; YouTube her birini planlanan saatte kendisi açar. ⏰ ile işaretlenirler.)
2. Listeyi kullanıcıya göster ve **açıkça onay iste** ("Bu N gönderi şimdi paylaşılsın mı?"). Kullanıcı evet demeden devam etme.
3. Onay gelirse: `python -m araclar.yayinla --gercek $ARGUMENTS`
4. Sonuçları (URL'ler, hatalar) özetle. Hata alan gönderi varsa `teknik-uzman` alt ajanını o dosyalarla çağır ve önerdiği çözümü aktar.
5. Değişen gönderi dosyalarını commit'le: `git add icerik/gonderiler && git commit -m "Yayın: <kimlikler>"`.
