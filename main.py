import logging
import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
import google.generativeai as genai

# 1. FLASK SERVER (Render uchun)
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    # Render avtomatik ravishda PORT muhit o'zgaruvchisini beradi
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. BOT SOZLAMALARI
# Maslahat: Tokenlarni Render Settings -> Env Vars bo'limiga qo'shing
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8373360174:AAFxh3p5al6CiWStNmnaFeSAFCeWrfGR4iw")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCwTal5pIcI024UKB2au7QbZ1rtlP22OYw")

genai.configure(api_key=GEMINI_API_KEY, transport='rest')
MODEL_NAME = 'gemini-1.5-flash' 
model = genai.GenerativeModel(model_name=MODEL_NAME)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Render'da doimiy ishlovchi bot tayyor. Savolingizni yuboring.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        response = model.generate_content(user_text)
        if response and response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("Gemini bo'sh javob qaytardi.")
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await update.message.reply_text(f"Xatolik yuz berdi: {str(e)}")

if __name__ == '__main__':
    # Web serverni alohida thread'da ishga tushiramiz
    keep_alive()
    
    # Botni ishga tushirish
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print(f"--- Bot Render muhitida ishga tushdi ---")
    application.run_polling()