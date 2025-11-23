import requests
import json
from collections import defaultdict

# JSON URL
JSON_URL = "https://playify.pages.dev/Ziotv.json"

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
        
        if any(x in name_lower for x in ['sport', 'cricket', 'football', 'tennis', 'fifa', 'espn', 'euro', 'kabaddi', 'hockey', 'wwe', 'f1', 'moto']):
            category = 'Sports'
        elif any(x in name_lower for x in ['kids', 'cartoon', 'pogo', 'nick', 'disney', 'hungama', 'sonic', 'discovery kids']):
            category = 'Kids'
        elif any(x in name_lower for x in ['movie', 'cinema', 'gold', 'max', 'flix', 'pictures', 'film', 'action', 'classic']):
            category = 'Movies'
        elif any(x in name_lower for x in ['news', 'aaj tak', 'ndtv', 'abp', 'india today', 'republic', 'times now', 'news18', 'cnbc', 'zee news']):
            category = 'News'
        elif any(x in name_lower for x in ['music', 'mtv', '9xm', 'zoom', 'bindass', 'b4u']):
            category = 'Music'
        elif any(x in name_lower for x in ['bhakti', 'spiritual', 'religious', 'aastha', 'sanskar']):
            category = 'Religious'
        elif any(x in name_lower for x in ['hd', 'plus', 'colors', 'zee', 'star', 'sony', 'sab', '&tv', 'rishtey', 'utsav', 'life ok']):
            category = 'Entertainment'
        else:
            category = 'Others'
        
        categories[category].append(channel)
    
    return categories

def create_m3u_playlist(categories):
    """M3U playlist banata hai - Tivimate/OTT Navigator compatible"""
    m3u_content = '#EXTM3U x-tvg-url=""\n\n'
    
    category_order = ['Entertainment', 'Movies', 'Sports', 'Kids', 'News', 'Music', 'Religious', 'Others']
    
    for category in category_order:
        if category not in categories:
            continue
            
        channels = categories[category]
        m3u_content += f"# ===== {category.upper()} ({len(channels)} Channels) =====\n\n"
        
        for channel in channels:
            name = channel.get('name', 'Unknown')
            logo = channel.get('logo', '')
            link = channel.get('link', '')
            cookie = channel.get('cookie', '')
            drm_scheme = channel.get('drmScheme', '')
            drm_license = channel.get('drmLicense', '')
            
            # Basic EXTINF line
            m3u_content += f'#EXTINF:-1 tvg-logo="{logo}" group-title="{category}",{name}\n'
            
            # Add HTTP headers for compatible players
            if cookie:
                cookie_clean = cookie.replace('"', '').strip()
                m3u_content += f'#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36\n'
                m3u_content += f'#EXTVLCOPT:http-cookie={cookie_clean}\n'
            
            # Add Kodiprop for Kodi users (alternative format)
            if cookie:
                cookie_clean = cookie.replace('"', '').strip()
                m3u_content += f'#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
                m3u_content += f'#KODIPROP:inputstream.adaptive.stream_headers=Cookie={cookie_clean}\n'
            
            # Add DRM info as metadata (for reference)
            if drm_scheme:
                m3u_content += f'#EXTGRP:{category}\n'
            
            # Stream URL
            m3u_content += f'{link}\n\n'
    
    return m3u_content

def main():
    print("🔄 Fetching JSON data...")
    data = fetch_json()
    
    if not data:
        print("❌ Failed to fetch JSON")
        return
    
    print(f"✅ Found {len(data)} channels")
    
    print("📂 Categorizing channels...")
    categories = categorize_channels(data)
    
    for category, channels in sorted(categories.items()):
        print(f"   {category}: {len(channels)} channels")
    
    print("📝 Creating M3U playlist...")
    m3u_content = create_m3u_playlist(categories)
    
    with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    print(f"✅ Playlist created: playlist.m3u")
    print(f"📊 Total channels: {len(data)}")
    print(f"🍪 Cookies and headers included!")
    print("")
    print("⚠️  IMPORTANT:")
    print("   These streams require DRM support.")
    print("   Use: Tivimate Pro, OTT Navigator, or IPTV Smarters Pro")

if __name__ == "__main__":
    main()
