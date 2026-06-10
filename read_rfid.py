#!/usr/bin/env python3
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests
import time

GPIO.setwarnings(False)
reader = SimpleMFRC522()

play_url = "http://192.168.111.98:5000/cast"
stop_url = "http://192.168.111.98:5000/stop"

# --- Logic Variables ---
current_playing_hex = None
last_seen_timestamp = 0
REMOVAL_THRESHOLD_SECONDS = 1.5  # Seconds the reader must be empty before stopping

print("RFID Reader Active. Place a tag to play, remove it to stop.")

try:
    while True:
        # Non-blocking read. Returns the ID if present, or None if empty.
        full_id_decimal = reader.read_id_no_block()
        current_time = time.time()

        if full_id_decimal is not None:
            # ---> A TAG IS PRESENT <---
            full_id_hex = hex(full_id_decimal)[2:]
            first_4_bytes_hex = full_id_hex[:8]
            
            # Update the timestamp showing the tag is still here
            last_seen_timestamp = current_time

            # Is this a new tag we haven't started playing yet?
            if first_4_bytes_hex != current_playing_hex:
                print(f"New tag detected: {first_4_bytes_hex}. Sending PLAY command.")
                try:
                    response = requests.post(play_url, json={"card_id": first_4_bytes_hex})
                    if response.status_code == 200:
                        print(" > Play command successful.")
                except Exception as e:
                    print(f" > Connection Error: {e}")
                
                # Lock in this tag as currently playing
                current_playing_hex = first_4_bytes_hex

        else:
            # ---> NO TAG IS PRESENT <---
            if current_playing_hex is not None:
                # A tag WAS playing, check if it's been gone longer than the threshold
                if (current_time - last_seen_timestamp) > REMOVAL_THRESHOLD_SECONDS:
                    print("Tag removed. Sending STOP command.")
                    try:
                        requests.post(stop_url)
                        print(" > Stop command successful.")
                    except Exception as e:
                        print(f" > Connection Error: {e}")
                    
                    # Reset the currently playing state so a new tag can trigger
                    current_playing_hex = None

        # Short sleep to prevent the CPU from running at 100%
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    GPIO.cleanup()
