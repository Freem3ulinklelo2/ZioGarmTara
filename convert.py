import requests
import os
from collections import defaultdict

# ==============================
# 🔐 SOURCES FROM GITHUB SECRETS
# ==============================

JSON_URL = os.environ.get("JSON_SOURCE_URL")
M3U_FALLBACK_URL = os.environ.get("M3U_SOURCE_URL")

# ==============================
# FETCH FUNCTIONS
# ==============================

def fetch_json():
    try:
        r = requests.get(JSON_URL, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ JSON fetch failed: {e}")
        return None

def fetch_m3u():
    try:
        r = requests.get(M3U_FALLBACK_URL, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"❌ M3U fetch failed: {e}")
        return None

# ==============================
# LOGO MAP (FROM JSON ONLY)
# ==============================

def build_logo_map(json_data):
    logo_map = {}
    for ch in json_data:
        name = ch.get("name", "").strip().lower()
        logo = ch.get("logo", "").strip()
        if name and logo:
            logo_map[name] = logo
    return logo_map

# ==============================
# EXISTING CATEGORY LOGIC (UNCHANGED)
# ==============================

def categorize_channels(channels):
    categories = defaultdict(list)

    for channel in channels:
        name = channel.get("name", "")
        name_lower = name.lower()

        if any(x in name_lower for x in ['sport', 'cricket', 'football', 'tennis', 'fifa', 'kabaddi', 'wwe']):
            category = 'Sports'
        elif any(x in name_lower for x in ['kids', 'cartoon', 'disney', 'hungama']):
            category = 'Kids'
        elif any(x in name_lower for x in ['movie', 'cinema', 'gold', 'max', 'flix']):
            category = 'Movies'
        elif any(x in name_lower for x in ['news', 'ndtv', 'aaj tak', 'republic']):
            category = 'News'
        elif any(x in name_lower for x in ['music', 'mtv', '9xm']):
            category = 'Music'
        elif any(x in name_lower for x in ['bhakti', 'aastha', 'sanskar']):
            category = 'Religious'
        else:
            category = 'Entertainment'

        categories[category].append(channel)

    return categories

# ==============================
# M3U CREATION (UNCHANGED + LOGO OVERRIDE)
# ==============================

def create_m3u_playlist(categories, logo_map):
    m3u = '#EXTM3U x-tvg-url="https://avkb.short.gy/jioepg.xml.gz"\n\n'

    streamflex = {
        "name": "StreamFlex+",
        "logo": "https://sflex07.fun/StreamFlexLogo.png",
        "link": "https://sflex07.fun/StreamFlexTG.ts"
    }

    for category, channels in categories.items():

        # ✅ StreamFlex+ (UNCHANGED)
        m3u += f'#EXTINF:-1 group-title="{category}" tvg-logo="{streamflex["logo"]}",{streamflex["name"]}\n'
        m3u += '#EXTVLCOPT:http-user-agent=StreamFlex/7.1.3 (Linux;Android 13)\n'
        m3u += f'{streamflex["link"]}\n\n'

        for ch in channels:
            name = ch.get("name", "")
            key = name.lower()
            logo = logo_map.get(key, ch.get("logo", ""))  # 🔑 override

            m3u += f'#EXTINF:-1 group-title="{category}" tvg-logo="{logo}",{name}\n'

            if ch.get("drmScheme") and ch.get("drmLicense"):
                m3u += f'#KODIPROP:inputstream.adaptive.license_type={ch["drmScheme"]}\n'
                m3u += f'#KODIPROP:inputstream.adaptive.license_key={ch["drmLicense"]}\n'

            m3u += '#EXTVLCOPT:http-user-agent=StreamFlex/7.1.3 (Linux;Android 13)\n'

            if ch.get("cookie"):
                m3u += f'#EXTVLCOPT:http-cookie={ch["cookie"]}\n'

            m3u += f'{ch["link"]}\n\n'

    return m3u

# ==============================
# MAIN
# ==============================

def main():
    print("🔄 Fetching JSON...")
    json_data = fetch_json()

    if json_data:
        logo_map = build_logo_map(json_data)
        categories = categorize_channels(json_data)
        m3u = create_m3u_playlist(categories, logo_map)

        with open("ZioGarmTara.m3u", "w", encoding="utf-8") as f:
            f.write(m3u)

        print("✅ Playlist generated from JSON (logos updated)")
        return

    print("⚠️ JSON failed → fallback M3U")
    fallback_m3u = fetch_m3u()
    if fallback_m3u:
        with open("ZioGarmTara.m3u", "w", encoding="utf-8") as f:
            f.write(fallback_m3u)
        print("✅ Fallback M3U saved")

if __name__ == "__main__":
    main()
