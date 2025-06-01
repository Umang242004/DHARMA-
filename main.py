import tweepy
import schedule
import time
import os
from flask import Flask
from threading import Thread

# Load Twitter API keys from environment
API_KEY = os.environ["API_KEY"]
API_SECRET = os.environ["API_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_SECRET = os.environ["ACCESS_SECRET"]

# Twitter auth - using API v2
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# Load shlokas from a text file
with open("shlokas.txt", "r", encoding="utf-8") as f:
    content = f.read()
    shlokas = [s.strip() for s in content.split("________________________________________") if s.strip()]

index_file = "index.txt"

def get_index():
    return int(open(index_file).read()) if os.path.exists(index_file) else 0

def save_index(i):
    with open(index_file, "w") as f:
        f.write(str(i))

def post_shloka():
    index = get_index()
    if index < len(shlokas):
        tweet = shlokas[index]
        print(f"\n🧪 Previewing Shloka #{index + 1}:\n\n{tweet}\n\n📤 Tweeting now...")
        try:
            response = client.create_tweet(text=tweet)
            print("✅ Tweet sent successfully!\n")
            print(f"Tweet ID: {response.data['id']}")
            save_index(index + 1)
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")
    else:
        print("🎉 All shlokas have been posted.")

# Flask web server
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

def run_scheduler():
    """Run the scheduler in a separate thread"""
    print("🤖 Twitter Bot Starting...")
    print("📋 Preview mode - showing what will be tweeted:")
    post_shloka()

    # Schedule next posts
    schedule.every().day.at("08:00").do(post_shloka)
    schedule.every().day.at("20:00").do(post_shloka)

    print("⏰ Bot scheduled for 08:00 and 20:00 daily")
    print("🔄 Running continuously...")

    # Main scheduler loop
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # Start the scheduler in a background thread
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Start the Flask web server
    print("🌐 Starting web server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
