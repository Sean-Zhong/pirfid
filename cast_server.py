from flask import Flask, request, jsonify
from androidtv import AndroidTV
import logging
import time

# Set up logging to show information level messages
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# A dictionary mapping a card ID to a YouTube Music playlist URL.
card_to_playlist = {
    "908452881079": "https://music.youtube.com/playlist?list=OLAK5uy_nMi553Un-V3VCacIvHuLPUgXfEdPmHaP8&si=zvXkdmnNiDZy4cE1",
    "769481040605": "https://music.youtube.com/playlist?list=OLAK5uy_lh8IDILeWhuRYlJsOS7DndJkBr94VnKcY&si=c4ANd_WLxYWERxXZ"
}

# --- Android TV Setup ---
ANDROID_TV_IP = "192.168.111.148"
atv = None

try:
    logging.info(f"Attempting to connect to Android TV at {ANDROID_TV_IP}...")
    atv = AndroidTV(host=ANDROID_TV_IP, adbkey='/root/.android/adbkey')
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

        # Step 1: Force stop the YouTube Music app to ensure a clean state
        atv.adb_shell('am force-stop com.google.android.apps.youtube.music')
        time.sleep(2) # Give it a moment to stop

        # Step 2: Send the deep link command to open the playlist view.
        atv.adb_shell(f"am start -a android.intent.action.VIEW -d '{playlist_url}'")

        # Step 3: Add a short delay to allow the app to load.
        time.sleep(5)

        # Step 4: Send a key event to start playback.
        atv.adb_shell("input keyevent KEYCODE_MEDIA_PLAY_PAUSE")

        return jsonify({"status": "success", "message": f"Playing playlist for card ID: {card_id}"}), 200

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
