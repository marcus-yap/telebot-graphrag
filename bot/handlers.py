from telegram import Update
from telegram.ext import ContextTypes
from bot.response_pipeline import get_bot_response

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a message :)")

# main handler
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = get_bot_response(user_message)
    
    if not response:
        await update.message.reply_text("Sorry, I couldn't find a response for that.")
        return
    
    reply = "\n\n".join([f". {item['text']}" for item in response])
    await update.message.reply_text(reply)