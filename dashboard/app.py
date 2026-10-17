import os
import sys
import json
import shutil
import time
from pathlib import Path
from datetime import datetime, time as dtime, timedelta, timezone
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from config.settings import (
    CANDIDATES_DIR, APPROVED_DIR, STYLE_PRESETS,
    get_gemini_api_key, YOUTUBE_CLIENT_SECRET_FILE, BASE_DIR
)
from src.automation.flow_cdp_bot import FlowCDPBot
from src.generator.google_labs_prompter import GoogleLabsPrompter
from src.video_engine.video_enhancer import VideoEnhancer
from src.automation.safari_bridge import SafariBridge
from src.automation.downloads_watcher import DownloadsWatcher
from src.youtube.uploader import YouTubeUploader
from src.api.shortcuts_server import start_shortcuts_api

# Start iPhone Shortcuts API Webhook Server in Background
start_shortcuts_api()

st.set_page_config(
    page_title="Veo 3.1 • AI 3D Shorts Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# 2026 CYBERPUNK / GLASSMORPHISM HUD DESIGN SYSTEM
# -------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@400;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #06080d;
        background-image: 
            radial-gradient(at 15% 15%, rgba(99, 102, 241, 0.12) 0px, transparent 50%),
            radial-gradient(at 85% 85%, rgba(236, 72, 153, 0.10) 0px, transparent 50%),
            radial-gradient(at 50% 50%, rgba(139, 92, 246, 0.05) 0px, transparent 60%);
        color: #F1F5F9;
    }
    
    /* Native macOS Desktop App Look (Hide only web clutter) */
    #MainMenu { display: none !important; }
    footer { display: none !important; height: 0; }
    .stDeployButton, [data-testid="stAppDeployButton"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    [data-testid="stToolbarActions"] { display: none !important; }

    /* Desktop Styles: Permanent pinned sidebar, no collapse */
    @media (min-width: 769px) {
        header[data-testid="stHeader"] {
            background: transparent !important;
            height: 0px !important;
            min-height: 0px !important;
            pointer-events: none !important;
        }

        [data-testid="stSidebarCollapseButton"],
        button[data-testid="stSidebarCollapseButton"],
        [data-testid="stExpandSidebarButton"],
        button[data-testid="stExpandSidebarButton"],
        [data-testid="stSidebarCollapsedControl"],
        button[aria-label*="sidebar" i],
        button[kind="headerNoPadding"] {
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
            width: 0 !important;
            height: 0 !important;
            opacity: 0 !important;
        }

        section[data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            min-width: 325px !important;
            max-width: 345px !important;
            width: 335px !important;
            transform: none !important;
            transition: none !important;
            margin-left: 0 !important;
            left: 0 !important;
            opacity: 1 !important;
        }
    }

    /* Mobile Styles (iPhone Safari & Apple Shortcuts Web View) */
    @media (max-width: 768px) {
        header[data-testid="stHeader"] {
            background: rgba(6, 8, 13, 0.9) !important;
            backdrop-filter: blur(10px) !important;
            height: 3.5rem !important;
            pointer-events: auto !important;
        }
        
        .hero-container {
            padding: 1.2rem 1.4rem !important;
            border-radius: 16px !important;
        }
        
        .hero-title {
            font-size: 1.7rem !important;
            line-height: 1.2 !important;
        }

        .hero-chips {
            flex-direction: column !important;
            gap: 6px !important;
        }
        
        .hud-console {
            padding: 1.2rem !important;
        }

        .glass-card {
            padding: 1.2rem !important;
        }
    }

    /* Hide injected helper iframe */
    iframe[title="streamlit.components.v1.html"] {
        position: absolute !important;
        width: 0 !important;
        height: 0 !important;
        border: none !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* Hero Banner */
    .hero-container {
        position: relative;
        background: linear-gradient(135deg, rgba(22, 27, 46, 0.9), rgba(12, 14, 25, 0.95));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 22px;
        padding: 2.2rem 2.5rem;
        margin-bottom: 2rem;
        backdrop-filter: blur(24px);
        box-shadow: 0 20px 45px -15px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        overflow: hidden;
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2));
        border: 1px solid rgba(139, 92, 246, 0.4);
        color: #C084FC;
        padding: 5px 14px;
        border-radius: 30px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }
    
    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.7rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #FFFFFF 20%, #E2E8F0 60%, #A5B4FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.15;
    }
    
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.02rem;
        margin-top: 0.6rem;
        font-weight: 400;
    }

    .hero-chips {
        display: flex;
        gap: 12px;
        margin-top: 1.3rem;
        flex-wrap: wrap;
    }

    .hero-chip {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 6px 14px;
        font-size: 0.82rem;
        color: #CBD5E1;
        font-weight: 500;
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(17, 21, 37, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(20px);
        box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.5);
    }

    /* Credit Card in Sidebar */
    .credit-box {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.75), rgba(15, 23, 42, 0.85));
        border: 1px solid rgba(129, 140, 248, 0.28);
        border-radius: 18px;
        padding: 1.3rem;
        margin: 1rem 0;
    }
    .credit-title {
        font-size: 0.75rem;
        font-weight: 700;
        color: #818CF8;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .credit-val {
        font-family: 'Outfit', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0.2rem 0;
    }
    .credit-progress-bg {
        width: 100%;
        height: 6px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 6px;
        overflow: hidden;
        margin: 0.6rem 0;
    }
    .credit-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #6366F1, #A855F7);
        border-radius: 6px;
    }
    .credit-sub {
        font-size: 0.82rem;
        color: #34D399;
        font-weight: 600;
    }

    /* High-Tech Loading HUD */
    .hud-console {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.95), rgba(10, 15, 30, 0.98));
        border: 1px solid rgba(139, 92, 246, 0.4);
        border-radius: 20px;
        padding: 1.8rem;
        margin: 1.5rem 0;
        box-shadow: 0 0 35px rgba(99, 102, 241, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    .hud-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .hud-badge-pulse {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.78rem;
        font-weight: 700;
        color: #34D399;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
    }
    .hud-dot {
        width: 8px;
        height: 8px;
        background: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10B981;
    }
    .hud-pct {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #818CF8, #C084FC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hud-progress-container {
        width: 100%;
        height: 10px;
        background: rgba(255, 255, 255, 0.07);
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 1rem;
    }
    .hud-progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #4F46E5, #9333EA, #EC4899);
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.6);
        transition: width 0.3s ease;
    }
    .hud-stage {
        font-family: 'Outfit', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.3rem;
    }
    .hud-detail {
        font-size: 0.9rem;
        color: #94A3B8;
        line-height: 1.4;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #C026D3 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.7rem 1.4rem !important;
        font-weight: 700 !important;
        font-size: 0.96rem !important;
        box-shadow: 0 8px 25px -6px rgba(124, 58, 237, 0.5) !important;
        transition: all 0.25s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 32px -4px rgba(192, 38, 211, 0.6) !important;
    }

    /* Tabs Styling */
    div[data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    div[data-baseweb="tab"] {
        border-radius: 10px !important;
        padding: 8px 18px !important;
        font-weight: 600 !important;
        color: #94A3B8 !important;
        border: none !important;
    }
    div[aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(168, 85, 247, 0.25)) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
    }

    /* Candidate Video Card */
    .video-card-container {
        background: rgba(18, 22, 38, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.6rem;
        margin-bottom: 2rem;
        box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.6);
        transition: border 0.3s ease;
    }
    .video-card-container:hover {
        border: 1px solid rgba(129, 140, 248, 0.35);
    }

    /* Badges */
    .badge-emerald {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-purple {
        background: rgba(168, 85, 247, 0.15);
        color: #C084FC;
        border: 1px solid rgba(168, 85, 247, 0.3);
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    video {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# Otomatik Olarak Sidebar'ı Açık ve Sabit Tut (Gizleme/Kapatmayı Devre Dışı Bırak)
components.html(
    """
    <script>
    (function() {
        try {
            // LocalStorage'daki Streamlit stSidebarCollapsed anahtarlarını temizle
            for (let i = localStorage.length - 1; i >= 0; i--) {
                const k = localStorage.key(i);
                if (k && k.includes('stSidebarCollapsed')) {
                    localStorage.removeItem(k);
                }
            }
        } catch(e) {}

        function forceSidebarOpen() {
            try {
                const parentWin = window.parent || window;
                const isDesktop = parentWin.innerWidth > 768;
                if (!isDesktop) return; // Mobil cihazlarda (iPhone) sidebar'ı zorla açma

                const doc = window.parent.document;
                const expandBtn = doc.querySelector('[data-testid="stExpandSidebarButton"]');
                if (expandBtn) {
                    expandBtn.click();
                }
                const sidebar = doc.querySelector('section[data-testid="stSidebar"]');
                if (sidebar) {
                    sidebar.style.transform = 'none';
                    sidebar.style.minWidth = '325px';
                    sidebar.style.maxWidth = '345px';
                    sidebar.style.display = 'block';
                    sidebar.style.visibility = 'visible';
                    sidebar.style.opacity = '1';
                }
                const collapseBtn = doc.querySelector('[data-testid="stSidebarCollapseButton"]');
                if (collapseBtn) {
                    collapseBtn.style.display = 'none';
                }
            } catch(e) {}
        }
        forceSidebarOpen();
        setTimeout(forceSidebarOpen, 100);
        setTimeout(forceSidebarOpen, 400);
        setTimeout(forceSidebarOpen, 1000);
    })();
    </script>
    """,
    height=0,
    width=0
)

# Otomatik İndirme İzleyicisini Başlat
if "watcher_started" not in st.session_state:
    watcher = DownloadsWatcher()
    watcher.start()
    st.session_state["watcher_started"] = True


def get_candidate_videos():
    candidates = []
    if not CANDIDATES_DIR.exists():
        return candidates

    for v_dir in sorted(CANDIDATES_DIR.glob("short_*"), key=lambda x: x.stat().st_ctime, reverse=True):
        meta_file = v_dir / "metadata.json"
        video_file = v_dir / "final_short.mp4"
        if meta_file.exists() and video_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    meta["dir"] = str(v_dir)
                    candidates.append(meta)
            except Exception:
                pass
    return candidates


# -------------------------------------------------------------
# SIDEBAR NAVIGATION & SYSTEM METRICS
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem;">
        <span style="font-size: 2rem;">🎬</span>
        <div>
            <div style="font-family: 'Outfit'; font-weight: 800; font-size: 1.25rem; color: #FFFFFF; line-height: 1.1;">FLOW STUDIO</div>
            <div style="font-size: 0.75rem; color: #818CF8; font-weight: 600; letter-spacing: 0.05em;">AUTOPILOT V2.5</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Kredi Durumu (Anında yüklenir, sayfayı asla dondurmaz)
    if "flow_credits" not in st.session_state:
        st.session_state["flow_credits"] = 930

    curr_cred = st.session_state["flow_credits"]
    rem_videos = max(0, curr_cred // 15)
    pct_fill = min(100.0, max(0.0, (curr_cred / 1000.0) * 100.0))

    st.markdown(f"""
    <div class="credit-box">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="credit-title">GOOGLE FLOW KREDİSİ</span>
            <span class="badge-purple">⚡ Pro</span>
        </div>
        <div class="credit-val">{curr_cred} 🪙</div>
        <div class="credit-progress-bg">
            <div class="credit-progress-fill" style="width: {pct_fill}%;"></div>
        </div>
        <div class="credit-sub">🚀 ~{rem_videos} Adet 3D Video Üretilebilir</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📡 Sistem Bağlantıları")
    token_exists = (BASE_DIR / "token.json").exists()
    current_gemini_key = get_gemini_api_key()
    gemini_active = bool(current_gemini_key and len(current_gemini_key.strip()) > 5)

    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.caption("YouTube Kanalı:")
        st.markdown('<span class="badge-emerald">● Satisphoria</span>' if token_exists else '<span style="color:#F59E0B">● Bekliyor</span>', unsafe_allow_html=True)
    with col_stat2:
        st.caption("Gemini AI:")
        st.markdown('<span class="badge-emerald">● Aktif</span>' if gemini_active else '<span style="color:#F59E0B">● Şablon</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🔑 Google Pro Otomasyonu")
    st.caption("Chrome profilini açıp tek tıkla Flow oturumunu başlat:")
    if st.button("🌐 Chrome Flow Penceresini Aç", use_container_width=True):
        bot = FlowCDPBot()
        bot.open_chrome_for_login()
        st.success("Flow açıldı! Pencereyi arka planda açık bırakabilirsiniz.")

    with st.expander("⚙️ Gemini API Anahtarı"):
        new_gemini = st.text_input("API Key", value=current_gemini_key, type="password")
        if st.button("Kaydet", use_container_width=True):
            env_path = BASE_DIR / ".env"
            with open(env_path, "w") as f:
                f.write(f"GEMINI_API_KEY={new_gemini}\n")
                f.write(f"YOUTUBE_CLIENT_SECRET_FILE={YOUTUBE_CLIENT_SECRET_FILE}\n")
            st.success("Kaydedildi!")


# -------------------------------------------------------------
# HERO BANNER
# -------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">⚡ NEXT-GEN VEO 3.1 AUTONOMOUS PIPELINE</div>
    <h1 class="hero-title">Google Flow 3D AI Studio</h1>
    <div class="hero-subtitle">Google Pro Hesabınızla Sıfır Ekstra Masraf: Otonom Prompt ➔ Otomatik Onay ➔ 4K 60FPS Video ➔ ASMR Ses Montajı ➔ YouTube Yayın</div>
    <div class="hero-chips">
        <span class="hero-chip">📐 1080x1920 9:16 Shorts</span>
        <span class="hero-chip">🎧 Dinamik ASMR Çocuk Müziği</span>
        <span class="hero-chip">✨ %100 Otonom İndirme & Montaj</span>
        <span class="hero-chip">🚀 Sıfır Kopyala-Yapıştır</span>
    </div>
</div>
""", unsafe_allow_html=True)

candidate_list = get_candidate_videos()
cand_count_str = f" ({len(candidate_list)})" if candidate_list else ""

tab_autopilot, tab_review, tab_safari = st.tabs([
    "🚀 1. Otonom 3D Video Üretici",
    f"🎯 2. Aday Videolar & YouTube Yayın{cand_count_str}",
    "🧪 3. Safari & Manuel Mod"
])


# -------------------------------------------------------------
# TAB 1: OTONOM ÜRETİM
# -------------------------------------------------------------
with tab_autopilot:
    if "last_video_success" in st.session_state and st.session_state["last_video_success"]:
        lv = st.session_state["last_video_success"]
        st.success(f"🎉 Son Üretilen Video: **{lv.get('title')}** stüdyoya eklendi! İncelemek veya zamanlamak için **🎯 2. Aday Videolar** sekmesine geçebilirsiniz.")

    col_main, col_info = st.columns([1.8, 1.1])

    with col_main:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🪄 Yeni 3D Pixar Videosu Oluştur")
        st.caption("Yapay zeka her seferinde sıfırdan tamamen özgün, viral ve yüksek izlenme potansiyeline sahip bir karakter senaryosu üretir.")

        topic_mode = st.selectbox(
            "Viral Kategori / Karakter Seçimi:",
            [
                "🎲 Rastgele En Viral Trend (AI Tamamen Özgün Seçim)",
                "🦉 Sevimli Bebek Baykuş & Yıldız Tozu Ninnisi (Baby Owl)",
                "🦔 Meşe Palamudu Şapkalı Sevimli Kirpi & Ateş Böcekleri (Baby Hedgehog)",
                "🦦 Sevimli Bebek Su Samuru & Parlayan İnciler (Baby Otter Pearls)",
                "🐧 Şapkalı Tombik Penguen & Gökkuşağı Buz Pisti (Baby Penguin)",
                "🦊 Kristal Çiçekli Büyülü Mağara & Sevimli Tilki (Baby Fox)",
                "🐼 Bebek Kızıl Panda & Çilekli Pasta Fırını (Baby Red Panda Bakery)",
                "🐰 Düşük Stimülasyonlu Sevimli 3D Tavşan & Orman (Low Stimulation Bunny)",
                "🐉 3D Bebek Ejderha & Büyülü Baloncuklar (Baby Dragon Bubble Bath)",
                "🥞 3D Sevimli Ayıcık & Dev Krep Kulesi (Mini Bear Pancake)",
                "🐘 Sevimli Bebek Fil & Büyülü Kelebek Yağmuru (Baby Elephant)"
            ]
        )

        batch_num = st.slider("Üretilecek Video Sayısı:", 1, 5, 1)

        st.markdown("<br>", unsafe_allow_html=True)
        start_btn = st.button(f"🚀 {batch_num} Adet 3D Videoyu Google Flow'dan Üret", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_info:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 🌟 Otonom Özellikler")
        st.markdown("""
        * **1. Canlı Prompt:** Gemini 3.6 tarafından tamamen benzersiz hazırlanır.
        * **2. Akıllı Onay:** Ekranda beliren *"Onayla ve bir daha sorma"* butonuna bot anında tıklar.
        * **3. Akıllı Hafıza:** Sayfadaki eski videoları hafızaya alır, asla eski videoyu tekrar indirmez.
        * **4. Yüksek Hızlı İndirme:** Video bittiğinde doğrudan CDN'den çekilir.
        * **5. ASMR Audio Mix:** 9:16 formata getirilip sakinleştirici fon müziği giydirilir.
        * **6. Otomatik Kredi Takibi:** Üretim bitince kalan kredi panelde anında güncellenir.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    # CANLI YENİ NESİL HUD KONSOLU
    hud_placeholder = st.empty()

    if start_btn:
        bot = FlowCDPBot()
        has_error = False
        error_msg = ""

        for b in range(batch_num):
            def render_hud(ratio, stage, detail):
                pct = int(ratio * 100)
                hud_placeholder.markdown(f"""
                <div class="hud-console">
                    <div class="hud-header">
                        <div class="hud-badge-pulse">
                            <div class="hud-dot"></div>
                            VEO 3.1 OTONOM PIPELINE AKTİF • [{b+1}/{batch_num}]
                        </div>
                        <div class="hud-pct">%{pct}</div>
                    </div>
                    <div class="hud-progress-container">
                        <div class="hud-progress-bar" style="width: {pct}%;"></div>
                    </div>
                    <div class="hud-stage">{stage}</div>
                    <div class="hud-detail">{detail}</div>
                </div>
                """, unsafe_allow_html=True)

            try:
                t_arg = None if "Rastgele" in topic_mode else topic_mode
                res = bot.generate_flow_video_full_auto(topic=t_arg, progress_callback=render_hud)
                st.toast(f"✅ Video Hazır: {res['title']}")
            except Exception as e:
                has_error = True
                error_msg = str(e)
                st.error(f"Hata oluştu: {e}")
                break

        if not has_error:
            hud_placeholder.markdown("""
            <div class="hud-console" style="border-color: rgba(52, 211, 153, 0.5);">
                <div class="hud-header">
                    <div class="hud-badge-pulse" style="color: #34D399; border-color: rgba(52, 211, 153, 0.4);">
                        <div class="hud-dot" style="background: #34D399;"></div>
                        TAMAMLANDI
                    </div>
                    <div class="hud-pct" style="background: linear-gradient(90deg, #34D399, #10B981); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">%100</div>
                </div>
                <div class="hud-stage">🎉 Tüm Videolar Başarıyla Hazırlandı!</div>
                <div class="hud-detail">1080x1920 9:16 montajı yapıldı, ASMR fon müziği eklendi ve '🎯 2. Aday Videolar' sekmesine yerleştirildi.</div>
            </div>
            """, unsafe_allow_html=True)

            # Krediyi otomatik güncelle
            try:
                updated_cred = bot.get_flow_credit_balance()
                if updated_cred is not None:
                    st.session_state["flow_credits"] = updated_cred
                else:
                    st.session_state["flow_credits"] = max(0, st.session_state["flow_credits"] - (batch_num * 15))
            except Exception:
                pass

            if "res" in locals() and res:
                st.session_state["last_video_success"] = res

            time.sleep(2)
            st.rerun()
        else:
            hud_placeholder.markdown(f"""
            <div class="hud-console" style="border-color: rgba(239, 68, 68, 0.5);">
                <div class="hud-header">
                    <div class="hud-badge-pulse" style="color: #EF4444; border-color: rgba(239, 68, 68, 0.4);">
                        <div class="hud-dot" style="background: #EF4444;"></div>
                        İŞLEM KESİNTİYE UĞRADI
                    </div>
                    <div class="hud-pct" style="color: #EF4444;">HATA</div>
                </div>
                <div class="hud-stage" style="color: #FCA5A5;">⚠️ Video Üretimi Sırasında Sorun Oluştu</div>
                <div class="hud-detail">{error_msg}</div>
            </div>
            """, unsafe_allow_html=True)


# -------------------------------------------------------------
# TAB 2: ADAY VİDEOLAR & YOUTUBE YAYIN
# -------------------------------------------------------------
with tab_review:
    candidate_list = get_candidate_videos()

    if not candidate_list:
        st.info("📭 Henüz bekleyen video yok. '1. Otonom 3D Video Üretici' sekmesinden hemen bir video oluşturabilirsiniz!")
    else:
        st.markdown(f"### 🎯 İnceleme Bekleyen **{len(candidate_list)}** Adet 3D Video")

        for cand in candidate_list:
            cid = cand.get("video_id", f"short_{int(time.time())}")
            st.markdown('<div class="video-card-container">', unsafe_allow_html=True)
            col_v1, col_v2 = st.columns([1.1, 1.9])

            with col_v1:
                v_path = cand.get("video_path")
                if os.path.exists(v_path):
                    st.video(v_path)
                else:
                    st.warning("Video dosyası bulunamadı.")

            with col_v2:
                st.markdown(f"#### 🎬 {cand.get('title')}")

                created_str = cand.get("created_at", "")
                time_display = "Yeni İndirildi"
                if created_str:
                    try:
                        dt_obj = datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S")
                        months_tr = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
                        time_display = f"{dt_obj.day} {months_tr[dt_obj.month]} {dt_obj.year} • {dt_obj.strftime('%H:%M')}"
                    except Exception:
                        time_display = created_str

                st.markdown(f"""
                <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 0.85rem;">
                    <span class="badge-emerald">📅 İndirildi: {time_display}</span>
                    <span class="badge-purple">⚡ 10s 9:16 Shorts</span>
                    <span style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 4px 10px; border-radius: 8px; font-size: 0.8rem; font-weight: 600;">🎧 ASMR Audio</span>
                </div>
                """, unsafe_allow_html=True)

                # HER VİDEOYA ÖZEL EŞSİZ KEY: BÖYLECE BAŞLIKLAR ASLA BİRBİRİNE KARIŞMAZ!
                title_val = st.text_input("Başlık", value=cand.get("title", ""), key=f"title_{cid}")
                desc_val = st.text_area("Açıklama & Etiketler", value=cand.get("description", ""), height=90, key=f"desc_{cid}")

                col_opt1, col_opt2 = st.columns(2)

                with col_opt1:
                    privacy_choice = st.selectbox(
                        "Gizlilik Durumu",
                        ["public", "unlisted", "private"],
                        key=f"priv_{cid}",
                        format_func=lambda x: {
                            "public": "🌐 Herkese Açık (Public)",
                            "unlisted": "🔗 Liste Dışı",
                            "private": "🔒 Gizli (Private)"
                        }.get(x, x)
                    )

                with col_opt2:
                    is_scheduled = st.checkbox("📅 İleri Bir Tarihe Planla", key=f"sched_{cid}")

                publish_at_iso = None
                if is_scheduled:
                    sc_col1, sc_col2 = st.columns(2)
                    with sc_col1:
                        target_date = st.date_input("🗓️ Yayın Günü", min_value=datetime.today().date(), key=f"date_{cid}")
                    with sc_col2:
                        target_time = st.time_input("⏰ Yayın Saati", value=dtime(18, 0), key=f"time_{cid}")

                    # Kullanıcının yerel saat dilimini (Türkiye UTC+3) dikkate alıp UTC'ye çeviriyoruz
                    local_tz = datetime.now().astimezone().tzinfo
                    combined_local = datetime.combine(target_date, target_time, tzinfo=local_tz)
                    utc_dt = combined_local.astimezone(timezone.utc)
                    publish_at_iso = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                    st.caption(f"📌 YouTube Planlama: **{combined_local.strftime('%d %B %Y • %H:%M')} (TSİ Yerel Saat)**")

                col_btn1, col_btn2 = st.columns([1.3, 1])

                with col_btn1:
                    if st.button("🚀 YouTube'a Yayınla / Planla", type="primary", key=f"up_{cid}", use_container_width=True):
                        with st.spinner("YouTube API ile yükleniyor..."):
                            try:
                                uploader = YouTubeUploader()
                                res = uploader.upload_short(
                                    video_path=cand["video_path"],
                                    title=title_val,
                                    description=desc_val,
                                    tags=cand.get("tags", []),
                                    privacy_status=privacy_choice,
                                    publish_at=publish_at_iso,
                                    thumbnail_path=cand.get("thumbnail_path")
                                )
                                st.success(f"🎉 Başarılı! Video yüklendi: [Shorts'ta İzle]({res['url']})")
                                cand_dir = Path(cand["dir"])
                                if cand_dir.exists():
                                    shutil.move(str(cand_dir), str(APPROVED_DIR / cand_dir.name))
                                time.sleep(2)
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Yükleme hatası: {ex}")

                with col_btn2:
                    if st.button("🗑️ Adayı Sil", key=f"del_{cid}", use_container_width=True):
                        cand_dir = Path(cand["dir"])
                        if cand_dir.exists():
                            shutil.rmtree(str(cand_dir))
                        st.warning("Video listeden kaldırıldı.")
                        time.sleep(1)
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------------------------------------
# TAB 3: SAFARI & MANUEL MOD
# -------------------------------------------------------------
with tab_safari:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🧪 Safari & Manuel Mod")
    st.caption("Otomasyon yerine Safari üzerinden manuel kopyala-yapıştır ile çalışmak isterseniz bu sekmeyi kullanabilirsiniz.")

    p_eng = GoogleLabsPrompter()
    manual_topic = st.text_input("Özel Karakter / Fikir:", placeholder="Örn: Bebek sincap kış için ceviz topluyor")

    if st.button("📋 Yeni Prompt & Açıklama Üret", use_container_width=True):
        m_data = p_eng.generate_master_prompt(manual_topic)
        st.session_state["manual_p"] = m_data

    if "manual_p" in st.session_state:
        m = st.session_state["manual_p"]
        st.text_area("Flow Promptu (Kopyalayın):", m["master_video_prompt"], height=100)
        st.text_input("YouTube Başlığı:", m["title"])
        st.text_area("YouTube Açıklaması:", m["description"], height=80)
    st.markdown('</div>', unsafe_allow_html=True)
