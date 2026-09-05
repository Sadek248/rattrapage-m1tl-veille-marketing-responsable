# Veille marketing responsable - M1 Tech Lead

## Outil retenu
Raindrop.io : collection de liens annotés avec catégories par tags et publication en lecture seule. La documentation officielle confirme l'import CSV (url, folder, title, note, tags, created) et le partage public sans compte lecteur :
- https://help.raindrop.io/import
- https://help.raindrop.io/public-page
- https://raindrop.io/

Le statut effectif de publication est enregistré dans config/publication.json. Une procédure seule ne vaut pas une veille en ligne. Tant que watch_url est vide, la consigne de mise en place reste à finaliser.

## Collection et contenus
Titre : Veille marketing responsable - M1 Tech Lead
Description : Sources vérifiées sur les preuves environnementales, l'influence, la vie privée, la sobriété numérique, la consommation et la transparence textile. Corpus initial : 19 références, consultées le 05/09/2026.

Le fichier outputs/veille_raindrop.csv contient toutes les publications avec leur titre, URL, résumé, intérêt métier, date et limite de lecture. Il est généré à partir de data/sources.csv ; aucune ressaisie de ces contenus n'est nécessaire. Les tags sont éditoriaux et indépendants des résultats ML.

## Mise en place
1. Se connecter à Raindrop.io avec un compte gratuit et une adresse vérifiée.
2. Ouvrir Paramètres > Import et charger outputs/veille_raindrop.csv.
3. Vérifier les 19 liens proposés et démarrer l'import. La collection est créée à partir du champ folder.
4. Ouvrir la collection, vérifier les annotations et activer Partager > Page publique.
5. Récupérer le lien affiché et le conserver dans config/publication.json.
6. Contrôler la page hors connexion : titre, nombre de liens, annotations et ouverture de plusieurs sources.
7. Régénérer le PDF avec les liens publics vérifiés.

## Recherche et sélection
Requêtes : "communication responsable" ADEME ; "greenwashing" ARPP ; "2024/825" EUR-Lex ; "Green Claims" Parlement européen ; "pixels courriels" CNIL ; "influence responsable" ADEME DGCCRF ; "affichage environnemental vêtements" ; "sustainability" "programmatic".
Critères : organisme identifiable, document primaire, accès public, date explicite ou absence signalée, méthode identifiable pour les enquêtes, utilité décisionnelle. Exclure les doublons, annonces commerciales non étayées et textes hors sujet. Les sources professionnelles expriment également les intérêts de leur secteur.

## Routine et automatisation
Chaque semaine : exécuter python src/collect_rss.py, lire data/collected/rss_candidates.csv et le journal réseau. Le flux IAB Tech Lab est découvert dans le HTML de son site. La couverture RSS initiale est volontairement limitée ; elle ne remplace pas la revue des pages ADEME, CNIL, DGCCRF et européennes.
Lire les candidats utiles, reformuler leur résumé et les ajouter au corpus validé avec métadonnées. Réexporter le CSV Raindrop, importer les nouveautés et relancer python src/analyze_sources.py. Les imports Raindrop ignorent les doublons existants ; les corrections d'une fiche déjà importée se font dans l'outil.
Chaque mois : synthétiser changements de statut, nouvelles publications et décisions. Contrôler les URL et retirer ou signaler les références obsolètes.

Automatisé à l'exécution : lecture RSS, préfiltrage lexical, déduplication, TF-IDF, essais KMeans, proximité documentaire et exports. Manuel : lancement hebdomadaire, lecture critique, validation et partage. Aucun abonnement payant, clé secrète ou planification exécutée en arrière-plan n'est requis. Le filtrage RSS n'est pas présenté comme du ML.
