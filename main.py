import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- CONFIGURATION ---
# Replace these with your actual KeyAuth Seller settings
KEYAUTH_SELLER_KEY = os.environ.get("KEYAUTH_SELLER_KEY", "YOUR_SELLER_KEY_HERE")
KEYAUTH_API_URL = "https://keyauth.win/api/seller/"
# It is better to use an environment variable for the token!
BOT_TOKEN = "7455950486:AAH41crmMxtNg3FFyetNXDf27ZBTF3dtoEI"

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Check Status", callback_data='status_help')],
        [InlineKeyboardButton("🔄 Reset HWID", callback_data='reset_help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💎 <b>Welcome to Fluorite Bot</b>\nManage your licenses instantly.",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'status_help':
        await query.edit_message_text("Usage: <code>/status YOUR_KEY</code>", parse_mode="HTML")
    elif query.data == 'reset_help':
        await query.edit_message_text("Usage: <code>/reset YOUR_KEY</code>", parse_mode="HTML")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ <b>Please provide a key.</b>\nUsage: <code>/status KEY</code>", parse_mode="HTML")
        return
    
    key = context.args[0].upper()
    
    try:
        params = {"sellerkey": KEYAUTH_SELLER_KEY, "type": "info", "key": key}
        response = requests.get(KEYAUTH_API_URL, params=params, timeout=10)
        data = response.json()
        
        if data.get("success"):
            key_info = data.get("key", {})
            # KeyAuth returns 'active' as a status or boolean usually
            await update.message.reply_text(
                f"🔑 <b>Key Status</b>\n\n"
                f"<b>Key:</b> <code>{key}</code>\n"
                f"<b>Status:</b> ✅ Active\n"
                f"<b>Expiry:</b> {key_info.get('expires', 'N/A')}",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(f"❌ <b>Error:</b> {data.get('message', 'Key not found.')}", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Status error: {e}")
        await update.message.reply_text("❌ <b>API Error.</b> Please try again later.", parse_mode="HTML")

async def reset_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ <b>Usage:</b> <code>/reset KEY</code>", parse_mode="HTML")
        return
    
    key = context.args[0].upper()
    try:
        # KeyAuth Seller API reset type is usually 'reset'
        params = {"sellerkey": KEYAUTH_SELLER_KEY, "type": "reset", "key": key}
        response = requests.get(KEYAUTH_API_URL, params=params, timeout=10)
        data = response.json()
        
        if data.get("success"):
            await update.message.reply_text(f"✅ <b>HWID Reset successfully</b> for: <code>{key}</code>", parse_mode="HTML")
        else:
            await update.message.reply_text(f"❌ <b>Reset Failed:</b> {data.get('message')}", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Reset error: {e}")
        await update.message.reply_text("❌ <b>API Error.</b>", parse_mode="HTML")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📚 <b>Available Commands</b>\n\n"
        "/start - Start the bot\n"
        "/reset KEY - Reset key HWID\n"
        "/status KEY - Check key status\n"
        "/help - Show this message"
    )
    await update.message.reply_text(help_text, parse_mode="HTML")

def main():
    if not BOT_TOKEN:
        logger.error("No Bot Token provided!")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset_key))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    logger.info("✅ Fluorite Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
