from flask import Flask, request, jsonify
import pychromecast
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

card_to_playlist = {
    "908452881079": "https://music.youtube.com/playlist?list=OLAK5uy_nMi553Un-V3VCacIvHuLPUgXfEdPmHaP8&si=zvXkdmnNiDZy4cE1",
    "769481040605": "https://music.youtube.com/playlist?list=OLAK5uy_lh8IDILeWhuRYlJsOS7DndJkBr94VnKcY&si=c4ANd_WLzYWERxXZ"
}

cast = None
browser = None

try:
    print("Scanning for Chromecast devices...")
    chromecasts, browser = pychromecast.get_chromecasts()

    # This code is now correct for your modern pychromecast version
    cast = next((cc for cc in chromecasts if cc.device.friendly_name == 'MIBOX3'), None)

    if cast:
        cast.wait()
        logging.info(f"Successfully connected to Chromecast: {cast.device.friendly_name}")
    else:
        logging.error("MIBOX3 not found on the network. Make sure it's on and connected to the same network.")
        exit()

except Exception as e:
    logging.error(f"An error occurred during Chromecast discovery: {e}")
    exit()

finally:
    if browser:
        pychromecast.discovery.stop_discovery(browser)

@app.route("/cast", methods=["POST"])
def cast_music():
    try:
        data = request.json
        card_id = data.get("card_id")

        if card_id not in card_to_playlist:
            return jsonify({"status": "error", "message": "Card ID not found"}), 404

        playlist_url = card_to_playlist[card_id]

        logging.info(f"Received card ID {card_id}. Casting playlist: {playlist_url}")

        mc = cast.media_controller
        mc.play_media(playlist_url, "audio/mp4")

        return jsonify({"status": "success", "message": f"Casting playlist for card ID: {card_id}"}), 200

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
