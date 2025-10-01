#!/usr/bin/env python3
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests
import time

GPIO.setwarnings(False)

reader = SimpleMFRC522()

server_url = "http://192.168.111.98:5000/cast"

while True:
    try:
        print("Place your RFID tag near the reader...")
        full_id_decimal, text = reader.read()
        full_id_hex = hex(full_id_decimal)[2:]
        first_4_bytes_hex = full_id_hex[:8]
        response = requests.post(server_url, json={"card_id": first_4_bytes_hex})

        if response.status_code == 200:
            print("Successfully sent command to server.")
        else:
            print(f"Failed to send command. Server responded with status code: {response.status_code}")
            print(f"Response text: {response.text}")

    except Exception as e:
        print(f"An error occurred: {e}")
    time.sleep(2)

GPIO.cleanup()
