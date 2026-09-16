"""Construction du jeu d'entraînement depuis la couche gold.

Pistes de features, à valider empiriquement :

  - upstream_delay_minutes     retard observé à la gare amont (variable clé)
  - corridor_position          position sur l'axe
  - is_origin_hub              retard initial ou hérité
  - is_terminus_reversal       marge de retournement à Marseille
  - commercial_mode            TER, TGV, Intercités
  - hour, day_of_week          effets de pointe
  - is_holiday                 vacances scolaires, jours fériés
  - active_disruption          perturbation déclarée sur le parcours

Attention au biais de fuite : ne jamais inclure le retard à la gare cible
mesuré APRES l'instant de prédiction.
"""
