import asyncio
import struct
import csv
import time
from bleak import BleakScanner, BleakClient
import nest_asyncio

nest_asyncio.apply()

CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

# INITIALISATION DU FICHIER CSV

filename = "vibrations_test.csv"
csvfile = open(filename, 'w', newline='')
writer = csv.writer(csvfile)
writer.writerow(["timestamp", "x", "y", "z"])  # en-tête
print(f"Enregistrement dans : {filename}")

# TRAITEMENT DES DONNÉES REÇUES

sample_count = 0
start_time = time.time()

def handle_data(sender, data):
    global sample_count
    for i in range(0, len(data), 6):
        x, y, z = struct.unpack("<hhh", data[i:i+6])
        ax = x / 512
        ay = y / 512
        az = z / 512
        t = round(sample_count / 200, 4)
        writer.writerow([t, ax, ay, az])
        sample_count += 1

        if sample_count % 200 == 0:
            print(f"{sample_count} échantillons enregistrés ({t:.1f}s)")

# CONNEXION BLE ET ACQUISITION

async def main():
    print("Recherche ESP32-IMU...")
    device = await BleakScanner.find_device_by_name("ESP32-IMU")
    if not device:
        print("Capteur non trouvé")
        csvfile.close()
        return

    async with BleakClient(device) as client:
        print("Connecté !")
        await client.start_notify(CHAR_UUID, handle_data)
        await asyncio.sleep(60)  # enregistre pendant 60 secondes

    csvfile.close()
    print(f"Terminé. {sample_count} échantillons sauvegardés dans {filename}")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())