"""YouTube için bir kerelik OAuth yetkilendirmesi; yenileme tokenını yazdırır.

Kendi bilgisayarınızda çalıştırın (tarayıcı açılır):
    python -m araclar.youtube_yetkilendir istemci_sirri.json
    python -m araclar.youtube_yetkilendir istemci_sirri.json cocuk   # çocuk kanalı

Çocuk kanalı için tarayıcıda o kanalın (marka hesabının) seçildiğinden emin olun.
"""

import sys

from google_auth_oauthlib.flow import InstalledAppFlow

from .platformlar.youtube import KAPSAMLAR, TOKEN_DEGISKENI

if __name__ == "__main__":
    if len(sys.argv) not in (2, 3) or (len(sys.argv) == 3 and sys.argv[2] not in TOKEN_DEGISKENI):
        sys.exit(__doc__)
    kanal = sys.argv[2] if len(sys.argv) == 3 else "ana"
    akis = InstalledAppFlow.from_client_secrets_file(sys.argv[1], KAPSAMLAR)
    kimlik = akis.run_local_server(port=0, access_type="offline", prompt="consent")
    print("\n.env dosyanıza ekleyin:")
    print(f"YOUTUBE_ISTEMCI_ID={kimlik.client_id}")
    print(f"YOUTUBE_ISTEMCI_SIRRI={kimlik.client_secret}")
    print(f"{TOKEN_DEGISKENI[kanal]}={kimlik.refresh_token}")
