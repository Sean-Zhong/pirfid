from flask import Flask, request, jsonify
from androidtv import AndroidTV
import logging

# Set up logging to show information level messages
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# A dictionary mapping a card ID to a YouTube Music playlist URL.
# This remains the same.
card_to_playlist = {
    "908452881079": "https://music.youtube.com/playlist?list=OLAK5uy_nMi553Un-V3VCacIvHuLPUgXfEdPmHaP8&si=zvXkdmnNiDZy4cE1",
    "769481040605": "https://music.youtube.com/playlist?list=OLAK5uy_lh8IDILeWhuRYlJsOS7DndJkBr94VnKcY&si=c4ANd_WLzYWERxXZ"
}

# --- Android TV Setup ---
# IMPORTANT: Replace "YOUR_ANDROID_TV_IP" with your Android TV's actual IP address.
ANDROID_TV_IP = "192.168.111.148"
atv = None

try:
    logging.info(f"Attempting to connect to Android TV at {ANDROID_TV_IP}...")
    # Establish connection to the Android TV
    atv = AndroidTV(ANDROID_TV_IP)
    if not atv.is_on:
        atv.turn_on() # Turn on the TV if it's off
    logging.info(f"Successfully connected to Android TV at {ANDROID_TV_IP}")

except Exception as e:
    logging.error(f"Failed to connect to Android TV at {ANDROID_TV_IP}. Error: {e}")
    logging.error("Please ensure ADB Debugging is enabled on the TV and you have accepted the connection prompt from this server.")
    exit()

@app.route("/cast", methods=["POST"])
def cast_music():
    """
    API endpoint to play a YouTube Music playlist on an Android TV based on a card ID.
    """
    try:
        data = request.json
        card_id = data.get("card_id")

        if card_id not in card_to_playlist:
            return jsonify({"status": "error", "message": "Card ID not found"}), 404

        playlist_url = card_to_playlist[card_id]
        logging.info(f"Received card ID {card_id}. Playing playlist: {playlist_url}")

        # Use a deep link to open the YouTube Music playlist on the Android TV.
        # This is equivalent to running the ADB command:
        # adb shell am start -a android.intent.action.VIEW -d <playlist_url>
        atv.deep_link(playlist_url)

        return jsonify({"status": "success", "message": f"Playing playlist for card ID: {card_id}"}), 200

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Run the Flask application on all available network interfaces.
    app.run(host="0.0.0.0", port=5000)

