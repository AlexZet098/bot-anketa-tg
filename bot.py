import logging
import asyncio
from telegram import BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from handlers import (
    start, fio, dob, date, reason, source, height, waist, hips, general_health,
    cancel, add_question, save_question, get_id, send_test_file
)

# Ваш токен и список ID администраторов
TOKEN = '7112103187:AAFRB0oWUFfzXJgwKFDtxgmBpu07qu3e16k'
ADMIN_IDS = ['427264609', '1056118643']

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Определение состояний для опроса
(FIO, DOB, DATE, REASON, SOURCE, HEIGHT, WAIST, HIPS, GENERAL_HEALTH, NEW_QUESTION) = range(10)


async def set_commands(application: Application) -> None:
    commands = [
        BotCommand("start", "Начать опрос"),
        BotCommand("add_question", "Добавить новый вопрос"),
        BotCommand("send_test_file", "Отправить тестовый файл (только для администраторов)"),
        BotCommand("get_id", "Получить свой Telegram ID")
    ]
    await application.bot.set_my_commands(commands)


async def main():
    application = Application.builder().token(TOKEN).connect_timeout(30).read_timeout(30).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, fio)],
            DOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, dob)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date)],
            REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, reason)],
            SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, source)],
            HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, height)],
            WAIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, waist)],
            HIPS: [MessageHandler(filters.TEXT & ~filters.COMMAND, hips)],
            GENERAL_HEALTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, general_health)],
            NEW_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_question)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('add_question', add_question))
    application.add_handler(CommandHandler('send_test_file', send_test_file))
    application.add_handler(CommandHandler('get_id', get_id))

    # Устанавливаем команды бота
    await set_commands(application)

    # Запуск бота
    await application.initialize()
    await application.start()
    logger.info("Bot started.")

    # Запуск polling
    await application.updater.start_polling()
    logger.info("Polling started.")

    # Ожидание завершения работы
    await application.updater.idle()

    # Завершение работы приложения
    await application.stop()
    await application.shutdown()


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except Exception as e:
        logger.error(f"Ошибка запуска цикла событий: {e}")
