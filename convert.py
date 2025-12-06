import requests
import json
from collections import defaultdict

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

def create_universal_m3u_playlist(categories):
    """
    Universal M3U playlist - Works in ALL players!
    - Tivimate Pro: ✅
    - OTT Navigator: ✅
    - NS Player: ✅
    - VLC: ✅
    - MX Player: ✅
    - Perfect Player: ✅
    - Kodi: ✅
    """
    
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
        
        # StreamFlex+ channel add karo har category mein
        m3u_content += f'#EXTINF:-1 tvg-id="streamflexplus" tvg-logo="{streamflex_channel["logo"]}" group-title="{category}",{streamflex_channel["name"]}\n'
        m3u_content += f'#EXTVLCOPT:http-user-agent=StreamFlex/7.1.3 (Linux;Android 13) StreamFlex/69.1 ExoPlayerLib/824.0\n'
        m3u_content += f'#EXTVLCOPT:http-referrer=https://sflex07.fun/\n'
        m3u_content += f'{streamflex_channel["link"]}\n\n'
        
        # Ab baaki channels add karo
        channels = categories[category]
        
        for channel in channels:
            name = channel.get('name', 'Unknown')
            logo = channel.get('logo', '')
            link = channel.get('link', '')
            cookie = channel.get('cookie', '')
            drm_scheme = channel.get('drmScheme', '')
            drm_license = channel.get('drmLicense', '')
            
            # Clean channel name
            name_clean = name.replace('|', '-').replace('&', 'and').strip()
            
            # Create safe tvg-id
            tvg_id = name_clean.lower().replace(' ', '_').replace('+', 'plus')
            
            # ═══════════════════════════════════════════════════════
            # HYBRID FORMAT - Multiple player compatibility
            # ═══════════════════════════════════════════════════════
            
            # EXTINF line with full metadata
            m3u_content += f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{name_clean}" tvg-logo="{logo}" group-title="{category}",{name_clean}\n'
            
            # ─────────────────────────────────────────────────────
            # KODIPROP tags (for Kodi + OTT Navigator)
            # ─────────────────────────────────────────────────────
            if drm_scheme:
                m3u_content += f'#KODIPROP:inputstream.adaptive.license_type={drm_scheme}\n'
            
            if drm_license:
                m3u_content += f'#KODIPROP:inputstream.adaptive.license_key={drm_license}\n'
            
            # For MPEG-DASH streams
            if '.mpd' in link or 'dash' in link.lower():
                m3u_content += '#KODIPROP:inputstream=inputstream.adaptive\n'
                m3u_content += '#KODIPROP:inputstream.adaptive.manifest_type=mpd\n'
            
            # ─────────────────────────────────────────────────────
            # EXTVLCOPT tags (for VLC, Tivimate, MX Player)
            # ─────────────────────────────────────────────────────
            
            # User-Agent - Multiple formats for compatibility
            m3u_content += '#EXTVLCOPT:http-user-agent=JioCinema/5.8.3 (Linux;Android 13) ExoPlayerLib/2.11.7\n'
            
            # Referrer
            m3u_content += '#EXTVLCOPT:http-referrer=https://www.jiocinema.com/\n'
            
            # Cookie handling - Multiple methods
            if cookie:
                cookie_clean = cookie.replace('"', '').strip()
                
                # Method 1: Standard header format (Tivimate, VLC)
                m3u_content += f'#EXTVLCOPT:http-header=Cookie: {cookie_clean}\n'
                
                # Method 2: KODIPROP format (for compatibility)
                m3u_content += f'#KODIPROP:inputstream.adaptive.stream_headers=Cookie={cookie_clean}\n'
            
            # ─────────────────────────────────────────────────────
            # EXTHTTP tags (for NS Player compatibility)
            # ─────────────────────────────────────────────────────
            if cookie:
                cookie_clean = cookie.replace('"', '').strip()
                m3u_content += f'#EXTHTTP:{{"cookie":"{cookie_clean}"}}\n'
            
            # ─────────────────────────────────────────────────────
            # Stream URL with pipe format (fallback method)
            # ─────────────────────────────────────────────────────
            
            # Build headers for pipe format (works in many players)
            headers = []
            headers.append('User-Agent=JioCinema/5.8.3 (Linux;Android 13) ExoPlayerLib/2.11.7')
            headers.append('Referer=https://www.jiocinema.com/')
            
            if cookie:
                cookie_clean = cookie.replace('"', '').strip()
                headers.append(f'Cookie={cookie_clean}')
            
            # Final URL with pipe headers
            headers_str = '&'.join(headers)
            final_url = f'{link}|{headers_str}'
            
            m3u_content += f'{final_url}\n\n'
    
    return m3u_content

