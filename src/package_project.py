from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'outputs/Projet_veille_marketing_responsable.zip'


def package():
    roots = ['src', 'tests', 'data', 'docs', 'analysis', 'config', 'outputs']
    files = [ROOT / name for name in ['README.md', 'requirements.txt', '.gitignore', '.gitattributes']]
    for name in roots:
        files.extend(path for path in (ROOT / name).rglob('*') if path.is_file()
                     and '__pycache__' not in path.parts and path.suffix not in {'.pyc', '.zip'})
    with ZipFile(OUTPUT, 'w', ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, path.relative_to(ROOT))
    print(f'{len(files)} fichiers: {OUTPUT}')


if __name__ == '__main__':
    package()
