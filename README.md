# Veille digitale pour le marketing responsable

Projet de rattrapage M1 Tech Lead, Digital Campus - CHOUIKHA Mohamed Sadok.

**Dépôt public :** https://github.com/Sadek248/rattrapage-m1tl-veille-marketing-responsable

**État de livraison :** analyse, sources et étude corrigées et testées. La collection Raindrop doit encore être importée et rendue publique sur le compte de l'étudiant. Le PDF porte explicitement la mention « version à finaliser » tant que ce lien n'est pas vérifié. Les URL et le statut sont centralisés dans config/publication.json.

## Exigences et planning indicatif (150 minutes)

| Temps | Réalisation |
|---|---|
| 0-10 min | Lire le sujet et vérifier comptes et partage public |
| 10-45 min | Sélectionner et documenter au moins 5 sources fiables |
| 45-65 min | Importer et annoter la collection de curation |
| 65-100 min | Nettoyer, analyser avec scikit-learn et tester |
| 100-125 min | Rédiger une étude de marché de 2 pages maximum |
| 125-150 min | Publier le dépôt, générer le PDF et vérifier les accès |

Ce planning est une proposition méthodologique, pas un relevé du temps effectivement passé.

## Structure

- data/sources.csv : 19 références validées et métadonnées de consultation.
- data/feeds.json : flux de collecte.
- data/collected/ : candidats RSS et journal réseau, séparés du corpus étudié.
- src/analyze_sources.py : TF-IDF, essais KMeans et rapprochements documentaires.
- src/collect_rss.py : collecte bornée et préfiltrage, sans clé d'API.
- src/export_curation.py : fichier d'import Raindrop, 19 liens annotés.
- src/generate_pdf.py : dossier PDF et étude autonome.
- analysis/ : exports, métriques et décision sur le regroupement.
- tests/ : données fictives uniquement en mémoire et dossiers temporaires.
- docs/ : méthode de veille, étude, conformité et fiche orale.
- outputs/ : PDF de livraison, étude, import et compte rendu d'audit.

## Installation et exécution sous Windows

Python 3.12 ou version compatible avec les dépendances. Depuis la racine du dépôt (remplacer py -3.12 par py -3 si seule une version plus récente est installée) :

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe src\analyze_sources.py
.\.venv\Scripts\python.exe src\export_curation.py
.\.venv\Scripts\python.exe src\generate_pdf.py
```

La génération PDF et l'analyse fonctionnent sans réseau après installation. Pour actualiser les candidats :

```powershell
.\.venv\Scripts\python.exe src\collect_rss.py
```

Le corpus validé n'est jamais écrasé par la collecte. Relire les candidats avant de les ajouter. Aucun mot de passe ni jeton n'est nécessaire pour ces commandes.

## Méthode et résultats vérifiés

Les champs title et summary sont analysés. Ce sont des résumés éditoriaux, pas des textes intégralement extraits. Les catégories et intérêts métier sont exclus des entrées ML. La normalisation retire accents, URL, ponctuation et mots outils. Les URL et textes identiques sont dédupliqués ; les cas invalides sont signalés.

TF-IDF utilise mots et groupes de deux mots. KMeans teste 2 à 5 groupes (random_state=42, n_init=20), avec au moins deux documents par groupe pour qu'un candidat soit admissible. Le meilleur candidat atteint une silhouette cosinus de **0,042**, sous le seuil heuristique de 0,10. **Aucune partition thématique n'est donc retenue.** Le groupe 0 des exports représente le corpus global, pas un thème découvert.

Le document représentatif est choisi par distance au centroïde. Les cinq paires les plus proches figurent dans analysis/similar_sources.csv. Les liens S05-S06, S09-S19 et S12-S13 rapprochent respectivement les documents ARPP, Green Claims et affichage textile. Aucun pourcentage de précision ou de part de marché n'est calculé.

Le score de l'ancienne version (0,013, distance euclidienne, autres textes d'entrée) n'est pas directement comparable à la silhouette cosinus actuelle.

## Veille et publication

Raindrop est l'outil de curation retenu. outputs/veille_raindrop.csv importe titres, liens, dates, résumés et tags en une opération. La mise en ligne nécessite un compte connecté avec e-mail vérifié. Voir docs/veille_digitale.md. La routine hebdomadaire n'est pas un service déjà planifié.

Le PDF global fait 5 pages : accès aux livrables, étude de 2 pages, bibliographie. La limite du sujet concerne l'étude, pas tout le dossier. Le fichier outputs/Etude_de_marche.pdf contient uniquement cette étude.

Pour finaliser après obtention du lien public de la collection :

```powershell
.\.venv\Scripts\python.exe src\finalize_delivery.py --watch-url "URL_PUBLIQUE_RAINDROP" --verified-in-browser
```

Après vérification des 19 liens et annotations hors connexion, cette commande contrôle les URL, met à jour la configuration et régénère le PDF. Elle ne publie pas elle-même la collection. Le lien exemple n'est pas une URL réelle. Le drapeau confirme le contrôle visuel, car un statut HTTP 200 seul ne prouve pas que la collection est lisible.

## Limites

Corpus documentaire sélectionné, biais de reformulation, pas de lemmatisation, pas de terrain commercial. Certaines ressources sont anciennes et restent des références ; le statut de la procédure Green Claims repose sur la dernière fiche officielle accessible, mise à jour le 20 juin 2026. La lecture des fiches de présentation des guides ne vaut pas lecture intégrale des rapports. Les dates inconnues restent vides. Le contrôle réseau direct peut être refusé par un site même si son contenu est consultable via la recherche.

## Vérification

14 tests couvrent normalisation, colonnes, doublons, corpus réduit, vocabulaire vide, centroïde, reproductibilité, séparation des annotations humaines, lecture RSS et erreurs réseau. Le PDF est rendu en images et relu visuellement ; liens et nombre de pages sont contrôlés avec pypdf. Le compte rendu détaillé est fourni dans outputs/Compte_rendu_audit.md.
