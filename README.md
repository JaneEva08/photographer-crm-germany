# VPh03 — CRM фотографа

Учебное продолжение проекта `photographer-site`: локальная мини-CRM для демо-фотографа в Германии. API хранит клиентов, съёмки (сделки) и задачи; настольный клиент показывает записи и выгружает три отдельных отчёта в Google Drive как Google Sheets.

Все данные тестовые: имена вымышлены, email используют зарезервированный домен `.test`. В репозитории нет реальных данных клиентов, OAuth-файла или токена.

## Состав

- `backend/` — FastAPI CRUD API, SQLAlchemy модели и повторяемый генератор до 10 000 синтетических клиентов, съёмок и задач.
- `ui/app.py` — Tkinter-клиент: просмотр, добавление и удаление записей, экспорт отчётов.
- `google_integration/` — OAuth пользователя и создание таблиц через Drive API и Sheets API.
- `docker-compose.yml` — PostgreSQL и API; профиль `demo-data` запускает начальное наполнение.
- `tests/` — изолированные проверки API на SQLite в памяти.

## Локальный запуск

Нужны Docker Desktop (Compose) и Python 3.12. В терминале из этой папки:

```powershell
Copy-Item .env.example .env
docker compose up --build -d db api
docker compose --profile demo-data run --rm seed
```

API и Swagger: <http://localhost:8000/docs>. Для настольного окна на компьютере с Python:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m ui.app
```

Окно может добавлять клиентов, съёмки и задачи минимальными формами, удалять выбранную строку и обновлять список. Остальные поля можно заполнить через Swagger/API.

## Google OAuth — настройка при первом экспорте

Нужен OAuth Client ID типа **Desktop app** в Google Cloud; созданный ранее сервисный аккаунт для этого задания не заменяет пользовательский OAuth. В проекте Cloud включи Google Drive API и Google Sheets API. Для OAuth выбери External + Testing и добавь аккаунт, которым будешь входить, в Test users. В разделе Data Access добавь только scope `https://www.googleapis.com/auth/drive.file`: приложение создаёт собственные таблицы и не просит полный доступ ко всем твоим таблицам. Скачанный JSON положи как `config/oauth_client.json` рядом с этим README. Не отправляй файл в чат или Git.

Кнопка экспорта откроет пользовательскую авторизацию в браузере и локально сохранит `config/token.json`; оба файла игнорируются Git. По желанию укажи ID существующей папки Drive в `GOOGLE_DRIVE_FOLDER_ID` файла `.env`. Иначе таблицы создадутся в корне Drive. После экспорта окно покажет отдельные ссылки на три таблицы.

## Проверки и известные ограничения

Проверки 2026-11-03: 2 API-теста и SQLite smoke-прогон прошли; Docker Compose поднял PostgreSQL и API, healthcheck БД прошёл, API вернул по 1000 записей клиентов, съёмок и задач, Swagger ответил HTTP 200. Google OAuth Desktop Client прошёл с `drive.file`; экспорт создал три таблицы Google Sheets, ссылки и подробный статус приведены в [`HOMEWORK.md`](HOMEWORK.md). OAuth JSON и токен остаются локальными и исключены из Git.

Снимки Tkinter CRM, Swagger и всех трёх Google Sheets вложены в `HOMEWORK.md`; окно CRM показывает 1000 клиентов и подключение к API.
