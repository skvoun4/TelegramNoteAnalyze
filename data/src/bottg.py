import openai
import logging
import csv
import os
import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Установите свой API ключ OpenAI
openai.api_key = ''

# Установите свой API токен Telegram, полученный от BotFather
TELEGRAM_API_TOKEN = ''

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация подключения к MySQL
DB_CONFIG = {
    'host': '',      # Замените на адрес вашего MySQL-сервера
    'user': '',           # Укажите пользователя MySQL
    'password': '',   # Укажите пароль пользователя
    'database': ''   # Название базы данных
}

# Установление соединения с MySQL
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Инициализация базы данных
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Создание таблицы для заметок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                text TEXT NOT NULL
            )
        ''')
        conn.commit()
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
    finally:
        conn.close()

# Функция для приветственного сообщения
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я Bolknote_AI. Напиши /help, чтобы увидеть доступные команды.")

# Функция для вывода списка команд
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "/start - Запустить бота и получить приветственное сообщение\n"
        "/help - Получить список доступных команд\n"
        "/addnote <text> - Добавить новую заметку с текстом для анализа\n"
        "/viewnotes - Просмотреть все сохраненные заметки\n"
        "/delete_note <note_id> - Удалить заметку по ее идентификатору\n"
        "/analyze <note_id> - Проанализировать текст заметки с использованием ChatGPT\n"
        "/export - Экспортировать заметки в CSV файл\n"
        "/import <filename> - Импортировать заметки из готового CSV файла\n"
        "/feedback <text> - Отправить отзыв или предложение о боте"
    )
    await update.message.reply_text(help_text)

# Функция для добавления заметки
async def addnote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    note_text = ' '.join(context.args)
    if not note_text:
        await update.message.reply_text("Пожалуйста, укажите текст заметки.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (text) VALUES (%s)", (note_text,))
        conn.commit()
        note_id = cursor.lastrowid
        await update.message.reply_text(f"Заметка добавлена с идентификатором: {note_id}")
    except Exception as e:
        logger.error(f"Ошибка при добавлении заметки: {e}")
        await update.message.reply_text("Произошла ошибка при добавлении заметки.")
    finally:
        conn.close()

# Функция для просмотра всех заметок
async def viewnotes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes")
        notes = cursor.fetchall()
        conn.close()

        if not notes:
            await update.message.reply_text("У вас нет заметок.")
        else:
            notes_list = "\n".join([f"{note[0]}: {note[1]}" for note in notes])
            await update.message.reply_text(f"Ваши заметки:\n{notes_list}")
    except Exception as e:
        logger.error(f"Ошибка при просмотре заметок: {e}")
        await update.message.reply_text("Произошла ошибка при просмотре заметок.")

# Функция для удаления заметки
async def delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        note_id = int(context.args[0])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
        conn.commit()

        if cursor.rowcount > 0:
            await update.message.reply_text(f"Заметка с идентификатором {note_id} удалена.")
        else:
            await update.message.reply_text(f"Заметка с идентификатором {note_id} не найдена.")
    except (IndexError, ValueError):
        await update.message.reply_text("Пожалуйста, укажите идентификатор заметки для удаления.")
    finally:
        conn.close()

# Функция для анализа текста заметки с помощью ChatGPT
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        note_id = int(context.args[0])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT text FROM notes WHERE id = %s", (note_id,))
        note = cursor.fetchone()
        conn.close()

        if note is None:
            await update.message.reply_text(f"Заметка с идентификатором {note_id} не найдена.")
            return

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": note[0]}]
        )
        analysis = response.choices[0].message['content']
        await update.message.reply_text(f"Результат анализа заметки:\n{analysis}")
    except (IndexError, ValueError):
        await update.message.reply_text("Пожалуйста, укажите идентификатор заметки для анализа.")

# Функция для экспорта заметок в CSV
async def export_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes")
        notes = cursor.fetchall()
        conn.close()

        with open('notes_export.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Text'])
            writer.writerows(notes)

        await update.message.reply_text("Заметки экспортированы в файл notes_export.csv.")
    except Exception as e:
        logger.error(f"Ошибка при экспорте заметок: {e}")
        await update.message.reply_text("Произошла ошибка при экспорте заметок.")

# Основная функция для запуска бота
def main() -> None:
    init_db()  # Инициализация базы данных MySQL
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("addnote", addnote))
    application.add_handler(CommandHandler("viewnotes", viewnotes))
    application.add_handler(CommandHandler("delete_note", delete_note))
    application.add_handler(CommandHandler("analyze", analyze))
    application.add_handler(CommandHandler("export", export_notes))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
