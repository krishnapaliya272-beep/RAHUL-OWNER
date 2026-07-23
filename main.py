import os
import random
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# --- Configs from Render Environment ---
RAW_TOKENS = [
    os.getenv("BOT_TOKEN"),
    os.getenv("BOT_TOKEN_2") or os.getenv("BOT_TOKEN2"),
    os.getenv("BOT_TOKEN_3") or os.getenv("BOT_TOKEN3"),
    os.getenv("BOT_TOKEN_4") or os.getenv("BOT_TOKEN4"),
    os.getenv("BOT_TOKEN_5") or os.getenv("BOT_TOKEN5"),
]

BOT_TOKENS = [t.strip() for t in RAW_TOKENS if t and len(t.strip()) > 10]
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
REACTIONS_POOL = ["👍", "❤️", "🔥", "👏", "😍", "🎉", "🤩", "💯"]

web_app = Flask(__name__)

# Global instances list
BOT_APPS = []

async def send_single_reaction(app_instance, chat_id: int, message_id: int, emoji: str):
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

@web_app.route('/')
def home():
    return "Multi-Bot Webhook Active!", 200

@web_app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        try:
            json_data = request.get_json(force=True)
            if BOT_APPS:
                update = Update.de_json(json_data, BOT_APPS[0].bot)
                asyncio.run(BOT_APPS[0].process_update(update))
        except Exception as e:
            print(f"Webhook Error: {e}")
    return "OK", 200

async def setup_bots_and_webhook():
    global BOT_APPS
    if not BOT_TOKENS:
        print("No tokens found!")
        return

    # Setup All Bots
    for token in BOT_TOKENS:
        app = ApplicationBuilder().token(token).build()
        await app.initialize()
        await app.start()
        BOT_APPS.append(app)

    # Attach handler to main bot
    BOT_APPS[0].add_handler(MessageHandler(filters.ChatType.CHANNEL & ~filters.COMMAND, auto_react_multi))

    # Set Webhook for Main Bot
    webhook_url = f"{RENDER_URL}/webhook"
    await BOT_APPS[0].bot.set_webhook(url=webhook_url, drop_pending_updates=True)
    print(f"✅ Webhook set successfully to: {webhook_url}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup_bots_and_webhook())

    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)
