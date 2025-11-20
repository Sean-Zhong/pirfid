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
    "71fb59bc": "library://album/1", #Illmatic
    "a1fd59bc": "library://album/2",  #Ride the lightning
    "81015abc": "library://album/4", #Stories
    "91ff59bc": "library://album/5" #Minecraft
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

        uri = card_to_playlist[card_id]
        media_type = uri.split("://")[1].split("/")[0]
        
        logging.info(f"Calling music_assistant.play_media with URI: {uri} on player {MEDIA_PLAYER_ENTITY_ID}")

        service_url = f"{HA_URL}/api/services/music_assistant/play_media"
        
        headers = {
            "Authorization": f"Bearer {HA_TOKEN}",
            "Content-Type": "application/json",
        }

        payload = {
            "entity_id": MEDIA_PLAYER_ENTITY_ID,
            "media_id": uri,
            "media_type": media_type 
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
