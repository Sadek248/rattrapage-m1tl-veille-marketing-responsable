# Expliquer le projet en quelques minutes

## Objectif
Surveiller les évolutions utiles à une entreprise de marketing responsable, les documenter et en tirer trois actions réalistes : vérifier les preuves des campagnes, tester un cas textile et instaurer une revue régulière.

## Données
19 références documentaires sélectionnées auprès d'organismes identifiables. Les textes analysés sont des titres et résumés reformulés après consultation, pas les textes intégraux des publications. Le CSV conserve dates, URL, intérêt et limites. Le lecteur RSS produit séparément des candidats non encore validés.

## TF-IDF
Chaque document devient un vecteur de poids. Un terme fréquent dans un document mais moins courant dans le corpus pèse davantage. Les accents et mots outils sont normalisés. Les thèmes et commentaires ajoutés par le rédacteur sont exclus de l'entrée pour limiter le biais de classement.

## KMeans et décision
KMeans cherche des centres et affecte les documents au centre le plus proche. Il reçoit plusieurs nombres de groupes possibles, de 2 à 5. random_state=42 et n_init=20 rendent les essais reproductibles dans le même environnement. Une silhouette cosinus compare proximité au groupe et séparation avec les autres groupes ; ce n'est pas un taux de précision.

## Résultat à défendre
Le meilleur candidat donne 0,042, sous notre seuil de prudence de 0,10. Ce seuil est un choix méthodologique, pas une loi statistique. On ne retient donc pas de partition. Un résultat négatif vaut mieux qu'une interprétation artificielle. Le rapprochement des documents reste utile : ARPP bilan/recommandation, Green Claims position/suivi et affichage textile méthode/lancement.

## Limites et intérêt métier
Petit corpus, sélection humaine, résumés qui influencent le vocabulaire, pas de données de ventes ni d'entretiens. On ne calcule pas de part de marché et on ne prédit pas une croissance. L'outil aide à préparer une lecture croisée, à limiter les doublons et à vérifier les statuts des informations. Les recommandations métier relèvent de l'analyse documentaire humaine.

## Ce qui fonctionne automatiquement
La collecte RSS, le nettoyage, la déduplication, TF-IDF, les essais KMeans et les exports s'exécutent par commande. La décision de retenir une source et de publier son annotation reste humaine. Aucun service payant ni clé d'API n'est nécessaire pour l'analyse.
