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

STREAMFLEX_UA        = "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"
STREAMFLEX_WATERMARK = "StreamFlex"
STREAMFLEX_TG        = "@StreamFlex19"
DEFAULT_CATEGORY     = "Entertainment"

# ==============================
# CATEGORY ORDER
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
# (used only for sorting: Hindi first, regional after)
# ==============================

REGIONAL_KEYWORDS = [
    "bengali", "bangla", "kannada", "malayalam", "malyalam",
    "marathi", "tamil", "telugu", "punjabi", "gujarati",
    "bhojpuri", "rajasthani", "haryanvi", "nepali",
    "assamese", "maithili", "odia", "odiya", "oriya",
    "odisha", "tarang", "otv", "sambad", "kanak",
]

# ==============================
# PURE REGIONAL CHANNEL NAMES
# These land in "Other Languages" ONLY if no content keyword matches
# ==============================

PURE_REGIONAL_NAMES = [
    # Bengali
    "star jalsha", "zee bangla", "colors bangla", "sun bangla",
    "maach bhaat", "jalsha movies", "star jalsha hd",
    # Kannada
    "star suvarna", "zee kannada", "colors kannada", "udaya tv",
    "star suvarna hd", "zee kannada hd",
    # Malayalam
    "asianet", "surya tv", "mazhavil manorama", "flowers tv",
    "safari tv", "kairali tv", "media one", "reporter tv",
    "asianet hd", "surya tv hd",
    # Marathi
    "star pravah", "zee marathi", "colors marathi", "sony marathi",
    "fakt marathi", "star pravah hd",
    # Tamil
    "sun tv", "vijay tv", "zee tamil", "colors tamil", "star vijay",
    "kalaignar tv", "polimer tv", "jaya tv", "captain tv",
    "sun tv hd", "vijay tv hd",
    # Telugu
    "star maa", "zee telugu", "colors telugu", "etv telugu",
    "gemini tv", "maa gold", "star maa hd", "zee telugu hd",
    # Punjabi
    "ptc punjabi", "ptc news", "zee punjabi", "colors punjabi",
    # Gujarati
    "colors gujarati", "zee gujarati", "tv9 gujarati",
    # Bhojpuri
    "bhojpuri cinema", "mahua tv", "enter10 bhojpuri",
    # Urdu
    "zee salaam", "dd urdu", "ary digital", "geo tv",
]

# ==============================
# CONTENT CATEGORY MAP
# CHECKED FIRST — regional content channels stay in correct category
# ==============================

CONTENT_MAP = [

    # ---- Sports ----
    (["star sports", "sony six", "sony ten",
      "dd sports", "willow", "eurosport",
      "ten sports", "dsport", "1sports", "1 sports",
      "sports18", "sports 18", "jio sports",
      "fight sports", "kheloyar", "fancode",
      "cricket", "kabaddi", "wrestling"],               "Sports"),

    # ---- Movies ----
    (["zee cinema", "sony max", "star gold",
      "b4u movies", "zee bollywood", "zee action",
      "sony wah", "mm movies", "ultra movies",
      "star utsav movies", "colors cineplex",
      "&pictures", "& pictures",
      "maa movies", "gemini movies",
      "udaya movies", "kairali movies",
      "sun music", "cinemax", "zee classic",
      " movies", "movie "],                             "Movies"),

    # ---- Kids ----
    (["pogo", "disney junior", "disney channel",
      "disney xd", "hungama tv",
      "nickelodeon", "nick jr", "sonic ",
      "cartoon network", "baby tv",
      "cbeebies", "super hungama", "marvel hq",
      " kids", "junior "],                              "Kids"),

    # ---- News ----
    (["aaj tak", "ndtv 24x7", "ndtv india", "india tv",
      "zee news", "abp news", "abp live",
      "tv9 bharatvarsh", "news18 india",
      "republic bharat", "republic tv",
      "mirror now", "times now",
      "wion", "dd news", "dd national",
      "india news", " news"],                           "News"),

    # ---- Business News ----
    (["cnbc awaaz", "cnbc tv18", "zee business",
      "et now", "ndtv profit", "bloomberg"],            "Business News"),

    # ---- Music ----
    (["mtv india", "vh1", "b4u music",
      "9xm", "9x jalwa", "9x tashan",
      "9x jhakaas", "9x bindaas",
      "zee music", "sony mix", "mastiii",
      "ishq fm", " music"],                             "Music"),

    # ---- Devotional ----
    (["aastha", "sanskar", "sadhna tv",
      "ishwar tv", "divya tv", "god tv",
      "peace tv", "disha tv", "bhakti tv",
      "zee anmol", "mantra tv",
      "devotional", "spiritual"],                       "Devotional"),

    # ---- Lifestyle ----
    (["tlc", "fox life", "ndtv good times",
      "zee living", "living foodz",
      "food food", "travel xp",
      " lifestyle", "fashion tv"],                      "Lifestyle"),

    # ---- Infotainment ----
    (["zoom tv", "e! entertainment",
      "star world", "colors infinity",
      "& flix", "&flix", "infotainment"],               "Infotainment"),

    # ---- Knowledge ----
    (["nat geo", "national geographic",
      "discovery", "animal planet",
      "history tv18", "dd bharati",
      "curiosity", " knowledge"],                       "Knowledge"),

    # ---- Educational ----
    (["dd kisan", "swayam", "class plus",
      "educational", " education"],                     "Educational"),

    # ---- Shopping ----
    (["home shop 18", "naaptol", "star cj",
      "telebrand", "shop cj", " shopping"],             "Shopping"),

    # ---- English ----
    (["cnn", "bbc world", "fox news",
      "sky news", "hbo", "showtime",
      "comedy central", "abc news",
      "nbc news", " english"],                          "English"),

    # ---- Odia ----
    (["odia ", " odia", "odiya", "oriya",
      "tarang", "otv", "sambad",
      "kanak", "odisha tv", "ollywood"],                "Odia"),
]

