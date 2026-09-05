import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

from src.analyze_sources import AnalysisConfig, canonical_url, load_sources, normalize_text, representative_index, run_analysis


class AnalyzeSourcesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write_corpus(self, texts):
        rows = [{"id": f"S{i}", "url": f"https://example.test/{i}", "title": f"Article {i}",
                 "organisation": "Test fictif", "summary": text} for i, text in enumerate(texts)]
        path = self.root / "corpus.csv"
        pd.DataFrame(rows).to_csv(path, index=False)
        return path

    def test_normalization_accents_missing_and_urls(self):
        self.assertEqual(normalize_text("Écologie: https://example.com  été!!!"), "ecologie ete")
        self.assertEqual(normalize_text(float("nan")), "")
        self.assertEqual(normalize_text(None), "")

    def test_url_validation_and_fragment_deduplication(self):
        self.assertEqual(canonical_url(" https://EXAMPLE.test/a/#part "), "https://example.test/a")
        self.assertEqual(canonical_url("javascript:alert(1)"), "")
        self.assertEqual(canonical_url("https://user:pass@example.test"), "")

    def test_missing_columns(self):
        path = self.root / "missing.csv"
        path.write_text("id,title\n1,test\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Colonnes"):
            load_sources(path)

    def test_duplicate_urls_invalid_rows_and_missing_summary(self):
        path = self.write_corpus(["textile coton recyclage durable", "donnees consentement traceurs utilisateurs", "autre contenu de test"])
        df = pd.read_csv(path)
        df.loc[2, "url"] = df.loc[0, "url"] + "#ancre"
        df.to_csv(path, index=False)
        loaded = load_sources(path)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded.attrs["removed_rows"], 1)

    def test_duplicate_texts_rejected(self):
        path = self.write_corpus(["meme texte identique ici"] * 3)
        # Les chiffres des titres sont retires par le nettoyage.
        with self.assertRaisesRegex(ValueError, "Corpus trop petit"):
            run_analysis(AnalysisConfig(path, self.root / "out"))

    def test_one_document_rejected(self):
        path = self.write_corpus(["coton textile durable recyclage"])
        with self.assertRaisesRegex(ValueError, "Corpus trop petit"):
            run_analysis(AnalysisConfig(path, self.root / "out"))

    def test_two_documents_have_global_output(self):
        path = self.write_corpus(["textile coton recyclage durable", "donnees consentement traceurs utilisateurs"])
        result = run_analysis(AnalysisConfig(path, self.root / "out"))
        self.assertFalse(result["clustering_accepted"])
        self.assertIsNone(result["silhouette"])
        self.assertEqual(result["clusters"], 1)

    def test_empty_vocabulary(self):
        path = self.write_corpus(["le la les de", "avec pour sur dans"])
        df = pd.read_csv(path)
        df["title"] = ["la le", "de du"]
        df.to_csv(path, index=False)
        with self.assertRaisesRegex(ValueError, "Vocabulaire vide"):
            run_analysis(AnalysisConfig(path, self.root / "out"))

    def test_representative_is_nearest_not_first(self):
        matrix = csr_matrix([[10., 0.], [1., 0.], [2., 0.]])
        self.assertEqual(representative_index(matrix, np.array([0, 1, 2]), np.array([1.4, 0.])), 1)

    def test_clear_groups_and_reproducible_exports(self):
        path = self.write_corpus([
            "textile coton recyclage vetement tissu rouge",
            "textile coton recyclage vetement tissu vert",
            "textile coton recyclage vetement tissu jaune",
            "cookies consentement donnees traceurs navigateur choix",
            "cookies consentement donnees traceurs navigateur accord",
            "cookies consentement donnees traceurs navigateur refus"])
        first = run_analysis(AnalysisConfig(path, self.root / "out"))
        second = run_analysis(AnalysisConfig(path, self.root / "out2"))
        self.assertTrue(first["clustering_accepted"])
        self.assertEqual(first["clusters"], 2)
        self.assertEqual(first, second)
        for filename in ("sources_clustered.csv", "cluster_summary.csv", "metrics.json", "model_selection.csv", "similar_sources.csv"):
            self.assertEqual((self.root / "out" / filename).read_bytes(), (self.root / "out2" / filename).read_bytes())

    def test_human_tags_do_not_change_analysis(self):
        path = self.write_corpus(["textile coton recyclage durable", "donnees consentement traceurs utilisateurs"])
        first = load_sources(path)["analysis_text"].tolist()
        df = pd.read_csv(path)
        df["theme"] = ["donnees", "textile"]
        df["interest_for_watch"] = ["biais artificiel"] * 2
        df.to_csv(path, index=False)
        self.assertEqual(first, load_sources(path)["analysis_text"].tolist())


if __name__ == "__main__":
    unittest.main()
