import logging
import asyncio
from telegram import BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from handlers import (
    start, fio, dob, date, reason, source, height, waist, hips, general_health,
    cancel, add_question, save_question
)

# Ваш токен и список ID администраторов
TOKEN = '7112103187:AAFRB0oWUFfzXJgwKFDtxgmBpu07qu3e16k'
ADMIN_IDS = ['1056118643', '427264609']

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


# Настройка команды бота
async def set_commands(application: Application) -> None:
    commands = [
        BotCommand("start", "Начать опрос"),
        BotCommand("add_question", "Добавить новый вопрос")
    ]
    await application.bot.set_my_commands(commands)


async def main() -> None:
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Настраиваем обработчик разговоров
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, fio)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, dob)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, date)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, reason)],
            4: [MessageHandler(filters.TEXT & ~filters.COMMAND, source)],
            5: [MessageHandler(filters.TEXT & ~filters.COMMAND, height)],
            6: [MessageHandler(filters.TEXT & ~filters.COMMAND, waist)],
            7: [MessageHandler(filters.TEXT & ~filters.COMMAND, hips)],
            8: [MessageHandler(filters.TEXT & ~filters.COMMAND, general_health)],
            9: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_question)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Добавляем обработчики в приложение
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('add_question', add_question))

    # Устанавливаем команды бота
    await set_commands(application)

    # Запускаем приложение
    logger.info("Bot started.")
    await application.initialize()
    await application.start()
    logger.info("Polling started.")

    # Используем бесконечный цикл ожидания
    try:
        await application.updater.start_polling(timeout=60)  # Увеличиваем таймаут до 60 секунд
        await asyncio.Event().wait()  # Бесконечное ожидание
    finally:
        await application.stop()
        logger.info("Bot stopped.")


if __name__ == '__main__':
    asyncio.run(main())
