import time
import sys
import select
from RF24 import RF24, RF24_PA_HIGH, RF24_250KBPS, RF24_CRC_16

# Configuración
CE_PIN = 22
CSN_PIN = 0
CHANNEL = 76
ADDRESS = b"00001"

radio = RF24(CE_PIN, CSN_PIN)

if not radio.begin():
    raise RuntimeError("No se pudo inicializar el nRF24L01")

radio.setChannel(CHANNEL)
radio.setDataRate(RF24_250KBPS)
radio.setPALevel(RF24_PA_HIGH)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.setCRCLength(RF24_CRC_16)
radio.openWritingPipe(ADDRESS)
radio.openReadingPipe(1, ADDRESS)
radio.flush_rx()
radio.flush_tx()
radio.startListening()

print("=== MODO RESCATE RPi 5 ===")
print(f"Canal: {CHANNEL}, Address: {ADDRESS}")
print("Escribe y Enter para enviar. Ctrl+C para salir.\n")

while True:
    try:
        # ===== RX =====
        if radio.available():
            # Leer TODO lo que haya en el buffer
            while radio.available():
                size = radio.getDynamicPayloadSize()
                if 0 < size <= 32:
                    data = radio.read(size)
                    try:
                        msg = data.decode("utf-8", errors="replace")
                        print(f"[{time.strftime('%H:%M:%S')}] <= RX: {msg}")
                    except:
                        pass
                else:
                    break
            
            # RESET CRÍTICO: Después de recibir, reiniciamos
            radio.stopListening()
            time.sleep(0.01)
            radio.flush_rx()
            radio.startListening()

        # ===== TX =====
        if select.select([sys.stdin], [], [], 0.02)[0]:
            text = sys.stdin.readline().strip()
            if text:
                radio.stopListening()
                time.sleep(0.01)
                radio.flush_tx()
                
                ok = radio.write(text.encode("utf-8"))
                print(f"[{time.strftime('%H:%M:%S')}] => TX (ok={ok}): {text}")
                
                time.sleep(0.01)
                radio.flush_rx()
                radio.startListening()

        time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nSaliendo...")
        break