def main():
    print("="*70)
    print("🚀 UNIVERSAL M3U PLAYLIST GENERATOR - ALL PLAYERS SUPPORTED!")
    print("="*70)
    print("\n🔄 Fetching JSON data from Playify...")
    
    data = fetch_json()
    
    if not data:
        print("❌ Failed to fetch JSON")
        return
    
    print(f"✅ Found {len(data)} channels")
    
    print("\n📂 Categorizing channels...")
    categories = categorize_channels(data)
    
    print("\n📊 Category Distribution:")
    total_streamflex = 0
    for category, channels in sorted(categories.items()):
        total_streamflex += 1
        print(f"   📺 {category}: {len(channels)} channels (+1 StreamFlex+)")
    
    print(f"\n🎯 Total with StreamFlex+: {len(data) + total_streamflex}")
    
    print("\n📝 Creating UNIVERSAL M3U playlist...")
    print("   ⏳ Adding hybrid compatibility layers...")
    
    m3u_content = create_universal_m3u_playlist(categories)
    
    # Save the playlist
    with open('ZioGarmTara.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    print("\n" + "="*70)
    print("✅ SUCCESS! Playlist created: ZioGarmTara.m3u")
    print("="*70)
    
    print("\n🎉 COMPATIBILITY STATUS:\n")
    print("   ✅ Tivimate Pro      - EXTVLCOPT headers + Pipe format")
    print("   ✅ OTT Navigator     - KODIPROP + EXTVLCOPT hybrid")
    print("   ✅ NS Player         - EXTHTTP + Pipe format")
    print("   ✅ VLC Player        - EXTVLCOPT headers")
    print("   ✅ MX Player         - Pipe format fallback")
    print("   ✅ Perfect Player    - Multiple header methods")
    print("   ✅ Kodi (+ Adaptive) - KODIPROP tags")
    print("   ✅ GSE Smart IPTV    - Universal format")
    
    print("\n📋 FEATURES INCLUDED:\n")
    print("   🔹 EPG Guide URL")
    print("   🔹 StreamFlex+ in every category")
    print("   🔹 DRM metadata (ClearKey/Widevine)")
    print("   🔹 Cookie authentication (3 formats)")
    print("   🔹 User-Agent headers")
    print("   🔹 Referrer headers")
    print("   🔹 Pipe format with headers")
    print("   🔹 KODIPROP for Kodi/OTT")
    print("   🔹 EXTHTTP for NS Player")
    
    print("\n⚙️  HOW TO USE:\n")
    print("   1. Upload ZioGarmTara.m3u to GitHub")
    print("   2. Use raw link in your IPTV player")
    print("   3. Player will auto-detect best format")
    print("   4. Enjoy all channels!")
    
    print("\n⚠️  IMPORTANT NOTES:\n")
    print("   🔸 Some channels need DRM keys (not in source)")
    print("   🔸 Cookies may expire over time")
    print("   🔸 NS Player & OTT Navigator = Best for DRM")
    print("   🔸 Tivimate may need manual User-Agent setting")
    print("   🔸 If channel doesn't work, try different player")
    
    print("\n💡 TROUBLESHOOTING:\n")
    print("   • Black screen → Try NS Player or OTT Navigator")
    print("   • Buffering → Enable hardware decoding")
    print("   • Auth error → Cookies expired, update JSON")
    print("   • No audio → Check player audio codec support")
    
    print("\n🌐 GitHub Link:")
    print("   https://raw.githubusercontent.com/Freem3ulinklelo2/ZioGarmTara/main/ZioGarmTara.m3u")
    
    print("\n" + "="*70)
    print("🎬 HAPPY STREAMING! All players supported now! 🎬")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
