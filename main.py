import logging
import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

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

genai.configure(api_key=GEMINI_API_KEY)

# Xavfsizlik filtrlarini yumshatamiz (javob qaytmaslik ehtimolini kamaytirish uchun)
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    safety_settings=safety_settings
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Men tayyorman. Savolingizni yuboring.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Gemini'dan javob so'raymiz
        response = model.generate_content(user_text)
        
        # Javobni tekshirish
        if response.parts:
            text_reply = response.text
            if len(text_reply) > 4096:
                for i in range(0, len(text_reply), 4096):
                    await update.message.reply_text(text_reply[i:i+4096])
            else:
                await update.message.reply_text(text_reply)
        else:
            # Agar javob bloklangan bo'lsa
            await update.message.reply_text("Kechirasiz, bu savolga javob berolmayman (xavfsizlik filtri).")
            
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Xatolik: {error_msg}")
        # Aniq xatolikni foydalanuvchiga ko'rsatish (muammoni topish uchun)
        await update.message.reply_text(f"Xatolik yuz berdi: {error_msg[:100]}...")

if __name__ == '__main__':
    keep_alive()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()