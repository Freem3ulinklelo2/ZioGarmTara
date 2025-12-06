import requests
import json
from collections import defaultdict

# JSON URL
JSON_URL = "https://playify.pages.dev/Jiotv.json"

def fetch_json():
    """JSON ko fetch karta hai"""
    try:
        response = requests.get(JSON_URL, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching JSON: {e}")
        return None

def categorize_channels(channels):
    """Channels ko category wise organize karta hai"""
    categories = defaultdict(list)
    
    for channel in channels:
        name = channel.get('name', 'Unknown')
        name_lower = name.lower()
        
        if any(x in name_lower for x in ['sport', 'cricket', 'football', 'tennis', 'fifa', 'espn', 'euro', 'kabaddi', 'hockey', 'wwe', 'f1', 'moto', 'racing']):
            category = 'Sports'
        elif any(x in name_lower for x in ['kids', 'cartoon', 'pogo', 'nick', 'disney', 'hungama', 'sonic', 'discovery kids', 'junior']):
            category = 'Kids'
        elif any(x in name_lower for x in ['movie', 'cinema', 'gold', 'max', 'flix', 'pictures', 'film', 'action', 'classic', 'thriller']):
            category = 'Movies'
        elif any(x in name_lower for x in ['news', 'aaj tak', 'ndtv', 'abp', 'india today', 'republic', 'times now', 'news18', 'cnbc', 'zee news', 'tv9']):
            category = 'News'
        elif any(x in name_lower for x in ['music', 'mtv', '9xm', 'zoom', 'bindass', 'b4u', 'mastii']):
            category = 'Music'
        elif any(x in name_lower for x in ['bhakti', 'spiritual', 'religious', 'aastha', 'sanskar', 'vedic']):
            category = 'Religious'
        elif any(x in name_lower for x in ['hd', 'plus', 'colors', 'zee', 'star', 'sony', 'sab', '&tv', 'rishtey', 'utsav', 'life', 'dangal']):
            category = 'Entertainment'
        else:
            category = 'Others'
        
        categories[category].append(channel)
    
    return categories

def create_m3u_playlist(categories):
    """M3U playlist banata hai - Exact format matching"""
    # M3U Header with EPG
    m3u_content = '#EXTM3U\n'
    m3u_content += '#EXTM3U x-tvg-url="https://avkb.short.gy/jioepg.xml.gz"\n\n'
    
    category_order = ['Entertainment', 'Movies', 'Sports', 'Kids', 'News', 'Music', 'Religious', 'Others']
    
    # StreamFlex+ channel details
    streamflex_channel = {
        'name': 'StreamFlex+',
        'logo': 'https://sflex07.fun/StreamFlexLogo.png',
        'link': 'https://sflex07.fun/StreamFlexTG.ts'
    }
    
    for category in category_order:
        if category not in categories:
            continue
        
        # Pehle StreamFlex+ channel add karo har category mein
        m3u_content += f'#EXTINF:-1 group-title="{category}" tvg-logo="{streamflex_channel["logo"]}",{streamflex_channel["name"]}\n'
        m3u_content += '#EXTVLCOPT:http-user-agent=StreamFlex/7.1.3 (Linux;Android 13) StreamFlex/69.1 ExoPlayerLib/824.0\n'
        m3u_content += f'{streamflex_channel["link"]}\n\n'
        
        # Ab baaki channels add karo
        channels = categories[category]
        
        for channel in channels:
            name = channel.get('name', 'Unknown')
            logo = channel.get('logo', '')
            link = channel.get('link', '')
            cookie = channel.get('cookie', '')
            drm_scheme = channel.get('drmScheme', 'clearkey')
            drm_license = channel.get('drmLicense', '')
            
            # EXTINF line with metadata
            m3u_content += f'#EXTINF:-1 group-title="{category}" tvg-logo="{logo}",{name}\n'
            
            # KODIPROP for DRM
            if drm_scheme:
                m3u_content += f'#KODIPROP:inputstream.adaptive.license_type={drm_scheme}\n'
            
            # If DRM license URL available (though keys are not in JSON)
            if drm_license:
                m3u_content += f'#KODIPROP:inputstream.adaptive.license_key={drm_license}\n'
            
            # User-Agent (proper JioTV format)
            m3u_content += '#EXTVLCOPT:http-user-agent=StreamFlex/7.1.3 (Linux;Android 13) StreamFlex/69.1 ExoPlayerLib/824.0\n'
            
            # Cookie in EXTHTTP format
            if cookie:
                cookie_clean = cookie.replace('"', '').strip()
                m3u_content += f'#EXTHTTP:{{"cookie":"{cookie_clean}"}}\n'
            
            # Stream URL
            m3u_content += f'{link}\n\n'
    
    return m3u_content

def main():
    print("🔄 Fetching JSON data from Playify...")
    data = fetch_json()
    
    if not data:
        print("❌ Failed to fetch JSON")
        return
    
    print(f"✅ Found {len(data)} channels")
    
    print("📂 Categorizing channels...")
    categories = categorize_channels(data)
    
    for category, channels in sorted(categories.items()):
        print(f"   {category}: {len(channels)} channels (+1 StreamFlex+)")
    
    print("📝 Creating M3U playlist (JioTV format)...")
    m3u_content = create_m3u_playlist(categories)
    
    with open('ZioGarmTara.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    total_with_streamflex = len(data) + len(categories)
    
    print(f"✅ Playlist created: ZioGarmTara.m3u")
    print(f"📊 Total channels: {total_with_streamflex} ({len(data)} + {len(categories)} StreamFlex+)")
    print(f"📺 Format: JioTV compatible with DRM support")
    print(f"⭐ StreamFlex+ added at top of each category!")
    print("")
    print("⚠️  IMPORTANT NOTES:")
    print("   - EPG URL included for guide data")
    print("   - Cookies included from source JSON")
    print("   - DRM license URLs included (but not decryption keys)")
    print("   - Use Tivimate Pro or OTT Navigator for best results")
    print("")
    print("⚠️  NOTE: Actual ClearKey decryption keys are NOT in source JSON!")
    print("   Channels may not play without proper license keys.")

if __name__ == "__main__":
    main()
