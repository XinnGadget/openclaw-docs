---
summary: "Руководство по работе со службой Gateway, её жизненному циклу и операциям"
read_when:
  - При запуске или отладке процесса Gateway
title: "Руководство по работе с Gateway"
---

# Руководство по работе с Gateway

Используйте эту страницу для первичного запуска и последующей эксплуатации службы Gateway.

<CardGroup cols={2}>
  <Card title="Углублённая диагностика" icon="siren" href="/gateway/troubleshooting">
    Диагностика по симптомам с точными последовательностями команд и сигнатурами логов.
  </Card>
  <Card title="Конфигурация" icon="sliders" href="/gateway/configuration">
    Руководство по настройке, ориентированное на задачи, + полный справочник по конфигурации.
  </Card>
  <Card title="Управление секретами" icon="key-round" href="/gateway/secrets">
    Контракт SecretRef, поведение при создании снимка во время выполнения, операции миграции и перезагрузки.
  </Card>
  <Card title="Контракт плана секретов" icon="shield-check" href="/gateway/secrets-plan-contract">
    Точные правила для `secrets apply` (целевой путь/путь) и поведение профиля аутентификации только с ссылками.
  </Card>
</CardGroup>

## Локальный запуск за 5 минут

<Steps>
  <Step title="Запустить Gateway">

```bash
openclaw gateway --port 18789
# отладка/трассировка, зеркалируемая в stdio
openclaw gateway --port 18789 --verbose
# принудительно завершить слушатель на выбранном порту, затем запустить
openclaw gateway --force
```

  </Step>

  <Step title="Проверить работоспособность службы">

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
```

Базовый показатель работоспособности: `Runtime: running` и `RPC probe: ok`.

  </Step>

  <Step title="Проверить готовность канала">

```bash
openclaw channels status --probe
```

При доступном Gateway выполняется проверка каналов для каждой учётной записи в реальном времени и, при необходимости, аудит.
Если Gateway недоступен, CLI вместо вывода результатов проверки в реальном времени возвращает сводку каналов только на основе конфигурации.

  </Step>
</Steps

<Note>
Перезагрузка конфигурации Gateway отслеживает активный путь к файлу конфигурации (определяется на основе значений по умолчанию для профиля/состояния или переменной `OPENCLAW_CONFIG_PATH`, если она задана).
Режим по умолчанию — `gateway.reload.mode="hybrid"`.
После первой успешной загрузки работающий процесс использует активный снимок конфигурации в памяти; при успешной перезагрузке этот снимок атомарно заменяется.
</Note>

## Модель выполнения

- Один постоянно работающий процесс для маршрутизации, плоскости управления и соединений каналов.
- Один мультиплексированный порт для:
  - WebSocket-управления/RPC;
  - HTTP API, совместимых с OpenAI (`/v1/models`, `/v1/embeddings`, `/v1/chat/completions`, `/v1/responses`, `/tools/invoke`);
  - Управляющего интерфейса и хуков.
- Режим привязки по умолчанию: `loopback`.
- Аутентификация требуется по умолчанию. В настройках с общим секретом используются `gateway.auth.token` / `gateway.auth.password` (или `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`), а в настройках обратного прокси без loopback можно использовать `gateway.auth.mode: "trusted-proxy"`.

## Конечные точки, совместимые с OpenAI

Наиболее важные точки совместимости OpenClaw сейчас:

- `GET /v1/models`
- `GET /v1/models/{id}`
- `POST /v1/embeddings`
- `POST /v1/chat/completions`
- `POST /v1/responses`

Почему этот набор важен:

- Большинство интеграций Open WebUI, LobeChat и LibreChat сначала проверяют `/v1/models`.
- Многие конвейеры RAG и памяти ожидают `/v1/embeddings`.
- Клиенты, работающие с агентами, всё чаще предпочитают `/v1/responses`.

Примечание по планированию:

- `/v1/models` ориентирован на агентов: он возвращает `openclaw`, `openclaw/default` и `openclaw/<agentId>`.
- `openclaw/default` — это стабильный псевдоним, который всегда сопоставляется с настроенным агентом по умолчанию.
- Используйте `x-openclaw-model`, если хотите переопределить поставщика/модель бэкенда; в противном случае будет использоваться обычная модель и настройки встраивания, заданные для выбранного агента.

Все эти точки работают на основном порту Gateway и используют ту же границу аутентификации доверенного оператора, что и остальная часть HTTP API Gateway.

### Приоритет порта и привязки

| Настройка | Порядок определения |
| ------------ | ------------------------------------------------------------- |
| Порт Gateway | `--port` → `OPENCLAW_GATEWAY_PORT` → `gateway.port` → `18789` |
| Режим привязки | CLI/переопределение → `gateway.bind` → `loopback` |

### Режимы горячей перезагрузки

| `gateway.reload.mode` | Поведение |
| --------------------- | ------------------------------------------ |
| `off` | Перезагрузка конфигурации не выполняется |
| `hot` | Применяются только безопасные для горячей перезагрузки изменения |
| `restart` | Перезапуск при изменениях, требующих перезагрузки |
| `hybrid` (по умолчанию) | Горячая перезагрузка, когда это безопасно, перезапуск — когда необходимо |

## Набор команд для оператора

```bash
openclaw gateway status
openclaw gateway status --deep   # добавляет сканирование служб на системном уровне
openclaw gateway status --json
openclaw gateway install
openclaw gateway restart
openclaw gateway stop
openclaw secrets reload
openclaw logs --follow
openclaw doctor
```

`gateway status --deep` предназначен для дополнительного обнаружения служб (LaunchDaemons/systemd системные юниты/schtasks), а не для более глубокой проверки работоспособности RPC.

## Несколько шлюзов на одном хосте

В большинстве случаев на одной машине должен работать один шлюз. Один шлюз может поддерживать несколько агентов и каналов.

Несколько шлюзов нужны только в том случае, если вы намеренно хотите обеспечить изоляцию или использовать спасательного бота.

Полезные проверки:

```bash
openclaw gateway status --deep
openclaw gateway probe
```

Чего ожидать:

- `gateway status --deep` может сообщить о `Other gateway-like services detected (best effort)` и вывести подсказки по очистке, если остались устаревшие установки launchd/systemd/schtasks.
- `gateway probe` может выдать предупреждение о `multiple reachable gateways`, если отвечает более одного целевого шлюза.
- Если это сделано намеренно, изолируйте порты, конфигурацию/состояние и корневые каталоги рабочих пространств для каждого шлюза.

Подробная настройка: [/gateway/multiple-gateways](/gateway/multiple-gateways).

## Удаленный доступ

Предпочтительный способ: Tailscale/VPN.
Альтернативный способ: SSH-туннель.

```bash
ssh -N -L 18789:127.0.0.1:18789 user@host
```

Затем подключите клиенты локально к `ws://127.0.0.1:18789`.

