import os
import time
import requests
import tweepy
import schedule
from flask import Flask
from threading import Thread

# Load Twitter API keys from environment variables
API_KEY = os.environ["API_KEY"]
API_SECRET = os.environ["API_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_SECRET = os.environ["ACCESS_SECRET"]

# JSONBin.io configuration
BIN_ID = os.environ["BIN_ID"]  # e.g., '661fabcde12a5d1234567890a'
API_KEY_JSONBIN = os.environ["JSONBIN_API_KEY"]  # Starts with $2b$

HEADERS = {
    "X-Master-Key": API_KEY_JSONBIN,
    "Content-Type": "application/json"
}
BASE_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

# Tweepy client
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# Load shlokas
with open("shlokas.txt", "r", encoding="utf-8") as f:
    content = f.read()
    shlokas = [s.strip() for s in content.split("________________________________________") if s.strip()]

# --- JSONBin index management ---
def get_index():
    try:
        res = requests.get(f"{BASE_URL}/latest", headers=HEADERS)
        return res.json()["record"]["index"]
    except Exception as e:
        print("⚠ Error getting index:", e)
        return 0

def save_index(new_index):
    try:
        res = requests.put(BASE_URL, headers=HEADERS, json={"index": new_index})
        if res.status_code == 200:
            print("✅ Index saved.")
        else:
            print("❌ Failed to save index:", res.status_code, res.text)
    except Exception as e:
        print("❌ Exception saving index:", e)

# --- Twitter posting function ---
def post_shloka():
    index = get_index()
    if index < len(shlokas):
        tweet = shlokas[index]
        print(f"\n🧪 Posting Shloka #{index + 1}:\n\n{tweet}\n")
        try:
            response = client.create_tweet(text=tweet)
            print(f"✅ Tweet sent! ID: {response.data['id']}")
            save_index(index + 1)
        except Exception as e:
            print(f"❌ Tweet failed: {e}")
    else:
        print("🎉 All shlokas have been posted.")

# --- Flask App for UptimeRobot ---
app = Flask(__name__)  # ✅ Correct

@app.route('/')
def home():
    return "🤖 Bot is online!"

@app.route('/ping')
def ping():
    return "pong"

@app.route('/status')
def status():
    index = get_index()
    total = len(shlokas)
    return {
        "status": "running",
        "current_index": index,
        "total_shlokas": total,
        "remaining": total - index
    }

# --- Scheduler thread ---
def run_scheduler():
    print("🤖 Scheduler running...")
    post_shloka()
    schedule.every().day.at("08:00").do(post_shloka)
    schedule.every().day.at("20:00").do(post_shloka)
    while True:
        schedule.run_pending()
        time.sleep(60)

# --- Main ---
if __name__ == "__main__":
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    app.run(host="0.0.0.0", port=5000)
