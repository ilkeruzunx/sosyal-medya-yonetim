import json
import subprocess
import sys
from pathlib import Path

import pytest

from araclar import icerik, onayla, yayinla
from araclar.icerik import KOK, dogrula, oku

ORNEK = KOK / "icerik" / "ornek-gonderi.md"


@pytest.fixture
def klasor(tmp_path, monkeypatch):
    monkeypatch.setattr(icerik, "GONDERI_KLASORU", tmp_path)
    monkeypatch.setattr(yayinla, "tumunu_oku", lambda: icerik.tumunu_oku(tmp_path))
    monkeypatch.setattr(onayla, "tumunu_oku", lambda: icerik.tumunu_oku(tmp_path))
    return tmp_path


def _kopya(klasor, **degisiklik):
    g = oku(ORNEK)
    g.veri.update(degisiklik)
    g.yol = klasor / f"{g.kimlik}.md"
    g.kaydet()
    return g


def test_ornek_gecerli():
    assert dogrula(oku(ORNEK)) == []


def test_kaydet_oku_gidis_donus(klasor):
    g = _kopya(klasor)
    tekrar = oku(g.yol)
    assert tekrar.veri == g.veri
    assert tekrar.govde == g.govde


@pytest.mark.parametrize("degisiklik, beklenen", [
    ({"tur": "shorts"}, "geçersiz tür"),
    ({"metin": "#a " * 31}, "hashtag"),
    ({"medya": []}, "medya"),
    ({"medya": ["http://guvensiz.com/v.mp4"]}, "https://"),
    ({"durum": "onaylandi"}, "onaylayan"),
    ({"platform": "youtube", "tur": "video"}, "baslik"),
    ({"tur": "hikaye"}, "metin' paylaşılmaz"),
    ({"tur": "hikaye", "metin": "", "medya": ["https://a/1.jpg", "https://a/2.jpg"]}, "tek medya"),
    ({"platform": "facebook", "tur": "hikaye", "metin": "", "medya": ["http://a/1.jpg"]}, "https://"),
])
def test_dogrulama_hatalari(degisiklik, beklenen):
    g = oku(ORNEK)
    g.veri.update(degisiklik)
    assert any(beklenen in h for h in dogrula(g))


def test_onay_yalnizca_incelenmisler(klasor):
    g = _kopya(klasor)
    assert onayla.main([g.kimlik, "--ad", "Test"]) == 1
    assert oku(g.yol).durum == "taslak"

    _kopya(klasor, durum="incelendi")
    assert onayla.main([g.kimlik, "--ad", "Test"]) == 0
    sonuc = oku(g.yol)
    assert sonuc.durum == "onaylandi" and sonuc.veri["onaylayan"] == "Test"


def test_yayinla_kuru_calisma_paylasmaz(klasor, monkeypatch, capsys):
    g = _kopya(klasor, durum="onaylandi", onaylayan="Test",
               planlanan_tarih="2020-01-01T10:00:00+03:00")
    monkeypatch.setattr(yayinla, "istemci", lambda p: pytest.fail("kuru çalışmada API çağrıldı"))
    assert yayinla.main([]) == 0
    assert "[KURU]" in capsys.readouterr().out
    assert oku(g.yol).durum == "onaylandi"


def test_yayinla_gercek_durumu_gunceller(klasor, monkeypatch):
    g = _kopya(klasor, durum="onaylandi", onaylayan="Test",
               planlanan_tarih="2020-01-01T10:00:00+03:00")
    _kopya(klasor, id="gelecek", durum="onaylandi", onaylayan="Test",
           planlanan_tarih="2099-01-01T10:00:00+03:00")

    class Sahte:
        @staticmethod
        def yayinla(_):
            return {"platform_id": "123", "url": "https://instagram.com/p/x"}

    monkeypatch.setattr(yayinla, "istemci", lambda p: Sahte)
    assert yayinla.main(["--gercek"]) == 0
    sonuc = oku(g.yol)
    assert sonuc.durum == "yayinlandi"
    assert sonuc.veri["yayin"]["platform_id"] == "123"
    assert oku(klasor / "gelecek.md").durum == "onaylandi"


