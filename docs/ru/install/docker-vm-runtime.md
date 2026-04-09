---
summary: "Общие шаги настройки среды выполнения Docker VM для долго работающих хостов OpenClaw Gateway"
read_when:
  - Вы развёртываете OpenClaw на облачной VM с Docker
  - Вам нужен общий процесс подготовки бинарных файлов, сохранения данных и обновления
title: "Среда выполнения Docker VM"
---

# Среда выполнения Docker VM

Общие шаги настройки для установок Docker на виртуальных машинах (VM), таких как GCP, Hetzner и аналогичные провайдеры VPS.

## Подготовка необходимых бинарных файлов в образе

Установка бинарных файлов внутри работающего контейнера — ловушка.
Всё, что установлено во время выполнения, будет потеряно при перезапуске.

Все внешние бинарные файлы, необходимые для навыков (skills), должны быть установлены на этапе сборки образа.

Ниже приведены примеры лишь трёх распространённых бинарных файлов:

- `gog` — для доступа к Gmail;
- `goplaces` — для работы с Google Places;
- `wacli` — для работы с WhatsApp.

Это примеры, а не полный список. Вы можете установить столько бинарных файлов, сколько необходимо, используя тот же шаблон.

Если позже вы добавите новые навыки, зависящие от дополнительных бинарных файлов, вам необходимо:

1. Обновить Dockerfile.
2. Пересобрать образ.
3. Перезапустить контейнеры.

**Пример Dockerfile**

```dockerfile
FROM node:24-bookworm

RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

# Пример бинарного файла 1: Gmail CLI
RUN curl -L https://github.com/steipete/gog/releases/latest/download/gog_Linux_x86_64.tar.gz \
  | tar -xz -C /usr/local/bin && chmod +x /usr/local/bin/gog

# Пример бинарного файла 2: Google Places CLI
RUN curl -L https://github.com/steipete/goplaces/releases/latest/download/goplaces_Linux_x86_64.tar.gz \
  | tar -xz -C /usr/local/bin && chmod +x /usr/local/bin/goplaces

# Пример бинарного файла 3: WhatsApp CLI
RUN curl -L https://github.com/steipete/wacli/releases/latest/download/wacli_Linux_x86_64.tar.gz \
  | tar -xz -C /usr/local/bin && chmod +x /usr/local/bin/wacli

# Добавьте дополнительные бинарные файлы ниже, используя тот же шаблон

WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY ui/package.json ./ui/package.json
COPY scripts ./scripts

RUN corepack enable
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build
RUN pnpm ui:install
RUN pnpm ui:build

ENV NODE_ENV=production

CMD ["node","dist/index.js"]
```

<Note>
URL-адреса для загрузки выше предназначены для x86_64 (amd64). Для VM на базе ARM (например, Hetzner ARM, GCP Tau T2A) замените URL-адреса для загрузки на соответствующие варианты для ARM64 на странице выпусков каждого инструмента.
</Note>

## Сборка и запуск

```bash
docker compose build
docker compose up -d openclaw-gateway
```

Если сборка завершается с ошибкой `Killed` или `exit code 137` во время выполнения команды `pnpm install --frozen-lockfile`, значит, на VM не хватает памяти.
Перед повторной попыткой используйте VM с более высоким классом ресурсов.

Проверка бинарных файлов:

```bash
docker compose exec openclaw-gateway which gog
docker compose exec openclaw-gateway which goplaces
docker compose exec openclaw-gateway which wacli
```

Ожидаемый результат:

```
/usr/local/bin/gog
/usr/local/bin/goplaces
/usr/local/bin/wacli
```

Проверка Gateway:

```bash
docker compose logs -f openclaw-gateway
```

Ожидаемый результат:

```
[gateway] listening on ws://0.0.0.0:18789
```

## Что и где сохраняется

OpenClaw работает в Docker, но Docker не является источником достоверных данных.
Всё долговременное состояние должно сохраняться при перезапусках, перестройках и перезагрузках.

| Компонент | Расположение | Механизм сохранения | Примечания |
| --- | --- | --- | --- |
| Конфигурация Gateway | `/home/node/.openclaw/` | Монтирование тома хоста | Включает `openclaw.json`, `.env` |
| Профили аутентификации моделей | `/home/node/.openclaw/agents/` | Монтирование тома хоста | `agents/<agentId>/agent/auth-profiles.json` (OAuth, API-ключи) |
| Конфигурации навыков | `/home/node/.openclaw/skills/` | Монтирование тома хоста | Состояние на уровне навыков |
| Рабочее пространство агента | `/home/node/.openclaw/workspace/` | Монтирование тома хоста | Код и артефакты агента |
| Сессия WhatsApp | `/home/node/.openclaw/` | Монтирование тома хоста | Сохраняет вход через QR-код |
| Связка ключей Gmail | `/home/node/.openclaw/` | Монтирование тома + пароль | Требуется `GOG_KEYRING_PASSWORD` |
| Внешние бинарные файлы | `/usr/local/bin/` | Образ Docker | Должны быть подготовлены на этапе сборки |
| Среда выполнения Node | Файловая система контейнера | Образ Docker | Пересобирается при каждой сборке образа |
| Пакеты ОС | Файловая система контейнера | Образ Docker | Не устанавливайте во время выполнения |
| Контейнер Docker | Временный | Возможность перезапуска | Можно безопасно удалять |

## Обновление

Чтобы обновить OpenClaw на VM:

```bash
git pull
docker compose build
docker compose up -d
```