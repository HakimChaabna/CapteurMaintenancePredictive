import numpy as np
import matplotlib.pyplot as plt

# ============================================================
#  DONNEES EXPERIMENTALES  (a modifier avec tes valeurs)
# ============================================================
# Resistances de charge (en ohms) -- on retire le point R=0 (a vide)
R_exp = np.array([1.0, 1.1111, 1.25, 1.4285, 1.6667, 2.0, 2.5, 3.3333, 5.0, 10.0])
# Tensions mesurees aux bornes de la charge (en volts)
U_exp = np.array([0.21, 0.25, 0.28, 0.32, 0.36, 0.39, 0.44, 0.50, 0.60, 0.75])

# Puissance experimentale : P = U^2 / R  (en milliwatts)
P_exp = (U_exp**2 / R_exp) * 1000  # *1000 pour passer en mW

# ============================================================
#  PARAMETRES DU MODELE DE THEVENIN
# ============================================================
V_OC = 1.02      # tension a vide mesuree (volts)
R_int = 2.8      # resistance interne (ohms)

# ============================================================
#  COURBE THEORIQUE : P(R) = V_OC^2 * R / (R_int + R)^2
# ============================================================
R_theo = np.linspace(0.1, 12, 500)  # plage continue de resistances
P_theo = (V_OC**2 * R_theo / (R_int + R_theo)**2) * 1000  # en mW

# ============================================================
#  FIGURE
# ============================================================
plt.figure(figsize=(8, 5))
plt.plot(R_theo, P_theo, '-', color='black', linewidth=2,
         label='Modele de Thevenin (theorique)')
plt.plot(R_exp, P_exp, 'o-', color='#8db62a', markersize=8,
         linewidth=1.5, label='Points experimentaux')
plt.axvline(R_int, color='gray', linestyle='--', alpha=0.6,
            label=f'R_int = {R_int} Ohm')
plt.xlabel("Resistance de charge R (Ohm)")
plt.ylabel("Puissance P (mW)")
plt.title("Comparaison experience / theorie  P = f(R)")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()