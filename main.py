# Bot version 1.0.1
import os
import sys
import signal
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Sprawdzanie tokena
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("Error: No BOT_TOKEN provided in environment variables")
    sys.exit(1)

print(f"Starting bot...")

# Przechowywanie odpowiedzi (w prostej wersji - w pamięci)
attendance = {}

# Obsługa zamykania
def signal_handler(signum, frame):
    print('Shutting down bot...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Reszta kodu pozostaje bez zmian...

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Komenda startowa"""
    await update.message.reply_text(
        "Cześć! Jestem botem do zarządzania obecnością na spotkaniach Mastermind."
        "\nUżyj /spotkanie aby utworzyć nowe głosowanie obecności."
    )

async def create_meeting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tworzenie nowego spotkania"""
    # Przyciski do głosowania
    keyboard = [
        [
            InlineKeyboardButton("✅ Będę", callback_data='yes'),
            InlineKeyboardButton("❌ Nie będę", callback_data='no'),
            InlineKeyboardButton("❓ Może", callback_data='maybe')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Data następnego spotkania
    next_meeting = datetime.now() + timedelta(days=1)
    meeting_date = next_meeting.strftime("%d.%m.%Y")
    
    message = (
        f"📅 Spotkanie Mastermind - {meeting_date}, 20:30\n\n"
        "Potwierdź swoją obecność:"
    )
    
    # Wysłanie wiadomości i zapisanie jej ID
    sent_message = await update.message.reply_text(message, reply_markup=reply_markup)
    attendance[sent_message.message_id] = {
        'yes': [],
        'no': [],
        'maybe': []
    }

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obsługa odpowiedzi"""
    query = update.callback_query
    user = query.from_user.first_name
    choice = query.data
    message_id = query.message.message_id

    # Aktualizacja listy obecności
    for status in attendance[message_id]:
        if user in attendance[message_id][status]:
            attendance[message_id][status].remove(user)
    attendance[message_id][choice].append(user)

    # Przygotowanie zaktualizowanej wiadomości
    base_message = query.message.text.split('\n\n')[0]
    updated_message = f"{base_message}\n\n"
    updated_message += "👥 Lista obecności:\n"
    updated_message += f"✅ Będą: {', '.join(attendance[message_id]['yes'])}\n"
    updated_message += f"❌ Nie będą: {', '.join(attendance[message_id]['no'])}\n"
    updated_message += f"❓ Może: {', '.join(attendance[message_id]['maybe'])}"

    await query.message.edit_text(
        updated_message,
        reply_markup=query.message.reply_markup
    )
    await query.answer()

def main():
    """Uruchomienie bota"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Dodanie handlerów
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("spotkanie", create_meeting))
    application.add_handler(CallbackQueryHandler(button_click))
    
    # Uruchomienie bota
    application.run_polling()

if __name__ == '__main__':
    main()
