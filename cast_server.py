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
    "71fb59bc": {"media_id": "Illmatic", "media_type": "album", "shuffle": False},
    "a1fd59bc": {"media_id": "Ride the lightning", "media_type": "album", "shuffle": False},
    "81015abc": {"media_id": "Stories", "media_type": "album", "shuffle": False},
    "91ff59bc": {"media_id": "Minecraft", "media_type": "album", "shuffle": False},
    "10d5abce": {
        "media_id": "ytmusic--gpNMUhoC://playlist/RDCLAK5uy_neriXH6JbZPr7Pf4LOi5bGQP-_lWRZXs4",
        "media_type": "playlist",
        "shuffle": True
    }
}

if not all([HA_URL, HA_TOKEN, MEDIA_PLAYER_ENTITY_ID]):
    logging.error("Missing required environment variables (HA_URL, HA_TOKEN, MEDIA_PLAYER_ENTITY_ID)")
    exit()

@app.route("/cast", methods=["POST"])
def cast_music():
    try:
        data = request.json
        card_id = data.get("card_id")

        logging.info(f"THE SCANNER SENT THIS ID: '{card_id}'")

        if card_id not in card_to_playlist:
            return jsonify({"status": "error", "message": "Card ID not found"}), 404

        # Extract the dictionary values directly
        media_info = card_to_playlist[card_id]
        media_id = media_info["media_id"]
        media_type = media_info["media_type"]
        should_shuffle = media_info.get("shuffle", False) 

        headers = {
            "Authorization": f"Bearer {HA_TOKEN}",
            "Content-Type": "application/json",
        }

        # Base payload for Music Assistant
        payload = {
            "entity_id": MEDIA_PLAYER_ENTITY_ID,
            "media_id": media_id,
            "media_type": media_type
        }

        if should_shuffle:
            logging.info("Executing truly random shuffled playback sequence.")
            requests.post(f"{HA_URL}/api/services/media_player/clear_playlist", headers=headers, json={"entity_id": MEDIA_PLAYER_ENTITY_ID})
            requests.post(f"{HA_URL}/api/services/media_player/shuffle_set", headers=headers, json={"entity_id": MEDIA_PLAYER_ENTITY_ID, "shuffle": True})

            payload["enqueue"] = "add"
            response = requests.post(f"{HA_URL}/api/services/music_assistant/play_media", headers=headers, json=payload)

            requests.post(f"{HA_URL}/api/services/media_player/media_play", headers=headers, json={"entity_id": MEDIA_PLAYER_ENTITY_ID})

    else:
        logging.info("Executing standard sequential playback.")
        requests.post(f"{HA_URL}/api/services/media_player/shuffle_set", headers=headers, json={"entity_id": MEDIA_PLAYER_ENTITY_ID, "shuffle": False})

        payload["enqueue"] = "play"
        response = requests.post(f"{HA_URL}/api/services/music_assistant/play_media", headers=headers, json=payload)

    if response.status_code == 200:
        logging.info(f"Successfully sent command to Music Assistant.")
        return jsonify({"status": "success", "message": "Command sent."}), 200
    else:
        logging.error(f"Failed to call Music Assistant. Status: {response.status_code}, Response: {response.text}")
        return jsonify({"status": "error", "message": "Failed to call Music Assistant service."}), 500

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/stop", methods=["POST"])
def stop_music():
    try:
        logging.info(f"Calling media_player.media_pause on {MEDIA_PLAYER_ENTITY_ID}")

        service_url = f"{HA_URL}/api/services/media_player/media_pause"

        headers = {
            "Authorization": f"Bearer {HA_TOKEN}",
            "Content-Type": "application/json",
        }

        payload = {
            "entity_id": MEDIA_PLAYER_ENTITY_ID
        }

        response = requests.post(service_url, headers=headers, json=payload)

        if response.status_code == 200:
            logging.info("Successfully sent stop command.")
            return jsonify({"status": "success", "message": "Stop command sent."}), 200
        else:
            logging.error(f"Failed to stop. Status: {response.status_code}, Response: {response.text}")
            return jsonify({"status": "error", "message": "Failed to stop."}), 500

    except Exception as e:
        logging.error(f"An error occurred stopping: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
