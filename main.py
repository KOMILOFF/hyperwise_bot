import logging
import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
import google.generativeai as genai

# 1. FLASK SERVER (Render uyquga ketmasligi uchun)
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    # Render avtomatik taqdim etadigan portni olamiz
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True  # Asosiy dastur to'xtasa, bu ham to'xtaydi
    t.start()

# 2. BOT VA GEMINI SOZLAMALARI
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8373360174:AAFxh3p5al6CiWStNmnaFeSAFCeWrfGR4iw")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCwTal5pIcI024UKB2au7QbZ1rtlP22OYw")

# Gemini sozlamalari (Tuzatilgan qismi)
genai.configure(api_key=GEMINI_API_KEY)
# Model nomini aniq va transport sozlamasiz belgilaymiz
model = genai.GenerativeModel('gemini-1.5-flash')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Men endi barqaror ishlayapman. Savolingizni yuboring.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # Foydalanuvchiga bot o'ylayotganini ko'rsatish
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Gemini'dan javob so'raymiz
        response = model.generate_content(user_text)
        
        if response and response.text:
            # Javobni qismlarga bo'lib yuborish (agar juda uzun bo'lsa)
            if len(response.text) > 4096:
                for i in range(0, len(response.text), 4096):
                    await update.message.reply_text(response.text[i:i+4096])
            else:
                await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("Kechirasiz, javob topilmadi yoki filtrga tushdi.")
            
    except Exception as e:
        logging.error(f"Xatolik yuz berdi: {e}")
        await update.message.reply_text("Hozircha javob bera olmayman, birozdan so'ng qayta urinib ko'ring.")

if __name__ == '__main__':
    # Web serverni ishga tushirish
    keep_alive()
    
    # Telegram botni ishga tushirish
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("--- Bot Render-da muvaffaqiyatli ishga tushdi ---")
    application.run_polling()