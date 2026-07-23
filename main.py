import os
import random
import asyncio
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# --- Web Server for Render Keep-Alive ---
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

# Global dict to store initialized bot apps
BOT_APPS = []

async def send_single_reaction(app_instance, chat_id: int, message_id: int, emoji: str):
    """हर बॉट के बॉट-ऑब्जेक्ट से सुरक्षित रिएक्शन भेजता है"""
    try:
        await app_instance.bot.set_reaction(chat_id=chat_id, message_id=message_id, reaction=[emoji])
    except Exception as e:
        print(f"Reaction Error: {e}")

async def auto_react_multi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post:
        chat_id = update.channel_post.chat.id
        message_id = update.channel_post.message_id

        num_bots = len(BOT_APPS)
        if num_bots == 0:
            return

        chosen_emojis = random.sample(REACTIONS_POOL, k=min(num_bots, len(REACTIONS_POOL)))

        tasks = []
        for i, app_inst in enumerate(BOT_APPS):
            tasks.append(send_single_reaction(app_inst, chat_id, message_id, chosen_emojis[i]))
        
        await asyncio.gather(*tasks)

async def post_init(main_app):
    """सभी सेकेंडरी बॉट्स को प्रॉपर्ली Start/Initialize करेगा"""
    global BOT_APPS
    BOT_APPS.append(main_app)
    
    for token in BOT_TOKENS[1:]:
        sec_app = ApplicationBuilder().token(token).build()
        await sec_app.initialize()
        await sec_app.start()
        BOT_APPS.append(sec_app)
        
    print(f"✅ Successfully initialized {len(BOT_APPS)} bots!")

if __name__ == "__main__":
    # Flask Web Server बैकग्राउंड में
    threading.Thread(target=run_flask, daemon=True).start()

    if not BOT_TOKENS:
        print("Error: No BOT_TOKEN found in Environment Variables!")
    else:
        # Main Receiver Bot Setup
        main_app = ApplicationBuilder().token(BOT_TOKENS[0]).post_init(post_init).build()
        main_app.add_handler(MessageHandler(filters.ChatType.CHANNEL & ~filters.COMMAND, auto_react_multi))

        main_app.run_polling(drop_pending_updates=True)
