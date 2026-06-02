# Capteur autonome de maintenance prédictive

Système embarqué auto-alimenté par thermoélectricité pour analyser les vibrations d'une machine industrielle et anticiper les pannes.

## Principe

Un générateur thermoélectrique (TEG) convertit une différence de température en énergie. Cette énergie alimente un ESP32 qui réveille périodiquement un accéléromètre, mesure les vibrations, et transmet les données en Bluetooth Low Energy. L'analyse pour la maintenance prédictive est ensuite réalisée sur un ordinateur.

Pas de batterie. Pas de maintenance. Pas de câble.

## Architecture

```
TEG → BQ25570 (MPPT) → Supercondensateur → ESP32 + BMA400 → BLE → PC (analyse)
```

## Composants

| Composant | Référence | Rôle |
|-----------|-----------|------|
| TEG | SP1848-27145 | Récupération d'énergie (effet Seebeck) |
| Convertisseur | BQ25570 (CJMCU-2557) | Power management, démarrage à froid 330 mV |
| Stockage | Supercondensateurs 5 F VPF506M3R8 | Stockage tampon |
| Accéléromètre | SparkFun BMA400 (SEN-21208) | 3 axes, 15 µA |
| Microcontrôleur | uPesy ESP32 Wroom Low Power v1.2 | Traitement + BLE, deep sleep |

## Câblage du capteur (I2C)

| BMA400 | ESP32 |
|--------|-------|
| 3V3 | 3V3 |
| GND | GND |
| SDA | GPIO 21 |
| SCL | GPIO 22 |

Plage par défaut du BMA400 : +/-4 g, 12 bits, soit 512 LSB/g (valeur reprise côté PC pour la conversion en g).

## Fichiers

| Fichier | Description |
|---------|-------------|
| `Presentation.pdf` | Support de présentation du TIPE |
| `ESP32.py` | Firmware embarqué : cycle réveil, acquisition BMA400 en I2C, transmission BLE, deep sleep (MicroPython, à enregistrer comme `main.py`) |
| `Reception.py` | Réception BLE sur PC, horodatage réel, conversion en g, enregistrement CSV |
| `Analyse.py` | Analyse vibratoire : FFT, RMS, kurtosis, spectrogramme (Fe déduite des timestamps) |
| `Courbes_TEG.py` | Caractérisation du TEG (modèle de Thévenin, puissance vs résistance de charge) |
| `Courbe_BQ.py` | Courbe de charge des supercondensateurs via le BQ25570 |
| `Vibrations_sain.csv` | Acquisition de référence, état sain |
| `Vibrations_defaillant.csv` | Acquisition, état dégradé |
| `Vibrations.csv` | Acquisition de test, état sain |

## Utilisation

1. Enregistrer `ESP32.py` sous le nom `main.py` sur l'ESP32 (Thonny : Fichier, Enregistrer sous, MicroPython device, nom `main.py`).
2. Alimenter l'ESP32 : il démarre seul et attend la connexion BLE.
3. Lancer `Reception.py` sur le PC : les données sont enregistrées dans un CSV.
4. Lancer `Analyse.py` sur le CSV obtenu pour produire les graphes.

Dépendances PC : Python 3, bleak, pandas, numpy, scipy, matplotlib, nest_asyncio.

## Résultats

Énergie : puissance max du TEG d'environ 78 mW en pratique (93 mW en théorie). Consommation moyenne du système d'environ 1 mW, soit une large marge énergétique.

Vibrations : identification de la fréquence de rotation et de ses harmoniques par FFT, suivi de l'énergie vibratoire par RMS, détection de chocs par kurtosis. Comparaison entre un état sain et un état dégradé.

## Limites

Dissipateur thermique surdimensionné, démarrage à froid lent, dégradation du TEG dans le temps, portée de transmission BLE limitée, détection non temps réel (analyse différée sur le PC).
