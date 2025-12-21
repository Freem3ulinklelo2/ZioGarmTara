import requests
from collections import defaultdict

# ==============================
# SOURCES
# ==============================

# Primary JSON source
JSON_URL = "https://jtv.pfy.workers.dev"

# Fallback M3U source (Direct use if JSON fails)
M3U_FALLBACK_URL = "https://raw.githubusercontent.com/alex8875/m3u/refs/heads/main/jtv.m3u"


# ==============================
# FETCH FUNCTIONS
# ==============================

def fetch_json():
    """JSON fetch karta hai"""
    try:
        response = requests.get(JSON_URL, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching JSON: {e}")
        return None


def fetch_m3u():
    """Fallback M3U fetch karta hai"""
    try:
        response = requests.get(M3U_FALLBACK_URL, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Error fetching M3U: {e}")
        return None


# ==============================
# CHANNEL CATEGORIZATION
# ==============================

def categorize_channels(channels):
    """Channels ko category wise arrange karta hai"""
    categories = defaultdict(list)

    for channel in channels:
        name = channel.get('name', 'Unknown')
        name_lower = name.lower()

        if any(x in name_lower for x in ['sport', 'cricket', 'football', 'tennis', 'fifa', 'espn', 'kabaddi', 'hockey', 'wwe', 'f1']):
            category = 'Sports'
        elif any(x in name_lower for x in ['kids', 'cartoon', 'pogo', 'nick', 'disney', 'hungama', 'sonic']):
            category = 'Kids'
        elif any(x in name_lower for x in ['movie', 'cinema', 'gold', 'max', 'flix', 'pictures']):
            category = 'Movies'
        elif any(x in name_lower for x in ['news', 'aaj tak', 'ndtv', 'abp', 'republic', 'times now', 'news18']):
            category = 'News'
        elif any(x in name_lower for x in ['music', 'mtv', '9xm', 'zoom', 'b4u']):
            category = 'Music'
        elif any(x in name_lower for x in ['bhakti', 'spiritual', 'aastha', 'sanskar']):
            category = 'Religious'
        elif any(x in name_lower for x in ['colors', 'zee', 'star', 'sony', 'sab', '&tv', 'rishtey']):
            category = 'Entertainment'
        else:
            category = 'Others'

        categories[category].append(channel)

    return categories


# ==============================
# M3U CREATION
# ==============================

def create_m3u_playlist(categories):
    """Universal IPTV compatible M3U banata hai"""
    m3u = '#EXTM3U x-tvg-url="https://avkb.short.gy/jioepg.xml.gz"\n\n'

    category_order = [
        'Entertainment', 'Movies', 'Sports',
        'Kids', 'News', 'Music', 'Religious', 'Others'
    ]

    streamflex_channel = {
        'name': 'StreamFlex+',
        'logo': 'https://sflex07.fun/StreamFlexLogo.png',
        'link': 'https://sflex07.fun/StreamFlexTG.ts'
    }

    for category in category_order:
        if category not in categories:
            continue

        # StreamFlex+ channel (top of every category)
        m3u += f'#EXTINF:-1 group-title="{category}" tvg-logo="{streamflex_channel["logo"]}",{streamflex_channel["name"]}\n'
        m3u += '#EXTVLCOPT:http-user-agent=StreamFlex/7.1.3 (Linux;Android 13)\n'
        m3u += f'{streamflex_channel["link"]}\n\n'

        for ch in categories[category]:
            name = ch.get('name', 'Unknown')
            logo = ch.get('logo', '')
            link = ch.get('link', '')
            cookie = ch.get('cookie', '')
            drm_scheme = ch.get('drmScheme', '')
            drm_license = ch.get('drmLicense', '')

            m3u += f'#EXTINF:-1 group-title="{category}" tvg-logo="{logo}",{name}\n'

            if drm_scheme and drm_license:
                m3u += f'#KODIPROP:inputstream.adaptive.license_type={drm_scheme}\n'
                m3u += f'#KODIPROP:inputstream.adaptive.license_key={drm_license}\n'
                m3u += f'#EXTVLCOPT:http-clearkey-license={drm_license}\n'

            m3u += '#EXTVLCOPT:http-user-agent=StreamFlex/7.1.3 (Linux;Android 13)\n'

            if cookie:
                cookie_clean = cookie.replace('"', '').strip()
                m3u += f'#EXTHTTP:{{"cookie":"{cookie_clean}"}}\n'
                m3u += f'#EXTVLCOPT:http-cookie={cookie_clean}\n'

            m3u += f'{link}\n\n'

    return m3u


# ==============================
# MAIN EXECUTION
# ==============================

def main():
    print("🔄 Fetching JSON source...")
    data = fetch_json()

    # CASE 1: JSON SUCCESS
    if data and isinstance(data, list) and len(data) > 0:
        print(f"✅ JSON loaded: {len(data)} channels")

        categories = categorize_channels(data)
        m3u_content = create_m3u_playlist(categories)

        with open('ZioGarmTara.m3u', 'w', encoding='utf-8') as f:
            f.write(m3u_content)

        print("✅ Playlist created from JSON")

    # CASE 2: JSON FAIL → DIRECT M3U
    else:
        print("⚠️ JSON failed, switching to DIRECT M3U MODE")

        fallback_m3u = fetch_m3u()
        if not fallback_m3u:
            print("❌ Both JSON and M3U failed")
            return

        with open('ZioGarmTara.m3u', 'w', encoding='utf-8') as f:
            f.write(fallback_m3u)

        print("✅ Playlist created from fallback M3U")

    print("🚀 Done! GitHub Action will commit automatically.")


if __name__ == "__main__":
    main()
