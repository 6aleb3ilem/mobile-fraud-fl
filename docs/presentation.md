# Plan de présentation (10-15 slides)

## Slide 1 — Titre
Détection de fraude Mobile Money en architecture Edge-Fog-Cloud avec Federated Learning.

## Slide 2 — Contexte
- Croissance des services mobiles en Mauritanie.
- Besoin de sécurité et de confiance.

## Slide 3 — Problématique
- Détecter la fraude sans centraliser les données sensibles.

## Slide 4 — Objectifs
- Simulation réaliste.
- Détection locale.
- Agrégation fédérée.
- Monitoring temps réel.

## Slide 5 — Architecture globale
Schéma Edge (agences) → Fog (Spark) → Cloud (FedAvg) + Kafka + Dashboard.

## Slide 6 — Dataset synthétique
- Variables clés (montant, fréquence, heure, type, localisation...).
- Label fraude/non fraude.

## Slide 7 — Comportements frauduleux simulés
- High amount, burst, night activity, location shift, risky agent.

## Slide 8 — Edge (entraînement local)
- Modèle SGD logistic.
- Calcul score de risque.
- Envoi d'updates de paramètres.

## Slide 9 — Cloud (FedAvg)
- Agrégation pondérée des modèles locaux.
- Publication du modèle global.

## Slide 10 — Fog (Spark)
- Consommation des flux Kafka.
- Statistiques micro-batch par région.

## Slide 11 — Dashboard
- Transactions suspectes.
- Fraudes détectées.
- Régions touchées.
- Évolution métrique globale.

## Slide 12 — Résultats attendus
- Alertes temps réel.
- Itérations fédérées.
- Monitoring visible et interprétable.

## Slide 13 — Limites
- Données synthétiques.
- Simplifications FL/Spark.

## Slide 14 — Améliorations futures
- Validation plus robuste.
- Détection avancée (séquences temporelles).
- Déploiement cloud réel.

## Slide 15 — Conclusion
Architecture pédagogique, cohérente, exécutable localement, adaptée à un mémoire de master.
