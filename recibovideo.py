import time
import cv2
import numpy as np
from RF24 import RF24, RF24_PA_LOW, RF24_2MBPS

# Configuración NRF24L01
radio = RF24(22, 0)  # CE=GPIO22, CSN=GPIO8
pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]  # Pipe0:TX, Pipe1:RX

def setup_radio():
    if not radio.begin():
        raise RuntimeError("Error en NRF24L01")
    radio.setPALevel(RF24_PA_LOW)
    radio.setDataRate(RF24_2MBPS)
    radio.enableDynamicPayloads()
    radio.openReadingPipe(1, pipes[0])
    radio.openWritingPipe(pipes[1])
    print("Receptor listo (CE=GPIO22, CSN=GPIO8)")

def initiate_handshake():
    radio.stopListening()
    for _ in range(3):  # 3 intentos
        radio.write(b"READY")
        radio.startListening()
        start_time = time.time()
        while time.time() - start_time < 1:  # Timeout de 1 segundo
            if radio.available():
                ack = radio.read(radio.getDynamicPayloadSize() or 32)
                if ack == b"ACK":
                    print("Handshake exitoso")
                    return True
        print("Reintentando handshake...")
    return False

def receive_frame():
    # Recibe tamaño del frame (4 bytes)
    size_data = radio.read(4)
    if len(size_data) != 4:
        return None
    frame_size = int.from_bytes(size_data, byteorder='big')
    
    # Recibe datos
    frame_data = bytearray()
    while len(frame_data) < frame_size:
        if radio.available():
            chunk = radio.read(radio.getDynamicPayloadSize() or 32)
            frame_data.extend(chunk)
    return frame_data

def display_video():
    try:
        while True:
            if initiate_handshake():
                frame_data = receive_frame()
                if frame_data:
                    frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
                    cv2.imshow("Video", frame)
                    if cv2.waitKey(1) == ord('q'):
                        break
    except KeyboardInterrupt:
        radio.powerDown()
        cv2.destroyAllWindows()
        print("Receptor detenido")

if __name__ == "__main__":
    setup_radio()
    display_video()