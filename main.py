import os
import time
import tweepy
import schedule
import datetime
from flask import Flask
from threading import Thread

# --- Twitter API keys from Render environment ---
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

# --- Logging ---
def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    full_msg = f"[{timestamp} UTC] {msg}"
    print(full_msg)
    with open("bot_log.txt", "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")

# --- Index tracking ---
def get_index():
    if os.path.exists(index_file):
        index = int(open(index_file).read())
        log(f"📖 Current index: {index}")
        return index
    else:
        log("📖 index.txt not found. Starting from 0.")
        return 0

def save_index(i):
    log(f"💾 Saving index: {i}")
    with open(index_file, "w") as f:
        f.write(str(i))

# --- Post tweet ---
def post_shloka():
    index = get_index()
    if index < len(shlokas):
        tweet = shlokas[index]
        log(f"🧪 Posting Shloka #{index + 1}:\n{tweet}")
        try:
            response = client.create_tweet(text=tweet)
            log(f"✅ Tweet sent! ID: {response.data['id']}")
            save_index(index + 1)
        except Exception as e:
            log(f"❌ Error posting tweet: {e}")
    else:
        log("🎉 All shlokas have been posted.")

# --- Flask app setup ---
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Twitter Bot is running! Status: Active"

@app.route('/ping')
def ping():
    log("📶 Ping received from UptimeRobot")
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
    log("🤖 Scheduler started...")

    # Debug: show server UTC time
    log(f"🕒 Server UTC time now: {datetime.datetime.utcnow()}")

    # Optional: Tweet once at startup
    post_shloka()

    # Schedule at 02:30 and 14:30 UTC (→ 8 AM & 8 PM IST)
    schedule.every().day.at("02:30").do(lambda: log_and_post("02:30 UTC (8 AM IST)"))
    schedule.every().day.at("14:30").do(lambda: log_and_post("14:30 UTC (8 PM IST)"))

    log("📅 Scheduled for 02:30 and 14:30 UTC daily (8 AM & 8 PM IST)")

    while True:
        schedule.run_pending()
        time.sleep(60)

def log_and_post(label):
    log(f"⏰ Scheduled tweet triggered at: {label}")
    post_shloka()

# --- Main ---
if __name__ == "__main__":
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    log("🌐 Starting Flask server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
