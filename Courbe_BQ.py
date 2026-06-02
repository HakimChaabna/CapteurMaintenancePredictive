import numpy as np
import matplotlib.pyplot as plt

# ============================================================
#  DONNEES EXPERIMENTALES
# ============================================================
# Tension V_bat relevee toutes les 15 secondes (en volts)
V_bat = [0.08, 0.48, 0.74, 0.88, 1.01, 1.21, 1.41, 1.6, 1.74, 1.86,
         1.95, 1.99, 2.04, 2.08, 2.12, 2.16, 2.19, 2.28, 2.37, 2.42,
         2.45, 2.54, 2.56, 2.59, 2.6, 2.64, 2.65, 2.68, 2.7, 2.84,
         2.98, 3.12, 3.29, 3.44, 3.55, 3.66, 3.76, 3.85, 3.92, 3.99,
         4.0, 4.0, 4.0]

pas = 15

# Axe du temps 
temps_s = np.arange(len(V_bat)) * pas
# Conversion en minutes pour un affichage plus lisible
temps_min = temps_s / 60

# ============================================================
#  TRACE DE LA COURBE
# ============================================================
plt.figure(figsize=(9, 5.5))
plt.plot(temps_min, V_bat, 'o-', color='#8db62a', markersize=5,
         linewidth=1.5, label='V_bat mesuree')

# Ligne horizontale pour reperer V_OV (tension de regulation a 4V)
plt.axhline(4.0, color='black', linestyle='--', alpha=0.7,
            label='V_OV = 4 V (regulation)')

plt.xlabel("Temps (min)")
plt.ylabel("Tension V_bat (V)")
plt.title("Charge des supercondensateurs via le BQ25570")
plt.grid(True, alpha=0.3)
plt.legend()
plt.ylim(0, 4.5)
plt.tight_layout()
plt.show()

