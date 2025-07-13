import re
import requests
import xml.etree.ElementTree as ET
import pandas as pd

# ── CONFIG ───────────────────────────────────────────────────────────────────
ROBOTS_URL        = "https://jewelbox.co.in/robots.txt"
PRODUCT_SITEMAP   = "https://jewelbox.co.in/product-sitemap.xml"
OUTPUT_ALL        = "all_urls.xlsx"
OUTPUT_SKU        = "only_skus.xlsx"
SITEMAP_NS        = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
SKU_REGEX_PATTERN = r"^https://jewelbox\.co\.in/[a-z0-9-]+/$"


def discover_sitemaps(robots_txt: str) -> list[str]:
    """Return all sitemap URLs declared in robots.txt."""
    saps = []
    for line in robots_txt.splitlines():
        line = line.strip()
        if line.lower().startswith("sitemap:"):
            _, url = line.split(":", 1)
            saps.append(url.strip())
    return saps


def fetch_locs_from_sitemap(sitemap_url: str) -> list[str]:
    """Fetch a sitemap (URL or index) and return all <loc> URLs, recursing if needed."""
    resp = requests.get(sitemap_url, timeout=10)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    tag = root.tag.lower()
    locs = []

    # URL set: grab every <loc>
    if "urlset" in tag:
        for url in root.findall("sm:url", SITEMAP_NS):
            loc = url.find("sm:loc", SITEMAP_NS)
            if loc is not None and loc.text:
                locs.append(loc.text.strip())

    # Sitemap index: recurse into each child <loc>
    elif "sitemapindex" in tag:
        for sm in root.findall("sm:sitemap", SITEMAP_NS):
            loc = sm.find("sm:loc", SITEMAP_NS)
            if loc is not None and loc.text:
                locs.extend(fetch_locs_from_sitemap(loc.text.strip()))

    return locs


def main():
    # 1) Discover sitemaps
    robots = requests.get(ROBOTS_URL, timeout=10).text
    sitemap_urls = discover_sitemaps(robots)
    print(f"Found {len(sitemap_urls)} sitemaps in robots.txt")

    # 2) Fetch all URLs
    all_urls = []
    for sm in sitemap_urls:
        print(f"  → Parsing {sm}")
        try:
            urls = fetch_locs_from_sitemap(sm)
            print(f"    • {len(urls)} locs")
            all_urls.extend(urls)
        except Exception as e:
            print(f"    ⚠️  Failed parsing {sm}: {e}")

    # 3) Dedupe & report
    print(f"\nRaw URLs found:       {len(all_urls)}")
    unique_urls = sorted(set(all_urls))
    print(f"Unique URLs (dedup’d): {len(unique_urls)}\n")

    # 4) Cross-check product-sitemap.xml
    prod_urls = fetch_locs_from_sitemap(PRODUCT_SITEMAP)
    prod_set  = set(prod_urls)
    master_set = set(unique_urls)
    present   = master_set & prod_set
    missing   = prod_set - master_set
    print(f"Products in product-sitemap.xml:      {len(prod_urls)}")
    print(f"Product URLs present in master list:  {len(present)}")
    if missing:
        print("⚠️  Missing product URLs:")
        for u in sorted(missing):
            print("    ", u)
    else:
        print("✅ All product-sitemap URLs included\n")

    # 5) Filter only SKU‐style URLs
    sku_pattern = re.compile(SKU_REGEX_PATTERN)
    sku_urls = [u for u in unique_urls if sku_pattern.match(u)]
    print(f"URLs matching SKU pattern: {len(sku_urls)}\n")

    # 6) Export to Excel
    pd.DataFrame(unique_urls, columns=["URL"]).to_excel(OUTPUT_ALL, index=False)
    print(f"→ Wrote all URLs to       {OUTPUT_ALL}")
    pd.DataFrame(sku_urls, columns=["SKU_URL"]).to_excel(OUTPUT_SKU, index=False)
    print(f"→ Wrote only SKU-URLs to  {OUTPUT_SKU}")

    print("\n🎉 Done!")

if __name__ == "__main__":
    main()
