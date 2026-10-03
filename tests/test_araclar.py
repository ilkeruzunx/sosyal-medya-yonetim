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
