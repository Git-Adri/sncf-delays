# Exploration

`01_explore_api.ipynb` — à créer en premier.

Objectifs de ce notebook :

1. Résoudre les codes UIC réels des cinq gares via l'endpoint `places`
2. Appeler `departures` sur une gare et inspecter la structure complète
3. Vérifier que `data_freshness=realtime` renvoie bien un horaire différent
   de l'horaire théorique quand un train est en retard
4. Identifier le champ qui porte l'identifiant de circulation persistant
   d'une gare à l'autre (condition nécessaire à tout le projet)
5. Mesurer le quota réel : combien d'appels avant un HTTP 429
6. Vérifier si le quai (`stop_point`) est renseigné en temps réel

Le point 4 est le plus critique. Si aucun identifiant ne permet de suivre un
train d'une gare à l'autre, l'hypothèse de propagation devient beaucoup plus
difficile à tester et il faudra revoir l'approche.
