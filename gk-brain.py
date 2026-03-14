import os
import json
import time
from datetime import datetime
from openai import OpenAI
import telegram
import requests

# Secrets
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY")
CHANNEL_CHAT_IDS = os.getenv("CHANNEL_CHAT_IDS").split(",")

grok = OpenAI(base_url="https://api.x.ai/v1", api_key=GROK_API_KEY)
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Load all locked content
with open("brain-rules.md", "r", encoding="utf-8") as f:
    BRAIN_RULES = f.read()
with open("character-bible.md", "r", encoding="utf-8") as f:
    CHARACTER_BIBLE = f.read()

# Reply tracker (20 per user per 24h)
REPLIED_FILE = "reply-tracker.json"
if os.path.exists(REPLIED_FILE):
    with open(REPLIED_FILE) as f:
        reply_tracker = json.load(f)
else:
    reply_tracker = {}

def get_news_and_weather():
    try:
        weather = requests.get("https://wttr.in/London?format=%C+%t").text.strip()
        return f"Weather: {weather} | Latest crypto/political/graffiti news from last 2 hours."
    except:
        return "Weather and news checked."

def generate_lore_pair():
    prompt = f"""
    {BRAIN_RULES}
    {CHARACTER_BIBLE}

    Current time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
    {get_news_and_weather()}

    Generate the next 2 back-to-back lore posts exactly as the rules say.
    Include weather, holiday if any, random daily moments, and live news.
    Use the Eternal Codex for all characters.
    For each post, also generate a detailed image prompt for Grok Imagine.
    Separate with ---POST-2---
    """

    response = grok.chat.completions.create(
        model="grok-4-fast",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000
    )

    text = response.choices[0].message.content
    parts = text.split("---POST-2---")
    post1 = parts[0].strip()
    post2 = parts[1].strip() if len(parts) > 1 else "Continuation of the lore..."

    return post1, post2

def post_to_telegram(text):
    for chat_id in CHANNEL_CHAT_IDS:
        try:
            bot.send_message(chat_id=chat_id.strip(), text=text)
            time.sleep(2)
        except:
            pass

def main():
    print("GK BRAIN running at", datetime.utcnow())
    post1, post2 = generate_lore_pair()
    
    post_to_telegram(post1)
    print("✅ Post 1 sent")
    
    post_to_telegram(post2)
    print("✅ Post 2 sent")

    with open(REPLIED_FILE, "w") as f:
        json.dump(reply_tracker, f)

if __name__ == "__main__":
    main()
        json.dump(reply_tracker, f)

if __name__ == "__main__":
    main()
