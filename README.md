# 🐍 Python Automation Toolkit

**By GridGuard AI** — Four battle-tested automation scripts to eliminate repetitive work.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## What You Get

| Script | What It Does |
|---|---|
| **Web Scraper** | Configurable scraper with CSS selectors, pagination, rate limiting, CSV/JSON export |
| **File Organizer** | Sorts messy folders by file type or date — one command cleanup |
| **Email Templater** | Mail-merge engine: CSV data + template → personalized emails (preview mode) |
| **PDF Reporter** | Generates clean Markdown reports from CSV/JSON data — no heavy dependencies |

Each script is **standalone** — use one or all four. No complex setup, no accounts, no API keys.

---

## Quick Start

```bash
pip install -r requirements.txt
```

### 1. Web Scraper

Scrape any page using CSS selectors. Handles pagination, respects rate limits, exports to CSV or JSON.

```bash
# Scrape titles and links from a page
python -m toolkit.web_scraper \
  --url "https://news.ycombinator.com" \
  --selectors "title=.titleline>a::text" "link=.titleline>a::href" \
  --output results.csv

# With pagination (follows 'next' links up to 3 pages)
python -m toolkit.web_scraper \
  --url "https://example.com/listings" \
  --selectors "name=h2::text" "price=.price::text" \
  --pages 3 \
  --delay 2.0 \
  --output results.json
```

### 2. File Organizer

Point it at a messy folder. It sorts files into subfolders by type or by date.

```bash
# Organize by file type (Images/, Documents/, Videos/, etc.)
python -m toolkit.file_organizer --source ~/Downloads --mode type

# Organize by date (2026-03/, 2026-02/, etc.)
python -m toolkit.file_organizer --source ./dump --mode date

# Dry run — see what would happen without moving anything
python -m toolkit.file_organizer --source ~/Desktop --mode type --dry-run
```

### 3. Email Templater

Write a template, point it at a CSV, get personalized emails. Preview only — nothing is sent.

```bash
# Generate personalized emails from a CSV
python -m toolkit.email_templater \
  --template templates/welcome.txt \
  --data clients.csv \
  --output outbox/

# Preview first 3 emails to stdout
python -m toolkit.email_templater \
  --template templates/invoice.txt \
  --data billing.csv \
  --preview 3
```

**Template format** — use `{{column_name}}` placeholders:

```
Subject: Welcome aboard, {{first_name}}!

Hi {{first_name}},

Your account ({{email}}) is ready. Your plan: {{plan}}.

Best,
The Team
```

### 4. PDF Reporter

Turn CSV or JSON data into clean Markdown reports. Pipe to any Markdown-to-PDF tool or use as-is.

```bash
# Generate a report from CSV
python -m toolkit.pdf_reporter \
  --data sales_q1.csv \
  --title "Q1 Sales Report" \
  --output report.md

# From JSON with summary statistics
python -m toolkit.pdf_reporter \
  --data metrics.json \
  --title "Weekly Metrics" \
  --summary \
  --output weekly.md
```

---

## Use Cases

- **Freelancers**: Scrape leads, organize project files, send templated proposals
- **Small teams**: Generate weekly reports, clean shared drives, prep bulk emails
- **Developers**: Automate data collection, prototype pipelines, batch file ops
- **Students**: Research scraping, assignment organization, bulk email drafts

---

## Project Structure

```
python-automation-toolkit/
├── toolkit/
│   ├── __init__.py
│   ├── web_scraper.py
│   ├── file_organizer.py
│   ├── email_templater.py
│   └── pdf_reporter.py
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Requirements

- Python 3.9+
- Dependencies: `requests`, `beautifulsoup4` (installed via `pip install -r requirements.txt`)
- No API keys, no accounts, no external services

---

## License

MIT — use it in client projects, internal tools, or your own products. See [LICENSE](LICENSE).

---

**Built by [GridGuard AI](https://github.com/gridguard-ai)** — automation tools that actually work.
