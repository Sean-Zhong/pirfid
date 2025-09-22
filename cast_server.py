from flask import Flask, request, jsonify
import logging
import os
import requests

# Set up logging to show information level messages
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# --- Home Assistant Configuration ---
# These are loaded from the environment variables in your docker-compose.yml
HA_URL = os.getenv("HA_URL")
HA_TOKEN = os.getenv("HA_TOKEN")
MEDIA_PLAYER_ENTITY_ID = os.getenv("MEDIA_PLAYER_ENTITY_ID")

# A dictionary mapping a card ID to a YouTube Music playlist URL.
card_to_playlist = {
    "908452881079": "https://music.youtube.com/playlist?list=OLAK5uy_nMi553Un-V3VCacIvHuLPUgXfEdPmHaP8&si=zvXkdmnNiDZy4cE1",
    "769481040605": "https://music.youtube.com/playlist?list=OLAK5uy_lh8IDILeWhuRYlJsOS7DndJkBr94VnKcY&si=c4ANd_WLzYWERxXZ"
}

# Validate that environment variables are set
if not all([HA_URL, HA_TOKEN, MEDIA_PLAYER_ENTITY_ID]):
    logging.error("Missing required environment variables (HA_URL, HA_TOKEN, MEDIA_PLAYER_ENTITY_ID)")
    exit()

@app.route("/cast", methods=["POST"])
def cast_music():
    """
    API endpoint to trigger a Home Assistant service call to play media.
    """
    try:
        data = request.json
        card_id = data.get("card_id")

        if card_id not in card_to_playlist:
            return jsonify({"status": "error", "message": "Card ID not found"}), 404

        playlist_url = card_to_playlist[card_id]
        logging.info(f"Received card ID {card_id}. Triggering HA for playlist: {playlist_url}")

        # --- Home Assistant API Call ---
        service_url = f"{HA_URL}/api/services/media_player/play_media"
        
        headers = {
            "Authorization": f"Bearer {HA_TOKEN}",
            "Content-Type": "application/json",
        }

        payload = {
            "entity_id": MEDIA_PLAYER_ENTITY_ID,
            "media_content_id": playlist_url,
            "media_content_type": "playlist", # This is important for YouTube Music playlists
        }

        response = requests.post(service_url, headers=headers, json=payload)

        # Check if the API call was successful
        if response.status_code == 200:
            logging.info(f"Successfully sent command to Home Assistant. Status: {response.status_code}")
            return jsonify({"status": "success", "message": "Command sent to Home Assistant."}), 200
        else:
            logging.error(f"Failed to send command to Home Assistant. Status: {response.status_code}, Response: {response.text}")
            return jsonify({"status": "error", "message": "Failed to call Home Assistant service."}), 500

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
