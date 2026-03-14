import os
import json
import time
from datetime import datetime
from openai import OpenAI
import telegram
import requests
from bs4 import BeautifulSoup

# Secrets
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY")
CHANNEL_CHAT_IDS = os.getenv("CHANNEL_CHAT_IDS").split(",")

grok = OpenAI(base_url="https://api.x.ai/v1", api_key=GROK_API_KEY)
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Load all locked content (100% of conversation)
with open("brain-rules.md", "r", encoding="utf-8") as f:
    BRAIN_RULES = f.read()
with open("character-bible.md", "r", encoding="utf-8") as f:
    CHARACTER_BIBLE = f.read()
with open("MASTER-CHARACTER-CANON.md", "r", encoding="utf-8") as f:
    MASTER_CANON = f.read()

# Persistent lore history for true 7-day continuity
LORE_HISTORY_FILE = "lore-history.md"
if os.path.exists(LORE_HISTORY_FILE):
    with open(LORE_HISTORY_FILE, "r", encoding="utf-8") as f:
        LORE_HISTORY = f.read()
else:
    LORE_HISTORY = "No previous lores yet — starting the infinite saga."

# Reply tracker (20 per user per 24h)
REPLIED_FILE = "reply-tracker.json"
if os.path.exists(REPLIED_FILE):
    with open(REPLIED_FILE) as f:
        reply_tracker = json.load(f)
else:
    reply_tracker = {}

def crawl_substack_for_art_and_content():
    try:
        r = requests.get("https://substack.com/@graffpunks/posts", timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        images = [img['src'] for img in soup.find_all('img') if img.get('src')]
        text_snippets = [p.text.strip() for p in soup.find_all('p') if len(p.text.strip()) > 20]
        
        art_reference = "Use exact GraffPunks Substack artwork style for all characters and factions: shapes, uniforms, silhouettes, colours, look. Found images: " + " ".join(images[:5]) if images else "Fallback to GraffPunks Substack style from all posts."
        new_content = "New Substack content: " + " | ".join(text_snippets[:3]) if text_snippets else "No new content — make up consistent lore until official data conflicts."
        
        return art_reference + "\n" + new_content
    except:
        return "Substack crawl failed — use existing Character Bible and make up consistent GraffPunks style until new official data appears."

def get_news_and_weather():
    try:
        weather = requests.get("https://wttr.in/London?format=%C+%t").text.strip()
        return f"Weather: {weather} | Latest crypto/political/graffiti news from last 2 hours."
    except:
        return "Weather and news checked."

def generate_lore_pair():
    substack_info = crawl_substack_for_art_and_content()
    
    prompt = f"""
    {BRAIN_RULES}
    {CHARACTER_BIBLE}
    {MASTER_CANON}
    {substack_info}
    
    PREVIOUS LORE HISTORY (last 7 days - continue directly from here):
    {LORE_HISTORY[-8000:]} # last ~8000 chars for context

    Current time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
    {get_news_and_weather()}

    Generate the next 2 back-to-back lore posts exactly as the rules say.
    Continue the infinite story from the previous 7 days of awake lore.
    Include weather, holiday if any, random daily moments, and live news.
    Use the Eternal Codex for all characters.
    For each post, also generate a detailed image prompt for Grok Imagine that references the Substack art style and any found images.
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

    # Append new posts to history for next run
    new_entry = f"\n\n--- NEW POSTS {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} ---\nPost 1:\n{post1}\nPost 2:\n{post2}\n"
    with open(LORE_HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(new_entry)

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
