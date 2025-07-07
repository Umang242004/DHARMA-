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

# --- Twitter API client ---
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# --- Load shlokas from file ---
with open("shlokas.txt", "r", encoding="utf-8") as f:
    content = f.read()
    shlokas = [s.strip() for s in content.split("________________________________________") if s.strip()]

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
    index = get_index()
    if index < len(shlokas):
        tweet = shlokas[index]
        print(f"\n🧪 Posting Shloka #{index + 1}:\n\n{tweet}\n")
        try:
            response = client.create_tweet(text=tweet)
            print(f"✅ Tweet sent! ID: {response.data['id']}")
            save_index(index + 1)
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")
    else:
        print("🎉 All shlokas have been posted.")

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

# --- Scheduler ---
def run_scheduler():
    print("🤖 Scheduler started...")
    post_shloka()  # Optional: post one at startup

    # Schedule tweets at 08:00 IST and 20:00 IST (UTC+5:30 → 02:30 and 14:30 UTC)
    schedule.every().day.at("14:25").do(post_shloka)  # 08:00 IST
    schedule.every().day.at("14:30").do(post_shloka)  # 20:00 IST

    print("📅 Scheduled at 08:00 IST and 20:00 IST daily.")

    while True:
        schedule.run_pending()
        time.sleep(60)

# --- Main ---
if __name__ == "__main__":
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("🌐 Starting Flask server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
