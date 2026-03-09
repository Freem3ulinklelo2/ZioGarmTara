import requests
import os
import base64

# ==============================
# 🔐 SOURCES FROM GITHUB SECRETS
# ==============================

BASE_M3U_URL = os.environ.get("BASE_M3U_URL")  # Ab iski zaroorat nahi, bas JSON se kaam
LOGO_JSON_URL = os.environ.get("LOGO_JSON_URL")

# ==============================
# STREAMFLEX CONFIG
# ==============================

STREAMFLEX_UA = "StreamFlex/7.1.3 (Linux;Android 13) StreamFlex/69.1 ExoPlayerLib/824.0"
STREAMFLEX_WATERMARK = "StreamFlex"
STREAMFLEX_TG = "@StreamFlex19"

# ==============================
# FETCH JSON DATA
# ==============================

def fetch_json_data():
    try:
        r = requests.get(LOGO_JSON_URL, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ Error fetching JSON: {e}")
        return []

# ==============================
# BUILD M3U FROM JSON
# ==============================

def build_m3u(channels):
    lines = []
    
    # M3U Header with StreamFlex branding
    lines.append("#EXTM3U")
    lines.append(f"# Playlist: ZioGarmTara")
    lines.append(f"# Created by: {STREAMFLEX_WATERMARK}")
    lines.append(f"# Telegram: {STREAMFLEX_TG}")
    lines.append(f"# User-Agent: {STREAMFLEX_UA}")
    lines.append("")
    
    for ch in channels:
        name = ch.get("name", "Unknown").strip()
        logo = ch.get("logo", "").strip()
        link = ch.get("link", "").strip()
        cookie = ch.get("cookie", "").strip()
        drm_scheme = ch.get("drmScheme", "").strip()
        drm_license = ch.get("drmLicense", "").strip()
        
        if not link:
            continue
        
        # Build EXTINF line
        extinf = f'#EXTINF:-1 tvg-name="{name}"'
        if logo:
            extinf += f' tvg-logo="{logo}"'
        extinf += f' group-title="{STREAMFLEX_WATERMARK}",{name}'
        lines.append(extinf)
        
        # Add VLCOPT for User-Agent
        lines.append(f'#EXTVLCOPT:http-user-agent={STREAMFLEX_UA}')
        
        # Add Cookie if available
        if cookie:
            lines.append(f'#EXTVLCOPT:http-cookie={cookie}')
        
        # Add DRM headers if available
        if drm_scheme and drm_license:
            if drm_scheme.lower() == "clearkey":
                lines.append(f'#KODIPROP:inputstream.adaptive.license_type=clearkey')
                lines.append(f'#KODIPROP:inputstream.adaptive.license_key={drm_license}')
                lines.append(f'#EXTVLCOPT:http-header=Authorization=Bearer {drm_license}')
        
        # Add Stream URL
        lines.append(link)
        lines.append("")  # Empty line between channels
    
    return "\n".join(lines)

# ==============================
# MAIN
# ==============================

def main():
    print(f"🔄 Fetching JSON data from {LOGO_JSON_URL}...")
    channels = fetch_json_data()
    
    if not channels:
        print("❌ No channels found in JSON!")
        return
    
    print(f"✅ Found {len(channels)} channels")
    
    print(f"🛠 Building M3U with {STREAMFLEX_WATERMARK} branding...")
    m3u_content = build_m3u(channels)
    
    with open("ZioGarmTara.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"✅ ZioGarmTara.m3u created successfully!")
    print(f"📺 Total channels: {len(channels)}")
    print(f"🏷️  Watermark: {STREAMFLEX_WATERMARK}")
    print(f"📱 Telegram: {STREAMFLEX_TG}")

if __name__ == "__main__":
    main()
