import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()
logging.basicConfig(level=logging.INFO)
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

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN отсутствует: задайте секретную переменную на Render.")
    app = Application.builder().token(token).build()
    commands = {
        "start": start, "help": start, "services": services,
        "booking": booking, "cancel": cancel, "address": address,
        "contraindications": contraindications, "admin": admin,
    }
    for name, handler in commands.items():
        app.add_handler(CommandHandler(name, handler))
    logger.info("Starting Kegel03 bot in polling mode")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
