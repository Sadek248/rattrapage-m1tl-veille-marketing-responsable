from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

import feedparser

KEYWORDS = ('responsab', 'greenwash', 'influenc', 'publicit', 'cookie', 'traceur',
            'environn', 'consomm', 'donnee', 'sobriet', 'circul', 'textile',
            'sustainab', 'carbon', 'privacy', 'transparen', 'consent', 'clean room')
FIELDS = ['id', 'title', 'organisation', 'url', 'publication_date', 'consultation_date',
          'summary', 'text_type', 'review_status', 'feed_url']


def clean_html(value: str) -> str:
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', ' ', value))).strip()


def fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={'User-Agent': 'VeilleM1/1.0 (educational RSS reader)'})
    with urlopen(request, timeout=20) as response:
        data = response.read(3_000_001)
    if len(data) > 3_000_000:
        raise ValueError('Flux trop volumineux (limite 3 Mo).')
    return data


def parse_feed(data: bytes, organisation: str, feed_url: str, today: str) -> list[dict]:
    parsed = feedparser.parse(data)
    if not parsed.version:
        raise ValueError('La reponse ne contient pas de flux RSS/Atom reconnu.')
    rows = []
    for item in parsed.entries[:100]:
        title, link = clean_html(item.get('title', '')), item.get('link', '')
        excerpt = clean_html(item.get('summary', ''))
        search = unicodedata.normalize('NFKD', (title + ' ' + excerpt).lower())
        search = ''.join(c for c in search if not unicodedata.combining(c))
        # Filtre lexical de preselection, distinct du machine learning.
        if not title or not link.startswith(('https://', 'http://')) or not any(k in search for k in KEYWORDS):
            continue
        stamp = item.get('published_parsed') or item.get('updated_parsed')
        date = f'{stamp.tm_year:04d}-{stamp.tm_mon:02d}-{stamp.tm_mday:02d}' if stamp else ''
        if date and date > today:
            continue
        rows.append({'id': 'RSS-' + hashlib.sha256(link.encode()).hexdigest()[:12],
                     'title': title, 'organisation': organisation, 'url': link,
                     'publication_date': date, 'consultation_date': today,
                     'summary': ' '.join(excerpt.split()[:20]),
                     'text_type': 'Titre et extrait RSS (20 mots maximum)',
                     'review_status': 'A relire - hors corpus valide', 'feed_url': feed_url})
    return rows


def collect(config_path: Path, output: Path, fetcher=fetch_bytes) -> dict:
    feeds = json.loads(config_path.read_text(encoding='utf-8'))
    if not feeds:
        raise ValueError('Aucun flux configure.')
    today = datetime.now(timezone.utc).date().isoformat()
    rows, logs = [], []
    for feed in feeds:
        try:
            found = parse_feed(fetcher(feed['url']), feed['organisation'], feed['url'], today)
            rows.extend(found)
            logs.append({**feed, 'status': 'ok', 'candidates': len(found)})
        except Exception as error:
            logs.append({**feed, 'status': 'error', 'error': str(error)})
    unique = {row['url']: row for row in rows}
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'rss_candidates.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(unique.values())
    report = {'consultation_date': today, 'feeds': logs, 'candidates': len(unique),
              'all_failed': all(row['status'] == 'error' for row in logs)}
    (output / 'collection_log.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Collecte RSS sans cle API; preserve le corpus valide.')
    parser.add_argument('--feeds', default='data/feeds.json')
    parser.add_argument('--output-dir', default='data/collected')
    args = parser.parse_args()
    report = collect(Path(args.feeds), Path(args.output_dir))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(1 if report['all_failed'] else 0)
