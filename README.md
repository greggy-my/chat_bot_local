# Проект "Чат-бот с использованием LLM"

## Описание проекта

Проект представляет собой локальный чат-бот с использованием open-source LLM (Large Language Models). Основной целью бота является предоставление информации по теме программирования с простым пользовательским интерфейсом. Программа обладает векторной базой данных, содержащей информацию из открытых источников, и предоставляет пользователю возможность выбора параметров взаимодействия, таких как наличие памяти у бота и сложность используемой модели.

## Технологии проекта

- **Язык программирования:** Python
- **Скрейпинг:** LangChain
- **Модели:** Ollama (llama2:7b, llama2:13b, codellama:7b, codellama:13b)
- **Embedding:** sbert_large_nlu_ru через библиотеку transformers
- **Векторная база данных:** ChromaDB
- **HTTP запросы:** Локальный хост

## Как работает программа

1. Сбор URL статей с Habr по теме "Программирование" с фильтрами "лучшее" и "легкое".
2. Загрузка HTML страниц статей с использованием библиотеки LangChain (AsyncChromiumLoader и BeautifulSoupTransformer).
3. Разбиение текста статей на документы с сохранением метаданных (URL источника).
4. Векторизация текста каждого документа с использованием sbert_large_nlu_ru и сохранение в векторную базу данных ChromaDB.

Процесс обработки сообщения пользователя включает перевод вопроса в векторный вид, поиск подходящих статей на Habr, и классификацию сообщений на два класса: "Общие сообщения" и "Сообщения про код". После классификации выбирается подходящая модель с учетом предпочтений пользователя. Затем данные отправляются в выбранную модель для генерации ответа, который затем парсится и отображается.

## Запуск приложения

1. Установите необходимые зависимости, используя команду:
   ```
   pip install -r requirements.txt
   ```

2. Создайте базу данных, запустив скрейпер.
3. Скачайте Ollama.
4. Скачайте необходимые LLM модели через
   ```
   ollama pull <model>
   ```
5. Создайте классификационную версию модели через Modefile "hf_models/class_llm",
   модели чатов через Modefile "hf_models/chat_llm",
   а обычные модели через Modefile "hf_models/llm".
   ```
   ollama create <model> <path to Modelfile>
   ```
6. Внесите названия моделей в переменные в файле `main.py`.

Использованные модели:

- llama2:7b
- llama2:13b
- codellama:7b
- codellama:13b

## Проблемы проекта

1. Ответ модели выдается одним сообщением, а не постепенным написанием, что вызывает ожидание у пользователя.
2. База данных не несет достаточной информационной ценности (возможно имеет смысл создать базу на основе теоритической информации из открытых источников).
3. Для повышения эффективности процесса векторизации и поиска необходимо улучшить алгоритм обработки текста и использовать модель векторизации с большим количеством токенов на входе.

---

<div align="center">
  <img src="visual_interface/bot_image.png" alt="Project Logo" width="150">
</div>

---

### Спасибо за внимание!