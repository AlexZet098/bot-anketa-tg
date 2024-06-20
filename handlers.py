import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputFile
from telegram.ext import ConversationHandler, ContextTypes
from docx import Document
import json
import os

# Идентификаторы администраторов
ADMIN_IDS = ['427264609', '1056118643']

# Настройка логирования
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
(FIO, DOB, DATE, REASON, SOURCE, HEIGHT, WAIST, HIPS, GENERAL_HEALTH, NEW_QUESTION) = range(10)

# Вопросы анкеты
questions = [
    ("Пожалуйста, введите ваше ФИО:", FIO),
    ("Введите вашу дату рождения:", DOB),
    ("Введите дату заполнения анкеты:", DATE),
    ("С чем связано ваше обращение?", REASON),
    ("Откуда вы узнали о докторе?", SOURCE),
    ("Введите ваш рост (см):", HEIGHT),
    ("Введите объем талии (см):", WAIST),
    ("Введите объем бедер (см):", HIPS),
    ("Как вы оцениваете ваше общее состояние здоровья?", GENERAL_HEALTH)
]


# Функция сохранения ответов в файл
def save_response(user_data):
    try:
        fio = user_data.get('Пожалуйста, введите ваше ФИО:', 'unknown').replace(' ', '_')
        filename = f"Анкета_{fio}.docx"
        document = Document()
        for question, answer in user_data.items():
            document.add_paragraph(f"{question}: {answer}")
        document.save(filename)
        logger.info(f"Ответы сохранены в файл: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Не удалось сохранить ответы: {e}")
        return None


# Обработчики шагов анкеты
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"Пользователь {update.message.from_user.id} начал беседу.")
    await update.message.reply_text(
        "Здравствуйте! Пожалуйста, введите ваше ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )
    return FIO


async def fio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['Пожалуйста, введите ваше ФИО:'] = update.message.text
    await update.message.reply_text("Введите вашу дату рождения:")
    return DOB


async def dob(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['Введите вашу дату рождения:'] = update.message.text
    await update.message.reply_text("Введите дату заполнения анкеты:")
    return DATE


async def date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['Введите дату заполнения анкеты:'] = update.message.text
    await update.message.reply_text("С чем связано ваше обращение?")
    return REASON


async def reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['С чем связано ваше обращение?'] = update.message.text
    await update.message.reply_text("Откуда вы узнали о докторе?")
    return SOURCE


async def source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['Откуда вы узнали о докторе?'] = update.message.text
    await update.message.reply_text("Введите ваш рост (см):")
    return HEIGHT


async def height(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['Введите ваш рост (см):'] = update.message.text
    await update.message.reply_text("Введите объем талии (см):")
    return WAIST


async def waist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['Введите объем талии (см):'] = update.message.text
    await update.message.reply_text("Введите объем бедер (см):")
    return HIPS


async def hips(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['Введите объем бедер (см):'] = update.message.text
    await update.message.reply_text("Как вы оцениваете ваше общее состояние здоровья?",
                                    reply_markup=ReplyKeyboardMarkup(
                                        [['Очень хорошее', 'Хорошее', 'Удовлетворительное', 'Плохое', 'Очень плохое']],
                                        one_time_keyboard=True))
    return GENERAL_HEALTH


async def general_health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['Как вы оцениваете ваше общее состояние здоровья?'] = update.message.text
    await update.message.reply_text("Спасибо! Ваша анкета заполнена.", reply_markup=ReplyKeyboardRemove())

    # Сохраняем данные или обрабатываем их по мере необходимости
    logger.info(f"Пользователь {update.message.from_user.id} завершил опрос: {context.user_data}")
    filename = save_response(context.user_data)  # Сохраняем ответы в файл

    # Запускаем задачу для отправки файла администраторам через 2 минуты
    if filename:
        asyncio.create_task(send_responses_to_admins(context.application, filename))

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Анкета отменена.', reply_markup=ReplyKeyboardRemove())
    logger.info(f"Пользователь {update.message.from_user.id} отменил опрос.")
    return ConversationHandler.END


async def add_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if str(update.message.from_user.id) not in ADMIN_IDS:
        await update.message.reply_text("У вас нет прав на добавление вопросов.")
        return ConversationHandler.END
    await update.message.reply_text("Введите текст нового вопроса:")
    return NEW_QUESTION


async def save_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    new_question = update.message.text
    new_state = len(questions) + 10  # Добавляем смещение, чтобы избежать конфликта с существующими состояниями
    questions.append((new_question, new_state))
    await update.message.reply_text(f"Вопрос добавлен: {new_question}")
    logger.info(f"Администратор {update.message.from_user.id} добавил новый вопрос: {new_question}")
    return ConversationHandler.END


async def send_responses_to_admins(application, filename):
    await asyncio.sleep(10)  # Ждем 2 минуты
    for admin_id in ADMIN_IDS:
        try:
            with open(filename, "rb") as file:
                await application.bot.send_document(chat_id=admin_id, document=InputFile(file), filename=filename)
            logger.info(f"Файл с ответами отправлен администратору {admin_id}")
        except Exception as e:
            logger.error(f"Не удалось отправить файл с ответами администратору {admin_id}: {e}")
