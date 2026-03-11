# Mobile Fraud FL - Détection de fraude dans les transactions financières mobiles

Projet pédagogique **Edge-Fog-Cloud + Federated Learning** pour la détection de fraude Mobile Money en Mauritanie.

> Contexte métier simulé : services type **Bankily, Masrivi, Sadad** (aucune donnée réelle utilisée).

---

## 1) Contexte et problématique
La digitalisation rapide du Mobile Money améliore l'inclusion financière, mais augmente aussi les risques de fraude : usurpation, phishing, blanchiment, transactions anormales nocturnes, etc.

Une approche centralisée classique pose deux problèmes:
- confidentialité des données sensibles clients,
- latence et coûts de transport de données.

Ce projet propose une architecture distribuée :
- **Edge** : entraînement local dans les agences (les données restent locales),
- **Fog** : monitoring streaming intermédiaire,
- **Cloud** : agrégation globale des paramètres via **FedAvg**.

---

## 2) Objectifs
- Générer un dataset synthétique réaliste de transactions mobiles.
- Détecter localement le risque de fraude.
- Transporter événements et mises à jour via Kafka.
- Surveiller en temps réel via Spark Streaming.
- Agréger les modèles locaux avec FedAvg.
- Afficher les alertes et métriques dans un dashboard Streamlit.

---

## 3) Architecture choisie (simple et fonctionnelle)

```text
[Simulator JSON] -> Kafka topic: transactions
      |                 |
      |                 v
      |             [Fog / Spark Streaming] --> stats temps réel
      v
[Edge nodes (Nouakchott, Rosso, Kaédi)]
  entraînement local + métriques
      |
      v
Kafka topic: local_model_updates
      |
      v
[Cloud Aggregator / FedAvg]
  -> global_model_update.json
  -> Kafka topic: global_model_updates
      |
      v
[Dashboard Streamlit]
```

### Simplification pédagogique assumée
- Le modèle local est un **SGDClassifier logistique** (linéaire), choisi car ses paramètres peuvent être agrégés simplement.
- FedAvg est appliqué sur les coefficients/intercepts pondérés par le nombre d'échantillons.
- Le dashboard inclut un score de risque heuristique simple pour visualiser rapidement les alertes.

---

## 4) Technologies
- Python 3.11+
- Docker / Docker Compose
- Apache Kafka
- PySpark Structured Streaming
- scikit-learn, pandas, numpy
- Streamlit + Plotly
- joblib
- pytest

---

## 5) Structure du projet

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
│   ├── generate_transactions.py
│   └── producer_kafka.py
├── edge/
│   ├── edge_node_base.py
│   ├── edge_nouakchott.py
│   ├── edge_rosso.py
│   ├── edge_kaedi.py
│   └── local_training.py
├── fog/
│   └── spark_streaming_job.py
├── cloud/
│   ├── fedavg_aggregator.py
│   └── global_model_manager.py
├── dashboard/
│   └── app.py
├── common/
│   ├── config.py
│   ├── schemas.py
│   ├── utils.py
│   └── metrics.py
├── scripts/
│   └── run_local_pipeline.sh
└── tests/
    └── test_data_generation.py
