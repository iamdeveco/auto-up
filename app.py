import requests
from google_play_scraper import app as google_play_app
import json
from flask import Flask, jsonify
import threading
import time
from urllib.parse import urlparse

app = Flask(__name__)

# Global state to store the scraped data
version_data = {
    "latest_release_version": "",
    "server_url": "",
    "play_version": ""
}

def fetch_data():
    try:
        result = google_play_app('com.dts.freefireth', lang="fr", country='fr')
        version = result['version']

        r = requests.get(
            f'https://bdversion.ggbluefox.com/live/ver.php?version={version}&lang=ar&device=android&channel=android&appstore=googleplay&region=ME&whitelist_version=1.3.0&whitelist_sp_version=1.0.0&device_name=google%20G011A&device_CPU=ARMv7%20VFPv3%20NEON%20VMH&device_GPU=Adreno%20(TM)%20640&device_mem=1993'
        )

        data = r.json()
        
        # Extract fields
        ggp_url = data.get("ggp_url", "")
        host = urlparse(ggp_url).netloc if ggp_url else ""
        
        current_data = {
            "host": host,
            "latest_release_version": data.get("latest_release_version", ""),
            "server_url": data.get("server_url", ""),
            "play_version": version
        }
        
        print(f"[INFO] Data fetched at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        return current_data
    except Exception as e:
        print(f"[ERROR] Failed to fetch data: {e}")
        return {
            "error": str(e),
            "host": "",
            "latest_release_version": "",
            "server_url": "",
            "play_version": ""
        }

@app.route('/')
def get_version_data():
    data = fetch_data()
    return jsonify(data)

if __name__ == '__main__':
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000)
