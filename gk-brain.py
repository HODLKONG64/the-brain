import os
import json
import time
from datetime import datetime, timedelta
from openai import OpenAI
import telegram
import requests

# Secrets from GitHub
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY")
CHANNEL_CHAT_IDS = os.getenv("CHANNEL_CHAT_IDS").split(",")

grok = OpenAI(base_url="https://api.x.ai/v1", api_key=GROK_API_KEY)
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Load all locked rules
with open("brain-rules.md", "r", encoding="utf-8") as f:
    BRAIN_RULES = f.read()

# Reply tracker
REPLIED_FILE = "reply-tracker.json"
if os.path.exists(REPLIED_FILE):
    with open(REPLIED_FILE) as f:
        reply_tracker = json.load(f)
else:
    reply_tracker = {}

def get_current_weather():
    # Simple free weather check for London (you can expand later)
    try:
        r = requests.get("https://wttr.in/London?format=%C+%t")
        return r.text.strip()
    except:
        return "unknown weather"

def generate_lore_pair():
    prompt = f"""
    {BRAIN_RULES}

    Current time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
    Current weather: {get_current_weather()}

    Generate the next 2 back-to-back lore posts exactly as the rules say.
    Use the Eternal Codex File Stored on the World Chain for all characters.
    Include random daily moments, weather, and any holiday if today is one.
    Post 1: max length + image prompt.
    Post 2: continuation + image prompt.
    """

    response = grok.chat.completions.create(
        model="grok-4-fast",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000
    )

    text = response.choices[0].message.content

    # Split into Post 1 and Post 2
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
    print("GK BRAIN starting...")
    post1, post2 = generate_lore_pair()
    
    post_to_telegram(post1)
    print("Post 1 sent")
    
    post_to_telegram(post2)
    print("Post 2 sent")

    # Save reply tracker
    with open(REPLIED_FILE, "w") as f:
        json.dump(reply_tracker, f)

if __name__ == "__main__":
    main()
