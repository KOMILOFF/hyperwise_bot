import logging
import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
import google.generativeai as genai

# 1. FLASK SERVER
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# 2. BOT VA GEMINI SOZLAMALARI
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8373360174:AAFxh3p5al6CiWStNmnaFeSAFCeWrfGR4iw")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCwTal5pIcI024UKB2au7QbZ1rtlP22OYw")

# Gemini sozlamalari
genai.configure(api_key=GEMINI_API_KEY)

# MUHIM: Modelni yaratishda xatolikni oldini olish uchun nomni tekshiramiz
try:
    # 'models/' prefiksisiz yozib ko'ramiz, bu ko'p hollarda yordam beradi
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    logging.error(f"Model yuklashda xato: {e}")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Bot qayta sozlandi. Savolingizni yuboring.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Javob olish
        response = model.generate_content(user_text)
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("Gemini javob bera olmadi (xavfsizlik yoki bo'sh javob).")
            
    except Exception as e:
        error_str = str(e)
        logging.error(f"Xatolik: {error_str}")
        
        # Agar yana 404 xatosi chiqsa, muqobil modelni sinab ko'ramiz
        if "404" in error_str:
            await update.message.reply_text("Model topilmadi. Kutubxonalarni yangilash kerak yoki model nomi o'zgargan.")
        else:
            await update.message.reply_text(f"Xatolik: {error_str[:100]}")

if __name__ == '__main__':
    keep_alive()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()