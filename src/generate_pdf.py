from __future__ import annotations

import csv
import json
import re
from html import escape
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "RATTRAPAGE_M1TL_CHOUIKHA_Mohamed_Sadok.pdf"
STYLE = {
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=17, leading=21, spaceAfter=14, textColor=colors.HexColor("#193d38")),
    "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=13, leading=16, spaceAfter=9),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=10.7, leading=13, spaceBefore=9, spaceAfter=5),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.4, leading=12.5, spaceAfter=6),
    "small": ParagraphStyle("small", fontName="Helvetica", fontSize=8.2, leading=10.7, spaceAfter=7),
}


def as_pdf_link(url: str, label: str) -> str:
    return f'<link href="{escape(url, quote=True)}" color="#166e65"><u>{escape(label)}</u></link>'


def formatted(text: str, sources: dict) -> str:
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    for source_id, row in sources.items():
        text = re.sub(rf"\b{source_id}\b", lambda _: as_pdf_link(row["url"], source_id), text)
    return text


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#bac9c5"))
    canvas.line(1.6 * cm, 1.35 * cm, A4[0] - 1.6 * cm, 1.35 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(1.6 * cm, 0.95 * cm, "CHOUIKHA Mohamed Sadok | M1 Tech Lead | 05/09/2026")
    canvas.drawRightString(A4[0] - 1.6 * cm, 0.95 * cm, str(doc.page))
    canvas.restoreState()


def render(path: Path, story, title: str):
    SimpleDocTemplate(str(path), pagesize=A4, leftMargin=1.6 * cm, rightMargin=1.6 * cm,
                      topMargin=1.5 * cm, bottomMargin=1.8 * cm, title=title,
                      author="CHOUIKHA Mohamed Sadok").build(story, onFirstPage=footer, onLaterPages=footer)


def markdown_story(text: str, sources: dict):
    story = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line == "<!-- PAGEBREAK -->":
            story.append(PageBreak())
            continue
        style = "h1" if line.startswith("# ") else "h2" if line.startswith("## ") else "body"
        line = re.sub(r"^#{1,2} ", "", line)
        story.append(Paragraph(formatted(line, sources), STYLE[style]))
    return story


def build_pdf():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    work = ROOT / "work" / "pdf"
    work.mkdir(parents=True, exist_ok=True)
    sources = {row["id"]: row for row in csv.DictReader((ROOT / "data/sources.csv").open(encoding="utf-8"))}
    publication = json.loads((ROOT / "config/publication.json").read_text(encoding="utf-8"))
    metrics = json.loads((ROOT / "analysis/metrics.json").read_text(encoding="utf-8"))
    study_path = OUTPUT.parent / "Etude_de_marche.pdf"
    render(study_path, markdown_story((ROOT / "docs/etude_marche.md").read_text(encoding="utf-8"), sources),
           "Etude de marche - services de marketing responsable en France")
    pages = len(PdfReader(study_path).pages)
    if pages > 2:
        raise ValueError(f"L'etude depasse deux pages: {pages}. Corriger la mise en page.")
    ready = all(publication.get(k) for k in ("watch_url", "git_url", "study_url")) and publication.get("public_access_verified", False)
    story = [Paragraph("Mise en place d'une veille digitale pour le marketing responsable", STYLE["title"]),
             Paragraph("CHOUIKHA Mohamed Sadok<br/>Digital Campus - Mastère 1 Tech Lead", STYLE["body"]),
             Paragraph("Dossier de réalisation | 5 septembre 2026", STYLE["body"]),
             Spacer(1, 0.35 * cm),
             Paragraph("Livrable final" if ready else "VERSION À FINALISER - publication de la veille non vérifiée", STYLE["h2"]),
             Paragraph("Accès aux livrables", STYLE["h1"])]
    for key, label in (("watch_url", "Veille en ligne - collection Raindrop"), ("git_url", "Dépôt Git public - code, données, tests et résultats"), ("study_url", "Étude de marché - PDF de deux pages")):
        url = publication.get(key, "")
        text = as_pdf_link(url, label) if url else escape(label) + " : publication en attente."
        story.append(Paragraph(text, STYLE["body"]))
    story += [Spacer(1, 0.3 * cm), Paragraph("Démarche et résultats vérifiables", STYLE["h1"]),
              Paragraph(f"Recherche documentaire : {len(sources)} références documentées, issues de plus de cinq organismes. Les dates, types de documents et limites de lecture sont conservés dans le corpus.", STYLE["body"]),
              Paragraph("Veille : collection annotée préparée pour Raindrop, revue hebdomadaire et synthèse mensuelle. Collecte RSS distincte de la validation éditoriale et de l'analyse ML.", STYLE["body"]),
              Paragraph(f"Analyse : scikit-learn, TF-IDF et essais KMeans de 2 à 5 groupes. Meilleure silhouette cosinus : {metrics['best_candidate_silhouette']:.3f}. Aucune partition retenue au seuil de prudence choisi ; les rapprochements documentaires restent utiles à la lecture.", STYLE["body"]),
              Paragraph("Le dossier inclut l'étude sur les deux pages suivantes et une bibliographie cliquable. Le dépôt contient les commandes de reproduction, les tests et le journal de collecte.", STYLE["body"]),
              Paragraph("Correspondance avec le sujet", STYLE["h1"]),
              Paragraph("1. Recherche : corpus et bibliographie.<br/>2. Curation : collection Raindrop et procédure.<br/>3. ML : script, essais, métriques et tests.<br/>4. Marché : étude intégrée de deux pages.<br/>5. Livraison : PDF nommé et liens publics vérifiés après publication.", STYLE["body"])]
    render(work / "cover.pdf", story, "Dossier de veille")
    bibliography = [Paragraph("Bibliographie et traçabilité", STYLE["title"]),
                    Paragraph("Sources consultées le 05/09/2026. Cliquer sur le titre pour ouvrir la source. Les identifiants S01-S19 relient l'étude, le corpus et les résultats.", STYLE["body"])]
    for index, row in enumerate(sources.values()):
        if index == 10:
            bibliography.extend([PageBreak(), Paragraph("Bibliographie - suite", STYLE["title"])])
        date = row["publication_date"] or "date initiale non établie"
        bibliography.append(KeepTogether([Paragraph(f'<b>{row["id"]} | {escape(row["organisation"])}</b><br/>'
                                      + as_pdf_link(row["url"], row["title"])
                                      + f'<br/>{escape(date)}. {escape(row["date_basis"])}. {escape(row["verification_note"])}', STYLE["small"])]))
    render(work / "bibliography.pdf", bibliography, "Sources de la veille")
    writer = PdfWriter()
    for path in (work / "cover.pdf", study_path, work / "bibliography.pdf"):
        writer.append(path)
    # Renumeroter le dossier assemble; l'etude autonome conserve ses pages 1 et 2.
    from io import BytesIO
    from reportlab.pdfgen.canvas import Canvas
    for index, page in enumerate(writer.pages, start=1):
        buffer = BytesIO()
        canvas = Canvas(buffer, pagesize=A4)
        canvas.setFillColor(colors.white)
        canvas.rect(A4[0] - 3 * cm, 0.7 * cm, 2 * cm, 0.5 * cm, fill=1, stroke=0)
        canvas.setFillColor(colors.black)
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(A4[0] - 1.6 * cm, 0.95 * cm, f'{index} / {len(writer.pages)}')
        canvas.save()
        buffer.seek(0)
        page.merge_page(PdfReader(buffer).pages[0])
    writer.add_metadata({"/Title": "Mise en place d'une veille digitale pour le marketing responsable", "/Author": "CHOUIKHA Mohamed Sadok"})
    with OUTPUT.open("wb") as handle:
        writer.write(handle)
    print(json.dumps({"study_pages": pages, "dossier_pages": len(writer.pages), "ready_for_submission": bool(ready), "output": str(OUTPUT)}, ensure_ascii=False))


if __name__ == "__main__":
    build_pdf()
