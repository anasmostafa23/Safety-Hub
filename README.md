# 🛡️ Safety-Hub 

<div align="center">

**Цифровая система безопасности для проведения аудитов на производстве**

*A digital safety system for conducting workplace safety audits*

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot-API-blue.svg)](https://core.telegram.org/bots/api)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[🇺🇸 English](#english) • [🇷🇺 Русский](#русский)

</div>

---

## 📋 Оглавление / Table of Contents

- [Описание / Overview](#описание--overview)
- [Ключевые возможности / Key Features](#ключевые-возможности--key-features)
- [Архитектура системы / System Architecture](#архитектура-системы--system-architecture)
- [Установка и настройка / Installation & Setup](#установка-и-настройка--installation--setup)
- [Использование / Usage](#использование--usage)
- [Конфигурация / Configuration](#конфигурация--configuration)
- [API команды бота / Bot Commands](#api-команды-бота--bot-commands)
- [Структура проекта / Project Structure](#структура-проекта--project-structure)
- [Требования / Requirements](#требования--requirements)
- [Разработка / Development](#разработка--development)
- [Лицензия / License](#лицензия--license)

---

## Описание / Overview

**Safety-Hub** — это современная система для проведения цифровых аудитов безопасности на производственных объектах. Система заменяет традиционные бумажные чек-листы на интерактивный Telegram-бот с поддержкой двуязычного интерфейса (английский/русский).

**Safety-Hub** is a modern system for conducting digital safety audits at industrial sites. The system replaces traditional paper checklists with an interactive Telegram bot supporting a bilingual interface (English/Russian).

### 🎯 Цели проекта / Project Goals

- ✅ Цифровизация процесса аудита безопасности / Digitalize safety audit processes
- ✅ Снижение использования бумажной документации / Reduce paper documentation
- ✅ Автоматизация генерации отчетов / Automate report generation
- ✅ Анализ тенденций безопасности / Analyze safety trends
- ✅ Поддержка многоязычности / Multilingual support

---

## Ключевые возможности / Key Features

### 🤖 Telegram Bot (Основной интерфейс)
- **Интерактивные опросы** — Удобные кнопки для ответов на вопросы / Interactive surveys with convenient buttons
- **Двуязычная поддержка** — Вопросы и ответы на английском и русском / Bilingual support for questions and answers
- **Генерация PDF отчетов** — Автоматическое создание профессиональных отчетов / Automatic PDF report generation
- **Управление шаблонами** — Гибкая система чек-листов / Flexible template management system

### 📊 Dashboard (Аналитическая панель)
- **Визуализация данных** — Графики и диаграммы производительности / Data visualization with charts and graphs
- **Фильтрация и поиск** — Глубокий анализ по различным параметрам / Advanced filtering and search capabilities
- **Сравнительный анализ** — Оценка по сайтам и сотрудникам / Comparative analysis by sites and employees
- **ИИ ассистент** — Рекомендации на основе данных / AI assistant for data-driven recommendations

### 🗄️ Database (База данных)
- **SQLite** — Легковесная и надежная база данных / Lightweight and reliable database
- **SQLAlchemy ORM** — Удобный интерфейс для работы с данными / Convenient data access interface
- **Экспорт данных** — Возможность экспорта в CSV / Data export to CSV format

### ⚙️ Admin Panel (Админ панель)
- **PDF/DOCX Processing** — Конвертация документов безопасности в JSON шаблоны / Convert safety documents to JSON templates
- **AI-Powered Parsing** — Использование OpenAI для интеллектуального анализа документов / AI-powered document analysis
- **Template Management** — Полное управление шаблонами аудита / Complete audit template management
- **Multi-Template Support** — Динамическое переключение между шаблонами / Dynamic template switching

---

## Архитектура системы / System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Telegram Bot   │    │   Dashboard     │    │    Database     │
│                 │    │   (Streamlit)   │    │   (SQLite)      │
│ • Опросы        │◄──►│ • Аналитика     │◄──►│ • Пользователи  │
│ • Генерация PDF │    │ • Визуализация  │    │ • Аудиты        │
│ • Шаблоны       │    │ • AI ассистент  │    │ • Ответы        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Компоненты / Components

| Компонент / Component | Технология / Technology | Описание / Description |
|----------------------|------------------------|----------------------|
| **Bot Core** | python-telegram-bot | Основная логика Telegram бота / Main bot logic |
| **Database** | SQLAlchemy + SQLite | Хранение данных аудитов / Audit data storage |
| **Dashboard** | Streamlit | Веб-интерфейс аналитики / Web analytics interface |
| **PDF Generator** | ReportLab | Создание PDF отчетов / PDF report generation |
| **AI Assistant** | OpenAI GPT-4 | Анализ данных и рекомендации / Data analysis and recommendations |
| **Templates** | JSON | Гибкие чек-листы / Flexible checklists |

---

## Установка и настройка / Installation & Setup

### Предварительные требования / Prerequisites

- Python 3.8+
- Telegram Bot Token (от @BotFather)
- OpenAI API Key (для ИИ ассистента)

### Шаг 1: Клонирование репозитория / Clone Repository

```bash
git clone https://github.com/anasmostafa23/Safety-Hub.git
cd Safety-Hub
```

### Шаг 2: Установка зависимостей / Install Dependencies

```bash
pip install -r requirements.txt
```

### Шаг 3: Настройка окружения / Environment Setup

Создайте файл `.env` в корневой директории проекта:

```env
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

# OpenAI Configuration (для AI ассистента)
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration (опционально)
DATABASE_URL=sqlite:///database/safetyhub.db
```

### Шаг 4: Инициализация базы данных / Database Initialization

```bash
python -c "from database.models import init_db; init_db()"
```

### Шаг 5: Запуск бота / Run the Bot

```bash
python bot.py
```

### Шаг 6: Запуск Dashboard (в новом терминале) / Run Dashboard

```bash
streamlit run database/dashboard.py
```

---

## Использование / Usage

### 🚀 Запуск Telegram бота / Starting Telegram Bot

1. **Запустите бота** командой `/start`
2. **Введите ФИО** — Полное имя для отчета / Enter full name for the report
3. **Укажите ID объекта** — Идентификатор производственного объекта / Specify site ID
4. **Пройдите опрос** — Ответьте на вопросы безопасности / Complete the safety questionnaire
5. **Получите PDF отчет** — Автоматическая генерация отчета / Receive PDF report

### 📊 Использование Dashboard / Using Dashboard

1. **Откройте браузер** и перейдите на `http://localhost:8501`
2. **Выберите шаблон** аудита для анализа / Select audit template for analysis
3. **Настройте фильтры** по сайту, сотруднику и датам / Configure filters by site, employee, and dates
4. **Изучите аналитику** в различных вкладках / Explore analytics across different tabs
5. **Задайте вопросы** ИИ ассистенту для получения рекомендаций / Ask AI assistant for recommendations

### 📋 Пример рабочего процесса / Example Workflow

```
Пользователь → Запуск бота → Ввод данных → Опрос → Генерация PDF
     ↓
Администратор → Dashboard → Анализ данных → Отчеты → Рекомендации
```

---

## Конфигурация / Configuration

### Переменные окружения / Environment Variables

| Переменная / Variable | Описание / Description | Обязательна / Required |
|----------------------|------------------------|----------------------|
| `BOT_TOKEN` | Токен Telegram бота / Telegram bot token | ✅ Да / Yes |
| `OPENAI_API_KEY` | API ключ OpenAI для ИИ ассистента / OpenAI API key for AI assistant | ⚠️ Опционально / Optional |
| `DATABASE_URL` | URL базы данных / Database URL | ⚠️ Опционально / Optional |

### Шаблоны опросов / Survey Templates

Шаблоны хранятся в формате JSON в папке `templates/`:

```json
{
  "template_name": "Название шаблона / Template Name",
  "categories": [
    {
      "name": "Категория / Category",
      "questions": [
        {
          "keyword": "ключ_слово / keyword",
          "question_en": "Question in English",
          "question_ru": "Вопрос на русском",
          "options": ["Yes", "No", "N/A"]
        }
      ]
    }
  ]
}
```

---

## API команды бота / Bot Commands

| Команда / Command | Описание / Description | Доступ / Access |
|------------------|------------------------|----------------|
| `/start` | Начать новый аудит / Start new audit | Все / Everyone |
| `/myid` | Показать ваш Telegram ID / Show your Telegram ID | Все / Everyone |
| `/upload_audit` | Загрузить документ аудита / Upload audit document | Админ / Admin |
| `/list_templates` | Показать доступные шаблоны / List available templates | Админ / Admin |
| `/select_template` | Выбрать активный шаблон / Select active template | Админ / Admin |
| `/current_template` | Показать текущий шаблон / Show current template | Админ / Admin |

---

## Структура проекта / Project Structure

```
Safety-Hub/
├── bot.py                          # Основной файл бота / Main bot file
├── requirements.txt                # Зависимости Python / Python dependencies
├── README.md                       # Документация / Documentation
├── database/                       # База данных и модели / Database and models
│   ├── models.py                   # SQLAlchemy модели / SQLAlchemy models
│   ├── db.py                       # Функции базы данных / Database functions
│   ├── dashboard.py                # Streamlit приложение / Streamlit application
│   ├── creat_db.py                 # Создание базы данных / Database creation
│   └── safetyhub.db                # SQLite база данных / SQLite database
├── handlers/                       # Обработчики событий / Event handlers
│   ├── audit.py                    # Логика аудита / Audit logic
│   └── admin.py                    # Админ функции / Admin functions
├── templates/                      # Шаблоны опросов / Survey templates
│   ├── template1_full_bilingual.json # Двуязычный шаблон / Bilingual template
│   └── test_template2.json         # Тестовый шаблон / Test template
├── utils/                          # Вспомогательные утилиты / Utility functions
│   ├── audit_parser.py             # Парсер аудитов / Audit parser
│   ├── pdf_generator.py            # Генератор PDF / PDF generator
│   ├── template_loader.py          # Загрузчик шаблонов / Template loader
│   └── utils.py                    # Общие утилиты / Common utilities
└── exports/                        # Экспортированные данные / Exported data
```

---

## Требования / Requirements

### Основные зависимости / Core Dependencies

```txt
python-telegram-bot==20.8    # Telegram Bot API
reportlab==3.6.12           # PDF генерация / PDF generation
sqlalchemy                  # ORM для базы данных / Database ORM
streamlit                   # Веб фреймворк / Web framework
python-dotenv               # Управление окружением / Environment management
```

### Аналитические библиотеки / Analytics Libraries

```txt
pandas                      # Анализ данных / Data analysis
matplotlib                  # Визуализация / Visualization
seaborn                     # Статистические графики / Statistical plots
plotly                      # Интерактивные графики / Interactive plots
```

### ИИ и машинное обучение / AI & Machine Learning

```txt
openai                      # ИИ ассистент / AI assistant
streamlit-chat              # Чат интерфейс / Chat interface
```

---

## Разработка / Development

### Настройка окружения разработки / Development Setup

1. **Создайте виртуальное окружение** / Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или / or
venv\Scripts\activate     # Windows
```

2. **Установите зависимости разработки** / Install development dependencies:
```bash
pip install -r requirements.txt
```

3. **Настройте pre-commit hooks** (опционально):
```bash
pre-commit install
```

### Структура кода / Code Structure

- **handlers/** — Обработчики команд и событий бота / Bot command and event handlers
- **database/** — Модели данных и функции базы данных / Data models and database functions
- **utils/** — Вспомогательные функции и утилиты / Helper functions and utilities
- **templates/** — JSON шаблоны для опросов / JSON templates for surveys

---

[![Powered by Python](https://img.shields.io/badge/powered%20by-Python-blue.svg)](https://python.org)
[![For Industrial Safety](https://img.shields.io/badge/for-Industrial%20Safety-red.svg)](https://github.com/anasmostafa23/Safety-Hub)

</div>
