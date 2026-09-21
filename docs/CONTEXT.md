# Contexte du projet

Ce fichier récapitule les décisions prises en amont du développement.
Il sert de point d'entrée pour toute reprise du projet (y compris par un assistant IA).

## Objectif

Collecter en continu les données de circulation des trains SNCF sur un corridor
ferroviaire, construire un historique exploitable, puis entraîner un modèle de
prédiction des retards.

L'hypothèse de travail : sur un corridor ordonné, le retard d'un train observé
en amont est prédictif de son retard en aval. On veut mesurer et modéliser cette
propagation.

## Objectif secondaire (assumé)

Le projet est aussi un support de montée en compétence sur des technologies
demandées sur le marché et absentes de l'expérience professionnelle actuelle :
Airflow, dbt, S3, Terraform, DuckDB.

## Périmètre

Cinq gares de la transversale sud, dans l'ordre géographique :

1. Bordeaux Saint-Jean
2. Toulouse Matabiau
3. Montpellier Saint-Roch
4. Marseille Saint-Charles
5. Antibes

Ces gares sont sur le même axe : les mêmes circulations traversent plusieurs
points d'observation, ce qui rend la propagation des retards directement
mesurable sans avoir à reconstruire les correspondances de rames.

### Particularités à modéliser

- **Marseille Saint-Charles** est un terminus en cul-de-sac. Les trains
  Toulouse–Nice y font demi-tour. Le retard peut y être absorbé ou amplifié
  selon la marge de retournement.
- **Bordeaux** est le seul point connecté à la LGV Atlantique : source de
  perturbation exogène au corridor méditerranéen.
- **Bordeaux et Toulouse** sont des têtes de ligne (retard initial).
  **Antibes** est une gare de passage (retard hérité). Cette distinction est
  attendue comme fortement prédictive.
- **Montpellier** a deux gares (Saint-Roch et Sud de France). On ne retient
  que Saint-Roch.

## Volumétrie estimée

Environ 1 300 arrêts de train par jour sur les cinq gares.

| Couche | Volume |
|---|---|
| Bronze (S3, Parquet compressé) | quelques dizaines de Mo/mois |
| Silver + Gold (Postgres, dédoublonné) | ~12 Mo/mois |

## Principe de modélisation central

**Ne pas stocker les snapshots, stocker les transitions.**

Un polling naïf produit ~40 Mo/jour en base, car le même train réapparaît
identique dans des dizaines d'appels successifs. En ne conservant qu'une ligne
par changement d'état (train, gare, date), on descend sous 0,5 Mo/jour.

Les snapshots bruts restent archivés sur S3 : le brut n'est jamais perdu et
toute couche supérieure peut être reconstruite.

## Portée de la v1 : propagation intra-train uniquement

L'hypothèse de propagation suppose au départ que le retard se mesure sur un
même train, identifié par un id de circulation persistant (`headsign`) d'une
gare à l'autre. En pratique, la majorité des trajets sur le corridor
impliquent une correspondance — pas seulement à Marseille (terminus à
retournement), mais aussi entre les autres gares.

