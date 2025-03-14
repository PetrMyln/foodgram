# Foodgram

### Описание:

```
Учебный проект Foodgram посвящён работе с DjangoRESTAPi.
Проект Foodgram представляет площадку по обмену кулинарными рецептами.
```

### Ссылка на работающий сайт

```
https://food-gramtryam.zapto.org
```
### Автор
```
    ФИО: Мыльников Пётр Алексеевич

    GitHub: github.com/PetrMyln
```

### Техно-стек
```
    Язык программирования: Python

    Фреймворк: Django, Django REST Framework (DRF)

    База данных: PostgreSQL

    Фронтенд: HTML, CSS, JavaScript 

    Дополнительные технологии: Docker, Nginx

    CI/CD: GitHub Actions/GitLab CI
```

### Развертывание с Docker
```
1. Клонирование репозитория
git clone git@github.com:PetrMyln/foodgram.git

2. Переход в папку с docker-compose.yml
cd foodgram

3. Настройка .env
Создайте файл .env в корне проекта и заполните его по примеру:

cp example.env .env

Пример содержимого example.env:
SECRET_KEY=ваш-secret-key
DEBUG=True
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

4. Подъем контейнеров
docker-compose up -d --build

5. Подготовка базы данных
Выполните миграции и создайте суперпользователя:

docker-compose exec "Название контейнера" python manage.py migrate
docker-compose exec "Название контейнера" python manage.py createsuperuser

6. Импорт фикстур (если нужно)
для пустой базы, но только со всеми ингредиентами
docker-compose exec "Название контейнера" python manage.py adding

для тестов
docker-compose exec "Название контейнера" python manage.py addiddqd


7. Сборка статики
docker-compose exec "Название контейнера" python manage.py collectstatic

8. Запуск сервера
Сервер уже запущен после выполнения docker-compose up. Доступ к сайту:
    Веб-сайт: http://localhost:8000
    API: http://localhost:8000/api/

```

#  ПЕРЕД ПОСЛЕДНЕЙ ПРАВКОЙ УДАЛЮ и заменю супераюзера

```

в 6 рецепте https://food-gramtryam.zapto.org/recipes/6
описание .env

НА сайте предварительно 10 юзеров, 60 рецептов


добавить все ингредиенты и теги используйте для прохождения всех postman запросов
python manage.py adding

добавить тестовых юзеров, рецепты, теги
python manage.py addiddqd

для админки
login 1@1.ru 
password - 1
```
