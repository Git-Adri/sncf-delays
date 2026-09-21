# sncf-delays

Collecte en continu des circulations ferroviaires sur un corridor de cinq gares,
et prédiction de la propagation des retards le long de cet axe.

**Corridor observé** : Bordeaux Saint-Jean → Toulouse Matabiau → Montpellier
Saint-Roch → Marseille Saint-Charles → Antibes.

Ces gares sont sur le même axe, donc les mêmes circulations traversent
plusieurs points d'observation. La propagation d'un retard est mesurable
directement, sans reconstruire les correspondances de rames.

## Architecture

```
API SNCF
   │
   ▼
AWS Lambda + EventBridge        hébergé — tourne en continu
   │
   ▼
S3  (bronze, JSON puis Parquet) hébergé
   │
   ▼
Neon PostgreSQL (raw)           hébergé — managé, gratuit
   │
   ▼
dbt (silver → gold)             local
   │
   ▼
scikit-learn                    local
```

Airflow (local) orchestre le chargement et dbt.
DuckDB (local) interroge les Parquet S3 sans passer par la base.

Le détail des décisions et de leurs justifications est dans
[`docs/CONTEXT.md`](docs/CONTEXT.md).

### Pourquoi ce découpage

Seule la collecte est hébergée. L'API SNCF ne permet pas de rejouer le passé :
chaque minute non collectée est perdue définitivement. C'est la seule brique
qui ne tolère pas une machine éteinte.

Tout le reste — dbt, Airflow, entraînement — est du traitement aval qui peut
rattraper son retard. Aucune raison de le payer en continu.

### Principe de modélisation

**Ne pas stocker les snapshots, stocker les transitions.**

Un polling naïf produit environ 40 Mo/jour en base : le même train réapparaît
identique dans des dizaines d'appels successifs. En ne conservant qu'une ligne
par changement de retard, on descend sous 0,5 Mo/jour, et le tier gratuit Neon
(0,5 Go) tient plusieurs années.

Les snapshots bruts restent archivés sur S3, pour quelques centimes par mois.
Le brut n'est jamais perdu : toute couche supérieure est reconstructible.

## Arborescence

```
collector/          collecte — code déployé sur Lambda
  stations.py       référentiel des gares (id résolus, voir scripts/resolve_stations.py)
  sncf_client.py    client API
  storage.py        écriture des snapshots sur S3
  handler.py        point d'entrée Lambda
loader/             S3 → PostgreSQL, conversion Parquet
dbt/                transformations SQL
  models/bronze/    déclaration des sources
  models/silver/    dédoublonnage, calcul des retards
  models/gold/      features pour le modèle
airflow/dags/       orchestration des traitements aval
ml/                 features et entraînement
infra/terraform/    S3, Lambda, EventBridge
notebooks/          exploration
tests/              tests unitaires
docs/CONTEXT.md     décisions et justifications
```

## Démarrage

```bash
git clone <url> && cd sncf-delays
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # puis renseigner les valeurs
```

Prérequis à obtenir :

- **Clé API SNCF** — https://numerique.sncf.com/startup/api/
- **Base PostgreSQL** — https://neon.tech (plan gratuit)
- **Compte AWS** — pour S3 et Lambda

## État d'avancement

- [x] Architecture et périmètre définis
- [x] Squelette de projet
- [x] Clé API obtenue
- [ ] Exploration du format des réponses
- [x] Id des gares résolus et vérifiés
- [ ] Schéma de la couche raw
- [ ] Collecteur fonctionnel en local
- [ ] Déploiement Lambda
- [ ] Modèles dbt
- [ ] Baseline de prédiction

## Points laissés volontairement incomplets

Plusieurs fonctions lèvent `NotImplementedError` avec un commentaire décrivant
la logique visée. C'est délibéré : le parsing des réponses de l'API et le
schéma des tables doivent être écrits **après** avoir observé de vraies
réponses, pas devinés à partir de la documentation.

## Kafka

Absent de l'architecture. Pour un collecteur qui interroge une API toutes les
quelques minutes, Kafka n'apporte rien fonctionnellement.

Il peut être ajouté en local via Docker, entre collecte et stockage, à titre
de démonstration — c'est une techno demandée sur le marché. Mais c'est un
ajout pédagogique assumé, pas une nécessité technique, et gagne à être
présenté comme tel.

## Licence

Usage personnel. Les données SNCF sont soumises aux conditions du portail
open data SNCF.
