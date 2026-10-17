import argparse
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from src.pipeline import VideoPipeline


def main():
    parser = argparse.ArgumentParser(description="YouTube Shorts AI Otomatik Video Üretici")
    parser.add_argument("--topic", type=str, default=None, help="Özel video konusu (Boş bırakılırsa viral rastgele konu seçilir)")
    parser.add_argument("--style", type=str, default="pixar_3d", help="Görsel stili (pixar_3d, vibrant_cartoon, claymation, baby_monster_fluffy)")
    parser.add_argument("--voice", type=str, default="en-US-AnaNeural", help="Edge-TTS ses ID (en-US-AnaNeural, en-US-AndrewNeural vb.)")
    parser.add_argument("--scenes", type=int, default=5, help="Sahne sayısı (Varsayılan: 5)")
    parser.add_argument("--batch", type=int, default=1, help="Üretilecek video adedi (Varsayılan: 1)")

    args = parser.parse_args()

    print("=" * 60)
    print("🎬 YouTube Shorts AI Otomasyon Motoru Başlatılıyor...")
    print(f"📌 Hedef Pazar: US English | Stil: {args.style} | Ses: {args.voice}")
    print(f"📦 Üretilecek Aday Sayısı: {args.batch}")
    print("=" * 60)

    pipeline = VideoPipeline()

    for i in range(args.batch):
        print(f"\n🚀 [{i+1}/{args.batch}] Video üretimi başladı...")
        try:
            result = pipeline.generate_single_short(
                topic=args.topic,
                style_key=args.style,
                voice_id=args.voice,
                num_scenes=args.scenes,
                progress_callback=lambda p, msg: print(f"   [{int(p*100)}%] {msg}")
            )
            print(f"\n✅ Video Başarıyla Üretildi!")
            print(f"   🏷️ Başlık: {result['title']}")
            print(f"   📁 Dosya Yolu: {result['video_path']}")
            print(f"   ⏱️ Süre: {result['duration']:.1f} saniye")
        except Exception as e:
            print(f"\n❌ Hata oluştu: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("🎉 İşlem tamamlandı! Web kontrol panelini açmak için:")
    print("   streamlit run dashboard/app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
