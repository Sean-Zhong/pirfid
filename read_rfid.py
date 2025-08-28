#!/usr/bin/env python3
import RPi.GPIO as GPIO
import pychromecast
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

card_to_playlist = {
    "908452881079": "https://music.youtube.com/playlist?list=OLAK5uy_nMi553Un-V3VCacIvHuLPUgXfEdPmHaP8&si=zvXkdmnNiDZy4cE1 (Ride the Lightning)",
    "769481040605": "https://music.youtube.com/playlist?list=OLAK5uy_lh8IDILeWhuRYlJsOS7DndJkBr94VnKcY&si=c4ANd_WLzYWERxXZ (Illmatic)"
}

chromecasts = pychromecast.get_chromecasts()
cast = next(cc for cc in chromecasts if cc.device.friendly_name == 'MIBOX3')

# Wait for the cast to connect
cast.wait()

def play_music(card_id):
    if card_id in card_to_playlist:
        playlist_url = card_to_playlist[card_id]
        
        mc = cast.media_controller
        mc.play_media(playlist_url, "video/mp4")
        mc.block_until_active()

while True:
    try:
        print("Place your RFID tag near the reader...")
        id, text = reader.read()
        print(f"Tag ID: {id}")
        print(f"Text: {text}")
        play_music(id)
    finally:
        GPIO.cleanup()