def test_yayinla_hata_dosyaya_yazilir(klasor, monkeypatch):
    g = _kopya(klasor, durum="onaylandi", onaylayan="Test",
               planlanan_tarih="2020-01-01T10:00:00+03:00")

    class Bozuk:
        @staticmethod
        def yayinla(_):
            raise RuntimeError("token süresi doldu")

    monkeypatch.setattr(yayinla, "istemci", lambda p: Bozuk)
    assert yayinla.main(["--gercek"]) == 1
    sonuc = oku(g.yol)
    assert sonuc.durum == "hata" and "token" in sonuc.veri["hata"]


def _kanca(arac_girdisi):
    kanca = KOK / ".claude" / "hooks" / "onay_korumasi.py"
    return subprocess.run([sys.executable, str(kanca)], input=json.dumps({"tool_input": arac_girdisi}),
                          capture_output=True, text=True).returncode


def test_kanca_elle_onayi_engeller():
    yol = str(KOK / "icerik" / "gonderiler" / "x.md")
    assert _kanca({"file_path": yol, "old_string": "durum: incelendi",
                   "new_string": "durum: onaylandi"}) == 2
    assert _kanca({"file_path": yol, "content": "---\nonaylayan: Ajan\n---\n"}) == 2
    assert _kanca({"file_path": yol, "old_string": "durum: taslak",
                   "new_string": "durum: incelendi"}) == 0
    assert _kanca({"file_path": str(Path("/baska/dosya.md")), "content": "durum: onaylandi"}) == 0


def test_yayinla_id_ile_zamani_beklemez(klasor, monkeypatch):
    g = _kopya(klasor, durum="onaylandi", onaylayan="Test",
               planlanan_tarih="2099-01-01T10:00:00+03:00")

    class Sahte:
        @staticmethod
        def yayinla(_):
            return {"platform_id": "9", "url": "https://instagram.com/p/y"}

    monkeypatch.setattr(yayinla, "istemci", lambda p: Sahte)
    assert yayinla.main(["--id", g.kimlik, "--id", "olmayan", "--gercek"]) == 1
    assert oku(g.yol).durum == "yayinlandi"


@pytest.mark.parametrize("platform", ["instagram", "facebook"])
def test_hikaye_metinsiz_gecerli(platform):
    g = oku(ORNEK)
    g.veri.update(platform=platform, tur="hikaye", metin="", medya=["https://a/kare.jpg"])
    assert dogrula(g) == []


def test_instagram_hikaye_istekleri(monkeypatch):
    from araclar.platformlar import instagram
    monkeypatch.setenv("META_ERISIM_TOKENI", "t")
    monkeypatch.setenv("META_IG_KULLANICI_ID", "ig")
    cagrilar = []

    def sahte_istek(yontem, url, **kw):
        cagrilar.append((yontem, url, kw.get("data") or kw.get("params")))
        if url.endswith("/media"):
            return {"id": "k1"}
        if url.endswith("/media_publish"):
            return {"id": "m1"}
        if "fields" in (kw.get("params") or {}) and kw["params"]["fields"] == "status_code":
            return {"status_code": "FINISHED"}
        return {"permalink": None}

    monkeypatch.setattr(instagram, "istek", sahte_istek)
    g = oku(ORNEK)
    g.veri.update(tur="hikaye", metin="", medya=["https://a/klip.mp4"])
    sonuc = instagram.yayinla(g)
    olustur = cagrilar[0][2]
    assert olustur["media_type"] == "STORIES" and olustur["video_url"] == "https://a/klip.mp4"
    assert "caption" not in olustur
    assert sonuc == {"platform_id": "m1", "url": None, "tur": "hikaye"}


