import requests
import os
from collections import defaultdict

# ==============================
# 🔐 GITHUB SECRETS
# ==============================

LOGO_JSON_URL = os.environ.get("LOGO_JSON_URL")

# ==============================
# STREAMFLEX CONFIG
# ==============================

STREAMFLEX_UA      = "StreamFlex/7.1.3 (Linux;Android 13) StreamFlex/69.1 ExoPlayerLib/824.0"
STREAMFLEX_WATERMARK = "StreamFlex"
STREAMFLEX_TG      = "@StreamFlex19"
DEFAULT_CATEGORY   = "Entertainment"

# ==============================
# CATEGORY DISPLAY ORDER
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
# REGIONAL LANGUAGE KEYWORDS
# (used ONLY to sub-sort within a category — Hindi first, regional after)
# ==============================

REGIONAL_KEYWORDS = [
    "bengali", "bangla", "kannada", "malayalam", "malyalam",
    "marathi", "tamil", "telugu", "punjabi", "gujarati",
    "bhojpuri", "rajasthani", "haryanvi", "urdu", "nepali",
    "assamese", "maithili", "odia", "odiya", "oriya",
    "odisha", "tarang", "otv", "sambad", "kanak",
]

# ==============================
# CONTENT CATEGORY MAP
# NOTE: Checked FIRST — so "Star Sports Tamil" → Sports, NOT Other Languages
# ==============================

# Each entry: (keywords_list, category)
CONTENT_MAP = [

    # ---- Sports (checked FIRST — regional sports channels stay here) ----
    (["star sports", "sony six", "sony ten", "dd sports",
      "willow tv", "eurosport", "ten sports", "fight sports",
      "dsport", "1sports", "1 sports",
      "sports18", "sports 18", "jio sports",
      " sports", "sport ", "cricket", " ipl ",
      "kabaddi", "wrestling", "football tv",
      "kheloyar", "fancode"],                             "Sports"),

    # ---- Movies ----
    (["zee cinema", "sony max", "star gold", "b4u movies",
      "zee bollywood", "zee action", "sony wah", "mm movies",
      "ultra movies", "films", " movies", "movie ",
      "cinema ", "cinemax", "zee classic",
      "star utsav movies", "colors cineplex",
      "&pictures", "& pictures", "and pictures",
      "epic", "maa movies", "gemini movies",
      "udaya movies", "kairali movies",
      "mazhavil", "flowers"],                             "Movies"),

    # ---- Kids ----
    (["pogo", "disney junior", "disney channel", "disney xd",
      "hungama tv", "sonic nickelodeon", "nick jr",
      "cartoon network", "baby tv", "cbeebies",
      "super hungama", "marvel hq",
      " kids", "junior "],                               "Kids"),

    # ---- News ----
    (["aaj tak", "ndtv 24x7", "ndtv india", "india tv",
      "zee news", "abp news", "abp live", "tv9 bharatvarsh",
      "news18 india", "news18 ", "news 18",
      "republic bharat", "republic tv",
      "mirror now", "times now", "navbharat times",
      "wion", "dd news", "dd national",
      "india news", "samachar", " news"],                "News"),

    # ---- Business News ----
    (["cnbc awaaz", "cnbc tv18", "zee business",
      "et now", "ndtv profit", "business today",
      "money control", "bloomberg quint"],               "Business News"),

    # ---- Music ----
    (["mtv india", "vh1 india", "b4u music",
      "9xm", "9x jalwa", "9x tashan", "9x jhakaas",
      "zee music", "sony mix", "mastiii",
      "music india", "hits ", " hits",
      "ishq fm", "radio", " music"],                    "Music"),

    # ---- Devotional ----
    (["aastha", "sanskar tv", "sadhna tv", "ishwar tv",
      "divya tv", "god tv", "peace tv",
      "disha tv", "satsang", "bhakti tv",
      "zee anmol", "mantra tv",
      "devotional", "spiritual", "dharm"],              "Devotional"),

    # ---- Lifestyle ----
    (["tlc india", "fox life", "ndtv good times",
      "zee living", "living foodz", "food food",
      "enter10 talkies", "travel xp",
      "lifestyle ", " lifestyle",
      "fashion tv", " fashion"],                        "Lifestyle"),

    # ---- Infotainment ----
    (["zoom tv", "e! entertainment",
      "star world", "fx channel",
      "colors infinity", "& flix", "&flix",
      "studio ", "infotainment"],                       "Infotainment"),

    # ---- Knowledge ----
    (["nat geo wild", "national geographic",
      "discovery science", "discovery channel",
      "animal planet", "history tv18",
      "dd bharati", "curiosity stream",
      " knowledge"],                                    "Knowledge"),

    # ---- Educational ----
    (["dd kisan", "dd urdu", "dd retro",
      "swayam", "class plus", "byjus",
      "sharda", "educational", " education"],           "Educational"),

    # ---- Shopping ----
    (["home shop 18", "naaptol", "star cj alive",
      "telebrand", "shop cj", "news18 shoppping",
      " shopping", "shop "],                            "Shopping"),

    # ---- English (international) ----
    (["cnn international", "bbc world", "fox news",
      "sky news", "bloomberg tv", "cnbc world",
      "nat geo (english)", "discovery hd world",
      "hbo", "showtime", "comedy central",
      "nickelodeon (us)", "disney (us)",
      "abc news", "nbc news", " english"],              "English"),

    # ---- Odia ----
    (["odia ", " odia", "odiya", "oriya",
      "tarang tv", "otv ", " otv",
      "sambad", "kanak tv", "odisha tv",
      "prarthana", "ollywood"],                         "Odia"),

    # ---- Other Languages (checked LAST — only pure regional channels land here) ----
    (["bengali", "bangla", "kannada",
      "malayalam", "malyalam", "marathi",
      "tamil", "telugu", "punjabi",
      "gujarati", "bhojpuri", "rajasthani",
      "haryanvi", "urdu channel", "nepali",
      "assamese", "maithili"],                          "Other Languages"),
]