```

---

## 6) Description des services

### A. `simulator`
- Génère un dataset synthétique avec champs demandés:
  - `transaction_id`, `user_id`, `agent_id`, `region`, `amount`, `hour`, `day_of_week`, `transaction_type`, `latitude`, `longitude`, `transactions_last_1h`, `avg_amount_7d`, `deviation_from_user_pattern`, `device_changed`, `label_fraud`.
- Injecte plusieurs scénarios de fraude :
  - montant élevé,
  - burst nocturne,
  - incohérence géographique,
  - transferts rapides,
  - agent à risque.
- Peut publier les transactions dans Kafka.

### B. `edge`
- Simule 3 noeuds régionaux : Nouakchott, Rosso, Kaédi.
- Entraîne un modèle local (SGD logistique).
- Sauvegarde le modèle local.
- Publie les updates locales vers `local_model_updates`.

### C. `fog`
- Lit le topic `transactions` avec Spark Structured Streaming.
- Produit des agrégats temps réel (volume, fraude, montant moyen).

### D. `cloud`
- Consomme les updates locales.
- Applique FedAvg (pondération par `sample_count`).
- Sauvegarde le modèle global (`data/models/global_model_update.json`).
- Publie une update globale.

### E. `dashboard`
- Affiche transactions, alertes suspectes, fraudes bloquées (proxy), distribution du risque, fraudes par région, métriques globales.

---

## 7) Installation et exécution

## Option 1 - Exécution locale rapide (sans Kafka/Spark)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python simulator/generate_transactions.py --samples 5000 --fraud-ratio 0.12 --output data/raw/transactions.csv
python edge/local_training.py --csv data/raw/transactions.csv
streamlit run dashboard/app.py
```

## Option 2 - Pipeline Docker Compose
```bash
docker compose up --build kafka
# dans un autre terminal
docker compose up --build simulator edge_trainer cloud_aggregator dashboard
# optionnel monitoring Spark
docker compose up --build fog_streaming
```

Dashboard: http://localhost:8501

---

## 8) Pipeline de bout en bout
1. Générer les transactions synthétiques.
2. Publier vers Kafka (`transactions`).
3. Entraîner localement les Edge nodes.
4. Publier les paramètres locaux (`local_model_updates`).
5. Agréger via FedAvg dans le Cloud.
6. Exposer les résultats dans le dashboard.

---

## 9) Résultats attendus
- Dataset synthétique généré automatiquement.
- Trois modèles locaux sauvegardés (`edge_*.joblib`).
- Un fichier global FedAvg sauvegardé.
- Dashboard affichant:
  - total transactions,
  - nombre de fraudes,
  - alertes suspectes,
  - distribution du risque,
  - régions les plus touchées,
  - infos modèle global.

---

## 10) Métriques d'évaluation
Au minimum:
- Accuracy
- Precision
- Recall
- F1-score

Les métriques locales sont calculées à l'entraînement Edge. Le dashboard affiche des indicateurs de suivi opérationnel.

---

## 11) Commandes utiles
```bash
# Génération dataset
python simulator/generate_transactions.py --samples 3000 --fraud-ratio 0.15 --output data/raw/transactions.csv

# Entraînement local + publication updates
python edge/local_training.py --csv data/raw/transactions.csv --publish

# Agrégation globale
python cloud/fedavg_aggregator.py --expected-updates 3

# Tests
pytest -q
```

---

## 12) Questions possibles du professeur (et bonnes réponses)

1. **Pourquoi du Federated Learning ici ?**
   - Pour collaborer entre agences sans partager les données brutes clients.

2. **Pourquoi un modèle linéaire ?**
   - Pour garder une solution simple, explicable, et compatible avec une agrégation FedAvg pédagogique.

3. **Quel rôle de Kafka ?**
   - Bus d'événements pour transactions, alertes, et updates de modèles.

4. **Quel rôle du Fog ?**
   - Monitoring temps réel intermédiaire sans surcharge du Cloud.

5. **Limites de la version étudiante ?**
   - FedAvg mono-round simplifié, pas de chiffrement avancé ni orchestration FL complète.

6. **Comment améliorer ?**
   - Ajouter rounds FL multiples, évaluation globale automatisée, détection drift, sécurité (DP/secure aggregation), MLOps.

---

## 13) Livrables académiques conseillés
- Schéma d'architecture Edge-Fog-Cloud.
- Journal d'expériences (fraud_ratio, seuil de risque, performances).
- Captures dashboard.
- Discussion sur confidentialité / conformité BCM.

---

## 14) Sources de référence (contexte)
- Banque Centrale de Mauritanie : https://www.bcm.mr
- Kaggle Credit Card Fraud Dataset : https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
- GSMA Mobile Money : https://www.gsma.com/mobilemoney/

