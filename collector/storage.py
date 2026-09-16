"""Ecriture des snapshots bruts sur S3 (couche bronze).

Convention de partitionnement :

    s3://<bucket>/bronze/departures/dt=YYYY-MM-DD/hour=HH/<station>-<ts>.json.gz

Le partitionnement par date puis par heure permet à DuckDB et Athena de ne
lire que les partitions utiles (predicate pushdown). Ne pas mettre des
milliers de fichiers à plat : les moteurs de requête s'en sortent mal.

Le brut est stocké en JSON compressé et non en Parquet, volontairement : à ce
stade on ne connaît pas encore le schéma stable des réponses. La conversion en
Parquet se fait dans `loader/`, une fois le schéma figé.
"""

from __future__ import annotations

import gzip
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import boto3

logger = logging.getLogger(__name__)


def bronze_key(dataset: str, station_slug: str, moment: datetime | None = None) -> str:
    """Construit la clé S3 d'un snapshot."""
    moment = moment or datetime.now(timezone.utc)
    return (
        f"bronze/{dataset}"
        f"/dt={moment:%Y-%m-%d}"
        f"/hour={moment:%H}"
        f"/{station_slug}-{moment:%Y%m%dT%H%M%S}.json.gz"
    )


def put_snapshot(
    payload: dict[str, Any],
    dataset: str,
    station_slug: str,
    bucket: str | None = None,
) -> str:
    """Archive une réponse brute de l'API sur S3. Retourne la clé écrite."""
    bucket = bucket or os.environ["S3_BUCKET"]
    key = bronze_key(dataset, station_slug)
    body = gzip.compress(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    boto3.client("s3").put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
        ContentType="application/json",
        ContentEncoding="gzip",
    )
    logger.info("Snapshot écrit : s3://%s/%s (%d octets)", bucket, key, len(body))
    return key
