from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity

FRENCH_STOP_WORDS = sorted(set("""
a au aux avec ce ces cet cette dans de des du elle elles en et eux il ils je la le
les leur leurs lui ma mais me meme mes moi mon ne nos notre nous on ou par pas pour
qu que qui sa se ses son sur ta te tes toi ton tu un une vos votre vous est sont
etre ont avoir plus moins tout tous toute toutes comme aussi entre selon dont afin
ainsi partir notamment peut peuvent vers the of and in to for with from is are its
responsable responsables marketing communication publicite publicites source sources
guide document presente presentee propose pratiques enjeux
""".split()))
MIN_SILHOUETTE = 0.10  # Heuristique explicite, pas un seuil de validite scientifique.


@dataclass(frozen=True)
class AnalysisConfig:
    input_path: Path
    output_dir: Path
    random_state: int = 42


def normalize_text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value).lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"https?://\S+", " ", text)
    return re.sub(r"\s+", " ", re.sub(r"[^a-z\s]", " ", text)).strip()


def canonical_url(value: str) -> str:
    try:
        parts = urlsplit(value.strip())
        if parts.scheme not in {"http", "https"} or not parts.hostname:
            return ""
        if parts.username or parts.password:
            return ""
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(),
                           parts.path.rstrip("/"), parts.query, ""))
    except ValueError:
        return ""


