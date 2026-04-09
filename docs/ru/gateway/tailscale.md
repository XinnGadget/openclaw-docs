---
summary: "Интегрированный Tailscale Serve/Funnel для панели управления Gateway"
read_when:
  - Предоставление доступа к интерфейсу управления Gateway за пределами localhost
  - Автоматизация доступа к tailnet или публичной панели управления
title: "Tailscale"
---

# Tailscale (панель управления Gateway)

OpenClaw может автоматически настроить Tailscale **Serve** (tailnet) или **Funnel** (публичный доступ) для панели управления Gateway и порта WebSocket. При этом Gateway остаётся привязанным к loopback, а Tailscale обеспечивает HTTPS, маршрутизацию и (для Serve) заголовки идентификации.

## Режимы

- `serve`: Serve только для tailnet через `tailscale serve`. Gateway остаётся на `127.0.0.1`.
- `funnel`: Публичный HTTPS через `tailscale funnel`. Для OpenClaw требуется общий пароль.
- `off`: Режим по умолчанию (автоматизация Tailscale отключена).

## Аутентификация

Задайте параметр `gateway.auth.mode`, чтобы управлять процессом рукопожатия:

- `none` (только частный ingress);
- `token` (режим по умолчанию, если задан `OPENCLAW_GATEWAY_TOKEN`);
- `password` (общий секрет через `OPENCLAW_GATEWAY_PASSWORD` или конфигурацию);
- `trusted-proxy` (обратный прокси с учётом идентификации; см. [Trusted Proxy Auth](/gateway/trusted-proxy-auth)).

Когда `tailscale.mode = "serve"` и `gateway.auth.allowTailscale` имеет значение `true`, для аутентификации интерфейса управления/WebSocket можно использовать заголовки идентификации Tailscale (`tailscale-user-login`) без указания токена/пароля. OpenClaw проверяет идентификацию, разрешая адрес `x-forwarded-for` через локальный демон Tailscale (`tailscale whois`) и сопоставляя его с заголовком перед принятием.

OpenClaw обрабатывает запрос как Serve только в том случае, если он поступает с loopback с заголовками Tailscale `x-forwarded-for`, `x-forwarded-proto` и `x-forwarded-host`.

Конечные точки HTTP API (например, `/v1/*`, `/tools/invoke` и `/api/channels/*`) **не** используют аутентификацию по заголовкам идентификации Tailscale. Они по-прежнему следуют обычному режиму HTTP-аутентификации Gateway: по умолчанию используется аутентификация по общему секрету либо намеренно настроенная конфигурация `trusted-proxy` / `none` для частного ingress.

Этот поток без токена предполагает, что хост Gateway доверен. Если на том же хосте может выполняться недоверенный локальный код, отключите `gateway.auth.allowTailscale` и требуйте аутентификации по токену/паролю.

Чтобы требовать явных учётных данных по общему секрету, задайте `gateway.auth.allowTailscale: false` и используйте `gateway.auth.mode: "token"` или `"password"`.

## Примеры конфигурации

### Только для tailnet (Serve)

```json5
{
  gateway: {
    bind: "loopback",
    tailscale: { mode: "serve" },
  },
}
```

Открыть: `https://<magicdns>/` (или указанный вами `gateway.controlUi.basePath`)

### Только для tailnet (привязка к IP tailnet)

Используйте этот вариант, если хотите, чтобы Gateway прослушивал напрямую IP tailnet (без Serve/Funnel).

```json5
{
  gateway: {
    bind: "tailnet",
    auth: { mode: "token", token: "your-token" },
  },
}
```

Подключение с другого устройства tailnet:

- Интерфейс управления: `http://<tailscale-ip>:18789/`
- WebSocket: `ws://<tailscale-ip>:18789`

Примечание: loopback (`http://127.0.0.1:18789`) в этом режиме **работать не будет**.

### Публичный интернет (Funnel + общий пароль)

```json5
{
  gateway: {
    bind: "loopback",
    tailscale: { mode: "funnel" },
    auth: { mode: "password", password: "replace-me" },
  },
}
```

Предпочтительнее использовать `OPENCLAW_GATEWAY_PASSWORD`, а не сохранять пароль на диске.

## Примеры использования CLI

```bash
openclaw gateway --tailscale serve
openclaw gateway --tailscale funnel --auth password
```

## Примечания

- Для Tailscale Serve/Funnel необходимо, чтобы CLI `tailscale` был установлен и выполнен вход в систему.
- `tailscale.mode: "funnel"` отказывается запускаться, если режим аутентификации не `password`, чтобы избежать публичного доступа.
- Задайте `gateway.tailscale.resetOnExit`, если хотите, чтобы OpenClaw отменял конфигурацию `tailscale serve` или `tailscale funnel` при завершении работы.
- `gateway.bind: "tailnet"` — прямая привязка к tailnet (без HTTPS, без Serve/Funnel).
- `gateway.bind: "auto"` предпочитает loopback; используйте `tailnet`, если вам нужен только tailnet.
- Serve/Funnel предоставляют доступ только к **интерфейсу управления Gateway + WS**. Узлы подключаются через тот же endpoint Gateway WS, поэтому Serve может работать для доступа к узлам.

## Управление браузером (удалённый Gateway + локальный браузер)

Если вы запускаете Gateway на одном компьютере, но хотите управлять браузером на другом компьютере, запустите **узел-хост** на компьютере с браузером и убедитесь, что оба находятся в одном tailnet. Gateway будет перенаправлять действия браузера на узел; отдельный сервер управления или URL Serve не требуется.

Избегайте использования Funnel для управления браузером; рассматривайте сопоставление узлов как доступ оператора.

## Предварительные требования и ограничения Tailscale

- Для Serve необходимо включить HTTPS для вашего tailnet; CLI выдаст запрос, если это не сделано.
- Serve внедряет заголовки идентификации Tailscale; Funnel — нет.
- Для Funnel требуется Tailscale версии 1.38.3+, MagicDNS, включённый HTTPS и атрибут узла funnel.
- Funnel поддерживает только порты `443`, `8443` и `10000` через TLS.
- Для Funnel на macOS требуется вариант приложения Tailscale с открытым исходным кодом.

## Узнать больше

- Обзор Tailscale Serve: [https://tailscale.com/kb/1312/serve](https://tailscale.com/kb/1312/serve)
- Команда `tailscale serve`: [https://tailscale.com/kb/1242/tailscale-serve](https://tailscale.com/kb/1242/tailscale-serve)
- Обзор Tailscale Funnel: [https://tailscale.com/kb/1223/tailscale-funnel](https://tailscale.com/kb/1223/tailscale-funnel)
- Команда `tailscale funnel`: [https://tailscale.com/kb/1311/tailscale-funnel](https://tailscale.com/kb/1311/tailscale-funnel)