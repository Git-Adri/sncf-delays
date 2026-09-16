"""DAG de traitement quotidien.

Note d'architecture : ce DAG ne fait PAS la collecte. La collecte tourne sur
AWS Lambda, déclenchée par EventBridge, parce qu'elle doit fonctionner même
machine éteinte. Airflow orchestre uniquement les traitements aval, qui
peuvent rattraper leur retard sans perte de données.

Lancement en local :
    docker compose -f airflow/docker-compose.yml up
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task

DEFAULT_ARGS = {
    "owner": "adrien",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="sncf_daily_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="30 3 * * *",  # 3h30, après la fin du service de la veille
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["sncf", "data"],
)
def sncf_daily_pipeline():
    """Charge les snapshots de la veille, puis reconstruit silver et gold."""

    @task
    def load_bronze_to_raw(data_interval_start=None) -> int:
        """Lit les partitions S3 de la veille et charge la couche raw."""
        raise NotImplementedError("Voir loader/load_bronze.py")

    @task
    def run_dbt_build() -> None:
        """Reconstruit silver puis gold, avec les tests dbt."""
        raise NotImplementedError("dbt build --select silver gold")

    @task
    def check_freshness() -> None:
        """Alerte si aucune donnée n'a été collectée sur une plage active.

        Garde-fou indispensable : une Lambda qui échoue silencieusement
        pendant une semaine, c'est une semaine d'historique perdue sans
        possibilité de rattrapage.
        """
        raise NotImplementedError

    load_bronze_to_raw() >> run_dbt_build() >> check_freshness()


sncf_daily_pipeline()
