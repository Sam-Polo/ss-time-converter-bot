import os
import re
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pytz

# загрузка переменных окружения
load_dotenv()

# настройка логирования (вывод в stdout для docker logs)
logging.basicConfig(
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()  # вывод в stdout/stderr
    ]
)
logger = logging.getLogger(__name__)

# логирование для telegram библиотеки
telegram_logger = logging.getLogger('telegram')
telegram_logger.setLevel(logging.WARNING)  # только предупреждения и ошибки от telegram

# получение токена бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """обработчик команды /start"""
    try:
        user = update.effective_user
        chat = update.effective_chat
        logger.info(f"команда /start от пользователя {user.id} (@{user.username}) в чате {chat.id} ({chat.type})")
        
        await update.message.reply_text(
            "Привет! Я бот для конвертации времени.\n"
            "Напиши: \"конвертировать ЧЧ:ММ\" для конвертации текущего времени из МСК в Ташкент, Баку и UTC+0.\n"
            "Или используй /time."
        )
        logger.info(f"ответ на /start отправлен пользователю {user.id}")
        
    except Exception as e:
        logger.error(f"ошибка в обработчике /start: {e}", exc_info=True)
        try:
            await update.message.reply_text("❌ Произошла ошибка. Попробуй позже.")
        except:
            pass


async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """обработчик команды /time - конвертирует текущее время из МСК в Ташкент, Баку и UTC+0"""
    try:
        user = update.effective_user
        chat = update.effective_chat
        logger.info(f"команда /time от пользователя {user.id} (@{user.username}) в чате {chat.id}")
        
        # часовые пояса
        msk_tz = pytz.timezone('Europe/Moscow')
        tashkent_tz = pytz.timezone('Asia/Tashkent')
        baku_tz = pytz.timezone('Asia/Baku')
        utc_tz = pytz.UTC
        
        # получаем текущее время в МСК
        msk_time = datetime.now(msk_tz)
        logger.debug(f"текущее время МСК: {msk_time}")
        
        # конвертируем в UTC, затем в другие пояса
        utc_time = msk_time.astimezone(utc_tz)
        tashkent_time = utc_time.astimezone(tashkent_tz)
        baku_time = utc_time.astimezone(baku_tz)
        
        # форматируем время
        time_format = "%H:%M:%S %d.%m.%Y"
        
        response = (
            f"🕐 Время (МСК {msk_time.strftime('%H:%M')}):\n\n"
            f"🇺🇿 Ташкент: {tashkent_time.strftime(time_format)}\n"
            f"🇦🇿 Баку: {baku_time.strftime(time_format)}\n"
            f"🌍 UTC+0: {utc_time.strftime(time_format)}"
        )
        
        await update.message.reply_text(response)
        logger.info(f"ответ на /time отправлен пользователю {user.id}")
        
    except Exception as e:
        logger.error(f"ошибка в обработчике /time: {e}", exc_info=True)
        try:
            await update.message.reply_text("❌ Произошла ошибка при конвертации времени. Попробуй позже.")
        except:
            pass


def convert_time(hour: int, minute: int):
    """конвертирует время из МСК в Ташкент, Баку и UTC+0"""
    try:
        logger.debug(f"конвертация времени: {hour:02d}:{minute:02d} МСК")
        
        # часовые пояса
        msk_tz = pytz.timezone('Europe/Moscow')
        tashkent_tz = pytz.timezone('Asia/Tashkent')
        baku_tz = pytz.timezone('Asia/Baku')
        utc_tz = pytz.UTC
        
        # создаем объект времени на сегодня в МСК
        msk_now = datetime.now(msk_tz)
        msk_time = msk_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # конвертируем в UTC, затем в другие пояса
        utc_time = msk_time.astimezone(utc_tz)
        tashkent_time = utc_time.astimezone(tashkent_tz)
        baku_time = utc_time.astimezone(baku_tz)
        
        time_format = "%H:%M"
        date_format = "%d.%m.%Y"
        
        result = (
            f"🕐 Конвертация времени (МСК {msk_time.strftime(time_format)}):\n\n"
            f"🇺🇿 Ташкент: {tashkent_time.strftime(time_format)} ({tashkent_time.strftime(date_format)})\n"
            f"🇦🇿 Баку: {baku_time.strftime(time_format)} ({baku_time.strftime(date_format)})\n"
            f"🌍 UTC+0: {utc_time.strftime(time_format)} ({utc_time.strftime(date_format)})"
        )
        
        logger.debug(f"конвертация завершена успешно: МСК {hour:02d}:{minute:02d} -> Ташкент {tashkent_time.strftime(time_format)}, Баку {baku_time.strftime(time_format)}, UTC {utc_time.strftime(time_format)}")
        return result
        
    except Exception as e:
        logger.error(f"ошибка при конвертации времени {hour:02d}:{minute:02d}: {e}", exc_info=True)
        raise


