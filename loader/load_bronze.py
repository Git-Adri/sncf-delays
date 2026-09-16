"""Chargement des snapshots S3 vers la couche raw de PostgreSQL.

Etapes :
  1. lister les objets S3 d'une partition de date
  2. décompresser et parser chaque snapshot
  3. aplatir en lignes via collector.sncf_client.parse_departures
  4. insérer en base avec COPY (bien plus rapide que des INSERT unitaires)

Ce module est aussi le point de conversion JSON vers Parquet pour l'archivage
long terme, une fois le schéma stabilisé.

A ECRIRE après l'exploration de l'API.
"""
