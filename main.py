import os
import time
import tweepy
import schedule
from flask import Flask
from threading import Thread

# --- Twitter API keys from environment ---
API_KEY = os.environ["API_KEY"]
API_SECRET = os.environ["API_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_SECRET = os.environ["ACCESS_SECRET"]

# --- Twitter API client (v1.1) ---
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# --- Load shlokas from file ---
try:
    with open("shlokas.txt", "r", encoding="utf-8") as f:
        content = f.read()
        shlokas = [s.strip() for s in content.split("________________________________________") if s.strip()]
    print(f"📄 Loaded shlokas.txt with {len(shlokas)} entries")
except Exception as e:
    shlokas = []
    print(f"❌ Failed to load shlokas.txt: {e}")

index_file = "index.txt"

# --- Index tracking ---
def get_index():
    try:
        if os.path.exists(index_file):
            with open(index_file) as f:
                index = int(f.read().strip())
            print(f"📖 Current index: {index}")
            return index
        else:
            print("📖 index.txt not found. Starting from 0.")
            return 0
    except Exception as e:
        print(f"⚠️ Error reading index.txt: {e}. Resetting to 0.")
        return 0

def save_index(i):
    try:
        print(f"💾 Saving index: {i}")
        with open(index_file, "w") as f:
            f.write(str(i))
    except Exception as e:
        print(f"❌ Error saving index: {e}")

# --- Post tweet ---
def post_shloka():
    print("🔔 post_shloka() called...")
    try:
        index = get_index()
        if index < len(shlokas):
            tweet = shlokas[index]
            print(f"\n🧪 Posting Shloka #{index + 1}:\n\n{tweet}\n")
            response = api.update_status(status=tweet)
            print(f"✅ Tweet sent! ID: {response.id}")
            save_index(index + 1)
        else:
            print("🎉 All shlokas have been posted.")
    except Exception as e:
        print(f"❌ Error inside post_shloka(): {e}")

# --- Flask app setup ---
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Twitter Bot is running! Status: Active"

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

@app.route('/manual_tweet')
def manual_tweet():
    post_shloka()
    return "✅ Manually triggered tweet."

@app.route('/debug_tweet')
def debug_tweet():
    print("🐞 /debug_tweet called")
    post_shloka()
    return "🔧 post_shloka() manually triggered"

# --- Scheduler ---
def run_scheduler():
    print("🤖 Scheduler started...")

    try:
        print("🔁 Attempting immediate post...")
        post_shloka()
    except Exception as e:
        print(f"❌ Scheduler startup failed: {e}")

    schedule.every().day.at("02:30").do(post_shloka)  # 08:00 IST
    schedule.every().day.at("14:30").do(post_shloka)  # 20:00 IST

    print("📅 Scheduled at 08:00 IST and 20:00 IST daily.")

    while True:
        schedule.run_pending()
        time.sleep(60)

# --- Main ---
if __name__ == "__main__":
    print("📁 Current files in working dir:", os.listdir("."))
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("🌐 Starting Flask server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
