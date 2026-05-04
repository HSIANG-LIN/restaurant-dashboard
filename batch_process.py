#!/usr/bin/env python3
"""
Restaurant Dashboard - 批次處理 pending 佇列
每天半夜 24:00 由 cron 觸發，將 pending 中的餐廳定位並加入 restaurants.json
"""
import json, os, time, urllib.request, urllib.parse, subprocess, sys

BASE_DIR = os.path.expanduser("~/workspace/hermes_project/restaurant-dashboard")
PENDING_FILE = os.path.join(BASE_DIR, "pending.json")
DATA_FILE = os.path.join(BASE_DIR, "restaurants.json")
ENV_FILE = os.path.expanduser("~/.hermes/.env")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def geocode(address):
    """Use Nominatim to geocode an address, return (lat, lng) or (None, None)"""
    url = "https://nominatim.openstreetmap.org/search?q=" + urllib.parse.quote(address) + "&format=json&limit=1"
    req = urllib.request.Request(url, headers={"User-Agent": "HermesRestaurantBot/1.0"})
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"  ⚠️  Geocode failed for '{address}': {e}")
    return None, None

def load_token():
    """Load GITHUB_TOKEN from .env file"""
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("GITHUB_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

def git_commit_and_push(token):
    """Commit and push changes to GitHub"""
    os.chdir(BASE_DIR)
    subprocess.run(["git", "add", "restaurants.json"], check=False)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
    if result.returncode == 0:
        print("  ℹ️  No new data to commit.")
        return True
    date_str = time.strftime("%m/%d", time.localtime())
    subprocess.run(["git", "commit", "-m", f"auto: 批次新增餐廳 ({date_str})"], check=False)
    push_url = f"https://{token}@github.com/HSIANG-LIN/restaurant-dashboard.git"
    result = subprocess.run(["git", "push", push_url, "master"], capture_output=True, text=True)
    if result.returncode == 0:
        print("  ✅  Pushed to GitHub successfully.")
        return True
    else:
        print(f"  ❌  Push failed: {result.stderr}")
        return False

def main():
    print(f"🕐 [{time.strftime('%Y-%m-%d %H:%M:%S')}] 開始批次處理 pending 佇列...")
    
    # Load pending
    try:
        pending = load_json(PENDING_FILE)
    except (FileNotFoundError, json.JSONDecodeError):
        print("  ℹ️  No pending file or empty. Done.")
        return
    
    entries = pending.get("pending", [])
    if not entries:
        print("  ℹ️  No pending entries. Done.")
        return
    
    print(f"  📥  {len(entries)} 個待處理餐廳")
    
    # Load existing data
    try:
        data = load_json(DATA_FILE)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"restaurants": []}
    
    existing_urls = {r.get("url") for r in data["restaurants"]}
    
    added = 0
    skipped = 0
    failed = []
    
    for entry in entries:
        url = entry.get("url", "")
        
        # Skip duplicates
        if url in existing_urls:
            print(f"  ⏭️  Skipping duplicate: {entry.get('name', url)}")
            skipped += 1
            continue
        
        name = entry.get("name", "未知")
        address = entry.get("address", "")
        notes = entry.get("notes", "")
        source_time = entry.get("captured_at", time.strftime("%Y-%m-%dT%H:%M:%S+08:00"))
        
        print(f"  🔍  {name}...", end=" ", flush=True)
        
        # Geocode
        if address:
            lat, lng = geocode(address)
            if lat is None:
                print(f"⚠️  Geocode failed, will try street-level")
                # Try street name only
                street_parts = address.split("號")[0] if "號" in address else address
                street_parts = "/".join(street_parts.split("/")[:-1]) if "/" in street_parts else street_parts
                lat, lng = geocode(street_parts)
                if lat is None:
                    # Extract city/district level
                    parts = address.split("區")
                    if len(parts) >= 2:
                        lat, lng = geocode(parts[0] + "區")
                    if lat is None:
                        print(f"❌  Cannot geocode {address}")
                        failed.append(name)
                        continue
        
        # Generate unique ID
        ts = int(time.time())
        entry_id = f"rest_{ts}"
        existing_ids = {r["id"] for r in data["restaurants"]}
        while entry_id in existing_ids:
            ts += 1
            entry_id = f"rest_{ts}"
        
        new_entry = {
            "id": entry_id,
            "name": name,
            "url": url,
            "address": address,
            "lat": round(lat, 4),
            "lng": round(lng, 4),
            "notes": notes,
            "added_at": source_time
        }
        
        data["restaurants"].append(new_entry)
        existing_urls.add(url)
        added += 1
        print(f"✅  ({lat:.4f}, {lng:.4f})")
    
    # Save updated data
    save_json(DATA_FILE, data)
    
    # Clear pending
    save_json(PENDING_FILE, {"pending": []})
    
    print(f"\n📊 結果: {added} 新增, {skipped} 跳過(重複), {len(failed)} 失敗")
    
    if added > 0:
        token = load_token()
        if token:
            git_commit_and_push(token)
        else:
            print("  ❌  GITHUB_TOKEN not found in .env, cannot push.")
    else:
        print("  ℹ️  Nothing to push.")

if __name__ == "__main__":
    main()
