"""Référentiel des gares surveillées.

Les id ci-dessous ont été résolus contre l'API et validés dans
`notebooks/01_explore_api.ipynb` (étape 1). Le format des id SNCF est
`stop_area:SNCF:87XXXXXX` où 87XXXXXX est le code UIC à 8 chiffres de la
gare.

`scripts/resolve_stations.py` automatise cette résolution : il compare les
codes déclarés ici à ceux renvoyés par l'endpoint `places` de l'API et
signale les écarts, si SNCF venait à changer un identifiant.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Station:
    """Une gare du corridor surveillé."""

    slug: str
    """Identifiant court, utilisé comme clé en base et dans les chemins S3."""

    label: str
    """Nom lisible."""

    id: str
    """Identifiant Navitia de la gare (un stop_area), résolu contre l'API
    (voir `scripts/resolve_stations.py`). Utilisable tel quel dans les appels
    `stop_areas/{id}/departures` et `.../arrivals`."""

    corridor_position: int
    """Position sur le corridor, d'ouest en est. Sert à ordonner les gares
    pour l'analyse de propagation des retards."""

    is_origin_hub: bool
    """True si la gare est majoritairement une tête de ligne (retard initial),
    False si c'est surtout une gare de passage (retard hérité)."""

    is_terminus_reversal: bool
    """True si les circulations traversantes y font demi-tour, ce qui introduit
    une marge de retournement susceptible d'absorber ou d'amplifier le retard."""

    @property
    def uic(self) -> str:
        """Code UIC à 8 chiffres qui identifie une gare. Contenu à la fin de id: stop_area:SNCF:{uic} """
        if not self.id:
            return ""

        return self.id.split(":")[-1]


# Corridor transversale sud, ordonné d'ouest en est.
# Codes UIC résolus contre l'API (voir scripts/resolve_stations.py).
STATIONS: tuple[Station, ...] = (
    Station(
        slug="bordeaux_st_jean",
        label="Bordeaux Saint-Jean",
        id="stop_area:SNCF:87581009",
        corridor_position=1,
        is_origin_hub=True,
        is_terminus_reversal=False,
    ),
    Station(
        slug="toulouse_matabiau",
        label="Toulouse Matabiau",
        id="stop_area:SNCF:87611004",
        corridor_position=2,
        is_origin_hub=True,
        is_terminus_reversal=False,
    ),
    Station(
        slug="montpellier_st_roch",
        label="Montpellier Saint-Roch",
        id="stop_area:SNCF:87773002",
        corridor_position=3,
        is_origin_hub=False,
        is_terminus_reversal=False,
    ),
    Station(
        slug="marseille_st_charles",
        label="Marseille Saint-Charles",
        id="stop_area:SNCF:87751008",
        corridor_position=4,
        is_origin_hub=False,
        is_terminus_reversal=True,
    ),
    Station(
        slug="antibes",
        label="Antibes",
        id="stop_area:SNCF:87757674",
        corridor_position=5,
        is_origin_hub=False,
        is_terminus_reversal=False,
    ),
)

BY_SLUG: dict[str, Station] = {s.slug: s for s in STATIONS}
BY_UIC: dict[str, Station] = {s.uic: s for s in STATIONS}
