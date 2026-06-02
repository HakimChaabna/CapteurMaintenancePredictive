import asyncio
import struct
import csv
import time
from bleak import BleakScanner, BleakClient
import nest_asyncio

nest_asyncio.apply()

CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

# =============================================================================
# INITIALISATION DU FICHIER CSV
# =============================================================================

filename = "Vibrations.csv"
csvfile = open(filename, 'w', newline='')
writer = csv.writer(csvfile)
writer.writerow(["timestamp", "x", "y", "z"])  
print("Enregistrement dans : " + filename)

# =============================================================================
# TRAITEMENT DES DONNEES RECUES
# Horodatage REEL : on note l'instant d'arrivee de chaque paquet avec une
# horloge monotone (perf_counter), au lieu de fabriquer un temps a 200 Hz.
# Les 6 echantillons d'un paquet arrivent ensemble : on les repartit
# regulierement dans l'intervalle reel ecoule depuis le paquet precedent.
# =============================================================================

sample_count = 0
premier_paquet = None      # instant d'arrivee du tout premier paquet
dernier_t = None           # instant (relatif) du paquet precedent


def handle_data(sender, data):
    global sample_count, premier_paquet, dernier_t

    t_arrivee = time.perf_counter()
    if premier_paquet is None:
        premier_paquet = t_arrivee

    n = len(data) // 6                 # nb d'echantillons dans CE paquet
    if n == 0:
        return
    t_paquet = t_arrivee - premier_paquet

    # intervalle reel depuis le paquet precedent, reparti sur n echantillons
    if dernier_t is not None:
        dt_intra = (t_paquet - dernier_t) / n
    else:
        dt_intra = 0.005               # 1er paquet : 5 ms suppose
    dernier_t = t_paquet

    for k in range(n):
        x, y, z = struct.unpack("<hhh", data[k * 6:k * 6 + 6])
        ax, ay, az = x / 512, y / 512, z / 512
        t = round(t_paquet - (n - 1 - k) * dt_intra, 5)
        writer.writerow([t, ax, ay, az])
        sample_count += 1

    if sample_count % 200 == 0:
        print(str(sample_count) + " echantillons (" + format(t_paquet, ".1f") + "s)")


# =============================================================================
# CONNEXION BLE ET ACQUISITION
# =============================================================================

async def main():
    print("Recherche ESP32-IMU...")
    device = await BleakScanner.find_device_by_name("ESP32-IMU")
    if not device:
        print("Capteur non trouve")
        return

    async with BleakClient(device) as client:
        print("Connecte !")
        await client.start_notify(CHAR_UUID, handle_data)
        await asyncio.sleep(60)        # enregistre pendant 60 secondes
        await client.stop_notify(CHAR_UUID)


try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
finally:
    csvfile.close()
    if dernier_t and dernier_t > 0:
        fe_reelle = sample_count / dernier_t
        print("Frequence reelle moyenne : " + format(fe_reelle, ".1f") + " Hz")
    print("Termine. " + str(sample_count) + " echantillons dans " + filename)
