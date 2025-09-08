#!/usr/bin/env python3
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests
import time

GPIO.setwarnings(False)

reader = SimpleMFRC522()

server_url = "http://your-server-ip:port/cast"

while True:
    try:
        print("Place your RFID tag near the reader...")
        id, text = reader.read()
        print(f"Tag ID: {id}")

        # Send the RFID tag ID to the home server
        response = requests.post(server_url, json={"card_id": str(id)})

        if response.status_code == 200:
            print("Successfully sent command to server.")
        else:
            print(f"Failed to send command. Server responded with status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")
    
    time.sleep(2)  # Add a small delay to prevent rapid-fire requests

GPIO.cleanup()
