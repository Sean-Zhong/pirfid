from flask import Flask, request, jsonify
import logging
import os
import requests

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# --- Home Assistant Configuration ---
HA_URL = os.getenv("HA_URL")
HA_TOKEN = os.getenv("HA_TOKEN")
MEDIA_PLAYER_ENTITY_ID = os.getenv("MEDIA_PLAYER_ENTITY_ID")

# --- Manually constructed Music Assistant URIs ---
card_to_playlist = {
    "908452881079": "ytmusic://playlist/OLAK5uy_nMi553Un-V3VCacIvHuLPUgXfEdPmHaP8",
    "769481040605": "ytmusic://playlist/OLAK5uy_lh8IDILeWhuRYlJsOS7DndJkBr94VnKcY"
}

if not all([HA_URL, HA_TOKEN, MEDIA_PLAYER_ENTITY_ID]):
    logging.error("Missing required environment variables (HA_URL, HA_TOKEN, MEDIA_PLAYER_ENTITY_ID)")
    exit()

@app.route("/cast", methods=["POST"])
def cast_music():
    """
    API endpoint to trigger the Music Assistant (mass.play_media) service.
    """
    try:
        data = request.json
        card_id = data.get("card_id")

        if card_id not in card_to_playlist:
            return jsonify({"status": "error", "message": "Card ID not found"}), 404

        playlist_uri = card_to_playlist[card_id]
        logging.info(f"Received card ID {card_id}. Telling Music Assistant to play URI: {playlist_uri}")

        # --- Music Assistant API Call ---
        service_url = f"{HA_URL}/api/services/mass/play_media"
        
        headers = {
            "Authorization": f"Bearer {HA_TOKEN}",
            "Content-Type": "application/json",
        }

        payload = {
            "player_id": MEDIA_PLAYER_ENTITY_ID,
            "media_id": playlist_uri,
        }

        response = requests.post(service_url, headers=headers, json=payload)

        if response.status_code == 200:
            logging.info(f"Successfully sent command to Music Assistant.")
            return jsonify({"status": "success", "message": "Command sent to Music Assistant."}), 200
        else:
            logging.error(f"Failed to call Music Assistant. Status: {response.status_code}, Response: {response.text}")
            return jsonify({"status": "error", "message": "Failed to call Music Assistant service."}), 500

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
