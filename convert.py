import requests
import os
import re

# ==============================
# 🔐 SOURCES FROM GITHUB SECRETS
# ==============================

BASE_M3U_URL = os.environ.get("BASE_M3U_URL")
LOGO_JSON_URL = os.environ.get("LOGO_JSON_URL")

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
# BUILD LOGO MAP (NAME → LOGO)
# ==============================

def build_logo_map(json_data):
    logo_map = {}
    for ch in json_data:
        name = ch.get("name", "").strip().lower()
        logo = ch.get("logo", "").strip()
        if name and logo:
            logo_map[name] = logo
    return logo_map

# ==============================
# APPLY LOGOS TO BASE M3U
# ==============================

def apply_logos(base_m3u, logo_map):
    out = []
    lines = base_m3u.splitlines()

    for line in lines:
        if line.startswith("#EXTINF"):
            # Channel name
            name = line.split(",")[-1].strip()
            key = name.lower()

            logo = logo_map.get(key)

            # Remove old tvg-logo if exists
            line = re.sub(r'tvg-logo="[^"]*"', '', line)

            # Add new logo if available
            if logo:
                if "tvg-logo" in line:
                    pass
                else:
                    line = line.replace("#EXTINF:-1", f'#EXTINF:-1 tvg-logo="{logo}"')

            out.append(line)
        else:
            out.append(line)

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

    print(f"✅ Logos loaded: {len(logo_map)}")

    print("🛠 Replacing logos in base M3U...")
    final_m3u = apply_logos(base_m3u, logo_map)

    with open("ZioGarmTara.m3u", "w", encoding="utf-8") as f:
        f.write(final_m3u)

    print("✅ ZioGarmTara.m3u created successfully")

if __name__ == "__main__":
    main()
