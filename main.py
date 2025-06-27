import os
import time
import traceback
import tweepy
import schedule
import datetime
from flask import Flask
from threading import Thread

# --- Twitter API v2 Client Setup ---
API_KEY = os.environ["API_KEY"]
API_SECRET = os.environ["API_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_SECRET = os.environ["ACCESS_SECRET"]

client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# --- Load shlokas ---
with open("shlokas.txt", "r", encoding="utf-8") as f:
    content = f.read()
    shlokas = [s.strip() for s in content.split("________________________________________") if s.strip()]
print(f"📄 Loaded shlokas.txt with {len(shlokas)} entries")
print(f"📁 Current files in working dir: {os.listdir('.')}")

index_file = "index.txt"

# --- Index tracking ---
def get_index():
    if os.path.exists(index_file):
        index = int(open(index_file).read())
        print(f"📖 Current index: {index}")
        return index
    else:
        print("📖 index.txt not found. Starting from 0.")
        return 0

def save_index(i):
    print(f"💾 Saving index: {i}")
    with open(index_file, "w") as f:
        f.write(str(i))

# --- Post tweet ---
def post_shloka():
    print("🔔 post_shloka() called...")
    try:
        index = get_index()
        if index < len(shlokas):
            tweet = shlokas[index]
            print(f"\n🧪 Posting Shloka #{index + 1}:\n\n{tweet}\n")
            response = client.create_tweet(text=tweet)
            print(f"✅ Tweet sent! ID: {response.data['id']}")
            save_index(index + 1)
        else:
            print("🎉 All shlokas have been posted.")
    except Exception as e:
        print("❌ Error during tweet:")
        traceback.print_exc()

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

@app.route('/debug_tweet')
def debug_tweet():
    post_shloka()
    return "✅ Debug tweet attempt triggered."

@app.route('/auth_check')
def auth_check():
    try:
        me = client.get_me()
        return f"✅ Authenticated as @{me.data['username']}"
    except Exception as e:
        traceback.print_exc()
        return f"❌ Authentication failed: {e}"

# --- Scheduler setup ---
def run_scheduler():
    print("🤖 Scheduler started...")
    print("🔁 Attempting immediate post...")
    post_shloka()

    # Schedule at 08:00 and 20:00 IST → 02:30 & 14:30 UTC
    schedule.every().day.at("02:30").do(lambda: post_with_log("02:30 UTC (8 AM IST)"))
    schedule.every().day.at("14:30").do(lambda: post_with_log("14:30 UTC (8 PM IST)"))

    print("📅 Scheduled for 8 AM and 8 PM IST (02:30 & 14:30 UTC)")
    while True:
        schedule.run_pending()
        time.sleep(60)

def post_with_log(label):
    print(f"⏰ Scheduled tweet triggered at {label}")
    post_shloka()

# --- Main ---
if __name__ == "__main__":
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("🌐 Starting Flask server on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=False)
