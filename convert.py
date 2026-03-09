import requests
import os
import re
from collections import defaultdict

# ==============================
# 🔐 SOURCES FROM GITHUB SECRETS
# ==============================

LOGO_JSON_URL = os.environ.get("LOGO_JSON_URL")

# ==============================
# STREAMFLEX CONFIG
# ==============================

STREAMFLEX_UA = "Exoplayer"
STREAMFLEX_WATERMARK = "StreamFlex"
STREAMFLEX_TG = "@StreamFlex19"

# ==============================
# CATEGORIES & LANGUAGES DETECTION
# ==============================

CATEGORIES = {
    'Entertainment': ['colors', 'zee tv', 'sony', 'star plus', 'mtv', 'vh1', '9xm', 'zoom'],
    'Movies': ['hbo', 'sony max', 'star gold', 'zee cinema', '&pictures', 'movies now'],
    'Sports': ['star sports', 'sony ten', 'sony six', 'dd sports', 'euro sports'],
    'News': ['aaj tak', 'abp', 'ndtv', 'cnn', 'bbc', 'republic', 'times now', 'india today'],
    'Kids': ['cartoon', 'pogo', 'nick', 'disney', 'hungama', 'sonic'],
    'Music': ['mtv', 'vh1', '9xm', 'zoom', 'sony mix', 'mastiii'],
    'Devotional': ['aastha', 'sanskar', 'sadhna', 'divya']
}

def detect_category(name):
    name_lower = name.lower()
    for category, keywords in CATEGORIES.items():
        if any(keyword in name_lower for keyword in keywords):
            return category
    return 'Entertainment'

# ==============================
# AUTO TVG-ID GENERATOR
# ==============================

def generate_tvg_id(name):
    tvg = name.lower()
    tvg = re.sub(r'[^a-z0-9]+', '', tvg)
    return tvg

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

    categorized = defaultdict(list)

    for ch in channels:
        name = ch.get("name", "Unknown").strip()
        category = detect_category(name)
        categorized[category].append(ch)

    lines = []

    # Header
    lines.append("#EXTM3U")
    lines.append(f"# Playlist: ZioGarmTara")
    lines.append(f"# Created by: {STREAMFLEX_WATERMARK}")
    lines.append(f"# Telegram: {STREAMFLEX_TG}")
    lines.append("")

    for category in sorted(categorized.keys()):

        for ch in categorized[category]:

            name = ch.get("name", "Unknown").strip()
            logo = ch.get("logo", "").strip()
            link = ch.get("link", "").strip()
            cookie = ch.get("cookie", "").strip()
            drm_scheme = ch.get("drmScheme", "").strip()
            drm_license = ch.get("drmLicense", "").strip()

            if not link:
                continue

            tvg_id = generate_tvg_id(name)

            extinf = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{name}"'

            if logo:
                extinf += f' tvg-logo="{logo}"'

            extinf += f' group-title="{category}",{name}'

            lines.append(extinf)

            if drm_scheme and drm_license:
                lines.append('#KODIPROP:inputstream.adaptive.license_type=clearkey')
                lines.append(f'#KODIPROP:inputstream.adaptive.license_key={drm_license}')

            lines.append(f'#EXTVLCOPT:http-user-agent={STREAMFLEX_UA}')

            if cookie:
                lines.append(f'#EXTHTTP:{{"cookie":"{cookie}"}}')

            lines.append(link)
            lines.append("")

    return "\n".join(lines)

# ==============================
# MAIN
# ==============================

def main():
    print("🔄 Fetching JSON data...")

    channels = fetch_json_data()

    if not channels:
        print("❌ No channels found!")
        return

    print(f"✅ Found {len(channels)} channels")

    m3u_content = build_m3u(channels)

    with open("ZioGarmTara.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print("✅ ZioGarmTara.m3u created!")

if __name__ == "__main__":
    main()
