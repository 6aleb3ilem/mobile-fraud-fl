# Rapport académique — Détection de fraude Mobile Money par Federated Learning

## 1. Introduction
La fraude dans les transactions financières mobiles est un enjeu majeur pour les services numériques en Afrique de l'Ouest. Ce projet propose une architecture distribuée **Edge-Fog-Cloud** combinée à un **Federated Learning (FL)** simple pour détecter des comportements suspects en temps quasi réel.

## 2. Contexte mauritanien
La Mauritanie connaît une adoption croissante des services Mobile Money (ex. Bankily, Masrivi, Sadad). Dans ce contexte, les agences locales jouent un rôle important dans l'exécution et la supervision des transactions. Le projet reproduit ce cadre avec des **données synthétiques uniquement**.

## 3. Problématique
Comment détecter des fraudes mobiles en limitant le partage de données sensibles et en conservant un monitoring temps réel ?

## 4. Objectifs
### Objectif général
Concevoir un prototype local exécutable de détection de fraude Mobile Money avec architecture Edge-Fog-Cloud et FL.

### Objectifs spécifiques
- Générer un dataset synthétique réaliste.
- Entraîner des modèles locaux sur nœuds Edge.
- Agréger les modèles avec FedAvg au niveau Cloud.
- Analyser les flux en Fog avec Spark.
- Visualiser alertes et métriques dans un dashboard.

## 5. Architecture Edge-Fog-Cloud
- **Edge** : agences régionales simulées (Nouakchott, Rosso, Kaedi).
- **Fog** : traitement intermédiaire et monitoring Spark.
- **Cloud** : agrégation des mises à jour de modèles (FedAvg).
- **Kafka** : bus de messages inter-composants.

## 6. Principe du Federated Learning
Chaque nœud Edge entraîne localement un classifieur (SGD logistic). Les paramètres (`coef`, `intercept`) et le volume de données sont envoyés au Cloud. Le Cloud calcule une moyenne pondérée (FedAvg) :

\[
\theta^{global} = \sum_{k=1}^{K} \frac{n_k}{\sum_j n_j} \theta_k
\]

## 7. Pipeline Kafka / Spark
1. Simulator → topic `transactions`.
2. Edge → topics `alerts` et `local_model_updates`.
3. Fog consomme `transactions` + `alerts`, calcule snapshots analytiques.
4. Cloud FedAvg publie sur `global_model_updates`.
5. Dashboard lit les fichiers de sorties.

## 8. Simulation des données
Variables intégrées : montant, heure, fréquence, type, géolocalisation, changement d'appareil, agent, région, etc.
Scénarios de fraude simulés :
- montant anormalement élevé,
- rafales de transactions,
- activité nocturne,
- localisation incohérente,
- agent à risque.

## 9. Méthode de détection
- **Modèle local** : `SGDClassifier(loss='log_loss')`.
- **Variables mixtes** : numériques + catégorielles (OneHot).
- **Métriques locales** : accuracy, precision, recall, f1.

## 10. Résultats attendus
- Détection de transactions à risque dans `alerts`.
- Agrégation périodique de modèles locaux en global.
- Dashboard montrant évolution d'un score global et régions les plus touchées.

## 11. Discussion
La solution est volontairement minimale : elle illustre les concepts FL et streaming sans infrastructure cloud réelle. Elle est adaptée à un projet de master pour démonstration/explication.

## 12. Limites
- Données synthétiques uniquement.
- Pas de validation globale sur jeu de test central réel.
- Spark utilisé en mode local micro-batch.

## 13. Conclusion
Le prototype démontre qu'une architecture Edge-Fog-Cloud avec FL peut être implémentée de façon pédagogique, reproductible et portable via Docker Compose.

## 14. Références
1. Konečnỳ et al., Federated Learning (2016).
2. McMahan et al., Communication-Efficient Learning (2017).
3. Documentation Apache Kafka.
4. Documentation Apache Spark Structured Streaming.
5. Documentation scikit-learn.
