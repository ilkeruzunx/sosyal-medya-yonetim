"""YouTube için bir kerelik OAuth yetkilendirmesi; yenileme tokenını yazdırır.

Kendi bilgisayarınızda çalıştırın (tarayıcı açılır):
    python -m araclar.youtube_yetkilendir istemci_sirri.json
"""

import sys

from google_auth_oauthlib.flow import InstalledAppFlow

from .platformlar.youtube import KAPSAMLAR

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    akis = InstalledAppFlow.from_client_secrets_file(sys.argv[1], KAPSAMLAR)
    kimlik = akis.run_local_server(port=0, access_type="offline", prompt="consent")
    print("\n.env dosyanıza ekleyin:")
    print(f"YOUTUBE_ISTEMCI_ID={kimlik.client_id}")
    print(f"YOUTUBE_ISTEMCI_SIRRI={kimlik.client_secret}")
    print(f"YOUTUBE_YENILEME_TOKENI={kimlik.refresh_token}")
