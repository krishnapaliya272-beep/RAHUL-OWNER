import os
import random
import threading
from flask import Flask
import telebot

# --- Web Server for Render ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Multi-Bot Reaction Active!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- Environment Tokens ---
RAW_TOKENS = [
    os.getenv("BOT_TOKEN"),
    os.getenv("BOT_TOKEN_2") or os.getenv("BOT_TOKEN2"),
    os.getenv("BOT_TOKEN_3") or os.getenv("BOT_TOKEN3"),
    os.getenv("BOT_TOKEN_4") or os.getenv("BOT_TOKEN4"),
    os.getenv("BOT_TOKEN_5") or os.getenv("BOT_TOKEN5"),
]

BOT_TOKENS = [t.strip() for t in RAW_TOKENS if t and len(t.strip()) > 10]
REACTIONS_POOL = ["👍", "❤️", "🔥", "👏", "😍", "🎉", "🤩", "💯"]

# Create TeleBot Instances
BOT_INSTANCES = [telebot.TeleBot(token, threaded=False) for token in BOT_TOKENS]

def send_reaction(bot_obj, chat_id, message_id, emoji):
    try:
        bot_obj.set_message_reaction(chat_id=chat_id, message_id=message_id, reaction=[telebot.types.ReactionTypeEmoji(emoji)])
    except Exception as e:
        print(f"Reaction Error: {e}")

if __name__ == "__main__":
    # Flask Web Server
    threading.Thread(target=run_flask, daemon=True).start()

    if not BOT_INSTANCES:
        print("No tokens provided!")
    else:
        main_bot = BOT_INSTANCES[0]

        @main_bot.channel_post_handler(func=lambda message: True)
        def handle_channel_post(message):
            chat_id = message.chat.id
            msg_id = message.message_id
            
            num_bots = len(BOT_INSTANCES)
            chosen_emojis = random.sample(REACTIONS_POOL, k=min(num_bots, len(REACTIONS_POOL)))

            # Threading to send reactions in parallel
            threads = []
            for idx, b_inst in enumerate(BOT_INSTANCES):
                t = threading.Thread(target=send_reaction, args=(b_inst, chat_id, msg_id, chosen_emojis[idx]))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

        print(f"✅ Total Synced Bots: {len(BOT_INSTANCES)}")
        
        # Clear old conflict updates and run
        main_bot.infinity_polling(skip_pending=True)
