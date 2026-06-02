import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kurtosis
from scipy.signal import spectrogram


# =============================================================================
# 1. CHARGEMENT DES DONNEES
# =============================================================================

df = pd.read_csv("vibrations.csv")

t = df["timestamp"].values
x = df["x"].values
y = df["y"].values
z = df["z"].values

Fe = (len(t) - 1) / (t[-1] - t[0])
print("Frequence d'echantillonnage effective : {:.2f} Hz".format(Fe))
print("Frequence de Nyquist (max observable)  : {:.2f} Hz".format(Fe / 2))


# =============================================================================
# 2. SIGNAL TEMPOREL
# =============================================================================

fig, axes = plt.subplots(3, 1, figsize=(12, 6), sharex=True)
fig.suptitle("Signal temporel", fontsize=14)

axes[0].plot(t, x, color="royalblue", linewidth=0.5)
axes[0].set_ylabel("X (g)")
axes[0].set_ylim(-0.2, 0.2)
axes[1].plot(t, y, color="tomato", linewidth=0.5)
axes[1].set_ylabel("Y (g)")
axes[1].set_ylim(-0.2, 0.2)
axes[2].plot(t, z, color="seagreen", linewidth=0.5)
axes[2].set_ylabel("Z (g)")
axes[2].set_ylim(0.8, 1.1)
axes[2].set_xlabel("Temps (s)")

plt.tight_layout()
plt.show()


# =============================================================================
# 3. SPECTRE FREQUENTIEL (FFT)
# =============================================================================

def plot_fft(signal, Fe, label, color):
    N = len(signal)
    signal_centre = signal - np.mean(signal)
    fft = np.abs(np.fft.rfft(signal_centre)) / N
    freqs = np.fft.rfftfreq(N, d=1 / Fe)
    plt.plot(freqs, fft, color=color, linewidth=0.8, label=label)

fig, ax = plt.subplots(figsize=(12, 4))
fig.suptitle("Spectre frequentiel (FFT)", fontsize=14)
plot_fft(x, Fe, "X", "royalblue")
plot_fft(y, Fe, "Y", "tomato")
plot_fft(z, Fe, "Z", "seagreen")
plt.xlabel("Frequence (Hz)")
plt.ylabel("Amplitude (g)")
plt.legend()
plt.ylim(0, 0.008)
plt.tight_layout()
plt.show()


# =============================================================================
# 4. RMS
# =============================================================================

fenetre = int(round(Fe))   # ~1 seconde d'echantillons
rms_x, rms_y, rms_z, temps_rms = [], [], [], []

for i in range(0, len(x) - fenetre, fenetre):
    rms_x.append(np.sqrt(np.mean(x[i:i + fenetre] ** 2)))
    rms_y.append(np.sqrt(np.mean(y[i:i + fenetre] ** 2)))
    rms_z.append(np.sqrt(np.mean(z[i:i + fenetre] ** 2)))
    temps_rms.append(t[i])

fig, ax = plt.subplots(figsize=(12, 3))
ax.plot(temps_rms, rms_x, label="RMS X", color="royalblue")
ax.plot(temps_rms, rms_y, label="RMS Y", color="tomato")
ax.plot(temps_rms, rms_z, label="RMS Z", color="seagreen")
ax.set_xlabel("Temps (s)")
ax.set_ylabel("RMS (g)")
ax.set_title("RMS glissant - fenetre de 1 seconde")
ax.legend()
ax.set_ylim(0, 1.2)
plt.tight_layout()
plt.show()


# =============================================================================
# 5. KURTOSIS
# =============================================================================

kurt_x, kurt_y, kurt_z = [], [], []

for i in range(0, len(x) - fenetre, fenetre):
    kurt_x.append(kurtosis(x[i:i + fenetre], fisher=True))
    kurt_y.append(kurtosis(y[i:i + fenetre], fisher=True))
    kurt_z.append(kurtosis(z[i:i + fenetre], fisher=True))

fig, ax = plt.subplots(figsize=(12, 3))
ax.plot(temps_rms, kurt_x, label="Kurtosis X", color="royalblue")
ax.plot(temps_rms, kurt_y, label="Kurtosis Y", color="tomato")
ax.plot(temps_rms, kurt_z, label="Kurtosis Z", color="seagreen")
ax.axhline(y=0, color="gray", linestyle="--", label="Normal (0, loi gaussienne)")
ax.axhline(y=3, color="orange", linestyle="--", label="Alerte (exces de 3)")
ax.set_xlabel("Temps (s)")
ax.set_ylabel("Kurtosis (exces, Fisher)")
ax.set_title("Kurtosis glissant - fenetre de 1 seconde")
ax.legend()
ax.set_ylim(-2, 12)
plt.tight_layout()
plt.show()


# =============================================================================
# 6. SPECTROGRAMME
# =============================================================================

nperseg = min(256, len(x))

fig, axes = plt.subplots(3, 1, figsize=(12, 8))
fig.suptitle("Spectrogramme", fontsize=14)

for ax, signal, label, cmap in zip(
    axes, [x, y, z], ["X", "Y", "Z"], ["Blues", "Reds", "Greens"]
):
    f, t_spec, Sxx = spectrogram(signal - np.mean(signal), fs=Fe, nperseg=nperseg)
    ax.pcolormesh(t_spec, f, 10 * np.log10(Sxx + 1e-10), cmap=cmap, shading="gouraud")
    ax.set_ylabel("{} - Freq (Hz)".format(label))
    ax.set_ylim(0, Fe / 2)   # toute la bande observable, plus de 50 Hz en dur

axes[-1].set_xlabel("Temps (s)")
plt.tight_layout()
plt.show()
