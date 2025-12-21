import requests
import os
import re

# ==============================
# 🔐 SOURCES FROM GITHUB SECRETS
# ==============================

BASE_M3U_URL = os.environ.get("BASE_M3U_URL")
LOGO_JSON_URL = os.environ.get("LOGO_JSON_URL")

# ==============================
# STREAMFLEX USER AGENT
# ==============================

STREAMFLEX_UA = "StreamFlex/7.1.3 (Linux;Android 13) StreamFlex/69.1 ExoPlayerLib/824.0"

# ==============================
# PRIORITY CHANNEL KEYWORDS
# ==============================

PRIORITY_KEYS = [
    "star sports",
    "star plus",
    "star bharat",
    "colors",
    "rishtey",
    "disney",
    "hungama"
]

# ==============================
# FETCH FUNCTIONS
# ==============================

def fetch_base_m3u():
    r = requests.get(BASE_M3U_URL, timeout=30)
    r.raise_for_status()
    return r.text

def fetch_logo_json():
    try:
        r = requests.get(LOGO_JSON_URL, timeout=30)
        r.raise_for_status()
        return r.json()
    except:
        return []

# ==============================
# NORMALIZE NAME (LOGO MATCH)
# ==============================

def normalize(name: str) -> str:
    name = name.lower()
    name = re.sub(r'\b(hd|sd|tv|plus)\b', '', name)
    name = re.sub(r'[^a-z0-9 ]', '', name)
    return re.sub(r'\s+', ' ', name).strip()

# ==============================
# BUILD LOGO MAP
# ==============================

def build_logo_map(json_data):
    logo_map = {}
    for ch in json_data:
        name = ch.get("name", "")
        logo = ch.get("logo", "")
        if name and logo:
            logo_map[normalize(name)] = logo
    return logo_map

# ==============================
# APPLY LOGOS + UA FIX + PRIORITY
# ==============================

def process_m3u(base_m3u, logo_map):
    lines = base_m3u.splitlines()
    channels = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # ✅ FIX USER-AGENT (ygx → StreamFlex)
        if "user-agent" in line.lower():
            line = re.sub(
                r'(?i)user-agent=.*',
                f'#EXTVLCOPT:http-user-agent={STREAMFLEX_UA}',
                line
            )
            channels.append((False, line, None))
            i += 1
            continue

        if line.startswith("#EXTINF"):
            name = line.split(",")[-1].strip()
            url = lines[i + 1] if i + 1 < len(lines) else ""

            key = normalize(name)
            logo = logo_map.get(key)

            # remove old tvg-logo
            clean_line = re.sub(r'tvg-logo="[^"]*"', '', line)

            if logo:
                clean_line = clean_line.replace(
                    "#EXTINF:-1",
                    f'#EXTINF:-1 tvg-logo="{logo}"'
                )

            priority = any(k in key for k in PRIORITY_KEYS)

            channels.append((priority, clean_line, url))
            i += 2
        else:
            channels.append((False, line, None))
            i += 1

    # Priority channels on top
    channels.sort(key=lambda x: x[0], reverse=True)

    out = []
    for _, line, url in channels:
        out.append(line)
        if url:
            out.append(url)

    return "\n".join(out) + "\n"

# ==============================
# MAIN
# ==============================

def main():
    print("🔄 Fetching base M3U...")
    base_m3u = fetch_base_m3u()

    print("🔄 Fetching logo JSON...")
    json_data = fetch_logo_json()
    logo_map = build_logo_map(json_data)
    print(f"✅ Logos mapped: {len(logo_map)}")

    print("🛠 Applying logos + StreamFlex UA (ygx removed)...")
    final_m3u = process_m3u(base_m3u, logo_map)

    with open("ZioGarmTara.m3u", "w", encoding="utf-8") as f:
        f.write(final_m3u)

    print("✅ ZioGarmTara.m3u generated successfully")

if __name__ == "__main__":
    main()
