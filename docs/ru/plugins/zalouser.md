---
summary: "Плагин Zalo Personal: вход по QR-коду + обмен сообщениями через нативный zca-js (установка плагина + настройка канала + инструмент)"
read_when:
  - Вам нужна поддержка Zalo Personal (неофициальная) в OpenClaw
  - Вы настраиваете или разрабатываете плагин zalouser
title: "Плагин Zalo Personal"
---

# Zalo Personal (плагин)

Поддержка Zalo Personal в OpenClaw посредством плагина, использующего нативный `zca-js` для автоматизации работы обычной учётной записи пользователя Zalo.

> **Предупреждение:** неофициальная автоматизация может привести к приостановке действия учётной записи или её блокировке. Используйте на свой страх и риск.

## Наименование

Идентификатор канала — `zalouser`, чтобы чётко указать, что осуществляется автоматизация **личной учётной записи пользователя Zalo** (неофициально). Мы оставляем `zalo` для потенциальной будущей интеграции с официальным API Zalo.

## Где выполняется

Этот плагин выполняется **внутри процесса Gateway**.

Если вы используете удалённый Gateway, установите/настройте его на **машине, на которой запущен Gateway**, затем перезапустите Gateway.

Внешнее CLI-приложение `zca`/`openzca` не требуется.

## Установка

### Вариант А: установка из npm

```bash
openclaw plugins install @openclaw/zalouser
```

После этого перезапустите Gateway.

### Вариант Б: установка из локальной папки (разработка)

```bash
PLUGIN_SRC=./path/to/local/zalouser-plugin
openclaw plugins install "$PLUGIN_SRC"
cd "$PLUGIN_SRC" && pnpm install
```

После этого перезапустите Gateway.

## Настройка

Конфигурация канала располагается в разделе `channels.zalouser` (не в `plugins.entries.*`):

```json5
{
  channels: {
    zalouser: {
      enabled: true,
      dmPolicy: "pairing",
    },
  },
}
```

## CLI

```bash
openclaw channels login --channel zalouser
openclaw channels logout --channel zalouser
openclaw channels status --probe
openclaw message send --channel zalouser --target <threadId> --message "Hello from OpenClaw"
openclaw directory peers list --channel zalouser --query "name"
```

## Инструмент для агента

Название инструмента: `zalouser`

Действия: `send`, `image`, `link`, `friends`, `groups`, `me`, `status`

Действия с сообщениями в канале также поддерживают `react` для реакций на сообщения.