@pytest.fixture
def gelen(tmp_path, monkeypatch):
    from araclar import mesajlar
    monkeypatch.setattr(mesajlar, "DEPO", tmp_path / "mesajlar.json")
    monkeypatch.setattr(mesajlar, "DM_PLATFORMLARI", [])
    return mesajlar


def test_yorum_akisi(gelen, monkeypatch):
    m = gelen
    gonderilen = []

    class Sahte:
        @staticmethod
        def yorumlari_getir(_):
            return [{"platform_id": "c1", "gonderi_id": "m1", "gonderi_ozeti": "", "gonderi_url": None,
                     "yazar": "ayse", "metin": "Sipariş nasıl veriliyor?", "tarih": "2026-10-01T10:00:00+00:00"}]

        @staticmethod
        def yorum_yanitla(yid, metin):
            gonderilen.append((yid, metin))
            return {"yanit_id": "r1"}

    monkeypatch.setattr(m, "istemci", lambda p: Sahte)
    monkeypatch.setattr(m, "YORUM_PLATFORMLARI", ["instagram"])
    assert m.main(["cek"]) == 0
    assert m.main(["cek"]) == 0  # ikinci çekimde tekrar eklenmez
    assert len(m.yukle()["kayitlar"]) == 1

    assert m.main(["gonder", "1", "--ad", "T", "--gercek"]) == 1  # taslaksız gönderilemez
    assert m.main(["taslak", "1", "--kategori", "soru", "--yanit", "DM'den yazabilirsin 🌾"]) == 0
    assert m.main(["gonder", "1", "--ad", "T"]) == 0  # kuru çalışma
    assert gonderilen == []
    assert m.main(["gonder", "1", "--ad", "T", "--gercek"]) == 0
    assert gonderilen == [("c1", "DM'den yazabilirsin 🌾")]
    kayit = m.yukle()["kayitlar"][0]
    assert kayit["durum"] == "gonderildi" and kayit["onaylayan"] == "T"
    with pytest.raises(SystemExit):
        m.main(["taslak", "1", "--kategori", "soru", "--yanit", "x"])


def _dm(no, durum, son_yanit, **ek):
    return {"no": no, "tur": "dm", "platform": "instagram", "platform_id": f"m{no}", "konusma_id": "k1",
            "alici_id": "u1", "yazar": "veli", "metin": "Merhaba", "durum": durum,
            "cekilme": "2026-10-01T00:00:00+00:00", "tarih": "2026-10-01T00:00:00+00:00",
            "son_yanit": son_yanit, **ek}


def test_dm_akisi_ve_24_saat(gelen, monkeypatch):
    import datetime as dt
    m = gelen
    gelecek = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=5)).isoformat()
    gecmis = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)).isoformat()
    m.kaydet({"sayac": 2, "kayitlar": [
        _dm(1, "taslak", gecmis, yanit="Selam"),
        {**_dm(2, "taslak", gelecek, yanit="Merhaba, SSS'deki adımlarla sipariş verebilirsin."), "konusma_id": "k2"},
    ]})
    giden = []
    monkeypatch.setattr(m.mesajlasma, "dm_gonder", lambda alici, metin: giden.append((alici, metin)) or {"yanit_id": "x"})
    assert m.main(["gonder", "1", "2", "--ad", "T", "--gercek"]) == 1
    kayitlar = {k["no"]: k for k in m.yukle()["kayitlar"]}
    assert kayitlar[1]["durum"] == "suresi_doldu"
    assert kayitlar[2]["durum"] == "gonderildi" and len(giden) == 1


