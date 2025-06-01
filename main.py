
import tweepy
import schedule
import time
import os

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

# Test the bot with preview
print("🤖 Twitter Bot Starting...")
print("📋 Preview mode - showing what will be tweeted:")
post_shloka()

# Schedule next posts
schedule.every().day.at("08:00").do(post_shloka)
schedule.every().day.at("20:00").do(post_shloka)

print("⏰ Bot scheduled for 08:00 and 20:00 daily")
print("🔄 Running continuously...")

# Main loop
while True:
    schedule.run_pending()
    time.sleep(60)
