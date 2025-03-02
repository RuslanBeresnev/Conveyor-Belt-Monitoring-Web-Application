# Инструкция по запуску приложения

1. Склонировать репозиторий:
   ```git clone https://github.com/RuslanBeresnev/Conveyor-Belt-Monitoring-Web-Application```
2. Создать виртуальное окружение ```.venv``` в проекте
3. Установить все зависимости из ```requirements.txt```:
   ```
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Загрузить СУБД PostgreSQL: https://www.postgresql.org/download/  
При установке можно отметить дополнительный чек-бокс с графической утилитой "pgAdmin 4"
5. Добавить путь до консольной утилиты psql.exe в переменную PATH: ```C:\Program Files\PostgreSQL\17\bin```
6. Создать базу данных из скрипта ```DB_creating_script.txt```:
   - Через консоль с помощью команды psql
   - Либо в графической утилите "pgAdmin 4"
7. Заполнить таблицы "objects", "photo", "defects" тестовыми данными:
   - Вручную
   - Либо с помощью функций из модуля ```tests.test_defect_info_service```:
     ```
     create_db_tables()
     fill_db_with_data()
     ```
8. Скачать архив: https://drive.google.com/file/d/1Z5rEbuojpTs-UW7sXqcW73HDqdfr5s5z/view?usp=sharing
   Ввести пароль доступа для распаковки архива (пароль выдаётся только для проверки производственной практики)
9. Поместить файл ```client_secret.json``` в корневую директорию проекта - это необходимо для дальнейшей аутентификации через Google для отправки писем с тестового аккаунта
10. В корневой директории репозитория создать файл ```.env``` вида:
    ```
    TELEGRAM_BOT_TOKEN = "<token from file>"
    DATABASE_URL = "postgresql://<user>:<password>@localhost:5432/<DB_name>"
    ```
11. Выполнить вход в тестовый аккаунт Google (почта и пароль так же находятся в запороленном архиве)
12. Запустить сервер через терминал (из корня репозитория):
    ```
    fastapi dev application/main.py
    ```
13. Открыть страницу со сгенерированной документацией (формат OpenAPI): http://127.0.0.1:8000/docs
14. Протестировать вызовы различных эндпоинтов:
- ```/notification/with_telegram``` перед первым запросом требует предварительной отправки сообщения Telegram-боту ```@conveyor_belt_notification_bot```, чтобы зарегистрировать чат с пользователем (сообщения бота будут отправляться последнему пользователю, который отправил любое сообщение боту)
- ```/notification/with_gmail``` во время первого запроса при аутентификации необходимо выбрать тестовый аккаунт Google, указанный выше
- Для эндпоинтов из раздела "Defects Information Service" обязательно требуется созданная база данных (например, на локальном хосте)
15. Нажать ```Ctrl + C``` для остановки сервера и завершения работы приложения
16. <Опционально> Запустить линтер в консоли из корня репозитория:
    ```
    pylint ./**/*.py --disable=C0301,C0114,C0115,C0116
    ```
    (отключены предупреждение о превышении длины строки в 100 символов и предупреждение об отсутствии документации у модулей, классов и некоторых функций)
17. <Опционально> Запустить тесты в консоли из корня репозитория:
    ```
    pytest tests
    ```
