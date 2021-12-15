# Социальная сеть для публикации рецептов

[http://84.201.175.214] [http://geedee.ga]

##Тестовый пользователь
   логин:
   пароль:
## Описание функционала
Этот сервис позволяет добавлять рецепты блюд, подписываться на других атворов рецептов и добавлять рецепты в избранное и в корзину.
В сервисе предусмотрена воможность скачивания корзины покупок с ингрезиентами рецептов с указанием количества ингредиентов, необходимого для приготовления блюд в соответствии с рецептом.

Для удобства реализована функция регистрации пользователей.

## Технологии

- С проектом возможно работать через API. API сервис реализован на Django Rest Framework [https://www.django-rest-framework.org]. Документация API доступна по следующему адресу после запуска проекта /docs/redoc.
- Фронтэнд сайта реализован на основе React[https://reactjs.org].

## Возможнности

- Создавать, удалять, редактировать пользователя (может как администратор так и владелец профиля пользователя);
- Создавать, редактировать и удалять рецепты (удалить рецепт может только автор);
- Добавлять рецепт в избранное;
- Подписываться на других авторов
- Добавлять рецепт в корзину;
- Скачивать наборы ингредиентов для рецепты в формате pdf, в соответствии с составом и объемом ингрединтов, указанном в рецептах



## Установка приложения

- Клонировать и перейти в репозиторий с помощью терминала:

   ```sh
   git clone https://github.com/GenVas/foodgram-project-react
   ```

   ```sh
   cd foodgram-project-react
   ```

- Создать виртуальную среду

   ```sh

   ls
   ```

## Запуск с помощью Docker

   Проект рассчитан на запуск c помощью Docker и Docker-Compose

1. Установите docker и docker-compose

   Инструкция по установке доступна в официальной документации [https://www.docker.com/get-started]

   Образы проекта загружены в Docker Hub [geedeega/foodgram_frontend], [geedeega/foodgram_backend]

2. Сформируйте .env файл со следующими переменными:

   ```sh
   SECRET_KEY=<соответствующий ключ>
   DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
   DB_NAME=postgres # имя базы данных
   POSTGRES_USER=postgres # логин для подключения к базе данных
   POSTGRES_PASSWORD=postgres # пароль для подключения к БД
   DB_HOST=db # название сервиса (контейнера)
   DB_PORT=5432 # порт для подключения к БД
   EMAIL_FILE_PATH='/code/sent_emails/'
   ```

3. Запустите контенеры


    - Перейти в репозитории с помощью терминала в папку infra:

   ```sh
   cd infra
   ``` 
     - Запустить контейнеры:
   
   ```sh
   docker-compose up
   ```

4. Выполните миграции и создайте суперпользователя
   
   ```sh
   docker-compose exec backend python manage.py migrate --noinput
   ```

   ```sh
   docker-compose exec backend python manage.py createsuperuser
   ```

5. Соберите статистику:

   ```sh
   docker-compose exec backend python manage.py collectstatic --noinput
   ```

6. Загрузите в базу фикстуры:

   В корневой папке проекта лежит тестовая база данных. для ее загрузки используйте следующую команду:

   ```sh
   docker-compose exec backend python manage.py loaddata fixtures.json
   ```

   Более подробная информация о загрузке данных: https://docs.djangoproject.com/en/3.2/howto/initial-data/


## Работа с проектом на удаленном сервере

Сразу после клонирования проекта сделайте следующее:

- Установите Docker и Docker-compose. Эта команда скачает скрипт для установки докера:

   Инструкция по установке доступна в официальной документации [https://www.docker.com/get-started]

- скопируйте Docker-compose.yaml файл на сервер, например, c помошью scp
- скорпируйте папку nginx/ с конфигурацией сервера nginx в ту же директорию, где назодится файл Docker-compose

- добавьте в Secrets в разделе Actions репозитария своего проекта в разделе настройки следующие
secrets:

   Доступ к Docker:
      DOCKER_USERNAME
      DOCKER_PASSWORD
   Доступ к вашему серверу:
       HOST - IP server
	   USER - имя пользователя
	   PASSPHRASE пароль, если есть
	   SSH_KEY: ключ для доступа
   Cекретный ключ джанго:
      SECRET_KEY 
   Параметры базы данных Postgres:
      DB_ENGINE
      DB_NAME
      POSTGRES_USER
      POSTGRES_PASSWORD
      DB_HOST
      DB_PORT
   Телеграм:
      TELEGRAM_TO: ID аккаунта для получения сообщений
	  TELEGRAM_TOKEN: токен вашего бота для отправки сообщений

- перед отправкой кода на сервер проверьте, не занят ли порт nginx. Принеобходимости, остановите Nginx

   ```sh
   sudo systemctl stop nginx
   ```

## Тип лицензии

   MIT

## Полезные ссылки
   [Django 2.2.6]: <https://www.djangoproject.com/download/>
   [Python 3.7]: <https://www.python.org/downloads/release/python-390/>
   [Docker 20.10.8]: https://www.docker.com/
   [Nginx 1.19.3]: https://nginx.org/
   [React]https://reactjs.org
   [Django Rest Framework] https://www.django-rest-framework.org
   [GenVas/foodgram-project-react]: https://github.com/GenVas/foodgram-project-react.git 
   [postgres:12.4-alpine] https://hub.docker.com/r/onjin/alpine-postgres/
   [nginx:1.19.3-alpine] https://hub.docker.com/layers/nginx/library/nginx/1.19.3-alpine/images/sha256-4e21f77cde9aaeb846dc799b934a42b66939d19755d98829b705270e916c7479?context=explore 
   [GitHub Actions] https://docs.github.com/en/actions
