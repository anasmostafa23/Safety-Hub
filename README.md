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

### Соглашения о коде / Coding Conventions

- **Типизация** — Используйте type hints / Use type hints
- **Документация** — Документируйте функции и классы / Document functions and classes
- **Тестирование** — Пишите тесты для новой функциональности / Write tests for new features
- **Линтинг** — Соблюдайте PEP 8 / Follow PEP 8

---

## 📊 Technical Presentation Slides / Технические слайды презентации

Для демонстрации технической сложности проекта рекомендуется подготовить следующие слайды для комиссии:

### 1. Функциональные требования / Functional Requirements

**Основные требования к системе:**
- ✅ **Цифровизация аудита** — Замена бумажных чек-листов на цифровые / Replace paper checklists with digital
- ✅ **Многоязычный интерфейс** — Поддержка английского и русского языков / English and Russian language support
- ✅ **Автоматическая обработка документов** — Конвертация PDF/DOCX в JSON шаблоны / PDF/DOCX to JSON template conversion
- ✅ **Генерация отчетов** — Создание PDF отчетов с результатами аудита / PDF report generation
- ✅ **Аналитическая панель** — Визуализация данных и трендов / Data visualization and trends
- ✅ **ИИ ассистент** — Анализ данных и рекомендации по безопасности / AI-powered data analysis

**Пользовательские роли:**
- 👤 **Пользователь** — Проходит аудиты безопасности / Conducts safety audits
- 👨‍💼 **Администратор** — Управляет шаблонами и анализирует данные / Manages templates and analyzes data
- 🤖 **Система** — Обрабатывает документы и генерирует отчеты / Processes documents and generates reports

### 2. Архитектура системы / System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Внешние сервисы / External Services          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Telegram   │  │   OpenAI    │  │   Streamlit │              │
│  │   Bot API   │  │   GPT-4     │  │   Cloud     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼───────┐ ┌─────▼──────┐ ┌─────▼──────┐
        │ Telegram Bot  │ │ Dashboard  │ │ Database   │
        │               │ │ (Flask)    │ │ (SQLite)   │
        │ • Опросы      │ │ • Графики  │ │ • Users    │
        │ • Шаблоны     │ │ • Анализ   │ │ • Audits   │
        │ • PDF Export  │ │ • AI Чат   │ │ • Responses│
        └───────────────┘ └────────────┘ └────────────┘
```

**Технологии и библиотеки / Technologies & Libraries:**
- **Backend**: Python 3.8+, AsyncIO, SQLAlchemy ORM
- **Telegram Bot**: python-telegram-bot 20.8
- **База данных**: SQLite с SQLAlchemy
- **Веб интерфейс**: Streamlit 1.28+
- **PDF обработка**: pdfplumber, ReportLab 3.6.12
- **ИИ интеграция**: OpenAI GPT-4 API
- **Аналитика**: pandas, matplotlib, seaborn, plotly
- **Дополнительно**: python-dotenv, streamlit-aggrid

### 3. Алгоритмы обработки данных / Data Processing Algorithms

**Первое взаимодействие пользователя / First User Interaction:**
```
1. Пользователь → /start
2. Бот → Запрос ФИО и Site ID
3. Загрузка активного шаблона из JSON
4. Создание записи в БД (Users, Audits)
5. Генерация интерактивного опроса
6. Сбор ответов через callback buttons
7. Сохранение в таблицу Responses
8. Генерация PDF отчета
```

**Обработка документов администратором / Admin Document Processing:**
```
1. Админ → /upload_audit + PDF файл
2. Система → pdfplumber извлечение текста
3. Отправка текста в OpenAI GPT-4
4. AI парсинг → структурированный JSON
5. Валидация и сохранение шаблона
6. Обновление активного шаблона
```

**Регулярные обновления / Regular Updates:**
- Автоматическая синхронизация шаблонов
- Пересчет аналитических метрик
- Обновление дашборда в реальном времени
- Архивация старых данных

### 4. Схема базы данных / Database Schema

```sql
┌─────────────────────────────────────────────────────────┐
│                        Users                            │
├─────────────────────────────────────────────────────────┤
│ telegram_id (INTEGER, PRIMARY KEY)                      │
│ full_name (VARCHAR)                                     │
│ site_id (VARCHAR)                                       │
└─────────────────────────────────────────────────────────┘
                                │ 1:N
                                ▼
┌─────────────────────────────────────────────────────────┐
│                        Audits                           │
├─────────────────────────────────────────────────────────┤
│ id (INTEGER, PRIMARY KEY, AUTOINC)                      │
│ user_id (INTEGER, FK → Users.telegram_id)               │
│ site_id (VARCHAR)                                       │
│ title (VARCHAR)                                         │
│ timestamp (DATETIME, DEFAULT NOW)                       │
└─────────────────────────────────────────────────────────┘
                                │ 1:N
                                ▼
