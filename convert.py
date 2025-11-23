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
        # Channel name
        name = channel.get('name', 'Unknown')
        
        # Category detect
        name_lower = name.lower()
        
        if any(x in name_lower for x in ['sport', 'cricket', 'football', 'tennis', 'fifa', 'espn', 'euro']):
            category = 'Sports'
        elif any(x in name_lower for x in ['kids', 'cartoon', 'pogo', 'nick', 'disney', 'hungama']):
            category = 'Kids'
        elif any(x in name_lower for x in ['movie', 'cinema', 'gold', 'max', 'flix', 'pictures']):
            category = 'Movies'
        elif any(x in name_lower for x in ['news', 'aaj tak', 'ndtv', 'abp', 'india today', 'republic']):
            category = 'News'
        elif any(x in name_lower for x in ['music', 'mtv', '9xm', 'zoom']):
            category = 'Music'
        elif any(x in name_lower for x in ['bhakti', 'spiritual', 'religious', 'aastha']):
            category = 'Religious'
        elif any(x in name_lower for x in ['hd', 'plus', 'colors', 'zee', 'star', 'sony', 'sab']):
            category = 'Entertainment'
        else:
            category = 'Others'
        
        categories[category].append(channel)
    
    return categories

def create_m3u(categories):
    """M3U playlist banata hai with categories"""
    m3u_content = "#EXTM3U\n\n"
    
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
            
            # M3U format
            m3u_content += f'#EXTINF:-1 tvg-logo="{logo}" group-title="{category}",{name}\n'
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
    
    print("📝 Creating M3U playlist...")
    m3u_content = create_m3u(categories)
    
    # File save karo
    with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    print(f"✅ Playlist created: playlist.m3u")
    print(f"📊 Total channels: {len(data)}")

if __name__ == "__main__":
    main()
