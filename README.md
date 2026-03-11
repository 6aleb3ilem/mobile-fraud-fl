# Mobile Fraud FL — Détection de fraude dans les transactions financières mobiles

Prototype pédagogique **Edge-Fog-Cloud** avec **Federated Learning (FedAvg)**, **Kafka**, **Spark (PySpark)** et **Streamlit**, orienté contexte Mauritanie (Bankily, Masrivi, Sadad) avec **données 100% synthétiques**.

---

## 1) Contexte
Les services Mobile Money facilitent les paiements, transferts et retraits. En parallèle, les risques de fraude augmentent (transactions anormales, rafales, activités nocturnes, incohérences géographiques).

Ce projet montre comment bâtir une architecture distribuée où :
- les agences (Edge) entraînent localement,
- un Fog fait le monitoring intermédiaire,
- un Cloud agrège les modèles,
- un dashboard visualise les alertes et métriques.

---

## 2) Problématique
Comment détecter la fraude en quasi temps réel **sans centraliser les données sensibles** de chaque agence ?

---

## 3) Objectifs
- Générer un dataset synthétique réaliste de transactions mobiles.
- Entraîner des classifieurs locaux au niveau Edge.
- Transporter événements/mises à jour via Kafka.
- Produire des statistiques streaming via Spark.
- Agréger les paramètres locaux via FedAvg.
- Visualiser indicateurs et alertes dans Streamlit.

---

## 4) Architecture
Voir aussi `docs/architecture.md`.

- **A. simulator** : génération + publication Kafka.
- **B. edge_nodes** : entraînement local et détection locale.
- **C. kafka** : topics de flux et updates FL.
- **D. fog_layer** : monitoring Spark micro-batch.
- **E. cloud_aggregator** : FedAvg + gestion modèle global.
- **F. dashboard** : visualisation interactive.

### Topics Kafka
- `transactions`
- `alerts`
- `local_model_updates`
- `global_model_updates`

---

## 5) Technologies utilisées
- Python 3.11+
- Docker / Docker Compose
- Apache Kafka + Zookeeper
- PySpark
- scikit-learn, pandas, numpy
- Streamlit + Plotly

---

## 6) Structure du projet

```text
mobile-fraud-fl/
├── README.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── .env.example
├── docs/
│   ├── architecture.md
│   ├── report.md
│   └── presentation.md
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
│   └── run_local_demo.sh
├── tests/
│   ├── __init__.py
│   └── test_data_generation.py
└── notebooks/
    └── exploration.ipynb
```

---

## 7) Installation

### Option A — Python local
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Option B — Docker Compose (recommandé)
```bash
docker compose up --build
```

---

## 8) Lancement pas à pas

### 1) Générer un dataset offline
```bash
python -m simulator.generate_transactions --rows 3000 --output data/raw/simulated_transactions.csv
```

### 2) Lancer les tests minimaux
```bash
pytest -q
```

### 3) Lancer la stack complète
```bash
docker compose up --build
```

### 4) Ouvrir le dashboard
- URL : http://localhost:8501

---

## 9) Explication des services
- **simulator** : publie en boucle des transactions JSON.
- **edge_nouakchott / edge_rosso / edge_kaedi** : entraînement local, alertes, updates FL.
- **fog_streaming** : calcul de stats régionales (Spark local).
- **cloud_aggregator** : FedAvg sur paramètres locaux.
- **global_model_manager** : historique modèle global.
- **dashboard** : visualisation des outputs persistés.

---

## 10) Pipeline de bout en bout
1. Une transaction est simulée et poussée dans `transactions`.
2. Un nœud Edge régional l'ingère, met à jour son batch local, puis entraîne périodiquement.
3. Le nœud Edge publie sa mise à jour de modèle (`local_model_updates`) + alertes (`alerts`).
4. Le Fog agrège les statistiques en micro-batch et écrit des snapshots JSON.
5. Le Cloud applique FedAvg et publie `global_model_updates`.
6. Le dashboard affiche les indicateurs courants.

---

## 11) Résultats attendus
- Alertes de transactions suspectes visibles.
- Régions les plus exposées à la fraude identifiables.
- Historique d'évolution du modèle global (proxy).
- Démonstration claire de la chaîne Edge-Fog-Cloud + FL.

---

## 12) Limites
- Données synthétiques uniquement (pas de vérité terrain réelle).
- FedAvg simplifié sur modèle linéaire.
- Spark déployé en mode local micro-batch (pas cluster distribué complet).

---

## 13) Pistes d'amélioration
- Validation globale plus robuste avec dataset de test fixe.
- Détection séquentielle (LSTM/Transformers légers) pour patterns temporels.
- Gestion de dérive conceptuelle.
- Sécurisation avancée des mises à jour fédérées.

---

## 14) Livrables académiques
- Rapport : `docs/report.md`
- Présentation : `docs/presentation.md`
- Architecture : `docs/architecture.md`