<Warning>
SSH-туннели не обходят аутентификацию шлюза. Для аутентификации с общим секретом клиенты по-прежнему должны отправлять `token`/`password` даже через туннель. Для режимов с идентификацией запрос должен соответствовать этому пути аутентификации.
</Warning>

См.: [Удаленный Gateway](/gateway/remote), [Аутентификация](/gateway/authentication), [Tailscale](/gateway/tailscale).

## Контроль и жизненный цикл службы

Для обеспечения надёжности, близкой к производственной, используйте контролируемые запуски.

<Tabs>
  <Tab title="macOS (launchd)">

```bash
openclaw gateway install
openclaw gateway status
openclaw gateway restart
openclaw gateway stop
```

Метки LaunchAgent: `ai.openclaw.gateway` (по умолчанию) или `ai.openclaw.<profile>` (именованный профиль). `openclaw doctor` проверяет и исправляет отклонения конфигурации службы.

  </Tab>

  <Tab title="Linux (пользовательский systemd)">

```bash
openclaw gateway install
systemctl --user enable --now openclaw-gateway[-<profile>].service
openclaw gateway status
```

Для сохранения работы после выхода из системы включите lingering:

```bash
sudo loginctl enable-linger <user>
```

Пример ручного пользовательского юнита, если вам нужен пользовательский путь установки:

```ini
[Unit]
Description=OpenClaw Gateway
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/openclaw gateway --port 18789
Restart=always
RestartSec=5
TimeoutStopSec=30
TimeoutStartSec