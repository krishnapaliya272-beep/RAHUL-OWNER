import os
import random
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# --- Keep-Alive Web Server for Render ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Single Bot Reaction Active!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# Render Environment से टोकन उठाएगा
BOT_TOKEN = os.getenv("BOT_TOKEN")
REACTIONS_POOL = ["👍", "❤️", "🔥", "👏", "😍", "🎉", "🤩", "💯"]

async def auto_react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post:
        chat_id = update.channel_post.chat.id
        message_id = update.channel_post.message_id
        
        # रैंडम इमोजी चुनकर पोस्ट पर चिपकाएगा
        chosen_emoji = random.choice(REACTIONS_POOL)
        
        try:
            await context.bot.set_reaction(
                chat_id=chat_id,
                message_id=message_id,
                reaction=[chosen_emoji]
            )
            print(f"Reaction {chosen_emoji} added successfully!")
        except Exception as e:
            print(f"Error setting reaction: {e}")

if __name__ == "__main__":
    # Web server को background thread में चालू करें
    threading.Thread(target=run_flask, daemon=True).start()

    if not BOT_TOKEN:
        print("Error: BOT_TOKEN Environment Variable नहीं मिला!")
    else:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # चैनल पोस्ट पर रिएक्शन लगाने का हैंडलर
        app.add_handler(MessageHandler(filters.ChatType.CHANNEL & ~filters.COMMAND, auto_react))

        print("Bot Started...")
        app.run_polling(drop_pending_updates=True)
