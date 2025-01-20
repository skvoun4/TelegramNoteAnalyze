

# Telegram Note Analyzer

## Описание задания
Цель: Создание Telegram-бота, который сохраняет заметки пользователей, анализирует их с помощью моделей OpenAI и возвращает результат анализа.

Задача: Автоматизация обработки текстов, предоставление удобного интерфейса через Telegram и использование OpenAI API для анализа текста.

## Видение проекта
Удобство: Telegram-бот позволяет пользователям легко добавлять заметки и получать их анализ без сложных манипуляций.
Инновация: Использование современных NLP-моделей для анализа текста.
Масштабируемость: Проект можно расширить, добавив больше функций, таких как классификация, анализ тональности и другие.

## Описание проекта
Проект представляет собой Telegram-бота, который позволяет сохранять текстовые заметки и анализировать их с помощью OpenAI API.

## Функциональность
1. Добавление заметок (/addnote).
2. Анализ текста (/analyze).

## Пайплайн работы системы
 Описание пайплайна:

Пользователь → Telegram → API Telegram → Обработка (бот) → OpenAI API → Результат (анализ) → Пользователь

## Архитектура проекта

Описание архитектуры:

Telegram Bot:
Отвечает за взаимодействие с пользователем.

База данных SQLite:
Хранит заметки.

OpenAI API:
Выполняет анализ текста.

Тестирование:
Модульные тесты для проверки корректности работы системы.

Пользователь отправляет команду /addnote или /analyze в Telegram.
Бот обрабатывает входные данные (заметки сохраняются в БД).
При анализе бот вызывает OpenAI API и передаёт текст заметки.
Результат возвращается пользователю.
Все ошибки логируются, а результаты сохраняются.

## Требования
- Python 3.8+
- Telegram Bot API
- OpenAI API Key

## Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/skvoun4/TelegramNoteAnalyze.git

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt

3. Запустите бота:
  ```bash
  python src/bot.py

