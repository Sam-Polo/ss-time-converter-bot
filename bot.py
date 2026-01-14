import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import pytz

# загрузка переменных окружения
load_dotenv()

# настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# получение токена бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """обработчик команды /start"""
    await update.message.reply_text(
        "Привет! Я бот для конвертации времени.\n"
        "Используй /time для конвертации текущего времени из МСК в Ташкент и Баку."
    )


async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """обработчик команды /time - конвертирует время из МСК в Ташкент и Баку"""
    # часовые пояса
    msk_tz = pytz.timezone('Europe/Moscow')
    tashkent_tz = pytz.timezone('Asia/Tashkent')
    baku_tz = pytz.timezone('Asia/Baku')
    
    # получаем текущее время в UTC и конвертируем в нужные пояса
    utc_now = datetime.now(pytz.UTC)
    msk_time = utc_now.astimezone(msk_tz)
    tashkent_time = utc_now.astimezone(tashkent_tz)
    baku_time = utc_now.astimezone(baku_tz)
    
    # форматируем время
    time_format = "%H:%M:%S %d.%m.%Y"
    
    response = (
        f"🕐 Время в разных городах:\n\n"
        f"🇷🇺 МСК: {msk_time.strftime(time_format)}\n"
        f"🇺🇿 Ташкент: {tashkent_time.strftime(time_format)}\n"
        f"🇦🇿 Баку: {baku_time.strftime(time_format)}"
    )
    
    await update.message.reply_text(response)


async def convert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """обработчик команды /convert - конвертирует указанное время"""
    if not context.args:
        await update.message.reply_text(
            "Используй: /convert ЧЧ:ММ\n"
            "Пример: /convert 15:30"
        )
        return
    
    try:
        # парсим время из аргументов
        time_str = context.args[0]
        hour, minute = map(int, time_str.split(':'))
        
        # часовые пояса
        msk_tz = pytz.timezone('Europe/Moscow')
        tashkent_tz = pytz.timezone('Asia/Tashkent')
        baku_tz = pytz.timezone('Asia/Baku')
        
        # создаем объект времени на сегодня в МСК
        msk_now = datetime.now(msk_tz)
        msk_time = msk_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # конвертируем в UTC, затем в другие пояса
        utc_time = msk_time.astimezone(pytz.UTC)
        tashkent_time = utc_time.astimezone(tashkent_tz)
        baku_time = utc_time.astimezone(baku_tz)
        
        time_format = "%H:%M"
        date_format = "%d.%m.%Y"
        
        response = (
            f"🕐 Конвертация времени:\n\n"
            f"🇷🇺 МСК: {msk_time.strftime(time_format)} ({msk_time.strftime(date_format)})\n"
            f"🇺🇿 Ташкент: {tashkent_time.strftime(time_format)} ({tashkent_time.strftime(date_format)})\n"
            f"🇦🇿 Баку: {baku_time.strftime(time_format)} ({baku_time.strftime(date_format)})"
        )
        
        await update.message.reply_text(response)
        
    except (ValueError, IndexError):
        await update.message.reply_text(
            "❌ Неверный формат времени. Используй: /convert ЧЧ:ММ\n"
            "Пример: /convert 15:30"
        )


def main():
    """запуск бота"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен!")
        return
    
    # создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("convert", convert_command))
    
    # запускаем бота
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

