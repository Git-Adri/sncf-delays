"""Référentiel des gares surveillées.

ATTENTION : les identifiants ci-dessous sont des valeurs à VERIFIER contre
l'API avant toute utilisation. Le format des stop_area SNCF est
`stop_area:SNCF:87XXXXX` où 87XXXXX est le code UIC de la gare.

Pour récupérer l'identifiant réel d'une gare :

    GET https://api.sncf.com/v1/coverage/sncf/places?q=Bordeaux+Saint-Jean

puis filtrer les résultats dont `embedded_type == "stop_area"`.

Le script `scripts/resolve_stations.py` (à écrire) automatisera cette
résolution et mettra ce fichier à jour.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Station:
    """Une gare du corridor surveillé."""

    slug: str
    """Identifiant court, utilisé comme clé en base et dans les chemins S3."""

    label: str
    """Nom lisible."""

    uic: str
    """Code UIC à 7 chiffres. A VERIFIER contre l'API."""

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
    def stop_area(self) -> str:
        """Identifiant Navitia de la zone d'arrêt."""
        return f"stop_area:SNCF:{self.uic}"


# Corridor transversale sud, ordonné d'ouest en est.
# Les codes UIC sont des valeurs de départ A VERIFIER.
STATIONS: tuple[Station, ...] = (
    Station(
        slug="bordeaux_st_jean",
        label="Bordeaux Saint-Jean",
        uic="8758100",
        corridor_position=1,
        is_origin_hub=True,
        is_terminus_reversal=False,
    ),
    Station(
        slug="toulouse_matabiau",
        label="Toulouse Matabiau",
        uic="8761100",
        corridor_position=2,
        is_origin_hub=True,
        is_terminus_reversal=False,
    ),
    Station(
        slug="montpellier_st_roch",
        label="Montpellier Saint-Roch",
        uic="8768600",
        corridor_position=3,
        is_origin_hub=False,
        is_terminus_reversal=False,
    ),
    Station(
        slug="marseille_st_charles",
        label="Marseille Saint-Charles",
        uic="8775100",
        corridor_position=4,
        is_origin_hub=False,
        is_terminus_reversal=True,
    ),
    Station(
        slug="antibes",
        label="Antibes",
        uic="8775500",
        corridor_position=5,
        is_origin_hub=False,
        is_terminus_reversal=False,
    ),
)

BY_SLUG: dict[str, Station] = {s.slug: s for s in STATIONS}
BY_UIC: dict[str, Station] = {s.uic: s for s in STATIONS}
