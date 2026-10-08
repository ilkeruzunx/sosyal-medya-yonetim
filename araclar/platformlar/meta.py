"""Meta Graph API ortak ayarları (Instagram ve Facebook)."""

from .ortak import ortam


def taban() -> str:
    return f"https://graph.facebook.com/{ortam('META_API_SURUMU', 'v23.0')}"


def token() -> str:
    return ortam("META_ERISIM_TOKENI")
