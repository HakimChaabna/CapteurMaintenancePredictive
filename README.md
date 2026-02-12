# Capteur autonome de maintenance prédictive

Système embarqué auto-alimenté par thermoélectricité pour analyser les vibrations d'une machine industrielle et anticiper les pannes.

## Principe

Un générateur thermoélectrique (TEG) convertit une différence de température en énergie. Cette énergie alimente un ESP32 qui réveille périodiquement un accéléromètre, mesure les vibrations, et transmet les données en Bluetooth Low Energy.

Pas de batterie. Pas de maintenance. Pas de câble.

## Architecture

```
TEG → BQ25570 (MPPT) → Supercondensateur → ESP32 + BMA400 → BLE
```

## Composants

| Composant | Rôle |
|-----------|------|
| TEG | Récupération d'énergie (effet Seebeck) |
| BQ25570 | Power management, démarrage à froid 330 mV |
| LIC | Stockage tampon |
| BMA400 | Accéléromètre 3 axes, 3.5 µA |
| ESP32 | Traitement + transmission BLE, deep sleep ~10 µA |

## État

🚧 Projet en cours — phase assemblage et câblage.

Le code MicroPython de l'ESP32 sera ajouté ici au fur et à mesure du développement (acquisition, traitement du signal, transmission BLE, gestion du deep sleep).
