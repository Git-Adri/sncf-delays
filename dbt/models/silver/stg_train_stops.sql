-- Couche silver : une ligne par (train, gare, date de service) et par
-- TRANSITION de retard, pas par snapshot.
--
-- C'est le modèle central du projet. Un polling toutes les 2 minutes produit
-- des dizaines d'observations identiques pour un même train : on ne garde que
-- les instants où le retard annoncé change.
--
-- A ECRIRE une fois le schéma de la couche raw connu. Esquisse de logique :
--
--   1. déduper les snapshots sur (trip_id, station_slug, service_date, delay)
--      en conservant le premier collected_at de chaque palier
--   2. calculer delay_minutes = realtime_departure - theoretical_departure
--   3. marquer la dernière observation connue (retard final observé)
--
-- Penser à LAG() sur collected_at partitionné par (trip_id, station_slug)
-- pour détecter les changements de palier.

select
    null::text     as trip_id,
    null::text     as station_slug,
    null::date     as service_date,
    null::integer  as delay_minutes,
    null::timestamptz as observed_from,
    null::boolean  as is_final_observation
where false
