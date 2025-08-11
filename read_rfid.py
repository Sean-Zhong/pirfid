#!/usr/bin/env python3
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
    print("Place your RFID tag near the reader...")
    id, text = reader.read()
    print(f"Tag ID: {id}")
    print(f"Text: {text}")
finally:
    GPIO.cleanup()
