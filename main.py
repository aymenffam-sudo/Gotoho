import os
import logging
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# إعداد اللوغز
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- الإعدادات ---
TOKEN = "8541787354:AAEmvs6oZ4E-pErraa5ZCSDaKOFn2lwlc6s"
# يفضل وضع الـ Seller Key في متغيرات البيئة على Railway أو GitHub Secrets
KEYAUTH_SELLER_KEY = os.environ.get("KEYAUTH-fXN0u7-sgGJmR-CR3UXx-Uf9zBP-QiKunB-vyhSig", "KEYAUTH-fXN0u7-sgGJmR-CR3UXx-Uf9zBP-QiKunB-vyhSig")
KEYAUTH_API_URL = "https://keyauth.win/api/seller/"
CHANNEL_URL = "https://t.me/TYMOxitado"
SUPPORT_LINK = "https://t.me/TYMOxitado" 

# استعمال Client واحد مفتوح للسرعة
http_client = httpx.AsyncClient(timeout=10.0)

# --- القوائم ---
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📁 Get Files", callback_data="get_files"),
         InlineKeyboardButton("🔍 Check Status", callback_data="check_status")],
        [InlineKeyboardButton("🔄 Reset HWID", callback_data="reset_hwid_info")],
        [InlineKeyboardButton("🛒 Buy Keys", callback_data="buy_keys")],
        [InlineKeyboardButton("📞 Support", url=SUPPORT_LINK),
         InlineKeyboardButton("📢 Channel", url=CHANNEL_URL)],
    ]
    return InlineKeyboardMarkup(keyboard)

# --- العمليات الأساسية ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "👋 <b>مرحباً بك في متجر Fluorite!</b>\n\nاختر من القائمة أسفله لخدمتك:"
    if update.message:
        await update.message.reply_text(text, reply_markup=get_main_menu(), parse_mode="HTML")
    else:
        await update.callback_query.edit_message_text(text, reply_markup=get_main_menu(), parse_mode="HTML")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: <code>/status KEY</code>", parse_mode="HTML")
        return

    key = context.args[0].upper()
    sent_msg = await update.message.reply_text("⚡ <i>جاري التحقق...</i>", parse_mode="HTML")

    try:
        params = {"sellerkey": KEYAUTH_SELLER_KEY, "type": "info", "key": key}
        response = await http_client.get(KEYAUTH_API_URL, params=params)
        data = response.json()

        if data.get("success"):
            info = data.get("key", {})
            msg = (f"✅ <b>Key Info:</b>\n"
                   f"🔑 Key: <code>{key}</code>\n"
                   f"⏳ Expiry: {info.get('expires')}")
        else:
            msg = "❌ <b>الكود غير صحيح أو منتهي.</b>"
    except Exception as e:
        logger.error(f"Error: {e}")
        msg = "⚠️ عذراً، حدث خطأ في الاتصال بالسيرفر."

    await sent_msg.edit_text(msg, parse_mode="HTML")

# --- وظيفة Reset HWID ---
async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: <code>/reset KEY</code>", parse_mode="HTML")
        return

    key = context.args[0].upper()
    sent_msg = await update.message.reply_text("⏳ <i>جاري تصفير الـ HWID...</i>", parse_mode="HTML")

    params = {
        "sellerkey": KEYAUTH_SELLER_KEY,
        "type": "resethwid",
        "key": key
    }
    
    try:
        response = await http_client.get(KEYAUTH_API_URL, params=params)
        data = response.json()
        
        if data.get("success"):
            msg = f"✅ <b>بصحة و راحة!</b>\nتم تصفير HWID للكود: <code>{key}</code> بنجاح."
        else:
            # عرض سبب الفشل من KeyAuth (مثلاً الكود غير موجود)
            error_msg = data.get('message', 'Unknown error')
            msg = f"❌ <b>فشل التصفير:</b>\n{error_msg}"
            
    except Exception as e:
        logger.error(f"Reset Error: {e}")
        msg = "⚠️ حدث خطأ أثناء الاتصال بـ KeyAuth."

    await sent_msg.edit_text(msg, parse_mode="HTML")

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_status":
        await query.edit_message_text(
            "🔍 للتحقق من حالة الكود، أرسل:\n<code>/status YOUR_KEY</code>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back")]])
        )
    elif query.data == "reset_hwid_info":
        await query.edit_message_text(
            "🔄 لتصفير الـ HWID، أرسل الأمر التالي:\n\n<code>/reset YOUR_KEY</code>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back")]])
        )
    elif query.data == "back":
        await start(update, context)

# --- تشغيل البوت ---
def main():
    # تصحيح التوكن هنا
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("reset", reset_command)) # إضافة الهاندلر الجديد
    app.add_handler(CallbackQueryHandler(handle_callbacks))
    
    print("🚀 Bot is running with Reset HWID feature...")
    app.run_polling()

if __name__ == "__main__":
    main()
