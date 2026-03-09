import requests
import os
from collections import defaultdict

# ==============================
# 🔐 SOURCES FROM GITHUB SECRETS
# ==============================

LOGO_JSON_URL = os.environ.get("LOGO_JSON_URL")

# ==============================
# STREAMFLEX CONFIG
# ==============================

STREAMFLEX_UA = "StreamFlex/7.1.3 (Linux;Android 13) StreamFlex/69.1 ExoPlayerLib/824.0"
STREAMFLEX_WATERMARK = "StreamFlex"
STREAMFLEX_TG = "@StreamFlex19"
DEFAULT_CATEGORY = "Uncategorized"

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
# GROUP CHANNELS BY CATEGORY
# ==============================

def group_by_category(channels):
    grouped = defaultdict(list)
    for ch in channels:
        category = ch.get("category", "").strip() or DEFAULT_CATEGORY
        grouped[category].append(ch)
    return grouped

# ==============================
# BUILD M3U FROM JSON (CATEGORY-WISE)
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

    # Group channels by category
    grouped = group_by_category(channels)

    total = 0

    # Sort categories alphabetically (Uncategorized at end)
    sorted_categories = sorted(
        grouped.keys(),
        key=lambda x: (x == DEFAULT_CATEGORY, x.lower())
    )

    for category in sorted_categories:
        cat_channels = grouped[category]
        print(f"  📂 {category}: {len(cat_channels)} channels")

        lines.append(f"# ==================== {category.upper()} ====================")
        lines.append("")

        for ch in cat_channels:
            name       = ch.get("name", "Unknown").strip()
            logo       = ch.get("logo", "").strip()
            link       = ch.get("link", "").strip()
            cookie     = ch.get("cookie", "").strip()
            drm_scheme  = ch.get("drmScheme", "").strip()
            drm_license = ch.get("drmLicense", "").strip()

            if not link:
                continue

            # Build EXTINF line — group-title = category name
            extinf = f'#EXTINF:-1 tvg-name="{name}"'
            if logo:
                extinf += f' tvg-logo="{logo}"'
            extinf += f' group-title="{category}",{name}'
            lines.append(extinf)

            # User-Agent
            lines.append(f'#EXTVLCOPT:http-user-agent={STREAMFLEX_UA}')

            # Cookie
            if cookie:
                lines.append(f'#EXTVLCOPT:http-cookie={cookie}')

            # DRM
            if drm_scheme and drm_license:
                if drm_scheme.lower() == "clearkey":
                    lines.append(f'#KODIPROP:inputstream.adaptive.license_type=clearkey')
                    lines.append(f'#KODIPROP:inputstream.adaptive.license_key={drm_license}')
                    lines.append(f'#EXTVLCOPT:http-header=Authorization=Bearer {drm_license}')

            # Stream URL
            lines.append(link)
            lines.append("")
            total += 1

    return "\n".join(lines), total

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
    print(f"🛠  Building category-wise M3U with {STREAMFLEX_WATERMARK} branding...")
    print()

    m3u_content, total = build_m3u(channels)

    with open("ZioGarmTara.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print()
    print(f"✅ ZioGarmTara.m3u created successfully!")
    print(f"📺 Total channels added : {total}")
    print(f"🏷️  Watermark            : {STREAMFLEX_WATERMARK}")
    print(f"📱 Telegram             : {STREAMFLEX_TG}")

if __name__ == "__main__":
    main()
