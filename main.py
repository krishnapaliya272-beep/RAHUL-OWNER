import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

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
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("on", turn_on))
    app.add_handler(CommandHandler("off", turn_off))
    app.add_handler(CommandHandler("status", status_cmd))

    app.add_handler(MessageHandler(filters.ChatType.CHANNEL & ~filters.COMMAND, auto_react))

    app.run_polling()
