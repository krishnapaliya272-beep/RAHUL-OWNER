import os
import random
import asyncio
import threading
from flask import Flask
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# --- Web Server for Render Keep-Alive ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Multi-Bot Reaction System Active!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- Fetch Environment Variables ---
# यह अपने आप Render की Environment सेटिंग्स से टोकन उठा लेगा
RAW_TOKENS = [
    os.getenv("BOT_TOKEN"),
    os.getenv("BOT_TOKEN_2"),
    os.getenv("BOT_TOKEN_3"),
    os.getenv("BOT_TOKEN_4"),
    os.getenv("BOT_TOKEN_5"),
]

# खाली या न मिलने वाले टोकन हटाकर एक्टिव लिस्ट बनाएँ
BOT_TOKENS = [t.strip() for t in RAW_TOKENS if t and len(t.strip()) > 10]
BOT_INSTANCES = [Bot(token=t) for t in BOT_TOKENS]

REACTIONS_POOL = ["👍", "❤️", "🔥", "👏", "😍", "🎉", "🤩", "💯"]

async def send_single_reaction(bot_instance: Bot, chat_id: int, message_id: int, emoji: str):
    """हर एक बॉट से अलग-अलग रिएक्शन भेजने के लिए"""
    try:
        await bot_instance.set_reaction(chat_id=chat_id, message_id=message_id, reaction=[emoji])
    except Exception as e:
        print(f"Error from bot {bot_instance.id}: {e}")

async def auto_react_multi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post:
        chat_id = update.channel_post.chat.id
        message_id = update.channel_post.message_id

        num_bots = len(BOT_INSTANCES)
        if num_bots == 0:
            return

        # जितने बॉट मौजूद हैं, उतने रैंडम इमोजी चुनें
        chosen_emojis = random.sample(REACTIONS_POOL, k=min(num_bots, len(REACTIONS_POOL)))

        # सभी बॉट्स से एक साथ रिएक्शनTrigger करें
        tasks = []
        for i, bot_inst in enumerate(BOT_INSTANCES):
            tasks.append(send_single_reaction(bot_inst, chat_id, message_id, chosen_emojis[i]))
        
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Background Thread में Web Server चालू करें
    threading.Thread(target=run_flask, daemon=True).start()

    if not BOT_TOKENS:
        print("Error: Render Environment में कोई BOT_TOKEN नहीं मिला!")
    else:
        print(f"Total synced bots running: {len(BOT_TOKENS)}")
        
        # मुख्य बॉट (BOT_TOKEN) को पोलिंग पर रखें
        main_app = ApplicationBuilder().token(BOT_TOKENS[0]).build()
        main_app.add_handler(MessageHandler(filters.ChatType.CHANNEL & ~filters.COMMAND, auto_react_multi))

        main_app.run_polling(drop_pending_updates=True)