async def convert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """обработчик команды /convert - конвертирует указанное время"""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        if not context.args:
            logger.info(f"команда /convert без аргументов от пользователя {user.id} в чате {chat.id}")
            await update.message.reply_text(
                "Используй: /convert ЧЧ:ММ\n"
                "Пример: /convert 15:30"
            )
            return
        
        # парсим время из аргументов
        time_str = context.args[0]
        logger.info(f"команда /convert с аргументом '{time_str}' от пользователя {user.id} в чате {chat.id}")
        
        try:
            hour, minute = map(int, time_str.split(':'))
            
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                logger.warning(f"неверное время от пользователя {user.id}: {hour}:{minute}")
                raise ValueError("Неверное время")
            
            response = convert_time(hour, minute)
            await update.message.reply_text(response)
            logger.info(f"ответ на /convert отправлен пользователю {user.id}")
            
        except (ValueError, IndexError) as e:
            logger.warning(f"ошибка парсинга времени '{time_str}' от пользователя {user.id}: {e}")
            await update.message.reply_text(
                "❌ Неверный формат времени. Используй: /convert ЧЧ:ММ\n"
                "Пример: /convert 15:30"
            )
        
    except Exception as e:
        logger.error(f"ошибка в обработчике /convert: {e}", exc_info=True)
        try:
            await update.message.reply_text("❌ Произошла ошибка. Попробуй позже.")
        except:
            pass


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """обработчик сообщений - ищет паттерн 'конвертировать ЧЧ:ММ'"""
    try:
        if not update.message or not update.message.text:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        text = update.message.text
        
        logger.debug(f"получено сообщение от пользователя {user.id} в чате {chat.id}: {text[:50]}...")
        
        # ищем паттерн "конвертировать ЧЧ:ММ" (регистронезависимо, с любыми пробелами)
        # поддерживаем: "конвертировать 00:00", "Конвертировать 15:30", "КОНВЕРТИРОВАТЬ 12:00" и т.д.
        pattern = r'(?:конвертировать|convert)\s+(\d{1,2}):(\d{2})'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            try:
                hour = int(match.group(1))
                minute = int(match.group(2))
                
                logger.info(f"найден паттерн конвертации в сообщении от пользователя {user.id}: {hour}:{minute}")
                
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    logger.warning(f"неверное время в сообщении от пользователя {user.id}: {hour}:{minute}")
                    return  # игнорируем неверное время
                
                response = convert_time(hour, minute)
                await update.message.reply_text(response)
                logger.info(f"ответ на сообщение отправлен пользователю {user.id}")
                
            except (ValueError, IndexError) as e:
                logger.warning(f"ошибка парсинга времени из сообщения от пользователя {user.id}: {e}")
            except Exception as e:
                logger.error(f"ошибка при обработке сообщения от пользователя {user.id}: {e}", exc_info=True)
                
    except Exception as e:
        logger.error(f"критическая ошибка в обработчике сообщений: {e}", exc_info=True)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """обработчик всех необработанных ошибок"""
    logger.error(f"необработанная ошибка: {context.error}", exc_info=context.error)
    
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Произошла непредвиденная ошибка. Администратор уведомлен."
            )
        except:
            pass


def main():
    """запуск бота"""
    try:
        logger.info("=" * 50)
        logger.info("запуск бота конвертации времени")
        logger.info("=" * 50)
        
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN не установлен в переменных окружения!")
            return
        
        logger.info("токен бота загружен успешно")
        
        # создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        logger.info("приложение telegram создано")
        
        # регистрируем обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("time", time_command))
        application.add_handler(CommandHandler("convert", convert_command))
        logger.info("обработчики команд зарегистрированы: /start, /time, /convert")
        
        # регистрируем обработчик текстовых сообщений (должен быть после команд)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        logger.info("обработчик текстовых сообщений зарегистрирован")
        
        # регистрируем обработчик ошибок
        application.add_error_handler(error_handler)
        logger.info("обработчик ошибок зарегистрирован")
        
        # запускаем бота
        logger.info("бот запущен и готов к работе")
        logger.info("=" * 50)
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except KeyboardInterrupt:
        logger.info("получен сигнал остановки, завершение работы бота...")
    except Exception as e:
        logger.critical(f"критическая ошибка при запуске бота: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()

