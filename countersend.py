import time
from RF24 import RF24, RF24_PA_LOW

# Initialize radio
radio = RF24(22, 0)  # CE=GPIO22, CSN=SPI0 CE0 (adjust pins if needed)

# Match ESP32 settings
address = b"00001"  # Must be 5 bytes (same as ESP32)
radio.begin()
radio.openWritingPipe(address)
radio.setPALevel(RF24_PA_LOW)  # Match ESP32's PA level
radio.stopListening()  # Set as transmitter

print("Transmitter ready...")
print(f"Using channel: {radio.getChannel()}")

counter = 0  # Initialize counter

while True:
    message = f"Count: {counter}"  # Message format
    if radio.write(message.encode()):  # Send the message
        print(f"Sent: {message}")
    else:
        print("Failed to send")
    counter += 1  # Increment counter
    #time.sleep(0.1)  # Delay between transmissions