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

# --- Use the VALID URIs you found in the Music Assistant UI ---
card_to_playlist = {
    "71fb59bc": {"media_id": "Illmatic", "media_type": "album"},
    "a1fd59bc": {"media_id": "Ride the lightning", "media_type": "album"},
    "81015abc": {"media_id": "Stories", "media_type": "album"},
    "91ff59bc": {"media_id": "Minecraft", "media_type": "album"}
}

if not all([HA_URL, HA_TOKEN, MEDIA_PLAYER_ENTITY_ID]):
    logging.error("Missing required environment variables (HA_URL, HA_TOKEN, MEDIA_PLAYER_ENTITY_ID)")
    exit()

@app.route("/cast", methods=["POST"])
def cast_music():
    try:
        data = request.json
        card_id = data.get("card_id")

        if card_id not in card_to_playlist:
            return jsonify({"status": "error", "message": "Card ID not found"}), 404

        # Extract the dictionary values directly
        media_info = card_to_playlist[card_id]
        media_id = media_info["media_id"]
        media_type = media_info["media_type"]
        
        logging.info(f"Calling music_assistant.play_media with ID: '{media_id}' on player {MEDIA_PLAYER_ENTITY_ID}")

        service_url = f"{HA_URL}/api/services/music_assistant/play_media"
        
        headers = {
            "Authorization": f"Bearer {HA_TOKEN}",
            "Content-Type": "application/json",
        }

        payload = {
            "entity_id": MEDIA_PLAYER_ENTITY_ID,
            "media_id": media_id,
            "media_type": media_type,
            "enqueue": "play"
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
