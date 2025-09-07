import pychromecast
import time

print("Scanning for Chromecast devices...")
chromecasts, browser = pychromecast.get_chromecasts()

if not chromecasts:
    print("No Chromecasts found. Check your network connection.")
else:
    print("Found the following Chromecasts:")
    for cast in chromecasts:
        # The friendly_name and model_name are now under the 'device' object
        print(f"Name: {cast.device.friendly_name}")
        print(f"Model: {cast.device.model_name}")

pychromecast.discovery.stop_discovery(browser)