# ==============================
# DETECT CATEGORY
# ==============================

def detect_category(ch):
    # Priority 1: JSON field
    cat = ch.get("category", "").strip()
    if cat:
        return cat

    name_lower = " " + ch.get("name", "").lower() + " "

    # Priority 2: Content keywords (checked FIRST)
    for keywords, category in CONTENT_MAP:
        for kw in keywords:
            if kw in name_lower:
                return category

    # Priority 3: Pure regional channel list
    name_clean = ch.get("name", "").lower().strip()
    for regional_name in PURE_REGIONAL_NAMES:
        if regional_name in name_clean:
            return "Other Languages"

    return DEFAULT_CATEGORY


# ==============================
# IS REGIONAL (for sorting within category)
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
# BUILD SINGLE CHANNEL ENTRY
# Proper format for: TiviMate | OTT Navigator | NS Player | VLC | Kodi
# ==============================

def build_channel_entry(ch, category):
    lines = []

    name        = ch.get("name", "Unknown").strip()
    logo        = ch.get("logo", "").strip()
    link        = ch.get("link", "").strip()
    cookie      = ch.get("cookie", "").strip()
    drm_scheme  = ch.get("drmScheme", "").strip()
    drm_license = ch.get("drmLicense", "").strip()

    if not link:
        return []

    is_mpd = ".mpd" in link.lower()
    is_m3u8 = ".m3u8" in link.lower() or ".ts" in link.lower()

    # --- EXTINF ---
    extinf = f'#EXTINF:-1 tvg-name="{name}"'
    if logo:
        extinf += f' tvg-logo="{logo}"'
    extinf += f' group-title="{category}",{name}'
    lines.append(extinf)

    # --- MPD (DASH) Stream handling ---
    if is_mpd:
        lines.append('#KODIPROP:inputstream=inputstream.adaptive')
        lines.append('#KODIPROP:inputstream.adaptive.manifest_type=mpd')

        if drm_scheme.lower() == "clearkey":
            lines.append('#KODIPROP:inputstream.adaptive.license_type=clearkey')
            lines.append(f'#KODIPROP:inputstream.adaptive.license_key={drm_license}')

        # Build piped URL with headers (works in TiviMate, OTT Nav, NS Player)
        header_parts = [f"User-Agent={requests.utils.quote(STREAMFLEX_UA)}"]
        if cookie:
            header_parts.append(f"Cookie={requests.utils.quote(cookie)}")

        final_link = link + "|" + "&".join(header_parts)

    # --- HLS / M3U8 / TS Stream handling ---
    elif is_m3u8:
        header_parts = [f"User-Agent={requests.utils.quote(STREAMFLEX_UA)}"]
        if cookie:
            header_parts.append(f"Cookie={requests.utils.quote(cookie)}")

        final_link = link + "|" + "&".join(header_parts)

    # --- Fallback (direct stream) ---
    else:
        lines.append(f'#EXTVLCOPT:http-user-agent={STREAMFLEX_UA}')
        if cookie:
            lines.append(f'#EXTVLCOPT:http-cookie={cookie}')
        final_link = link

    lines.append(final_link)
    lines.append("")
    return lines


# ==============================
# BUILD FULL M3U
# ==============================

def build_m3u(channels):
    header_lines = [
        "#EXTM3U",
        f"# Playlist  : ZioGarmTara",
        f"# Created by: {STREAMFLEX_WATERMARK}",
        f"# Telegram  : {STREAMFLEX_TG}",
        f"# Players   : TiviMate | OTT Navigator | NS Player | VLC | Kodi",
        "",
    ]

    grouped = group_by_category(channels)

    known   = [c for c in CATEGORY_ORDER if c in grouped]
    unknown = sorted([c for c in grouped if c not in CATEGORY_ORDER])
    sorted_cats = known + unknown

    body_lines = []
    total = 0

    for category in sorted_cats:
        raw_list = grouped[category]

        # Hindi first, regional after
        hindi_ch    = [ch for ch in raw_list if not is_regional(ch.get("name", ""))]
        regional_ch = [ch for ch in raw_list if     is_regional(ch.get("name", ""))]
        cat_channels = hindi_ch + regional_ch

        print(f"  📂 {category:<20} → {len(cat_channels):>3} ch  "
              f"(Hindi: {len(hindi_ch)}, Regional: {len(regional_ch)})")

        body_lines.append(f"# ===== {category.upper()} =====")
        body_lines.append("")

        for ch in cat_channels:
            entry = build_channel_entry(ch, category)
            if entry:
                body_lines.extend(entry)
                total += 1

    return "\n".join(header_lines + body_lines), total


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
    print(f"🛠  Building M3U (MPD+DRM fix, Hindi first, Regional after)...\n")

    m3u_content, total = build_m3u(channels)

    out_file = "ZioGarmTara.m3u"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"\n{'='*52}")
    print(f"✅  {out_file} created!")
    print(f"📺  Total channels  : {total}")
    print(f"🏷️   Watermark       : {STREAMFLEX_WATERMARK}")
    print(f"📱  Telegram        : {STREAMFLEX_TG}")
    print(f"📡  Players         : TiviMate | OTT Navigator | NS Player | VLC | Kodi")
    print(f"{'='*52}")

if __name__ == "__main__":
    main()
