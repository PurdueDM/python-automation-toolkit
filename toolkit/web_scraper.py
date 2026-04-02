"""
Configurable Web Scraper — GridGuard AI Python Automation Toolkit

Scrapes web pages using CSS selectors with pagination support,
rate limiting, and CSV/JSON export.

Usage:
    python -m toolkit.web_scraper --url URL --selectors "name=selector" --output FILE
"""

import argparse
import csv
import json
import os
import sys
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

MAX_PAGES_LIMIT = 50


def parse_selector(raw):
    # type: (str) -> Tuple[str, str, str]
    """Parse 'name=selector::attr' into (name, css_selector, attribute).

    Supported formats:
        name=div.class          -> extracts text content
        name=div.class::text    -> extracts text content
        name=div.class::href    -> extracts href attribute
    """
    if "=" not in raw:
        raise ValueError("Selector must be 'name=css_selector', got: {}".format(raw))

    name, selector = raw.split("=", 1)
    name = name.strip()
    attr = "text"

    if "::" in selector:
        selector, attr = selector.rsplit("::", 1)

    return name, selector.strip(), attr.strip()


def find_next_page(soup, base_url, next_selector="a.morelink, a[rel='next']"):
    # type: (BeautifulSoup, str, str) -> Optional[str]
    """Try to find a 'next page' link."""
    link = soup.select_one(next_selector)
    if link and link.get("href"):
        return urljoin(base_url, link["href"])
    return None


def scrape(url, selectors, max_pages=1, delay=1.0, next_selector=None, headers=None):
    # type: (str, List[Tuple[str, str, str]], int, float, Optional[str], Optional[Dict]) -> List[Dict]
    """Scrape one or more pages, returning all rows."""
    headers = headers or DEFAULT_HEADERS
    all_rows = []  # type: List[Dict]
    current_url = url  # type: Optional[str]
    pages_scraped = 0
    max_pages = min(max_pages, MAX_PAGES_LIMIT)

    while current_url and pages_scraped < max_pages:
        print("[scraper] Page {}: {}".format(pages_scraped + 1, current_url))
        resp = requests.get(current_url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        columns = {}  # type: Dict[str, List[str]]

        for name, css_sel, attr in selectors:
            elements = soup.select(css_sel)
            values = []
            for el in elements:
                if attr == "text":
                    values.append(el.get_text(strip=True))
                else:
                    values.append(el.get(attr, ""))
            columns[name] = values

        max_rows = max((len(v) for v in columns.values()), default=0)
        for i in range(max_rows):
            row = {}
            for col_name in columns:
                row[col_name] = columns[col_name][i] if i < len(columns[col_name]) else ""
            all_rows.append(row)

        pages_scraped += 1

        if pages_scraped < max_pages:
            ns = next_selector or "a.morelink, a[rel='next']"
            current_url = find_next_page(soup, current_url, ns)
            if current_url:
                time.sleep(delay)
        else:
            current_url = None

    print("[scraper] Done -- {} rows from {} page(s)".format(len(all_rows), pages_scraped))
    return all_rows


def export_csv(rows, path):
    # type: (List[Dict], str) -> None
    if not rows:
        print("[scraper] No data to export.")
        return
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("[scraper] Saved {} rows to {}".format(len(rows), path))


def export_json(rows, path):
    # type: (List[Dict], str) -> None
    if not rows:
        print("[scraper] No data to export.")
        return
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print("[scraper] Saved {} rows to {}".format(len(rows), path))


def main():
    parser = argparse.ArgumentParser(
        description="Configurable web scraper with CSS selectors and CSV/JSON export."
    )
    parser.add_argument("--url", required=True, help="Target URL to scrape")
    parser.add_argument(
        "--selectors", nargs="+", required=True,
        help='Selectors as "name=css_selector::attr" (e.g. "title=h2::text")'
    )
    parser.add_argument("--output", default="output.csv", help="Output file (.csv or .json)")
    parser.add_argument("--pages", type=int, default=1, help="Max pages to scrape (default: 1)")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between pages in seconds")
    parser.add_argument("--next-selector", default=None, help="CSS selector for the 'next page' link")

    args = parser.parse_args()

    parsed = [parse_selector(s) for s in args.selectors]
    rows = scrape(args.url, parsed, max_pages=args.pages,
                  delay=args.delay, next_selector=args.next_selector)

    if args.output.endswith(".json"):
        export_json(rows, args.output)
    else:
        export_csv(rows, args.output)


if __name__ == "__main__":
    main()
