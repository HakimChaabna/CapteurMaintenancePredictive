from machine import Pin, I2C, deepsleep
import struct
import time
import bluetooth
from micropython import const

# =============================================================================
# CONFIGURATION DU CYCLE
# =============================================================================
DUREE_ACQUISITION_MS = 65000
DUREE_SLEEP_MS = 120000
TIMEOUT_CONNEXION_MS = 30000

# =============================================================================
# CONFIGURATION BLE (Nordic UART Service)
# =============================================================================
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_FLAG_NOTIFY = const(0x0010)

_SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_CHAR_UUID    = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")


class BLEIMU:
    def __init__(self):
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        self._connected = False
        self._handle = None
        self._register()
        self._advertise()

    def _register(self):
        services = (_SERVICE_UUID, ((_CHAR_UUID, _FLAG_NOTIFY),),)
        ((self._handle,),) = self._ble.gatts_register_services((services,))

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            self._connected = True
            print("PC connecte")
        elif event == _IRQ_CENTRAL_DISCONNECT:
            self._connected = False
            print("PC deconnecte")
            self._advertise()

    def _advertise(self):
        name = b"ESP32-IMU"
        payload = bytes([2, 0x01, 0x06, len(name) + 1, 0x09]) + name
        self._ble.gap_advertise(100000, adv_data=payload)

    def send(self, data):
        if self._connected:
            try:
                self._ble.gatts_notify(0, self._handle, data)
            except OSError:
                pass

    @property
    def connected(self):
        return self._connected

# =============================================================================
# CONFIGURATION DU CAPTEUR BMA400
# =============================================================================
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
addr = 0x14

chip_id = i2c.readfrom_mem(addr, 0x00, 1)[0]
assert chip_id == 0x90, "Erreur capteur: " + hex(chip_id)

i2c.writeto_mem(addr, 0x19, b'\x02')
time.sleep_ms(5)

def lire_acceleration():
    data = i2c.readfrom_mem(addr, 0x04, 6)
    brut = struct.unpack("<HHH", data)
    valeurs = []
    for v in brut:
        v = v & 0x0FFF
        if v > 2047:
            v -= 4096
        valeurs.append(v)
    return valeurs              # [x, y, z]


# =============================================================================
# PROGRAMME PRINCIPAL
# A chaque reveil depuis le deep sleep, le programme repart d'ici.
# =============================================================================
print("Reveil - demarrage du cycle")

ble = BLEIMU()
print("En attente de connexion BLE...")

# --- Attente de la connexion du PC (avec timeout) ---
t_debut_attente = time.ticks_ms()
while not ble.connected:
    if time.ticks_diff(time.ticks_ms(), t_debut_attente) > TIMEOUT_CONNEXION_MS:
        print("Pas de connexion, on se rendort")
        deepsleep(DUREE_SLEEP_MS)
    time.sleep_ms(100)

# --- Acquisition pendant 65 secondes ---
print("Connecte - debut acquisition")
SAMPLES_PER_PACKET = 6
buffer = []
interval_us = 5000

t_debut_acq = time.ticks_ms()
while time.ticks_diff(time.ticks_ms(), t_debut_acq) < DUREE_ACQUISITION_MS:
    t0 = time.ticks_us()

    x, y, z = lire_acceleration()
    buffer.append((x, y, z))

    if len(buffer) >= SAMPLES_PER_PACKET:
        if ble.connected:
            packet = b""
            for sx, sy, sz in buffer:
                packet += struct.pack("<hhh", sx, sy, sz)
            ble.send(packet)
        buffer.clear()

    elapsed = time.ticks_diff(time.ticks_us(), t0)
    remaining = interval_us - elapsed
    if remaining > 0:
        time.sleep_us(remaining)

# --- Fin d'acquisition, on se met en deep sleep ---
print("Fin acquisition - deep sleep " + str(DUREE_SLEEP_MS // 1000) + "s")
ble._ble.active(False)
time.sleep_ms(100)
deepsleep(DUREE_SLEEP_MS)
