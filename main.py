import os
import random
import asyncio
import threading
from flask import Flask
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# --- Keep-Alive Web Server for Render ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Multi-Bot Reaction System Active 24/7!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- Fetch Environment Variables ---
RAW_TOKENS = [
    os.getenv("BOT_TOKEN"),
    os.getenv("BOT_TOKEN_2") or os.getenv("BOT_TOKEN2"),
    os.getenv("BOT_TOKEN_3") or os.getenv("BOT_TOKEN3"),
    os.getenv("BOT_TOKEN_4") or os.getenv("BOT_TOKEN4"),
    os.getenv("BOT_TOKEN_5") or os.getenv("BOT_TOKEN5"),
]

BOT_TOKENS = [t.strip() for t in RAW_TOKENS if t and len(t.strip()) > 10]
REACTIONS_POOL = ["👍", "❤️", "🔥", "👏", "😍", "🎉", "🤩", "💯"]

# Initialized Bot Objects
BOT_INSTANCES = []

async def send_single_reaction(bot_obj: Bot, chat_id: int, message_id: int, emoji: str):
    """हर बॉट से अलग-अलग रिएक्शन भेजता है"""
    try:
        await bot_obj.set_reaction(chat_id=chat_id, message_id=message_id, reaction=[emoji])
    except Exception as e:
        print(f"Reaction Error: {e}")

async def auto_react_multi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post:
        chat_id = update.channel_post.chat.id
        message_id = update.channel_post.message_id

        num_bots = len(BOT_INSTANCES)
        if num_bots == 0:
            return

        chosen_emojis = random.sample(REACTIONS_POOL, k=min(num_bots, len(REACTIONS_POOL)))

        tasks = []
        for i, bot_obj in enumerate(BOT_INSTANCES):
            tasks.append(send_single_reaction(bot_obj, chat_id, message_id, chosen_emojis[i]))
        
        await asyncio.gather(*tasks)

async def post_init(main_app):
    """सभी बॉट्स को सही इवेंट लूप के अंदर शुरू करता है"""
    global BOT_INSTANCES
    BOT_INSTANCES.append(main_app.bot)
    
    for token in BOT_TOKENS[1:]:
        b = Bot(token=token)
        await b.initialize() # प्रॉपरली सेशंस चालू करता है
        BOT_INSTANCES.append(b)
        
    print(f"✅ Successfully initialized {len(BOT_INSTANCES)} bots!")

if __name__ == "__main__":
    # Web server को background thread में चालू करें
    threading.Thread(target=run_flask, daemon=True).start()

    if not BOT_TOKENS:
        print("Error: Render Environment में कोई BOT_TOKEN नहीं मिला!")
    else:
        # Main bot receiver setup
        main_app = ApplicationBuilder().token(BOT_TOKENS[0]).post_init(post_init).build()
        main_app.add_handler(MessageHandler(filters.ChatType.CHANNEL & ~filters.COMMAND, auto_react_multi))

        main_app.run_polling(drop_pending_updates=True)
