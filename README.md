# Détection de fraude dans les transactions financières mobiles (Edge-Fog-Cloud + Federated Learning)

Projet pédagogique (version simple et exécutable localement) pour simuler la détection de fraude Mobile Money dans un contexte mauritanien (Bankily, Masrivi, Sadad comme référence métier), avec **données 100% synthétiques**.

## 1) Objectif
Construire une chaîne complète locale avec Docker Compose :
- **Edge** : entraînement local par agence/région.
- **Fog** : monitoring streaming via Spark.
- **Cloud** : agrégation de modèles avec FedAvg simplifié.
- **Kafka** : bus d’événements.
- **Dashboard** : visualisation des alertes et métriques.

## 2) Simplifications assumées
Pour garder le projet clair et exécutable sur machine étudiante :
- Modèle local = `SGDClassifier(loss='log_loss')` (logistic regression en apprentissage linéaire).
- FedAvg = moyenne pondérée des coefficients/intercepts (pondération par volume de données local).
- Spark Streaming fait un monitoring régional temps réel (pas d’orchestration ML avancée côté Spark).

## 3) Architecture
```text
simulator -> Kafka(topic: transactions) -> fog(Spark Streaming) -> stats temps réel
edge nodes -> Kafka(topic: local_model_updates) -> cloud FedAvg -> global_model_updates
                                                    \
                                                     -> data/models/global_model_update.json
Dashboard Streamlit lit dataset + métriques globales
```

## 4) Arborescence
```text
mobile-fraud-fl/
├── README.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── .env.example
├── data/
│   ├── raw/
│   ├── processed/
│   └── models/
├── simulator/
│   ├── __init__.py
│   ├── generate_transactions.py
│   └── producer_kafka.py
├── edge/
│   ├── __init__.py
│   ├── edge_node_base.py
│   ├── edge_nouakchott.py
│   ├── edge_rosso.py
│   ├── edge_kaedi.py
│   └── local_training.py
├── fog/
│   ├── __init__.py
│   └── spark_streaming_job.py
├── cloud/
│   ├── __init__.py
│   ├── fedavg_aggregator.py
│   └── global_model_manager.py
├── dashboard/
│   ├── __init__.py
│   └── app.py
├── common/
│   ├── __init__.py
│   ├── config.py
│   ├── schemas.py
│   ├── utils.py
│   └── metrics.py
├── scripts/
│   ├── prepare_edge_datasets.py
│   └── run_local_pipeline.sh
└── tests/
    ├── __init__.py
    └── test_data_generation.py
```

## 5) Pipeline détaillé
1. `simulator/generate_transactions.py` génère un CSV synthétique avec patterns normaux + frauduleux.
2. `scripts/prepare_edge_datasets.py` découpe les données pour 3 nœuds (Nouakchott, Rosso, Kaedi).
3. Chaque nœud Edge entraîne localement son modèle (`edge/*.py`) et publie une update.
4. `cloud/fedavg_aggregator.py` agrège les updates locales en modèle global (FedAvg simplifié).
5. `fog/spark_streaming_job.py` surveille en streaming le topic `transactions`.
6. `dashboard/app.py` visualise fraude + métriques globales.

## 6) Données synthétiques générées
Colonnes principales :
- `transaction_id`, `user_id`, `agent_id`, `region`
- `amount`, `hour`, `day_of_week`, `transaction_type`
- `latitude`, `longitude`
- `transactions_last_1h`, `avg_amount_7d`, `deviation_from_user_pattern`, `device_changed`
- `label_fraud`

Exemples de comportements frauduleux simulés :
- montant anormalement élevé,
- fréquence élevée en 1h,
- transactions nocturnes,
- forte déviation du profil habituel,
- changement d’appareil.

## 7) Installation (local sans Docker)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m simulator.generate_transactions --rows 5000
python scripts/prepare_edge_datasets.py
python -m edge.edge_nouakchott
python -m edge.edge_rosso
python -m edge.edge_kaedi
python -m cloud.fedavg_aggregator --mode files
streamlit run dashboard/app.py
```

## 8) Exécution avec Docker Compose
### Lancer la stack
```bash
docker compose up --build
```

### Lancer uniquement le dashboard (si pipeline déjà exécuté)
```bash
docker compose up --build dashboard
```

### Exécuter le pipeline local depuis le conteneur app
```bash
docker compose run --rm app bash -lc "./scripts/run_local_pipeline.sh"
```

## 9) Commandes utiles
Publier les transactions vers Kafka :
```bash
python -m simulator.producer_kafka --input data/raw/transactions_synthetic.csv --sleep 0.05
```

Lancer Spark Streaming manuellement :
```bash
spark-submit fog/spark_streaming_job.py
```

## 10) Métriques suivies
- **Locales (Edge)** : accuracy, precision, recall, F1.
- **Globales (Cloud)** : moyenne des métriques locales + coefficients globaux FedAvg.
- **Monitoring (Fog)** : nombre de transactions et fraudes suspectées par région (streaming).

## 11) Résultats attendus
Après exécution correcte :
- fichiers datasets dans `data/raw/`,
- modèles locaux et updates dans `data/models/`,
- fichier `data/models/global_model_update.json`,
- dashboard accessible sur `http://localhost:8501`.

> Les valeurs finales (métriques exactes, courbes et statistiques) dépendront de ton exécution locale. Elles seront à compléter après ton run.

## 12) Livrables académiques
Les livrables chiffrés finaux (captures, métriques finales, interprétation) dépendent de ton exécution locale du projet. Une fois ton run terminé, tu pourras compléter cette section avec tes résultats observés.
