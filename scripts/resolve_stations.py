"""Résolution des codes UIC réels des gares surveillées.

Compare les codes UIC déclarés dans `collector.stations.STATIONS` à ceux
renvoyés par l'endpoint `places` de l'API SNCF, pour repérer les écarts.
Prototypé et validé dans `notebooks/01_explore_api.ipynb` (étape 1).

Usage :

    python -m scripts.resolve_stations
"""

from __future__ import annotations

from dataclasses import dataclass

from collector.sncf_client import SncfClient
from collector.stations import STATIONS, Station


@dataclass(frozen=True)
class UicMismatch:
    """Écart entre le code UIC déclaré dans `stations.py` et celui résolu via l'API."""

    station: Station

    resolved_uic: str | None
    """Code UIC renvoyé par l'API, ou None si aucun code de type "uic" n'a été trouvé."""


def find_uic_mismatches(
    client: SncfClient, stations: tuple[Station, ...] = STATIONS
) -> list[UicMismatch]:
    """Compare les UIC déclarés aux UIC résolus via `places` pour chaque gare.

    Ne retourne que les gares dont le code déclaré diverge du code résolu.
    """
    mismatches_list: list[UicMismatch] = []

    for station in stations:
        response = client.search_places(station.label)
        try:
            stop_area_codes = response["places"][0]["stop_area"]["codes"]

            uic_codes = [code["value"] for code in stop_area_codes if code["type"] == "uic"]
            resolved_uic = uic_codes[0] if uic_codes else None

        except (KeyError, IndexError):
            mismatches_list.append(UicMismatch(station=station, resolved_uic=None))
            continue

        if resolved_uic != station.uic:
            mismatches_list.append(UicMismatch(station=station, resolved_uic=resolved_uic))

    return mismatches_list


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    mismatches = find_uic_mismatches(SncfClient())

    if not mismatches:
        print("Tous les codes UIC déclarés correspondent à l'API.")
    else:
        for mismatch in mismatches:
            print(
                f"{mismatch.station.label}: {mismatch.station.uic} déclaré, "
                f"{mismatch.resolved_uic} résolu par l'API"
            )
