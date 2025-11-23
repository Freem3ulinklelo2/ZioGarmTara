import requests
import json
from collections import defaultdict
import urllib.parse

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
        # Channel ka naam
        name = channel.get('name', 'Unknown')
        
        # Category detect karo naam se
        name_lower = name.lower()
        
        if any(x in name_lower for x in ['sport', 'cricket', 'football', 'tennis', 'fifa', 'espn', 'euro', 'kabaddi', 'hockey']):
            category = 'Sports'
        elif any(x in name_lower for x in ['kids', 'cartoon', 'pogo', 'nick', 'disney', 'hungama', 'sonic']):
            category = 'Kids'
        elif any(x in name_lower for x in ['movie', 'cinema', 'gold', 'max', 'flix', 'pictures', 'film']):
            category = 'Movies'
        elif any(x in name_lower for x in ['news', 'aaj tak', 'ndtv', 'abp', 'india today', 'republic', 'times now', 'news18']):
            category = 'News'
        elif any(x in name_lower for x in ['music', 'mtv', '9xm', 'zoom', 'bindass']):
            category = 'Music'
        elif any(x in name_lower for x in ['bhakti', 'spiritual', 'religious', 'aastha', 'sanskar']):
            category = 'Religious'
        elif any(x in name_lower for x in ['hd', 'plus', 'colors', 'zee', 'star', 'sony', 'sab', '&tv', 'rishtey', 'utsav']):
            category = 'Entertainment'
        else:
            category = 'Others'
        
        categories[category].append(channel)
    
    return categories

def create_m3u_with_cookies(categories):
    """M3U playlist banata hai with cookies and headers"""
    m3u_content = "#EXTM3U x-tvg-url=\"\"\n\n"
    
    # Category order
    category_order = ['Entertainment', 'Movies', 'Sports', 'Kids', 'News', 'Music', 'Religious', 'Others']
    
    for category in category_order:
        if category not in categories:
            continue
            
        channels = categories[category]
        
        # Category header
        m3u_content += f"# ===== {category.upper()} ({len(channels)} Channels) =====\n\n"
        
        for channel in channels:
            name = channel.get('name', 'Unknown')
            logo = channel.get('logo', '')
            link = channel.get('link', '')
            cookie = channel.get('cookie', '')
            drm_scheme = channel.get('drmScheme', '')
            drm_license = channel.get('drmLicense', '')
            
            # EXTINF line with all metadata
            extinf_parts = [f'#EXTINF:-1']
            
            # Add tvg-logo
            if logo:
                extinf_parts.append(f'tvg-logo="{logo}"')
            
            # Add group-title
            extinf_parts.append(f'group-title="{category}"')
            
            # Join all parts
            m3u_content += ' '.join(extinf_parts) + f',{name}\n'
            
            # Add cookies and headers as #EXTVLCOPT
            if cookie:
                # Clean cookie string
                cookie_clean = cookie.replace('"', '').strip()
                m3u_content += f'#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\n'
                m3u_content += f'#EXTVLCOPT:http-referrer=https://www.jiocinema.com/\n'
                m3u_content += f'#EXTVLCOPT:http-cookie={cookie_clean}\n'
            
            # Add DRM info as comment (for reference)
            if drm_scheme and drm_license:
                m3u_content += f'#EXTHTTP:{"drm-scheme":"{drm_scheme}","drm-license":"{drm_license}"}\n'
            
            # Add stream URL
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
    
    # Category count print karo
    for category, channels in sorted(categories.items()):
        print(f"   {category}: {len(channels)} channels")
    
    print("📝 Creating M3U playlist with cookies...")
    m3u_content = create_m3u_with_cookies(categories)
    
    # File save karo
    with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    print(f"✅ Playlist created: playlist.m3u")
    print(f"📊 Total channels: {len(data)}")
    print(f"🍪 Cookies included!")

if __name__ == "__main__":
    main()
