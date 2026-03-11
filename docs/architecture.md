# Architecture pédagogique Edge-Fog-Cloud

## Vue d'ensemble

Le projet implémente une chaîne simple et exécutable localement :

1. **Simulator (Data source)**
   - Génère des transactions synthétiques Mobile Money (Mauritanie).
   - Publie les transactions sur Kafka (`transactions`) et certaines alertes sur `alerts`.

2. **Edge Nodes (Nouakchott, Rosso, Kaedi)**
   - Consomment les transactions de leur région.
   - Entraînent un classifieur local (SGD logistic) sur des mini-batches.
   - Émettent les mises à jour de paramètres vers `local_model_updates`.
   - Émettent des alertes de risque vers `alerts`.

3. **Fog Layer (Spark)**
   - Consomme `transactions` et `alerts`.
   - Produit des statistiques micro-batch (volume, fraudes, montants moyens par région).
   - Sauvegarde des snapshots JSON pour le dashboard.

4. **Cloud Aggregator (FedAvg)**
   - Récupère les mises à jour locales des Edge.
   - Agrège les paramètres avec FedAvg (pondération par nombre d'échantillons).
   - Publie les updates globales sur `global_model_updates`.

5. **Global Model Manager**
   - Persiste l'état du modèle global.
   - Maintient un historique de métriques globales simplifiées.

6. **Dashboard Streamlit**
   - Lit les snapshots Fog + historique Cloud.
   - Affiche transactions, fraudes, régions touchées, et évolution du modèle global.

## Topics Kafka

- `transactions`
- `alerts`
- `local_model_updates`
- `global_model_updates`

## Simplifications assumées

- FedAvg appliqué sur les paramètres d'un classifieur linéaire compatible.
- Métrique globale `accuracy_proxy` pédagogique (pas une vraie validation centralisée).
- Spark utilisé en micro-batch sur messages consommés (pas cluster Spark complet).
