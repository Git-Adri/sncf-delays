"""Entraînement du modèle de prédiction de retard.

Approche progressive recommandée :

  1. BASELINE d'abord. Prédire que le retard aval égale le retard amont.
     Mesurer son erreur. Aucun modèle n'a de valeur s'il ne la bat pas.
  2. Régression linéaire, pour l'interprétabilité.
  3. Gradient boosting, si le gain est réel.

Split temporel obligatoire : entraîner sur les semaines passées, tester sur
les semaines suivantes. Un split aléatoire ferait fuiter le futur dans
l'entraînement et donnerait des scores flatteurs et faux.
"""
