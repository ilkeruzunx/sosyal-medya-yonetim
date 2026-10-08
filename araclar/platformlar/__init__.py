"""Platform istemcileri. Her modül `yayinla(gonderi) -> dict` ve `metrikler(sonuc) -> dict` sağlar."""

from importlib import import_module


def istemci(platform: str):
    return import_module(f"araclar.platformlar.{platform}")
