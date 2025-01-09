# GoalStat API

![GoalStat API Logo](https://example.com/logo.png) <!-- Замените на реальную ссылку на изображение логотипа вашего проекта -->

GoalStat API — это RESTful API, предназначенное для предоставления футбольной статистики. Оно предлагает доступ к информации о матчах, игроках и командах, что позволяет разработчикам интегрировать футбольные данные в свои приложения.

## Технологии

- **FastAPI** — быстрое (высокопроизводительное) веб-приложение для создания API на Python.
- **PostgreSQL** — реляционная база данных для хранения данных.
- **Docker** — для контейнеризации приложения.
- **Docker Compose** — для упрощения настройки контейнеров.
- **Nginx** — для обслуживания запросов и проксирования.
- **GitHub Actions** — инструменты CI/CD для автоматического развертывания.

## Установка

Для запуска вашего экземпляра GoalStat API на локальном компьютере, следуйте инструкциям ниже:

### Предварительные требования

- [Docker](https://www.docker.com/get-started) и [Docker Compose](https://docs.docker.com/compose/install/)
- Python 3.7+ (необязательно, если вы используете Docker)

### Клонировать репозиторий

```bash
git clone https://github.com/Ivaaat/GoalStatsApi.git
cd goalstatapi
```

### Запуск через Docker 
docker-compose up --build

Это развернет API в контейнерах. После этого вы сможете получить доступ к API по адресу http://localhost:8000.

## Использование

### Эндпоинты
Корневой эндоинт 'https://www.goalstatsapi.ru/api/'

#### Получить все сезоны
GET /seasons/

Описание: Возвращает список всех сезонов.

#### Получить информацию о конкретном сезоне
GET /seasons/{season_id}

Описание: Возвращает информацию о сезоне с заданным ID.

### Пример запроса
  ```
  curl -X 'GET' \
    'https://www.goalstatsapi.ru/api/seasons/25' \
    -H 'accept: application/json' \
    -k
  ```
	
Response body
{
  "id": 25,
  "name": "2016/2017"
}

#### Получить всех чемпионатов в сезоне
GET /championships/?season_id={season_id}

Описание: Возвращает список всех чемпионатов.

### Пример запроса
  ```
  curl -X 'GET' \
    'https://www.goalstatsapi.ru/api/championships/?season_id=25' \
    -H 'accept: application/json' \
    -k
  ```

## Документация API

Полную документацию по API можно найти по следующему адресу: [Swagger UI](http://www.goalstatsapi.ru/docs).

## CI/CD

Этот проект использует GitHub Actions для автоматизации развертывания. Каждое изменение в основной ветке автоматически развертывается на сервере.


Спасибо за интерес к GoalStat API! 🚀
