"""Résolution des id stop_area réels des gares surveillées.

Compare les id stop_area déclarés dans `collector.stations.STATIONS` à ceux
renvoyés par l'endpoint `places` de l'API SNCF, pour repérer les écarts.
Prototypé et validé dans `notebooks/01_explore_api.ipynb` (étape 1).

Usage :

    python -m scripts.resolve_stations
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from collector.sncf_client import SncfClient, extract_id_from_places_response
from collector.stations import STATIONS, Station

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StopAreaMismatch:
    """Écart entre les id déclarés dans `stations.py` et celui résolu via l'API."""

    station: Station

    resolved_id: str | None
    """Id stop_area renvoyé par l'API, ou None si non trouvé."""


def find_id_mismatches(
    client: SncfClient, stations: tuple[Station, ...] = STATIONS
) -> list[StopAreaMismatch]:
    """Compare les id stop_area déclarés aux id résolus via `places` pour chaque gare.

    Ne retourne que les gares dont le code déclaré diverge du code résolu.
    """
    mismatches_list: list[StopAreaMismatch] = []

    for station in stations:
        resolved_ids = find_id_from_station_name(client, station.label)

        if resolved_ids != station.id:
            mismatches_list.append(
                StopAreaMismatch(station=station, resolved_id=resolved_ids)
            )

    return mismatches_list


def find_id_from_station_name(client: SncfClient, station_name: str) -> str | None:
    """Permet de récupérer l'id stop_area d'une gare à partir de son nom.
    Si aucune station n'est trouvée alors None est renvoyé
    """
    response = client.search_places(station_name)
    resolved_id = extract_id_from_places_response(response)

    return resolved_id


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    mismatches = find_id_mismatches(SncfClient())

    if not mismatches:
        print("Tous les stop_area déclarés correspondent à l'API.")
    else:
        for mismatch in mismatches:
            print(
                f"{mismatch.station.label}: {mismatch.station.id} déclaré, "
                f"{mismatch.resolved_id} résolu par l'API"
            )
