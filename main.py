import os
import random
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- Flask Server for Keep-Alive ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is alive and running 24/7!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- Telegram Bot Config ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6313249215"))

IS_ACTIVE = True
REACTIONS = ["👍", "❤️", "🔥", "👏", "😍"]

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**Auto Reaction Bot Active**\n\n"
        "Commands:\n"
        "▶️ /on - Turn ON auto reaction\n"
        "⏸️ /off - Turn OFF auto reaction\n"
        "📊 /status - View current status",
        parse_mode="Markdown"
    )

async def turn_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global IS_ACTIVE
    if update.effective_user.id != ADMIN_ID:
        return
    IS_ACTIVE = True
    await update.message.reply_text("✅ **Auto Reaction Enabled!**", parse_mode="Markdown")

async def turn_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global IS_ACTIVE
    if update.effective_user.id != ADMIN_ID:
        return
    IS_ACTIVE = False
    await update.message.reply_text("⏸️ **Auto Reaction Disabled!**", parse_mode="Markdown")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_text = "🟢 **ON**" if IS_ACTIVE else "🔴 **OFF**"
    await update.message.reply_text(f"📊 Status: {status_text}", parse_mode="Markdown")

async def auto_react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global IS_ACTIVE
    if not IS_ACTIVE:
        return

    if update.channel_post:
        try:
            chosen_emoji = random.choice(REACTIONS)
            await update.channel_post.set_reaction(reaction=chosen_emoji)
        except Exception as e:
            print(f"Reaction Error: {e}")

if __name__ == "__main__":
    # Flask Server को Background thread में चालू करें
    threading.Thread(target=run_flask, daemon=True).start()

    # Telegram Bot Polling चालू करें
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("on", turn_on))
    app.add_handler(CommandHandler("off", turn_off))
    app.add_handler(CommandHandler("status", status_cmd))

    app.add_handler(MessageHandler(filters.ChatType.CHANNEL & ~filters.COMMAND, auto_react))

    app.run_polling()
