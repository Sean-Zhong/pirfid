#!/usr/bin/env python3
import RPi.GPIO as GPIO
import pychromecast
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

card_to_playlist = {
    "908452881079": "https://music.youtube.com/playlist?list=OLAK5uy_nMi553Un-V3VCacIvHuLPUgXfEdPmHaP8&si=zvXkdmnNiDZy4cE1",
    "769481040605": "https://music.youtube.com/playlist?list=OLAK5uy_lh8IDILeWhuRYlJsOS7DndJkBr94VnKcY&si=c4ANd_WLzYWERxXZ"
}

chromecasts = pychromecast.get_chromecasts()

# Corrected line to find the Chromecast device
cast = next((cc for cc in chromecasts if cc.device.friendly_name == 'MIBOX3'), None)

if cast:
    # Wait for the cast to connect
    cast.wait()
else:
    print("MIBOX3 not found. Make sure it's on and connected to the same network.")
    exit()

def play_music(card_id):
    if card_id in card_to_playlist:
        playlist_url = card_to_playlist[card_id]
        
        # Check if the media controller is available
        if cast.media_controller:
            mc = cast.media_controller
            mc.play_media(playlist_url, "video/mp4")
            mc.block_until_active()
        else:
            print("Media controller is not available on this device.")

while True:
    try:
        print("Place your RFID tag near the reader...")
        id, text = reader.read()
        print(f"Tag ID: {id}")
        print(f"Text: {text}")
        play_music(str(id))  # Convert id to a string for dictionary lookup
    except Exception as e:
        print(f"An error occurred: {e}")

GPIO.cleanup()
