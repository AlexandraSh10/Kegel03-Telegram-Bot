import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("kegel03")

ADDRESS = "Улан-Удэ, ул. Бабушкина, 22Б, офис 311, офис-центр «Багульник»"
BOOKING_URL = os.getenv("DIKIDI_BOOKING_URL", "").strip()
ADMIN_CONTACT = os.getenv("ADMIN_CONTACT", "").strip()

def menu():
    rows = []
    if BOOKING_URL.startswith("https://"):
        rows.append([InlineKeyboardButton("Записаться через DIKIDI", url=BOOKING_URL)])
    if ADMIN_CONTACT.startswith("https://"):
        rows.append([InlineKeyboardButton("Связаться с администратором", url=ADMIN_CONTACT)])
    return InlineKeyboardMarkup(rows) if rows else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "Здравствуйте! 🌷 Добро пожаловать в студию КЕГЕЛЬ.\n"
        "Мы помогаем женщинам заботиться о мышцах тазового дна с помощью занятий на кресле Кегель.\n\n"
        "Занятие занимает около 30 минут, проходит в одежде.\n\n"
        "Команды: /services — услуги, /booking — запись, /cancel — отмена, "
        "/address — адрес, /contraindications — ограничения, /admin — администратор.",
        reply_markup=menu(),
    )

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "🌸 Занятия на кресле Кегель — около 30 минут, без переодевания.\n"
        "Также в студии можно уточнить информацию о других услугах.\n"
        "Подбор занятий индивидуален; результат не гарантируется.\n"
        "Для записи: /booking", reply_markup=menu()
    )

async def booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if BOOKING_URL.startswith("https://"):
        await update.effective_message.reply_text(
            "Выберите удобное время на странице DIKIDI. Запись подтверждается только в DIKIDI.",
            reply_markup=menu(),
        )
    else:
        await update.effective_message.reply_text(
            "Онлайн-запись скоро появится. Пока свяжитесь с администратором: /admin. "
            "Бот пока не может подтвердить запись."
        )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "Чтобы отменить или перенести запись, откройте свою запись в DIKIDI "
        "или свяжитесь с администратором: /admin. "
        "Бот не отменяет записи самостоятельно.", reply_markup=menu()
    )

async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("📍 " + ADDRESS)

async def contraindications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "Занятия подходят не всем. При беременности, наличии имплантированных "
        "электронных устройств, серьёзных заболеваниях или сомнениях "
        "перед посещением необходимо обсудить безопасность с врачом. "
        "Администратор не ставит диагнозы и не заменяет консультацию специалиста."
    )

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ADMIN_CONTACT:
        await update.effective_message.reply_text(
            "Связаться с администратором: " + ADMIN_CONTACT,
            reply_markup=menu(),
        )
    else:
        await update.effective_message.reply_text(
            "Контакт администратора пока настраивается. Адрес студии: " + ADDRESS
        )

async def group_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Respond only to clear service/booking questions; avoid interrupting group chat."""
    message = update.effective_message
    if not message or not message.text:
        return
    text = message.text.casefold()
    if any(word in text for word in ("записаться", "как запис", "онлайн-запись", "свободное время")):
        await booking(update, context)
    elif any(word in text for word in ("отменить запись", "перенести запись", "отмена записи")):
        await cancel(update, context)
    elif any(word in text for word in ("адрес студии", "где находитесь", "как вас найти")):
        await address(update, context)
    elif any(word in text for word in ("противопоказания", "кому нельзя")):
        await contraindications(update, context)
    elif any(word in text for word in ("сколько длится", "какие услуги", "что за кресло")):
        await services(update, context)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Kegel03 bot service online")

    def log_message(self, format, *args):
        return


def start_health_server():
    port = int(os.getenv("PORT", "10000"))
    ThreadingHTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()


def main():
    threading.Thread(target=start_health_server, daemon=True).start()
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN is missing; web health service is running, Telegram bot is NOT active.")
        threading.Event().wait()
        return
    app = Application.builder().token(token).build()
    commands = {
        "start": start, "help": start, "services": services,
        "booking": booking, "cancel": cancel, "address": address,
        "contraindications": contraindications, "admin": admin,
    }
    for name, handler in commands.items():
        app.add_handler(CommandHandler(name, handler))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT & ~filters.COMMAND, group_questions))
    logger.info("Starting Kegel03 bot in polling mode")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
