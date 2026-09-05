import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from generate_pdf import build_pdf

ROOT = Path(__file__).resolve().parents[1]


def public_get(url):
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(request, timeout=20) as response:
        return response.url, response.read(2_000_000)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Finaliser apres publication et controle visuel de la collection.')
    parser.add_argument('--watch-url', required=True)
    parser.add_argument('--verified-in-browser', action='store_true',
                        help='Confirme avoir verifie les 19 references et annotations sans connexion.')
    args = parser.parse_args()
    host = urlsplit(args.watch_url).hostname or ''
    if not args.watch_url.startswith('https://') or not (host.endswith('.raindrop.page') or host in {'raindrop.io', 'app.raindrop.io'}):
        parser.error('Fournir une vraie URL HTTPS de collection Raindrop publique.')
    if not args.verified_in_browser:
        parser.error('Verifier la collection hors connexion, puis ajouter --verified-in-browser.')
    config_path = ROOT / 'config/publication.json'
    config = json.loads(config_path.read_text(encoding='utf-8'))
    for url in (args.watch_url, config['git_url'], config['study_url']):
        final_url, content = public_get(url)
        if '/login' in final_url or '/account/' in final_url:
            raise ValueError('Une URL redirige vers une connexion: ' + url)
    config['watch_url'] = args.watch_url
    config['public_access_verified'] = True
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    build_pdf()
