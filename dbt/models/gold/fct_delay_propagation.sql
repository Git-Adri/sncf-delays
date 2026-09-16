-- Couche gold : table de features pour le modèle de prédiction.
--
-- Objectif : pour chaque passage d'un train à une gare, disposer du retard
-- observé en AMONT sur le corridor. C'est la variable explicative centrale
-- de l'hypothèse de travail.
--
-- A ECRIRE. Logique visée :
--
--   - joindre stg_train_stops sur lui-même par trip_id et service_date
--   - ne retenir que les paires dont corridor_position est strictement
--     inférieure (la gare amont)
--   - ajouter les attributs de gare : is_origin_hub, is_terminus_reversal
--   - ajouter les features temporelles : heure, jour de semaine, vacances
--   - cible : delay_minutes à la gare aval

select
    null::text    as trip_id,
    null::date    as service_date,
    null::text    as station_slug,
    null::integer as upstream_delay_minutes,
    null::integer as target_delay_minutes
where false
