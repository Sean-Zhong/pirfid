#!/usr/bin/env python3
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests
import time

GPIO.setwarnings(False)

reader = SimpleMFRC522()
server_url = "http://192.168.111.98:5000/cast"

# --- Logic Variables ---
last_scanned_hex = None
last_read_timestamp = 0
RESET_THRESHOLD_SECONDS = 3.0 

print("RFID Reader Active. Place a tag to play.")

try:
    while True:
        # reader.read() blocks here until a tag is detected
        full_id_decimal, text = reader.read()
        
        current_time = time.time()

        # Convert ID to hex
        full_id_hex = hex(full_id_decimal)[2:]
        first_4_bytes_hex = full_id_hex[:8]

        if (current_time - last_read_timestamp) > RESET_THRESHOLD_SECONDS:
            last_scanned_hex = None

        # CHECK 2: Is this a new tag?
        if first_4_bytes_hex != last_scanned_hex:
            print(f"New tag detected: {first_4_bytes_hex}")
            
            try:
                response = requests.post(server_url, json={"card_id": first_4_bytes_hex})
                if response.status_code == 200:
                    print(" > Command sent successfully.")
                else:
                    print(f" > Server Error: {response.status_code}")
            except Exception as e:
                print(f" > Connection Error: {e}")
            
            last_scanned_hex = first_4_bytes_hex
        
        else:
            print(".", end="", flush=True)

        # Update the timestamp of the last successful read
        last_read_timestamp = time.time()
        
        # Small delay to prevent CPU spiking, but short enough to catch removal
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    GPIO.cleanup()
