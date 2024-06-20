import logging
import asyncio
import nest_asyncio
from telegram import BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from handlers import (
    start, fio, dob, date, reason, source, height, waist, hips, general_health,
    cancel, add_question, save_question, FIO, DOB, DATE, REASON, SOURCE, HEIGHT, WAIST, HIPS, GENERAL_HEALTH, NEW_QUESTION
)

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

# Определение команд бота
async def set_commands(application: Application) -> None:
    commands = [
        BotCommand("start", "Начать опрос"),
        BotCommand("add_question", "Добавить новый вопрос"),
    ]
    await application.bot.set_my_commands(commands)

async def main() -> None:
    # Создание приложения Telegram Bot
    application = Application.builder().token("7112103187:AAFRB0oWUFfzXJgwKFDtxgmBpu07qu3e16k").build()

    # Обработчик последовательности вопросов
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

    # Устанавливаем команды бота
    await set_commands(application)

    # Запускаем бота
    await application.initialize()
    logger.info("Бот запущен.")
    await application.start()
    logger.info("Polling запущен.")

    # Используем встроенный метод run_polling для запуска и ожидания
    await application.updater.start_polling()

if __name__ == '__main__':
    nest_asyncio.apply()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем.")
