"""Point d'entrée AWS Lambda de la collecte.

Déclenché par EventBridge Scheduler. Pour chaque gare du corridor, interroge
l'API SNCF et archive la réponse brute sur S3.

Principe : ce handler ne fait AUCUNE transformation. Il collecte et archive.
Toute logique de parsing appartient aux couches supérieures, pour que le brut
reste rejouable si le parsing évolue.

Test en local :

    python -m collector.handler
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

from collector.sncf_client import SncfApiError, SncfClient
from collector.stations import STATIONS
from collector.storage import put_snapshot

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def is_active_hour(moment: datetime | None = None) -> bool:
    """Le trafic ferroviaire est nul la nuit. Inutile de collecter du vide."""
    moment = moment or datetime.now(timezone.utc)
    start = int(os.environ.get("ACTIVE_HOURS_START", 5))
    end = int(os.environ.get("ACTIVE_HOURS_END", 23))
    return start <= moment.hour < end


def handler(event: dict[str, Any] | None = None, context: Any = None) -> dict[str, Any]:
    """Collecte un snapshot pour chaque gare surveillée."""
    if not is_active_hour():
        logger.info("Hors plage active, collecte ignorée.")
        return {"status": "skipped", "reason": "inactive_hour"}

    client = SncfClient()
    written: list[str] = []
    failed: list[str] = []

    for station in STATIONS:
        for dataset, fetch in (
            ("departures", client.departures),
            ("arrivals", client.arrivals),
        ):
            try:
                payload = fetch(station.stop_area)
                written.append(put_snapshot(payload, dataset, station.slug))
            except SncfApiError as exc:
                # Une gare en échec ne doit pas faire tomber les quatre autres.
                logger.warning("Echec %s sur %s : %s", dataset, station.slug, exc)
                failed.append(f"{dataset}/{station.slug}")

    return {"status": "ok", "written": len(written), "failed": failed}


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    print(handler())
