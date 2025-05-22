import time
import numpy as np
from PIL import Image
from RF24 import RF24, RF24_PA_HIGH, RF24_1MBPS
import zlib

radio = RF24(22, 0)
address = b"IMG50KB"
radio.begin()
radio.openReadingPipe(0, address)
radio.setPALevel(RF24_PA_HIGH)
radio.startListening()

def recibir_imagen():
    # Recibir metadatos (6 bytes: 2 alto + 2 ancho + 4 tamaño)
    metadata = radio.read(8)
    h = int.from_bytes(metadata[:2], 'little')
    w = int.from_bytes(metadata[2:4], 'little')
    tamaño = int.from_bytes(metadata[4:8], 'little')
    
    # Recibir datos comprimidos
    datos = bytearray()
    while len(datos) < tamaño:
        if radio.available():
            datos.extend(radio.read(32))
            print(f"Recibido: {len(datos)}/{tamaño} bytes")
    
    # Descomprimir y reconstruir imagen
    img_data = zlib.decompress(datos)
    matriz = np.frombuffer(img_data, dtype=np.uint8).reshape(h, w)
    Image.fromarray(matriz).save("recibida.jpg")
    print(f"Imagen guardada ({w}x{h}, {len(datos)/1024:.1f} KB)")

while True:
    if radio.available():
        recibir_imagen()