def load_sources(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    required = {"id", "title", "organisation", "url", "summary"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes: {', '.join(sorted(missing))}")
    initial_count = len(df)
    df["url"] = df["url"].map(canonical_url)
    df = df[df["url"].ne("") & df["title"].str.strip().ne("")].copy()
    df = df.drop_duplicates("url")
    # Exclure les categories et annotations humaines pour ne pas dicter les groupes.
    df["analysis_text"] = (df["title"] + " " + df["summary"]).map(normalize_text)
    df = df[df["analysis_text"].str.split().str.len() >= 4]
    df = df.drop_duplicates("analysis_text").sort_values("id").reset_index(drop=True)
    if len(df) < 2:
        raise ValueError("Corpus trop petit: au moins deux textes distincts et valides sont requis.")
    if df["id"].eq("").any() or df["id"].duplicated().any():
        raise ValueError("Les identifiants doivent etre renseignes et uniques.")
    df.attrs["removed_rows"] = initial_count - len(df)
    return df


def representative_index(matrix, indices, center) -> int:
    distances = np.linalg.norm(matrix[indices].toarray() - center, axis=1)
    return int(indices[int(distances.argmin())])


def run_analysis(config: AnalysisConfig) -> dict:
    df = load_sources(config.input_path)
    removed = df.attrs["removed_rows"]
    vectorizer = TfidfVectorizer(stop_words=FRENCH_STOP_WORDS,
                                 ngram_range=(1, 2), max_df=1.0, sublinear_tf=True)
    try:
        matrix = vectorizer.fit_transform(df["analysis_text"])
    except ValueError as error:
        raise ValueError("Vocabulaire vide apres nettoyage et retrait des mots outils.") from error
    if (matrix.getnnz(axis=1) == 0).any():
        raise ValueError("Un document ne contient aucun terme exploitable apres nettoyage.")

    candidates, models = [], {}
    # Petit corpus: 2 a 5 groupes testes; au moins deux documents par groupe.
    for k in range(2, min(5, len(df) // 2) + 1):
        model = KMeans(n_clusters=k, random_state=config.random_state, n_init=20)
        labels = model.fit_predict(matrix)
        unique, counts = np.unique(labels, return_counts=True)
        score = float(silhouette_score(matrix, labels, metric="cosine")) if 1 < len(unique) < len(df) else None
        eligible = len(unique) == k and int(counts.min()) >= 2 and score is not None
        candidates.append({"k": k, "silhouette_cosine": score,
                           "min_cluster_size": int(counts.min()), "eligible": eligible})
        models[k] = model
    eligible = [row for row in candidates if row["eligible"]]
    best = max(eligible, key=lambda row: (row["silhouette_cosine"], -row["k"])) if eligible else None
    accepted = best is not None and best["silhouette_cosine"] >= MIN_SILHOUETTE
    if accepted:
        model = models[best["k"]]
        labels, centers = model.labels_, model.cluster_centers_
    else:
        labels = np.zeros(len(df), dtype=int)
        centers = np.asarray(matrix.mean(axis=0))
    df["cluster"] = labels
    terms = vectorizer.get_feature_names_out()
    rows = []
    for cluster_id in sorted(np.unique(labels)):
        indices = np.flatnonzero(labels == cluster_id)
        center = centers[cluster_id]
        representative = df.iloc[representative_index(matrix, indices, center)]
        top = [terms[i] for i in np.argsort(-center, kind="stable")[:8] if center[i] > 0]
        rows.append({"cluster": int(cluster_id), "documents": len(indices),
                     "top_terms": ", ".join(top), "source_ids": ", ".join(df.iloc[indices]["id"]),
                     "representative_id": representative["id"],
                     "representative_source": representative["title"],
                     "representative_url": representative["url"]})
    similarity = cosine_similarity(matrix)
    pairs = sorted(((float(similarity[i, j]), i, j) for i in range(len(df))
                    for j in range(i + 1, len(df))), reverse=True)[:5]
    neighbors = [{"id_a": df.iloc[i]["id"], "id_b": df.iloc[j]["id"],
                  "cosine_similarity": score} for score, i, j in pairs]
    result = {"documents": len(df), "removed_rows": removed, "clusters": len(rows),
              "clustering_accepted": bool(accepted),
              "best_candidate_k": best["k"] if best else None,
              "best_candidate_silhouette": best["silhouette_cosine"] if best else None,
              "silhouette": best["silhouette_cosine"] if accepted else None,
              "metric": "cosine", "acceptance_threshold": MIN_SILHOUETTE,
              "random_state": config.random_state, "analyzed_fields": ["title", "summary"]}
    output = config.output_dir
    output.mkdir(parents=True, exist_ok=True)
    df.to_csv(output / "sources_clustered.csv", index=False, encoding="utf-8")
    pd.DataFrame(rows).to_csv(output / "cluster_summary.csv", index=False, encoding="utf-8")
    pd.DataFrame(candidates, columns=["k", "silhouette_cosine", "min_cluster_size", "eligible"]).to_csv(output / "model_selection.csv", index=False)
    pd.DataFrame(neighbors).to_csv(output / "similar_sources.csv", index=False)
    (output / "metrics.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Resultats de l'analyse", "", f"Corpus: {len(df)} documents valides; {removed} lignes exclues.",
             "Textes analyses: titres et resumes rediges apres consultation. Les themes et annotations ne sont pas utilises.", "",
             "## Decision sur le regroupement", ""]
    lines.append(f"{len(rows)} groupes exploratoires retenus." if accepted else
                 "Aucune partition suffisamment convaincante selon la regle choisie. Un ensemble global est exporte; il ne constitue pas un theme decouvert.")
    lines += [f"Meilleur candidat admissible: {result['best_candidate_k']}; silhouette cosinus: {result['best_candidate_silhouette']}.",
              "Le seuil 0,10 est une heuristique explicite; la silhouette n'est ni une precision ni une preuve de validite metier.", ""]
    for row in rows:
        lines += [f"## Ensemble {row['cluster']} ({row['documents']} documents)",
                  f"Sources: {row['source_ids']}", f"Termes: {row['top_terms']}",
                  f"Document le plus proche du centroide: [{row['representative_id']} - {row['representative_source']}]({row['representative_url']})", ""]
    lines += ["## Rapprochements a examiner", ""]
    for row in neighbors:
        lines.append(f"- {row['id_a']} / {row['id_b']}: similarite cosinus {row['cosine_similarity']:.3f}.")
    lines += ["", "Utilite: reunir les documents voisins pour une lecture croisee et eviter de traiter plusieurs fois le meme sujet.",
              "Limites: petits textes reformules, selection non aleatoire, biais editorial, vocabulaire non lemmatise. Ni part de marche ni evolution temporelle ne sont mesurees."]
    (output / "insights.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyse TF-IDF et regroupement exploratoire prudent.")
    parser.add_argument("--input", default="data/sources.csv")
    parser.add_argument("--output-dir", default="analysis")
    args = parser.parse_args()
    try:
        print(json.dumps(run_analysis(AnalysisConfig(Path(args.input), Path(args.output_dir))), indent=2))
    except (ValueError, OSError, pd.errors.ParserError) as error:
        parser.exit(2, f"Erreur: {error}\n")
