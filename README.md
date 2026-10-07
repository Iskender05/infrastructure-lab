## Запуск

```bash
docker compose up --build
```

База и таблица создаются автоматически. Настройки уже заданы для локального запуска. При необходимости их можно изменить через `.env`, пример есть в `.env.example`.

После запуска открыть [http://localhost:8000/docs](http://localhost:8000/docs) — там можно попробовать все запросы.

## Проверка API

Примеры для Bash или Git Bash, выполнять во втором терминале:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/tasks
```

Добавить задачу:

```bash
curl -X POST http://localhost:8000/tasks -H 'Content-Type: application/json' -d '{"title":"Learn Docker","description":"Homework","completed":false}'
```

## Остановка

```bash
docker compose down
```

Остановить и удалить данные базы:

```bash
docker compose down -v
```
