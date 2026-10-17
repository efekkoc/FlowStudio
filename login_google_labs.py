import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from src.automation.google_labs_bot import GoogleLabsBot

if __name__ == "__main__":
    print("=" * 60)
    print("🔑 Google Labs Giriş Penceresi Başlatılıyor (Stealth Chrome)...")
    print("Açılan pencerede Google hesabınızla giriş yapın.")
    print("Giriş tamamlandıktan sonra pencereyi kapatabilirsiniz.")
    print("=" * 60)
    
    bot = GoogleLabsBot(headless=False)
    bot.open_login_window()
    print("✅ Oturum başarıyla hafızaya alındı!")
