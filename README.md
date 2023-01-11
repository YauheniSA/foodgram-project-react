![workflow badge](https://github.com/YauheniSA/foodgram-project-react/.github/workflows/main.yml/badge.svg)

![Jokes Card](https://readme-jokes.vercel.app/api)

# FOODGRAM
### Описание
Проект представляет собой сайт на основе API для публикаций рецептов

Проект доступен по ссылке: http://158.160.36.188/
### Технологии
Python 3.7
Django 2.2.16
DRF 3.12.4
DOCKER-COMPOSE 3.8

### Авторы
Евгений Семашкевич. SemashkevichEA@yandex.ru

### Как запустить backend проекта локально:
Ссылка на скачивание проекта:
```
git@github.com:YauheniSA/foodgram-project-react.git
```

```BASH
python -m venv venv
```

Cоздать и активировать виртуальное окружение:

```BASH
python -m venv venv
```

```BASH
source venv/scripts/activate
```

Установить зависимости из файла requirements.txt:

```BASH
python -m pip install --upgrade pip
```

```BASH
pip install -r requirements.txt
```

Выполнить миграции:

```BASH
python3 manage.py migrate
```
Если надо выполнить импорт из существующих csv-файлов:

```BASH
python manage.py load_ingredients
```

Запустить проект:

```BASH
python3 manage.py runserver
```

После этого api для тестирования будет доступно по ссылке

```
http://localhost/api/
```

Проверка работоспособности и функционала по ссылке:

```
http://localhost/admin/ 
```

# Работа с API:

Документация для работы с api доступна локально по ссылке:
`POST http://localhost/api/docs/`

### Запуск сервиса на сервере
Ссылка на скачивание проекта:
```
git@github.com:YauheniSA/foodgram-project-react.git
```

Скопируйте на сервер файлы docker-compose.yml и nginx.conf из папки infra/:
```
scp docker-compose.yml nginx.conf username@IP:/home/username/
```

Установите docker и docker-compose на сервер:
```
sudo apt install curl                                   
sudo apt install docker.io                                            
sudo apt install docker-compose   
```

В корневой папке проекта необходимо создать .env файл со следующми переменными:
```
SECRET_KEY -  Ключ Django проекта settings.py
DOCKER_USERNAME -  Имя пользователя DockerHub
DOCKER_PASSWORD - Пароль DockerHub
HTELEGRAM_TO - ID получателя телеграм сообщения
TELEGRAM_TOKEN - токен бота для рассылки
DB_ENGINE - django.db.backends.postgresql
DB_NAME - postgres
POSTGRES_USER - postgres
POSTGRES_PASSWORD - postgres
DB_HOST  - db
DB_PORT - 5432
```

Сборка образа и запуск контейнеров:
```
sudo docker-compose up -d --build
```

Выполнение миграций:
```
sudo docker compose exec backend python manage.py migrate
```

Создание суперпользователя:
```
sudo docker compose exec backend python manage.py createsuperuser
```

Наполнение базы игредиентами:
```
sudo docker compose exec backend python manage.py load_ingredients
```


Остановка контейнеров:
```
sudo docker-compose stop
```

Остановка и удаление контейнеров со всеми зависимостями:
```
sudo docker-compose down -v
```