Pour la v1, on se limite volontairement à la propagation **intra-train** :
deux observations ne sont rapprochées que si elles partagent le même id de
circulation. Un cas de correspondance ne produit alors simplement aucune
paire exploitable — pas d'erreur, juste une couverture réduite. La
propagation par correspondance (le retard d'un train amont qui impacte le
départ d'un train aval différent) est un axe d'extension explicitement mis
de côté pour l'instant, pas oublié.

Validé empiriquement dans `notebooks/01_explore_api.ipynb` (étape 4) : le
champ `headsign` d'une réponse `departures`/`arrivals` sert d'identifiant
persistant entre deux gares, confirmé via un croisement avec le lien
`origins` de l'arrivée correspondante à la gare cible.

## Architecture

```
API SNCF
   |
   v
AWS Lambda + EventBridge        <- hébergé, tourne en continu
   |
   v
S3 (bronze, Parquet)            <- hébergé
   |
   v
Neon PostgreSQL                 <- hébergé (managé, gratuit)
   |
   v
dbt (silver, gold)              <- local
   |
   v
scikit-learn                    <- local

Airflow (local) orchestre dbt et l'entraînement.
DuckDB (local) interroge les Parquet S3 sans passer par la base.
```

### Justification des choix d'hébergement

**Ce qui est hébergé** : uniquement la collecte et le stockage. L'API SNCF ne
permet pas de rejouer le passé — chaque minute non collectée est perdue
définitivement. C'est la seule brique qui ne tolère pas une machine éteinte.

Lambda plutôt qu'EC2 : le free tier Lambda est permanent (1M invocations/mois),
celui d'EC2 est limité à 12 mois.

Neon plutôt que RDS : RDS n'est gratuit que 12 mois puis coûte ~15-20 €/mois.
Neon reste gratuit, avec sauvegardes automatiques.

S3 pour le bronze : ~0,023 $/Go/mois après le free tier. 20 Go d'archives
coûtent moins de 50 centimes par mois.

**Ce qui est local** : dbt, Airflow, entraînement du modèle. Rien de tout cela
n'a besoin de tourner en continu. Airflow demande à lui seul ~2 Go de RAM,
incompatible avec toute instance gratuite.

## Langages

| Usage | Langage |
|---|---|
| Collecte, chargement, ML | Python |
| Transformations dbt | SQL |
| Infrastructure | HCL (Terraform) |

En volume, le SQL sera probablement la partie la plus dense du projet.

### Justification

Python est le standard de l'écosystème data visé : les DAG Airflow *sont* du
code Python, dbt est un outil Python, boto3 pour AWS, et scikit-learn n'a pas
d'équivalent sérieux ailleurs. Sur Lambda, les cold starts Python sont aussi
nettement meilleurs que ceux de la JVM.

C'est également ce que demandent les offres visées, qui placent Python et SQL
en tête des compétences attendues.

### Note importante

L'expérience professionnelle de la personne est en **Java** (Spark, Kafka,
Flink chez Thales). Ce n'est pas un handicap mais un atout : Java et Scala
restent dominants sur les gros traitements distribués, et maîtriser les deux
distingue des profils purement Python. Ce point ne doit pas être minimisé sous
prétexte que le projet personnel est en Python.

Si la brique Kafka de démonstration est ajoutée, un consumer Flink en Java
serait l'endroit naturel pour valoriser cette expérience et éviter un projet
mono-langage. Optionnel, et source de complexité.

Ce choix n'avait pas été discuté explicitement : il a été posé par défaut lors
de l'écriture du squelette, puis validé après coup.

### Sur Kafka

Kafka figurait dans l'architecture initiale puis a été retiré. Pour un
collecteur qui interroge une API toutes les 2 minutes, il n'apporte rien
fonctionnellement.

Il peut être ajouté en local via Docker, entre la collecte et le stockage,
**purement à titre de démonstration** — c'est une techno demandée sur le
marché. Mais c'est un ajout pédagogique assumé, pas une nécessité
d'architecture, et doit être présenté comme tel.

Coût d'un Kafka managé pour comparaison : AWS MSK dépasse 100 €/mois.

## Contraintes

- **Budget** : objectif 0 €/mois, quelques centimes tolérés.
- **Quota API** : l'accès développeur SNCF est plafonné. À 5 gares et un
  polling de 2 minutes, on est à ~3 600 appels/jour. Si le quota est trop
  serré : passer à 5 minutes (1 440 appels/jour), ou ne poller que sur la
  plage 5h–23h (-25 % de volume pour zéro perte utile).

## Contexte de la personne

Data Engineer, INSA Toulouse 2019, spécialisation Systèmes Distribués & Big Data.
Deux ans chez Thales Services (mission BNP Paribas) sur une plateforme de
collecte et traitement de données : Java, Spark, Kafka, Flink, Elasticsearch,
Hadoop. Puis plusieurs années en musique (Conservatoire de Toulouse, ingénieur
du son), avec maintien d'une pratique du développement en Python.

Retour vers l'ingénierie data en cours. IDE : IntelliJ. Cloud retenu : AWS.

## État d'avancement

- [x] Architecture définie
- [x] Périmètre des gares défini
- [x] Squelette de projet
- [ ] Clé API SNCF obtenue
- [ ] Exploration du format des réponses de l'API
- [ ] Schéma des tables
- [ ] Collecteur fonctionnel en local
- [ ] Déploiement Lambda
- [ ] Modèles dbt
- [ ] DAG Airflow
- [ ] Modèle de prédiction
