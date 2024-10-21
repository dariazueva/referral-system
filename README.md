# Реферальная система API

## Описание
Это RESTful API сервис для реферальной системы, позволяющий пользователям регистрироваться, аутентифицироваться и управлять своими реферальными кодами. Пользователи могут создавать, удалять и использовать реферальные коды для регистрации других пользователей.

## Функциональные требования
- Регистрация и аутентификация пользователя ;
- Возможность создания и удаления реферального кода (одновременно может быть активен только один код);
- Получение реферального кода по email-адресу реферера;
- Регистрация по реферальному коду в качестве реферала;
- Получение 	информации о рефералах по id реферера;
- UI документация.

## Технологический стек
- Django + Django REST Framework
- PostgreSQL
- Docker
- Учет асинхронного выполнения операций

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:dariazueva/referral-system.git
```

```
cd referral-system
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/Scripts/activate
    ```

```
python -m pip install --upgrade pip
```

Установите необходимые зависимости:

```
pip install -r requirements.txt

```

Создайте файл .env и заполните его своими данными по образцу:

```
POSTGRES_DB=referral_db
POSTGRES_USER=referral_user
POSTGRES_PASSWORD=referral_pas
DB_HOST=localhost
DB_PORT=5434
```

В консоли пропишите команду для запуска контейнера базы данныхЖ
```
docker run --name referral_db --env-file .env -p 5434:5432 -d postgres:13.10
```

Выполните миграции:

```
python manage.py migrate

```

Запустите сервер:

```
uvicorn referral_system.asgi:application --reload
```

Запустите тесты с помощью команды:
```
python manage.py test
```


## Автор
Зуева Дарья Дмитриевна
Github https://github.com/dariazueva/