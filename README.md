# API для сервиса YaMDb

API для сервиса YaMDb — базы отзывов о фильмах, книгах и музыке.

## Установка

Перед использованием программы необходимо установить Docker и Docker-compose

Инструкция по установке Docker - https://docs.docker.com/engine/install/

Инструкция по установке Docker-compose - https://docs.docker.com/compose/install/

## Использование

### Запуск приложения

Из директории проекта, выполните команду `docker-compose up` для запуска приложения

### Создание суперпользователя

```
docker-compose run web python manage.py createsuperuser
```

### Заполнения базы начальными данными

```
docker-compose run web python manage.py loaddata fixtures.json
```

## Технологии

- [Django](https://www.djangoproject.com/)
- [Postgresql](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)