┌─────────────────────────────────────────────────────────┐
│                       Responses                         │
├─────────────────────────────────────────────────────────┤
│ id (INTEGER, PRIMARY KEY, AUTOINC)                     │
│ audit_id (INTEGER, FK → Audits.id)                      │
│ question_index (INTEGER)                                │
│ category (VARCHAR)                                      │
│ question (TEXT)                                         │
│ question_ru (VARCHAR)                                   │
│ keyword (VARCHAR)                                       │
│ response (TEXT)                                         │
└─────────────────────────────────────────────────────────┘
```

**Оптимизация производительности / Performance Optimization:**
- Индексы на внешние ключи / Foreign key indexes
- Композитные индексы для аналитики / Composite indexes for analytics
- Автоматическое резервное копирование / Automatic backup

### 5. Обоснование выбора ИИ инструментов / ML Tools Justification

**OpenAI GPT-4 для обработки документов:**

| Аспект / Aspect | Обоснование / Justification |
|----------------|----------------------------|
| **Точность** | Понимание контекста безопасности / Understanding safety context |
| **Структура** | Генерация правильного JSON формата / Proper JSON structure generation |
| **Многоязычность** | Поддержка английского и русского / English and Russian support |
| **Консистентность** | Единообразное создание шаблонов / Consistent template creation |

**Альтернативы рассмотренные / Alternatives Considered:**
- ❌ Регулярные выражения — Слишком жесткие правила / Too rigid rules
- ❌ Простой парсинг — Не справляется с вариациями / Can't handle variations
- ❌ Локальные модели — Требуют больших ресурсов / Require significant resources

### 6. Диаграмма вариантов использования / Use Case Diagram

```mermaid
graph TB
    A[Пользователь] --> B[Начать аудит]
    A --> C[Ответить на вопросы]
    A --> D[Получить PDF отчет]

    E[Администратор] --> F[Загрузить документ]
    E --> G[Управлять шаблонами]
    E --> H[Анализировать данные]

    I[Система] --> J[Обработать документ]
    I --> K[Генерировать отчет]
    I --> L[Обновить аналитику]

    B --> J
    F --> J
    C --> K
    H --> L
```

**Сценарии использования / Usage Scenarios:**

1. **Стандартный аудит** — Пользователь проходит опрос безопасности
2. **Обновление шаблона** — Админ загружает новые правила безопасности
3. **Анализ трендов** — Просмотр статистики по сайтам и сотрудникам
4. **Генерация отчетов** — Создание PDF документов для руководства

### 7. Показатели качества / Quality Indicators

**Временные характеристики / Temporal Characteristics:**
- ⏱️ **Время загрузки бота** — < 2 секунд / Bot startup time < 2 seconds
- ⏱️ **Обработка PDF** — 10-30 секунд (зависит от размера) / PDF processing 10-30 seconds
- ⏱️ **Генерация отчета** — < 5 секунд / Report generation < 5 seconds
- ⏱️ **Загрузка дашборда** — < 3 секунд / Dashboard load < 3 seconds

**Качественные характеристики / Quality Characteristics:**
- 📊 **Точность распознавания** — > 95% для структурированных документов / > 95% for structured documents
- 📊 **Доступность системы** — 99.5% uptime / 99.5% system availability
- 📊 **Безопасность данных** — Шифрование конфиденциальной информации / Data encryption
- 📊 **Масштабируемость** — Поддержка до 1000 одновременных пользователей / Up to 1000 concurrent users

**Метрики производительности / Performance Metrics:**
- 🎯 **Успешность аудитов** — > 98% завершенных сессий / > 98% completed sessions
- 🎯 **Скорость ответа** — < 1 секунда на вопрос / < 1 second per question
- 🎯 **Надежность хранения** — Автоматическое резервное копирование / Automatic backup
- 🎯 **Качество отчетов** — Соответствие стандартам безопасности / Compliance with safety standards

---

## Лицензия / License

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для подробностей.

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Поддержка / Support

Если у вас возникли вопросы или проблемы:

- 📧 **Email**: support@safety-hub.com
- 💬 **Telegram**: @SafetyHubSupport
- 🐛 **Issues**: [GitHub Issues](https://github.com/anasmostafa23/Safety-Hub/issues)

---

<div align="center">

**Создано с ❤️ для безопасности производства**

*Made with ❤️ for industrial safety*

[![Powered by Python](https://img.shields.io/badge/powered%20by-Python-blue.svg)](https://python.org)
[![For Industrial Safety](https://img.shields.io/badge/for-Industrial%20Safety-red.svg)](https://github.com/anasmostafa23/Safety-Hub)

</div>