def test_dm_ayni_konusma_guncellenir(gelen, monkeypatch):
    import datetime as dt
    m = gelen
    gelecek = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=20)).isoformat()
    m.kaydet({"sayac": 1, "kayitlar": [_dm(1, "taslak", gelecek, yanit="eski taslak")]})
    yeni = {"platform_id": "m9", "konusma_id": "k1", "alici_id": "u1", "yazar": "veli",
            "metin": "Merhaba\nBir de fiyat?", "tarih": "2026-10-01T01:00:00+00:00", "son_yanit": gelecek}
    monkeypatch.setattr(m, "DM_PLATFORMLARI", ["instagram"])
    monkeypatch.setattr(m, "YORUM_PLATFORMLARI", [])
    monkeypatch.setattr(m.mesajlasma, "dmleri_getir", lambda p, s: [yeni])
    m.main(["cek"])
    kayitlar = m.yukle()["kayitlar"]
    assert len(kayitlar) == 1
    assert kayitlar[0]["durum"] == "yeni" and "yanit" not in kayitlar[0] and "fiyat" in kayitlar[0]["metin"]


def test_meta_dm_bekleyenleri_ayiklar(monkeypatch):
    import datetime as dt
    from araclar.platformlar import mesajlasma
    monkeypatch.setenv("META_ERISIM_TOKENI", "t")
    monkeypatch.setenv("META_SAYFA_ID", "sayfa")
    monkeypatch.setenv("META_IG_KULLANICI_ID", "ig")
    simdi = dt.datetime.now(dt.timezone.utc)
    z = lambda sa: (simdi - dt.timedelta(hours=sa)).strftime("%Y-%m-%dT%H:%M:%S+0000")
    yanit = {"data": [
        {"id": "k1", "messages": {"data": [  # en yeni önce: iki bekleyen, sonra bizim yanıtımız
            {"id": "a3", "message": "Fiyat?", "from": {"id": "u1", "username": "veli"}, "created_time": z(1)},
            {"id": "a2", "message": "Merhaba", "from": {"id": "u1", "username": "veli"}, "created_time": z(2)},
            {"id": "a1", "message": "Selam!", "from": {"id": "ig"}, "created_time": z(3)}]}},
        {"id": "k2", "messages": {"data": [  # son mesaj bizden: yanıt beklemiyor
            {"id": "b2", "message": "Rica ederiz", "from": {"id": "ig"}, "created_time": z(1)},
            {"id": "b1", "message": "Teşekkürler", "from": {"id": "u2"}, "created_time": z(2)}]}},
    ]}
    monkeypatch.setattr(mesajlasma, "istek", lambda *a, **k: yanit)
    sonuc = mesajlasma.dmleri_getir("instagram", simdi - dt.timedelta(days=1))
    assert len(sonuc) == 1
    assert sonuc[0]["metin"] == "Merhaba\nFiyat?" and sonuc[0]["alici_id"] == "u1"


def test_kayit_insana_ve_eski_kayit_temizligi(gelen, monkeypatch):
    m = gelen
    m.kaydet({"sayac": 2, "kayitlar": [
        {"no": 1, "tur": "yorum", "platform": "instagram", "platform_id": "a", "durum": "atlandi",
         "cekilme": "2020-01-01T00:00:00+00:00", "yazar": "x", "metin": "eski"},
        {"no": 2, "tur": "yorum", "platform": "instagram", "platform_id": "b", "durum": "yeni",
         "cekilme": "2020-01-01T00:00:00+00:00", "yazar": "y", "metin": "kargom gelmedi"},
    ]})
    assert m.main(["insana", "2", "--kategori", "sikayet", "--neden", "teslimat şikâyeti"]) == 0

    class Bos:
        @staticmethod
        def yorumlari_getir(_):
            return []

    monkeypatch.setattr(m, "istemci", lambda p: Bos)
    m.main(["cek"])
    kalan = m.yukle()["kayitlar"]
    assert [k["no"] for k in kalan] == [2] and kalan[0]["durum"] == "insana"


# --- Yer tutucu kontrolü ---

