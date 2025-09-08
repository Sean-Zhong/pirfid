from flask import Flask, request, jsonify
import pychromecast
import logging

# Set up logging to show information level messages
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# A dictionary mapping a card ID to a YouTube Music playlist URL.
card_to_playlist = {
    "908452881079": "https://music.youtube.com/playlist?list=OLAK5uy_nMi553Un-V3VCacIvHuLPUgXfEdPmHaP8&si=zvXkdmnNiDZy4cE1",
    "769481040605": "https://music.youtube.com/playlist?list=OLAK5uy_lh8IDILeWhuRYlJsOS7DndJkBr94VnKcY&si=c4ANd_WLzYWERxXZ"
}

cast = None
browser = None

try:
    print("Scanning for Chromecast devices...")
    # This function returns a list of chromecasts and the discovery browser object.
    # The browser object is needed to properly stop the discovery process.
    chromecasts, browser = pychromecast.get_chromecasts()

    # Find the Chromecast with the friendly name 'MIBOX3'.
    # Note: 'cast_info.friendly_name' is the correct attribute for modern pychromecast versions.
    cast = next((cc for cc in chromecasts if cc.cast_info.friendly_name == 'MIBOX3'), None)

    if cast:
        # Wait for the cast device to be ready to receive commands.
        cast.wait()
        logging.info(f"Successfully connected to Chromecast: {cast.cast_info.friendly_name}")
    else:
        logging.error("MIBOX3 not found on the network. Make sure it's on and connected to the same network.")
        # Exit the program if the target device is not found.
        exit()

except Exception as e:
    logging.error(f"An error occurred during Chromecast discovery: {e}")
    exit()

finally:
    if browser:
        # This is the correct way to stop the discovery browser in modern pychromecast versions.
        browser.stop_discovery()
        logging.info("Stopped Chromecast discovery.")

@app.route("/cast", methods=["POST"])
def cast_music():
    """
    API endpoint to cast a YouTube Music playlist to the selected Chromecast based on a card ID.
    """
    try:
        data = request.json
        card_id = data.get("card_id")

        if card_id not in card_to_playlist:
            return jsonify({"status": "error", "message": "Card ID not found"}), 404

        playlist_url = card_to_playlist[card_id]

        logging.info(f"Received card ID {card_id}. Casting playlist: {playlist_url}")

        mc = cast.media_controller
        # Use a generic audio mime type for better compatibility.
        mc.play_media(playlist_url, "audio/mpeg")

        return jsonify({"status": "success", "message": f"Casting playlist for card ID: {card_id}"}), 200

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Run the Flask application on all available network interfaces.
    app.run(host="0.0.0.0", port=5000)
