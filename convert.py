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
DEFAULT_CATEGORY = "Entertainment"

# ==============================
# CATEGORY ORDER (as shown in app)
# ==============================

CATEGORY_ORDER = [
    "Entertainment",
    "Movies",
    "News",
    "Business News",
    "Sports",
    "Music",
    "Kids",
    "Devotional",
    "Lifestyle",
    "Infotainment",
    "Knowledge",
    "Educational",
    "Shopping",
    "English",
    "Odia",
    "Other Languages",
]

# ==============================
# KEYWORD → CATEGORY MAP
# ==============================

KEYWORD_MAP = [
    # --- Other Languages (regional) ---
    (["bengali", "bangla", " bd "],                     "Other Languages"),
    (["kannada"],                                        "Other Languages"),
    (["malayalam", "malyalam"],                          "Other Languages"),
    (["marathi"],                                        "Other Languages"),
    (["tamil"],                                          "Other Languages"),
    (["telugu"],                                         "Other Languages"),
    (["punjabi", "gujarati", "bhojpuri",
      "rajasthani", "haryanvi", "urdu",
      "nepali", "assamese", "maithili"],                 "Other Languages"),

    # --- English ---
    (["cnn", "bbc", "fox news", "nbc", "abc news",
      "sky news", "bloomberg", "cnbc",
      "nat geo", "national geographic",
      "discovery", "history tv", "animal planet",
      "hbo", "showtime", "comedy central",
      "cartoon network", "nickelodeon",
      "disney channel", " english"],                     "English"),

    # --- Sports ---
    (["sports", "sport", "cricket", "football",
      "ipl", "kabaddi", "wrestling",
      "star sports", "sony six", "sony ten",
      "dd sports", "willow", "eurosport"],               "Sports"),

    # --- Movies ---
    (["movies", "movie", "cinema", "films",
      "zee cinema", "sony max", "star gold",
      "b4u movies", "zee bollywood",
      "zee action", "sony wah", "mm movies",
      "ultra movies"],                                   "Movies"),

    # --- News ---
    (["news", "aaj tak", "ndtv", "india tv",
      "zee news", "abp", "tv9", "news18",
      "republic", "mirror now", "times now",
      "wion", "dd news"],                               "News"),

    # --- Business News ---
    (["cnbc awaaz", "cnbc tv18",
      "zee business", "et now",
      "business", "money control"],                     "Business News"),

    # --- Music ---
    (["music", "mtv", "vh1", "b4u music",
      "9xm", "9x jalwa", "zee music",
      "sony mix", "mastiii"],                           "Music"),

    # --- Kids ---
    (["kids", "junior", "pogo",
      "disney junior", "hungama", "sonic",
      "nick jr", "baby tv", "cartoon"],                 "Kids"),

    # --- Devotional ---
    (["devotional", "dharm", "aastha",
      "sanskar", "sadhna", "ishwar",
      "divya", "spiritual", "bhakti",
      "god tv", "mantra"],                              "Devotional"),

    # --- Lifestyle ---
    (["lifestyle", "fashion", "food",
      "travel", "living", "home",
      "health", "zee living", "tlc",
      "fox life", "ndtv good times"],                   "Lifestyle"),

    # --- Infotainment ---
    (["infotainment", "zoom tv", "e! ",
      "star world", "fx ", "studio"],                   "Infotainment"),

    # --- Knowledge ---
    (["knowledge", "nat geo wild",
      "discovery science", "dd bharati",
      "curiosity"],                                     "Knowledge"),

    # --- Educational ---
    (["educational", "education",
      "dd kisan", "dd urdu",
      "swayam", "class plus"],                          "Educational"),

    # --- Shopping ---
    (["shopping", "home shop",
      "naaptol", "star cj", "telebrand"],               "Shopping"),

    # --- Odia ---
    (["odia", "odiya", "oriya",
      "odisha", "tarang", "otv",
      "sambad", "kanak"],                               "Odia"),
]

# ==============================
# AUTO CATEGORY DETECTOR
# ==============================

