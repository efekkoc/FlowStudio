import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from src.youtube.uploader import YouTubeUploader

if __name__ == "__main__":
    print("🔑 YouTube API Kimlik Doğrulaması Başlatılıyor...")
    print("Tarayıcınızda açılan pencereden Google hesabınızla giriş yapıp izin verin.")
    uploader = YouTubeUploader()
    success = uploader.authenticate()
    if success:
        print("\n🎉 TEBRİKLER! YouTube API kimlik doğrulaması başarıyla tamamlandı ve 'token.json' kaydedildi.")
        print("Artık web panelinden dilediğiniz videoyu tek tıkla yükleyebilirsiniz!")
    else:
        print("\n❌ Kimlik doğrulaması başarısız oldu. client_secrets.json dosyanızı kontrol edin.")
