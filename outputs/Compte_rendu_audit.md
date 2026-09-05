# Compte rendu d'audit - 5 septembre 2026

## Conclusion

Le projet répond aux exigences de recherche, de code, de machine learning, d'étude de marché et de dépôt Git public. La livraison n'est pas encore complète : la collection Raindrop n'a pas été créée et vérifiée publiquement. Le PDF conserve donc une mention de version à finaliser.

## Vérifications exécutées

| Contrôle | Résultat |
|---|---|
| Nom du PDF comparé au sujet photographié | Conforme : `RATTRAPAGE_M1TL_CHOUIKHA_Mohamed_Sadok.pdf` |
| Corpus | 19 références, plus de 5 organismes, métadonnées et limites de lecture |
| Dates sensibles | ARPP corrigé au 02/10/2024 ; directive 2024/825 et procédure Green Claims distinguées |
| Analyse ML | TF-IDF ; KMeans testé de 2 à 5 groupes ; meilleure silhouette cosinus 0,042 |
| Interprétation ML | Aucune partition retenue sous le seuil heuristique 0,10 ; pas de fausse précision |
| Tests | 14 tests unitaires réussis |
| Collecte RSS | Flux IAB Tech Lab lu ; un candidat séparé du corpus validé |
| Étude de marché | 2 pages exactement |
| Dossier PDF | 5 pages : accès, étude de 2 pages, bibliographie |
| Contrôle visuel PDF | Pages rendues en PNG et relues ; pas de chevauchement ou texte coupé constaté |
| Dépôt GitHub | Public et consultable sans connexion |
| Recherche de secrets | Aucun motif de jeton ou clé privée détecté dans les fichiers texte suivis |
| Veille en ligne | Fichier d'import Raindrop prêt ; collection publique non créée |

## Commandes de reproduction

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe src\collect_rss.py
.\.venv\Scripts\python.exe src\analyze_sources.py
.\.venv\Scripts\python.exe src\export_curation.py
.\.venv\Scripts\python.exe src\generate_pdf.py
```

## Barème et état

| Critère | Preuve | Statut | Action restante |
|---|---|---|---|
| Recherche documentaire | `data/sources.csv` et bibliographie cliquable | Vérifié | Aucune |
| Veille digitale | Import de 19 fiches annotées et routine documentée | Préparé | Importer et partager dans Raindrop |
| Script ML | Code, métriques, exports et 14 tests | Vérifié | Aucune |
| Étude de marché | PDF autonome de 2 pages | Vérifié | Lire pour la soutenance |
| Livraison | Dépôt public et PDF correctement nommé | Partiel | Ajouter le lien Raindrop et régénérer |

## Action manuelle minimale

Se connecter à Raindrop.io avec une adresse vérifiée. L'assistant peut ensuite importer `outputs/veille_raindrop.csv`, activer la page publique, vérifier les 19 fiches hors connexion, intégrer le lien et régénérer le PDF.

Le dépôt sur la plateforme de l'établissement reste à la charge de l'étudiant.
