import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import re
import html
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

# JST (UTC+9)
JST = timezone(timedelta(hours=9))

FEEDS = [
    {
        "id": "tech",
        "name": "テクノロジー全般",
        "urls": [
            "https://b.hatena.ne.jp/entrylist/it.rss"
        ]
    },
    {
        "id": "ai",
        "name": "AI・機械学習",
        "urls": [
            "https://b.hatena.ne.jp/search/tag?q=AI&mode=rss",
            "https://b.hatena.ne.jp/search/tag?q=%E6%A9%9F%E6%A2%B0%E5%AD%A6%E7%BF%92&mode=rss",
            "https://b.hatena.ne.jp/search/tag?q=LLM&mode=rss",
            "https://b.hatena.ne.jp/search/tag?q=ChatGPT&mode=rss"
        ]
    },
    {
        "id": "programming",
        "name": "プログラミング",
        "urls": [
            "https://b.hatena.ne.jp/search/tag?q=%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%9F%E3%83%B3%E3%82%B0&mode=rss",
            "https://b.hatena.ne.jp/search/tag?q=Python&mode=rss",
            "https://b.hatena.ne.jp/search/tag?q=JavaScript&mode=rss",
            "https://b.hatena.ne.jp/search/tag?q=TypeScript&mode=rss",
            "https://b.hatena.ne.jp/search/tag?q=Rust&mode=rss",
            "https://b.hatena.ne.jp/search/tag?q=Go&mode=rss"
        ]
    }
]

def is_safe_url(url):
    """Validate if URL uses http or https schemes only"""
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https')
    except Exception:
        return False

def fetch_feed(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_rss(xml_bytes, category_id):
    if not xml_bytes:
        return []

    items = []
    try:
        root = ET.fromstring(xml_bytes)
        
        namespaces = {
            'rss': 'http://purl.org/rss/1.0/',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'hatena': 'http://www.hatena.ne.jp/info/xmlns#'
        }

        for item in root.findall('.//{http://purl.org/rss/1.0/}item'):
            title_elem = item.find('rss:title', namespaces)
            link_elem = item.find('rss:link', namespaces)
            desc_elem = item.find('rss:description', namespaces)
            date_elem = item.find('dc:date', namespaces)
            count_elem = item.find('hatena:bookmarkcount', namespaces)
            img_elem = item.find('hatena:imageurl', namespaces)

            title = title_elem.text if title_elem is not None and title_elem.text else ""
            link = link_elem.text if link_elem is not None and link_elem.text else ""
            desc = desc_elem.text if desc_elem is not None and desc_elem.text else ""
            date_str = date_elem.text if date_elem is not None and date_elem.text else ""
            img_url = img_elem.text if img_elem is not None and img_elem.text else ""
            
            # Security: Validate URL Scheme
            if not is_safe_url(link):
                continue

            bookmark_count = 0
            if count_elem is not None and count_elem.text:
                try:
                    bookmark_count = int(count_elem.text)
                except ValueError:
                    bookmark_count = 0

            desc_clean = re.sub(r'<[^<]+?>', '', desc)
            desc_clean = html.unescape(desc_clean).strip()

            domain = ""
            if link:
                match = re.search(r'https?://([^/]+)', link)
                if match:
                    domain = match.group(1)

            date_formatted = date_str
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00")).astimezone(JST)
                    date_formatted = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    pass

            items.append({
                "title": html.unescape(title).strip(),
                "link": link,
                "description": desc_clean,
                "raw_date": date_str,
                "date_formatted": date_formatted,
                "bookmark_count": bookmark_count,
                "image_url": img_url if is_safe_url(img_url) else "",
                "domain": domain,
                "category": category_id
            })
    except Exception as e:
        print(f"Error parsing XML for {category_id}: {e}")

    return items

def main():
    now_jst = datetime.now(JST)
    today_str = now_jst.strftime("%Y-%m-%d")
    
    print(f"Fetching Hatena Bookmark RSS at {now_jst.isoformat()}...")

    all_items_dict = {}
    category_items = {
        "all": [],
        "tech": [],
        "ai": [],
        "programming": []
    }

    for cat in FEEDS:
        cat_id = cat["id"]
        print(f"Fetching category: {cat['name']} ({cat_id})...")
        for url in cat["urls"]:
            xml_data = fetch_feed(url)
            items = parse_rss(xml_data, cat_id)
            print(f"  [{url}] -> {len(items)} items found.")

            for item in items:
                link = item["link"]
                if link not in all_items_dict:
                    all_items_dict[link] = {**item, "categories": [cat_id]}
                else:
                    if cat_id not in all_items_dict[link]["categories"]:
                        all_items_dict[link]["categories"].append(cat_id)

    unique_items = list(all_items_dict.values())
    unique_items.sort(key=lambda x: (x["bookmark_count"], x["raw_date"]), reverse=True)

    for item in unique_items:
        category_items["all"].append(item)
        for cat_id in item["categories"]:
            if cat_id in category_items:
                category_items[cat_id].append(item)

    data_payload = {
        "date": today_str,
        "updated_at": now_jst.strftime("%Y-%m-%d %H:%M:%S JST"),
        "total_count": len(unique_items),
        "items": unique_items,
        "categories": {
            "all_count": len(category_items["all"]),
            "tech_count": len(category_items["tech"]),
            "ai_count": len(category_items["ai"]),
            "programming_count": len(category_items["programming"])
        }
    }

    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "data")
    os.makedirs(output_dir, exist_ok=True)

    today_file = os.path.join(output_dir, f"{today_str}.json")
    with open(today_file, "w", encoding="utf-8") as f:
        json.dump(data_payload, f, ensure_ascii=False, indent=2)
    print(f"Saved: {today_file}")

    latest_file = os.path.join(output_dir, "latest.json")
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(data_payload, f, ensure_ascii=False, indent=2)
    print(f"Saved: {latest_file}")

    dates_file = os.path.join(output_dir, "dates.json")
    existing_dates = []
    if os.path.exists(dates_file):
        try:
            with open(dates_file, "r", encoding="utf-8") as f:
                existing_dates = json.load(f)
        except Exception:
            existing_dates = []

    if today_str not in existing_dates:
        existing_dates.append(today_str)
    
    existing_dates.sort(reverse=True)

    with open(dates_file, "w", encoding="utf-8") as f:
        json.dump(existing_dates, f, ensure_ascii=False, indent=2)
    print(f"Updated dates.json: {existing_dates}")

if __name__ == "__main__":
    main()
