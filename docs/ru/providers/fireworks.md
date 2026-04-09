---
summary: "Настройка Fireworks (аутентификация + выбор модели)"
read_when:
  - Вы хотите использовать Fireworks с OpenClaw
  - Вам нужна переменная окружения с API-ключом Fireworks или идентификатор модели по умолчанию
---

# Fireworks

[Fireworks](https://fireworks.ai) предоставляет модели с открытыми весами (open-weight) и маршрутизируемые модели (routed models) через API, совместимый с OpenAI. В OpenClaw теперь включён встроенный плагин провайдера Fireworks.

- Провайдер: `fireworks`
- Аутентификация: `FIREWORKS_API_KEY`
- API: совместимый с OpenAI чат/дополнения (chat/completions)
- Базовый URL: `https://api.fireworks.ai/inference/v1`
- Модель по умолчанию: `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo`

## Быстрый старт

Настройте аутентификацию Fireworks через процесс онбординга:

```bash
openclaw onboard --auth-choice fireworks-api-key
```

Это сохранит ваш ключ Fireworks в конфигурации OpenClaw и установит модель Fire Pass Starter в качестве модели по умолчанию.

## Пример неинтерактивной настройки

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice fireworks-api-key \
  --fireworks-api-key "$FIREWORKS_API_KEY" \
  --skip-health \
  --accept-risk
```

## Примечание об окружении

Если шлюз (Gateway) запускается вне вашей интерактивной оболочки, убедитесь, что переменная `FIREWORKS_API_KEY` доступна и для этого процесса. Ключ, хранящийся только в `~/.profile`, не будет доступен демону launchd/systemd, если это окружение не импортировано туда соответствующим образом.

## Встроенный каталог

| Ссылка на модель | Название | Входные данные | Контекст | Максимальный объём вывода | Примечания |
| --- | --- | --- | --- | --- | --- |
| `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo` | Kimi K2.5 Turbo (Fire Pass) | текст, изображение | 256 000 | 256 000 | Модель по умолчанию, включённая в комплект Fireworks |

## Пользовательские идентификаторы моделей Fireworks

OpenClaw также поддерживает динамические идентификаторы моделей Fireworks. Используйте точный идентификатор модели или маршрутизатора, указанный в Fireworks, и добавьте к нему префикс `fireworks/`.

Пример:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "fireworks/accounts/fireworks/routers/kimi-k2p5-turbo",
      },
    },
  },
}
```

Если Fireworks опубликует более новую модель, например, свежую версию Qwen или Gemma, вы сможете переключиться на неё напрямую, используя идентификатор модели Fireworks, не дожидаясь обновления встроенного каталога.