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

STREAMFLEX_UA = "StreamFlex/7.1.3 (Linux;Android 13) StreamFlex/69.1 ExoPlayerLib/824.0"
STREAMFLEX_WATERMARK = "StreamFlex"
STREAMFLEX_TG = "@StreamFlex19"

# ==============================
# CATEGORIES & LANGUAGES DETECTION
# ==============================

CATEGORIES = {
    'Entertainment': ['colors', 'zee tv', 'sony', 'star plus', 'mtv', 'vh1', '9xm', 'zoom', 'et now', 'times now'],
    'Movies': ['hbo', 'sony max', 'star gold', 'zee cinema', '&pictures', 'movies now', 'romedy now', 'flix'],
    'Sports': ['star sports', 'sony ten', 'sony six', 'dd sports', 'euro sports', 'neo sports'],
    'News': ['aaj tak', 'abp', 'ndtv', 'cnn', 'bbc', 'republic', 'times now', 'india today', 'news18'],
    'Kids': ['cartoon', 'pogo', 'nick', 'disney', 'hungama', 'sonic', 'babytv'],
    'Music': ['mtv', 'vh1', '9xm', 'zoom', 'sony mix', 'mastiii'],
    'Devotional': ['aastha', 'sanskar', 'sadhna', 'divya'],
    'Regional': []
}

LANGUAGES = {
    'Hindi': ['hindi', 'colors', 'zee tv', 'sony', 'star plus', 'aaj tak', 'abp'],
    'English': ['english', 'hbo', 'cnn', 'bbc', 'sony pix', 'movies now'],
    'Tamil': ['tamil', 'sun tv', 'vijay', 'kalaignar', 'polimer', 'raj tv'],
    'Telugu': ['telugu', 'gemini', 'etv', 'maa tv', 'zee telugu'],
    'Malayalam': ['malayalam', 'asianet', 'surya', 'mazhavil'],
    'Kannada': ['kannada', 'udaya', 'zee kannada', 'colors kannada'],
    'Marathi': ['marathi', 'zee marathi', 'colors marathi', 'saam'],
    'Bengali': ['bengali', 'zee bangla', 'star jalsha', 'colors bangla'],
    'Punjabi': ['punjabi', 'zee punjabi', 'ptc', 'colors punjabi'],
    'Gujarati': ['gujarati', 'colors gujarati', 'etv gujarati'],
    'Urdu': ['urdu', 'geo', 'ary', 'hum', 'express']
}

def detect_category(name):
    name_lower = name.lower()
    for category, keywords in CATEGORIES.items():
        if any(keyword in name_lower for keyword in keywords):
            return category
    return 'Others'

def detect_language(name):
    name_lower = name.lower()
    for lang, keywords in LANGUAGES.items():
        if any(keyword in name_lower for keyword in keywords):
            return lang
    return 'Hindi'  # Default

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
    # Group by Category and Language
    categorized = defaultdict(lambda: defaultdict(list))
    
    for ch in channels:
        name = ch.get("name", "Unknown").strip()
        category = detect_category(name)
        language = detect_language(name)
        categorized[category][language].append(ch)
    
    lines = []
    
    # M3U Header
    lines.append("#EXTM3U")
    lines.append(f"# Playlist: ZioGarmTara")
    lines.append(f"# Created by: {STREAMFLEX_WATERMARK}")
    lines.append(f"# Telegram: {STREAMFLEX_TG}")
    lines.append(f"# Total Channels: {len(channels)}")
    lines.append(f"# Categories: Entertainment, Movies, Sports, News, Kids, Music, Devotional, Regional")
    lines.append(f"# Languages: Hindi, English, Tamil, Telugu, Malayalam, Kannada, Marathi, Bengali, Punjabi, Gujarati, Urdu")
    lines.append(f"# User-Agent: {STREAMFLEX_UA}")
    lines.append("")
    
    # Sort categories: Entertainment first, Others last
    sorted_categories = sorted(categorized.keys(), key=lambda x: (x == 'Others', x))
    
    for category in sorted_categories:
        lines.append(f"########## {category.upper()} ##########")
        lines.append("")
        
        # Sort languages: Hindi first, English second, others alphabetical
        sorted_langs = sorted(categorized[category].keys(), 
                            key=lambda x: (x not in ['Hindi', 'English'], 
                                         x != 'Hindi', 
                                         x != 'English', 
                                         x))
        
        for language in sorted_langs:
            lines.append(f"#### {language} ####")
            
            # Sort channels alphabetically
            sorted_channels = sorted(categorized[category][language], 
                                   key=lambda x: x.get('name', '').lower())
            
            for ch in sorted_channels:
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
                extinf += f' group-title="{category} | {language}",{name}'
                lines.append(extinf)
                
                # VLC Options
                lines.append(f'#EXTVLCOPT:http-user-agent={STREAMFLEX_UA}')
                
                if cookie:
                    lines.append(f'#EXTVLCOPT:http-cookie={cookie}')
                
                # DRM Headers
                if drm_scheme and drm_license:
                    if drm_scheme.lower() == "clearkey":
                        lines.append(f'#KODIPROP:inputstream.adaptive.license_type=clearkey')
                        lines.append(f'#KODIPROP:inputstream.adaptive.license_key={drm_license}')
                
                lines.append(link)
                lines.append("")
            
            lines.append("")  # Empty line after language group
    
    return "\n".join(lines)

# ==============================
# MAIN
# ==============================

def main():
    print(f"🔄 Fetching JSON data...")
    channels = fetch_json_data()
    
    if not channels:
        print("❌ No channels found!")
        return
    
    print(f"✅ Found {len(channels)} channels")
    print(f"🛠 Organizing by Categories & Languages...")
    
    m3u_content = build_m3u(channels)
    
    with open("ZioGarmTara.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"✅ ZioGarmTara.m3u created!")
    print(f"📺 Total: {len(channels)} channels")
    print(f"🏷️  Watermark: {STREAMFLEX_WATERMARK}")
    print(f"📱 Telegram: {STREAMFLEX_TG}")

if __name__ == "__main__":
    main()