def detect_category(ch):
    # Priority 1: explicit field in JSON
    cat = ch.get("category", "").strip()
    if cat:
        return cat

    name_lower = " " + ch.get("name", "").lower() + " "

    for keywords, category in KEYWORD_MAP:
        for kw in keywords:
            if kw in name_lower:
                return category

    return DEFAULT_CATEGORY

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
        category = detect_category(ch)
        grouped[category].append(ch)
    return grouped

# ==============================
# BUILD M3U (CATEGORY-WISE)
# Compatible: TiviMate, OTT Navigator, NS Player, VLC, Kodi
# ==============================

def build_m3u(channels):
    lines = []

    # M3U Header
    lines.append("#EXTM3U")
    lines.append(f"# Playlist  : ZioGarmTara")
    lines.append(f"# Created by: {STREAMFLEX_WATERMARK}")
    lines.append(f"# Telegram  : {STREAMFLEX_TG}")
    lines.append(f"# Players   : TiviMate | OTT Navigator | NS Player | VLC | Kodi")
    lines.append("")

    grouped = group_by_category(channels)

    # Respect CATEGORY_ORDER, append unknown ones alphabetically at end
    known   = [c for c in CATEGORY_ORDER if c in grouped]
    unknown = sorted([c for c in grouped if c not in CATEGORY_ORDER])
    sorted_cats = known + unknown

    total = 0

    for category in sorted_cats:
        cat_channels = grouped[category]
        print(f"  📂 {category:<20} → {len(cat_channels)} channels")

        lines.append(f"# ===== {category.upper()} =====")
        lines.append("")

        for ch in cat_channels:
            name        = ch.get("name", "Unknown").strip()
            logo        = ch.get("logo", "").strip()
            link        = ch.get("link", "").strip()
            cookie      = ch.get("cookie", "").strip()
            drm_scheme  = ch.get("drmScheme", "").strip()
            drm_license = ch.get("drmLicense", "").strip()

            if not link:
                continue

            # EXTINF line
            # group-title = category → creates folders in TiviMate / OTT Nav / NS Player
            extinf = f'#EXTINF:-1 tvg-name="{name}"'
            if logo:
                extinf += f' tvg-logo="{logo}"'
            extinf += f' group-title="{category}",{name}'
            lines.append(extinf)

            # User-Agent header (required by most Indian IPTV streams)
            lines.append(f'#EXTVLCOPT:http-user-agent={STREAMFLEX_UA}')

            # Cookie header
            if cookie:
                lines.append(f'#EXTVLCOPT:http-cookie={cookie}')

            # DRM — ClearKey
            if drm_scheme and drm_license:
                if drm_scheme.lower() == "clearkey":
                    lines.append(f'#KODIPROP:inputstream.adaptive.license_type=clearkey')
                    lines.append(f'#KODIPROP:inputstream.adaptive.license_key={drm_license}')
                    lines.append(f'#EXTVLCOPT:http-header=Authorization=Bearer {drm_license}')

            lines.append(link)
            lines.append("")
            total += 1

    return "\n".join(lines), total

# ==============================
# MAIN
# ==============================

def main():
    print(f"🔄 Fetching JSON from: {LOGO_JSON_URL}")
    channels = fetch_json_data()

    if not channels:
        print("❌ No channels found in JSON!")
        return

    print(f"✅ {len(channels)} channels fetched\n")
    print(f"🛠  Auto-detecting categories from channel names...\n")

    m3u_content, total = build_m3u(channels)

    out_file = "ZioGarmTara.m3u"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"\n{'='*45}")
    print(f"✅ {out_file} created successfully!")
    print(f"📺 Total channels  : {total}")
    print(f"🏷️  Watermark       : {STREAMFLEX_WATERMARK}")
    print(f"📱 Telegram        : {STREAMFLEX_TG}")
    print(f"📡 Players         : TiviMate | OTT Navigator | NS Player | VLC | Kodi")
    print(f"{'='*45}")

if __name__ == "__main__":
    main()