@pytest.mark.parametrize("degisiklik, beklenen", [
    ({"metin": "Yeni [MODEL] geldi"}, "[MODEL]"),
    ({"metin": "Pil sağlığı [PİL %] seviyesinde"}, "[PİL %]"),
    ({"metin": "Sadece [FİYAT] TL"}, "[FİYAT]"),
    ({"metin": "Satır\n[stok cihaz görünürse bu satırı ekle]\nson"}, "[stok cihaz görünürse"),
    ({"metin": "[ŞARJ ĞÜÖÇ]"}, "[ŞARJ ĞÜÖÇ]"),
    ({"platform": "youtube", "tur": "video", "baslik": "[MODEL] incelemesi"}, "'baslik' alanında"),
    ({"platform": "facebook", "tur": "baglanti", "medya": [],
      "baglanti": "[APPLE-RESMI-BAGLANTI: destek sayfası]"}, "[APPLE-RESMI-BAGLANTI"),
    ({"platform": "facebook", "tur": "baglanti", "medya": [],
      "baglanti": "[YOUTUBE-VIDEO-BAGLANTISI]"}, "'baglanti' geçerli"),
    ({"baglanti": "ftp://ornek.com/x"}, "'baglanti' geçerli"),
    ({"baglanti": "ornek.com"}, "'baglanti' geçerli"),
])
def test_yer_tutucu_hatalari(degisiklik, beklenen):
    g = oku(ORNEK)
    g.veri.update(degisiklik)
    assert any(beklenen in h for h in dogrula(g)), dogrula(g)


def test_yer_tutucu_yoksa_ve_gecerli_baglanti():
    g = oku(ORNEK)
    g.veri.update(platform="facebook", tur="baglanti", medya=[],
                  baglanti="https://support.apple.com/tr-tr/101575",
                  metin="Ayrıntılar için [Apple destek](https://support.apple.com) sayfasına bak.")
    assert dogrula(g) == []


def test_govdedeki_yer_tutucu_serbest():
    g = oku(ORNEK)
    g.govde += "\n## Üretim paketi\n[MODEL] çekimi, [PİL %] ekranı\n"
    assert dogrula(g) == []


# --- Ertelendi durumu ---

def test_ertelendi_gecerli_durum():
    assert "ertelendi" in icerik.DURUMLAR
    g = oku(ORNEK)
    g.veri.update(durum="ertelendi", medya=[], metin="[MODEL] [FİYAT]",
                  baglanti="[YOUTUBE-VIDEO-BAGLANTISI]")
    assert dogrula(g) == []


def test_ertelendi_ozette_gorunur_hata_saymaz(klasor, capsys):
    from araclar import dogrula as dogrula_cli
    g = _kopya(klasor, durum="ertelendi", medya=[])
    assert dogrula_cli.main([str(g.yol), "--ozet"]) == 0
    cikti = capsys.readouterr().out
    assert "ertelendi: 1" in cikti and g.kimlik in cikti and "0 hatalı" in cikti


def test_ertelendi_onaylanamaz(klasor, capsys):
    g = _kopya(klasor, durum="ertelendi")
    assert onayla.main([g.kimlik, "--ad", "Test"]) == 1
    assert "ertelendi" in capsys.readouterr().out
    sonuc = oku(g.yol)
    assert sonuc.durum == "ertelendi" and "onaylayan" not in sonuc.veri


def test_ertelendi_yayinlanmaz(klasor, monkeypatch):
    g = _kopya(klasor, durum="ertelendi", planlanan_tarih="2020-01-01T10:00:00+03:00")
    monkeypatch.setattr(yayinla, "istemci", lambda p: pytest.fail("ertelenen gönderi yayınlandı"))
    assert yayinla.main(["--gercek"]) == 0
    assert yayinla.main(["--id", g.kimlik, "--gercek"]) == 1
    assert oku(g.yol).durum == "ertelendi"