# ==============================
# DETECT CATEGORY
# ==============================

def detect_category(ch):
    # If JSON already has category, trust it
    cat = ch.get("category", "").strip()
    if cat:
        return cat

    name_lower = " " + ch.get("name", "").lower() + " "

    for keywords, category in CONTENT_MAP:
        for kw in keywords:
            if kw in name_lower:
                return category

    return DEFAULT_CATEGORY


# ==============================
# CHECK IF CHANNEL IS REGIONAL
# (Hindi = False → goes to top of category)
# (Regional language = True → goes below Hindi)
# ==============================

def is_regional(name):
    n = name.lower()
    return any(kw in n for kw in REGIONAL_KEYWORDS)


# ==============================
# FETCH JSON
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
# GROUP BY CATEGORY
# ==============================

def group_by_category(channels):
    grouped = defaultdict(list)
    for ch in channels:
        category = detect_category(ch)
        grouped[category].append(ch)
    return grouped


# ==============================
# BUILD M3U
# Compatible: TiviMate | OTT Navigator | NS Player | VLC | Kodi
# ==============================

def build_m3u(channels):
    lines = []

    lines.append("#EXTM3U")
    lines.append(f"# Playlist  : ZioGarmTara")
    lines.append(f"# Created by: {STREAMFLEX_WATERMARK}")
    lines.append(f"# Telegram  : {STREAMFLEX_TG}")
    lines.append(f"# Players   : TiviMate | OTT Navigator | NS Player | VLC | Kodi")
    lines.append("")

    grouped = group_by_category(channels)

    known   = [c for c in CATEGORY_ORDER if c in grouped]
    unknown = sorted([c for c in grouped if c not in CATEGORY_ORDER])
    sorted_cats = known + unknown

    total = 0

    for category in sorted_cats:
        raw_list = grouped[category]

        # --- Hindi first, regional after (stable sort) ---
        hindi_ch    = [ch for ch in raw_list if not is_regional(ch.get("name", ""))]
        regional_ch = [ch for ch in raw_list if     is_regional(ch.get("name", ""))]
        cat_channels = hindi_ch + regional_ch

        print(f"  📂 {category:<20} → {len(cat_channels):>3} ch  "
              f"(Hindi: {len(hindi_ch)}, Regional: {len(regional_ch)})")

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

            # group-title drives category folders in all players
            extinf = f'#EXTINF:-1 tvg-name="{name}"'
            if logo:
                extinf += f' tvg-logo="{logo}"'
            extinf += f' group-title="{category}",{name}'
            lines.append(extinf)

            # User-Agent (required for most streams)
            lines.append(f'#EXTVLCOPT:http-user-agent={STREAMFLEX_UA}')

            # Cookie
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
        print("❌ No channels found!")
        return

    print(f"✅ {len(channels)} channels fetched\n")
    print(f"🛠  Building category-wise M3U (Hindi first, Regional after)...\n")

    m3u_content, total = build_m3u(channels)

    out_file = "ZioGarmTara.m3u"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"\n{'='*50}")
    print(f"✅  {out_file} created!")
    print(f"📺  Total channels  : {total}")
    print(f"🏷️   Watermark       : {STREAMFLEX_WATERMARK}")
    print(f"📱  Telegram        : {STREAMFLEX_TG}")
    print(f"📡  Players         : TiviMate | OTT Navigator | NS Player | VLC | Kodi")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
