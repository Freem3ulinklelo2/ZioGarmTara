import requests
import json
from collections import defaultdict

# JSON URL
JSON_URL = "https://jtv.pfy.workers.dev"

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
    """M3U playlist banata hai - Tivimate Compatible Format"""
    # M3U Header with EPG
    m3u_content = '#EXTM3U x-tvg-url="https://avkb.short.gy/jioepg.xml.gz"\n\n'
    
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
            
            # KODIPROP for DRM - MULTIPLE FORMATS FOR COMPATIBILITY
            if drm_scheme and drm_license:
                # Format 1: Standard KODIPROP (OTT Navigator, NS Player)
                m3u_content += f'#KODIPROP:inputstream.adaptive.license_type={drm_scheme}\n'
                m3u_content += f'#KODIPROP:inputstream.adaptive.license_key={drm_license}\n'
                
                # Format 2: EXTVLCOPT format (Tivimate Premium)
                m3u_content += f'#EXTVLCOPT:http-clearkey-license={drm_license}\n'
                
                # Format 3: Alternate property (Some players)
                m3u_content += f'#EXT-X-STREAM-INF:CLEARKEY={drm_license}\n'
            
            # User-Agent (proper JioTV format) - Multiple formats for compatibility
            m3u_content += '#EXTVLCOPT:http-user-agent=StreamFlex/7.1.3 (Linux;Android 13) StreamFlex/69.1 ExoPlayerLib/824.0\n'
            m3u_content += '#KODIPROP:inputstream.adaptive.stream_headers=User-Agent=StreamFlex/7.1.3 (Linux;Android 13) StreamFlex/69.1 ExoPlayerLib/824.0\n'
            
            # Cookie in multiple formats
            if cookie:
                cookie_clean = cookie.replace('"', '').strip()
                # Format 1: EXTHTTP (NS Player, OTT Navigator)
                m3u_content += f'#EXTHTTP:{{"cookie":"{cookie_clean}"}}\n'
                # Format 2: EXTVLCOPT (Tivimate)
                m3u_content += f'#EXTVLCOPT:http-cookie={cookie_clean}\n'
                # Format 3: KODIPROP header (Some players)
                m3u_content += f'#KODIPROP:inputstream.adaptive.stream_headers=Cookie={cookie_clean}\n'
            
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
    
    print("📝 Creating M3U playlist (Universal format for all IPTV players)...")
    m3u_content = create_m3u_playlist(categories)
    
    with open('ZioGarmTara.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    total_with_streamflex = len(data) + len(categories)
    
    print(f"✅ Playlist created: ZioGarmTara.m3u")
    print(f"📊 Total channels: {total_with_streamflex} ({len(data)} + {len(categories)} StreamFlex+)")
    print(f"📺 Format: Universal (Tivimate, OTT Navigator, NS Player compatible)")
    print(f"⭐ StreamFlex+ added at top of each category!")
    print("")
    print("✅ COMPATIBILITY IMPROVEMENTS:")
    print("   ✓ Multiple clearkey formats added")
    print("   ✓ Cookie headers in 3 different formats")
    print("   ✓ User-Agent in multiple property formats")
    print("   ✓ Works with: Tivimate, OTT Navigator, NS Player, VLC")
    print("")
    print("⚠️  TIVIMATE USERS:")
    print("   - Make sure 'External Player' is DISABLED")
    print("   - Enable 'Use system player for DRM content' in settings")
    print("   - Update to latest Tivimate version (4.8+)")
    print("")
    print("⚠️  NOTE: Clearkey licenses must be valid!")
    print("   Channels will play if JSON source has correct license keys.")

if __name__ == "__main__":
    main()
