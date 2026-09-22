"""Client minimal de l'API SNCF (Navitia).

L'API SNCF expose Navitia. Les deux endpoints utiles pour ce projet :

  departures     prochains départs théoriques + temps réel d'une zone d'arrêt
  disruptions    perturbations en cours sur la couverture

Documentation : https://doc.navitia.io/

IMPORTANT : ce module est un squelette. Le parsing des réponses
(`parse_departures`) est volontairement laissé incomplet — il doit être écrit
APRES avoir observé de vraies réponses, pas deviné. Voir
`notebooks/01_explore_api.ipynb`.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.sncf.com/v1/coverage/sncf"
DEFAULT_TIMEOUT = 15
DEFAULT_COUNT = 50


class SncfApiError(RuntimeError):
    """Erreur renvoyée par l'API ou problème de transport."""


class SncfClient:
    """Client HTTP pour l'API SNCF.

    L'authentification se fait par HTTP Basic, la clé servant de nom
    d'utilisateur avec un mot de passe vide.
    """

    def __init__(self, api_key: str | None = None, timeout: int = DEFAULT_TIMEOUT) -> None:
        key = api_key or os.environ.get("SNCF_API_KEY")
        if not key:
            raise SncfApiError(
                "Clé API manquante. Renseigner SNCF_API_KEY dans l'environnement. "
                "Obtenir une clé sur https://numerique.sncf.com/startup/api/"
            )
        self._timeout = timeout
        self._session = requests.Session()
        self._session.auth = (key, "")
        self._session.headers.update({"Accept": "application/json"})

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{BASE_URL}/{path.lstrip('/')}"
        try:
            response = self._session.get(url, params=params, timeout=self._timeout)
        except requests.RequestException as exc:
            raise SncfApiError(f"Echec de la requête vers {path}") from exc

        if response.status_code == 429:
            raise SncfApiError("Quota API dépassé (429). Espacer les appels.")
        if not response.ok:
            raise SncfApiError(f"HTTP {response.status_code} sur {path}: {response.text[:200]}")

        return response.json()

    # -- Endpoints ---------------------------------------------------------

    def search_places(self, query: str) -> dict[str, Any]:
        """Recherche d'une gare par nom. Sert à résoudre les id des gares."""

        if not query:
            raise ValueError("query ne peut pas être vide")

        return self._get("places", {"q": query, "type[]": ["stop_area"]})

    def departures(self, stop_area: str, count: int = DEFAULT_COUNT) -> dict[str, Any]:
        """Prochains départs d'une zone d'arrêt, avec données temps réel.

        `data_freshness=realtime` est essentiel : sans ce paramètre l'API
        renvoie les horaires théoriques et le projet n'a aucun intérêt.
        """
        return self._get(
            f"stop_areas/{stop_area}/departures",
            {"count": count, "data_freshness": "realtime"},
        )

    def arrivals(self, stop_area: str, count: int = DEFAULT_COUNT) -> dict[str, Any]:
        """Prochaines arrivées d'une zone d'arrêt, avec données temps réel."""
        return self._get(
            f"stop_areas/{stop_area}/arrivals",
            {"count": count, "data_freshness": "realtime"},
        )

    def disruptions(self, count: int = DEFAULT_COUNT) -> dict[str, Any]:
        """Perturbations en cours sur la couverture SNCF."""
        return self._get("disruptions", {"count": count})


# -- Parsing ---------------------------------------------------------------


def parse_departures(payload: dict[str, Any], station_slug: str) -> list[dict[str, Any]]:
    """Aplatit une réponse `departures` en lignes exploitables.

    A ECRIRE après exploration du format réel. Les champs attendus, d'après la
    documentation Navitia, sont à confirmer :

      - stop_date_time.base_departure_date_time      horaire théorique
      - stop_date_time.departure_date_time           horaire temps réel
      - display_informations.headsign                numéro de train
      - display_informations.trip_short_name         numéro commercial
      - display_informations.direction               destination
      - display_informations.commercial_mode         TER, TGV, Intercités
      - stop_point.id                                identifiant du quai
      - links[].id où type == "disruption"           perturbation associée

    Le retard se calcule comme la différence entre l'horaire temps réel et
    l'horaire théorique. Attention aux passages de minuit et aux fuseaux :
    Navitia renvoie des horaires locaux au format YYYYMMDDTHHMMSS sans
    indicateur de fuseau.
    """
    raise NotImplementedError(
        "Ecrire ce parsing après avoir observé de vraies réponses de l'API. "
        "Voir notebooks/01_explore_api.ipynb"
    )

def extract_id_from_places_response(response: dict) -> str | None:
    """Permet de récupérer l'id stop_area d'une gare à partir de la reponse d'une recherche de gare.
    Si aucune gare n'est trouvée alors None est renvoyé
    """
    try:
        station_id = response['places'][0]['id']

    except (KeyError, IndexError):
        logger.warning("Structure de stop area inattendue, id ['places'][0]['id'] introuvable : %s", response)
        return None

    return station_id

def get_train_id_from_departure(departure: dict) -> str | None:
    """Permet de récupérer l'id d'un train à partir d'une reponse de departures() parmi la liste retournée.
    Si aucune id n'est trouvée alors None est renvoyé
    """
    try:
        train_nb = departure['display_informations']['headsign']
    except KeyError:
        logger.warning("Structure de départ inattendue, headsign ['display_informations']['headsign'] introuvable : %s", departure)
        return None

    return train_nb

def get_train_destination_from_departure(departure: dict) -> str | None:
    try:
        destination = departure['display_informations']['direction']
    except KeyError:
        logger.warning("Structure de départ inattendue, direction ['display_informations']['direction'] introuvable : %s", departure)
        return None

    return destination

def collected_at() -> str:
    """Horodatage de collecte, en UTC et au format ISO 8601.

    Ce champ est indispensable : c'est lui qui permet de reconstruire
    l'évolution d'un retard dans le temps à partir des snapshots.
    """
    return datetime.now(timezone.utc).isoformat()
