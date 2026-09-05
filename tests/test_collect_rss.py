import json
import tempfile
import unittest
from pathlib import Path

from src.collect_rss import collect, parse_feed

RSS = b'''<?xml version="1.0"?><rss version="2.0"><channel><title>Test fictif</title>
<item><title>Publicite responsable</title><link>https://example.test/article</link>
<description>Extrait artificiel pour les tests seulement.</description><pubDate>Mon, 01 Jun 2026 10:00:00 GMT</pubDate></item>
<item><title>Publicite future</title><link>https://example.test/future</link><pubDate>Fri, 01 Jan 2100 10:00:00 GMT</pubDate></item>
</channel></rss>'''


class CollectTests(unittest.TestCase):
    def test_parse_dates_and_exclude_future(self):
        rows = parse_feed(RSS, 'Test', 'https://example.test/rss', '2026-09-05')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['publication_date'], '2026-06-01')
        self.assertIn('hors corpus', rows[0]['review_status'])

    def test_reject_html(self):
        with self.assertRaises(ValueError):
            parse_feed(b'<html>Erreur serveur</html>', 'Test', 'https://example.test', '2026-09-05')

    def test_network_error_preserves_other_feeds_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            feeds = root / 'feeds.json'
            feeds.write_text(json.dumps([{'organisation': 'Test', 'url': url} for url in ['ok', 'ok2', 'bad']]))
            def fetch(url):
                if url == 'bad':
                    raise TimeoutError('test network timeout')
                return RSS
            report = collect(feeds, root / 'out', fetch)
            self.assertEqual(report['candidates'], 1)
            self.assertFalse(report['all_failed'])
            self.assertEqual(report['feeds'][-1]['status'], 'error')


if __name__ == '__main__':
    unittest.main()
