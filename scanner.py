from RF24 import RF24

radio = RF24(22, 0)  # CE=GPIO22, CSN=SPI0 CE0
radio.begin()

if not radio.isChipConnected():
    print("NRF24L01+ not detected! Check wiring.")
else:
    print("NRF24L01+ is connected!")
    radio.printDetails()  # Prints full radio configuration