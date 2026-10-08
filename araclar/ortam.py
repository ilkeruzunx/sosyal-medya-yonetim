"""`.env` dosyasını (varsa) yükler."""

from .icerik import KOK


def yukle() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(KOK / ".env")