def test_kanca_ertelendi_serbest():
    yol = str(KOK / "icerik" / "gonderiler" / "x.md")
    assert _kanca({"file_path": yol, "old_string": "durum: taslak",
                   "new_string": "durum: ertelendi"}) == 0
    assert _kanca({"file_path": yol, "old_string": "durum: ertelendi",
                   "new_string": "durum: taslak"}) == 0


ORNEK_COCUK = KOK / "icerik" / "ornek-cocuk-gonderi.md"


def test_ornek_cocuk_gecerli():
    assert dogrula(oku(ORNEK_COCUK)) == []


@pytest.mark.parametrize("degisiklik, beklenen", [
    ({"platform": "instagram", "tur": "reels"}, "yalnızca YouTube"),
    ({"yz_icerik": None}, "yz_icerik"),
    ({"metin": "Beğendiysen yorumlara yaz!"}, "yorum"),
    ({"metin": "Daha fazlası: https://ornek.com"}, "dış bağlantı"),
    ({"gizlilik": "unlisted"}, "unlisted"),
    ({"kanal": "bilinmeyen"}, "bilinmeyen kanal"),
])
def test_cocuk_dogrulama_hatalari(degisiklik, beklenen):
    g = oku(ORNEK_COCUK)
    g.veri.update(degisiklik)
    assert any(beklenen in h for h in dogrula(g))


def test_cocuk_guvenlik_bolumu_zorunlu():
    g = oku(ORNEK_COCUK)
    g.govde = g.govde.replace("## Çocuk güvenliği", "## Notlar")
    assert any("Çocuk güvenliği" in h for h in dogrula(g))


def test_youtube_cocuk_govdesi_ve_zamanlama():
    import datetime as dt
    from araclar.platformlar import youtube
    g = oku(ORNEK_COCUK)
    once = dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc)
    st = youtube.govde_olustur(g, once)["status"]
    assert "publishAt" not in st and st["privacyStatus"] == "public"  # zamanla istenmedi
    st = youtube.govde_olustur(g, once, zamanla=True)["status"]
    assert st["selfDeclaredMadeForKids"] is True and st["containsSyntheticMedia"] is False
    assert st["privacyStatus"] == "private" and st["publishAt"] == "2026-10-20T07:00:00Z"

    sonra = dt.datetime(2026, 11, 1, tzinfo=dt.timezone.utc)
    st = youtube.govde_olustur(g, sonra, zamanla=True)["status"]
    assert "publishAt" not in st and st["privacyStatus"] == "public"  # zaman geçmiş

    ana = oku(ORNEK)
    ana.veri.update(platform="youtube", tur="shorts", baslik="x")
    st = youtube.govde_olustur(ana, sonra)["status"]
    assert st["selfDeclaredMadeForKids"] is False and "containsSyntheticMedia" not in st


def test_yayinla_zamanla_ileri_youtube(klasor, monkeypatch):
    c = oku(ORNEK_COCUK)
    c.veri.update(durum="onaylandi", onaylayan="Test", planlanan_tarih="2099-01-01T10:00:00+03:00")
    c.yol = klasor / f"{c.kimlik}.md"
    c.kaydet()
    ig = _kopya(klasor, durum="onaylandi", onaylayan="Test", planlanan_tarih="2099-01-01T10:00:00+03:00")

    class Sahte:
        @staticmethod
        def yayinla(_, zamanla=False):
            assert zamanla
            return {"platform_id": "v1", "url": "https://youtu.be/v1", "kanal": "cocuk",
                    "zamanlanan_yayin": "2099-01-01T07:00:00Z"}

    monkeypatch.setattr(yayinla, "istemci", lambda p: Sahte)
    assert yayinla.main(["--gercek"]) == 0
    assert oku(c.yol).durum == "onaylandi"
    assert yayinla.main(["--zamanla", "--gercek"]) == 0
    assert oku(c.yol).veri["yayin"]["zamanlanan_yayin"] == "2099-01-01T07:00:00Z"
    assert oku(ig.yol).durum == "onaylandi"  # Instagram zamanlanamaz, beklemeye devam
