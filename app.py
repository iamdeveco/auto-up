import requests
from google_play_scraper import app as google_play_app
from flask import Flask, jsonify
from datetime import datetime, timedelta
import threading
import time
import traceback

app = Flask(__name__)
session = requests.Session()

cache = {
    "data": None,
    "last_update": 0
}

CACHE_TIME = 60


def parse_date(value):
    try:
        if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit()):
            return datetime.fromtimestamp(int(value))

        if isinstance(value, str):
            return datetime.strptime(value, "%b %d, %Y")
    except:
        return None
    return None


def updater():
    global cache

    while True:
        try:
            print("🔄 Fetching Play Store data...")

            result = google_play_app(
                'com.dts.freefireth',
                lang="en",
                country='us'
            )

            version = result.get('version', '')

            last_updated_raw = (
                result.get('updated')
                or result.get('lastUpdatedOn')
                or result.get('lastUpdated')
            )

            last_dt = parse_date(last_updated_raw)

            r = session.get(
                "https://version.ggwhitehawk.com/live/ver.php",
                params={
                    "version": version,
                    "lang": "bn",
                    "device": "android",
                    "channel": "android",
                    "appstore": "googleplay",
                    "region": "BD",
                    "whitelist_version": "1.3.0",
                    "whitelist_sp_version": "1.0.0"
                },
                timeout=10
            )

            data = r.json()

            cache["data"] = {
                "last_updated_on": last_dt.strftime("%b %d, %Y") if last_dt else "unknown",
                "release_version": data.get("latest_release_version", "unknown"),
                "server_url": data.get("server_url", "unknown"),
                "play_version": version,
                "next_update": (last_dt + timedelta(days=90)).strftime("%b %d, %Y") if last_dt else "unknown",
                "status": "success"
            }

            cache["last_update"] = time.time()

            print("✅ Cache updated")

        except Exception as e:
            print("❌ ERROR:", str(e))
            traceback.print_exc()

        time.sleep(CACHE_TIME)


@app.route('/')
def get_data():
    return jsonify(cache["data"] if cache["data"] else {"status": "loading"})


if __name__ == '__main__':
    thread = threading.Thread(target=updater, daemon=True)
    thread.start()

    app.run(host='0.0.0.0', port=5000, threaded=True)
