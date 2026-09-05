import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def export():
    rows = list(csv.DictReader((ROOT / 'data/sources.csv').open(encoding='utf-8')))
    target = ROOT / 'outputs/veille_raindrop.csv'
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['url', 'folder', 'title', 'note', 'tags', 'created'])
        writer.writeheader()
        for row in rows:
            note = (f"{row['organisation']} | Publication: {row['publication_date'] or 'non etablie'} | "
                    f"Consultation: {row['consultation_date']}\n{row['summary']}\n"
                    f"Interet: {row['interest_for_watch']}\n"
                    f"Portee: {row['consultation_scope']}\n{row['verification_note']}")
            writer.writerow({'url': row['url'], 'folder': 'Veille marketing responsable - M1 Tech Lead',
                             'title': f"{row['id']} - {row['title']}", 'note': note,
                             'tags': row['theme'], 'created': row['consultation_date']})
    print(f'{len(rows)} references exportees: {target}')


if __name__ == '__main__':
    export()
