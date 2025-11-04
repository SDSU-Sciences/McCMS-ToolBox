#!/usr/bin/env python3
"""
Crawl a site starting from one URL and export all (Reference Page, Text, Target URL)
into an Excel file. By default, crawls up to depth=2 on the same domain.

Usage:
  python crawl_links_to_excel.py https://example.com -o links.xlsx --depth 2 --max-pages 500 --all-domains
"""

import argparse
import time
from collections import deque
from urllib.parse import urljoin, urldefrag, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup


def normalize_link(base_url: str, href: str) -> str | None:
    """Make absolute URL, drop fragments, and filter out unwanted schemes."""
    if not href:
        return None
    href = href.strip()
    if href.startswith(("mailto:", "tel:", "javascript:", "data:")):
        return None
    # Join relative -> absolute
    abs_url = urljoin(base_url, href)
    # Remove fragment (#section)
    abs_url, _ = urldefrag(abs_url)
    return abs_url


def same_domain(u1: str, u2: str) -> bool:
    return urlparse(u1).netloc.lower() == urlparse(u2).netloc.lower()


def fetch_html(url: str, timeout: int = 20) -> str | None:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except requests.RequestException:
        return None


def extract_links_from_page(page_url: str, html: str) -> list[tuple[str, str]]:
    """Return list of (text, target_url) found on page_url."""
    soup = BeautifulSoup(html, "html.parser")
    results: list[tuple[str, str]] = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(separator=" ", strip=True)
        target = normalize_link(page_url, a["href"])
        if not target:
            continue
        if not text:
            # Optionally, try alt/title fallbacks:
            text = a.get("title", "").strip()
        if text:
            results.append((text, target))
    return results


def crawl(start_url: str, max_depth: int, max_pages: int, stay_on_domain: bool, delay: float):
    """
    BFS crawl up to max_depth (0 = just the start page).
    Returns a list of dict rows: {"Reference Page", "Text", "Target URL"}.
    """
    start_url = normalize_link(start_url, "") or start_url
    visited_pages: set[str] = set()
    queue = deque([(start_url, 0)])

    rows: list[dict] = []

    while queue and len(visited_pages) < max_pages:
        url, depth = queue.popleft()
        if url in visited_pages:
            continue
        if stay_on_domain and not same_domain(start_url, url):
            # Do not crawl off-domain pages
            continue

        html = fetch_html(url)
        visited_pages.add(url)

        if html is None:
            # Could not fetch page; continue
            continue

        # Extract links on this page (includes "tabs above" / nav menus)
        links = extract_links_from_page(url, html)
        for text, target in links:
            rows.append({
                "Reference Page": url,
                "Text": text,
                "Target URL": target
            })

        # Enqueue next-level pages (only http(s))
        if depth < max_depth:
            for _, target in links:
                if target.startswith(("http://", "https://")):
                    if not stay_on_domain or same_domain(start_url, target):
                        if target not in visited_pages:
                            queue.append((target, depth + 1))

        if delay > 0:
            time.sleep(delay)

    # Deduplicate exact rows and return
    df = pd.DataFrame(rows, columns=["Reference Page", "Text", "Target URL"])
    if not df.empty:
        df = df.drop_duplicates().reset_index(drop=True)
    return df


def main():
    parser = argparse.ArgumentParser(description="Crawl links and export to Excel.")
    parser.add_argument("url", help="Starting page URL (e.g., https://example.com)")
    parser.add_argument("-o", "--output", default="links.xlsx", help="Output Excel file")
    parser.add_argument("--depth", type=int, default=2, help="Crawl depth (0 = only the start page)")
    parser.add_argument("--max-pages", type=int, default=500, help="Max pages to visit")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay (seconds) between requests")
    parser.add_argument(
        "--all-domains",
        action="store_true",
        help="Allow crawling off the start domain (default: stay on same domain)"
    )
    args = parser.parse_args()

    df = crawl(
        start_url=args.url,
        max_depth=args.depth,
        max_pages=args.max_pages,
        stay_on_domain=(not args.all_domains),
        delay=args.delay,
    )

    # Requires: pip install pandas openpyxl requests beautifulsoup4
    df.to_excel(args.output, index=False)
    print(f"Visited up to {args.max_pages} pages, depth={args.depth}.")
    print(f"Saved {len(df)} rows to '{args.output}'.")


if __name__ == "__main__":
    main()
