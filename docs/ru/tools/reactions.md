 ---
summary: "Семантика инструментов реакций во всех поддерживаемых каналах"
read_when:
  - Работа с реакциями в любом канале
  - Изучение различий в работе реакций с эмодзи на разных платформах
title: "Реакции"
---

# Реакции

Агент может добавлять и удалять реакции с эмодзи к сообщениям, используя инструмент `message` с действием `react`. Поведение реакций зависит от канала.

## Как это работает

```json
{
  "action": "react",
  "messageId": "msg-123",
  "emoji": "thumbsup"
}
```

- Параметр `emoji` обязателен при добавлении реакции.
- Чтобы удалить реакции бота, установите для `emoji` пустую строку (`""`).
- Чтобы удалить определённый эмодзи, установите `remove: true` (при этом `emoji` должен быть непустым).

## Поведение в каналах

<AccordionGroup>
  <Accordion title="Discord и Slack">
    - Пустое значение `emoji` удаляет все реакции бота к сообщению.
    - При `remove: true` удаляется только указанный эмодзи.
  </Accordion>

  <Accordion title="Google Chat">
    - Пустое значение `emoji` удаляет реакции приложения к сообщению.
    - При `remove: true` удаляется только указанный эмодзи.
  </Accordion>

  <Accordion title="Telegram">
    - Пустое значение `emoji` удаляет реакции бота.
    - При `remove: true` реакции также удаляются, но для проверки инструмента по-прежнему требуется непустое значение `emoji`.
  </Accordion>

  <Accordion title="WhatsApp">
    - Пустое значение `emoji` удаляет реакцию бота.
    - При `remove: true` значение `emoji` внутренне сопоставляется с пустой строкой (но в вызове инструмента `emoji` всё равно должен быть указан).
  </Accordion>

  <Accordion title="Zalo Personal (zalouser)">
    - Требуется непустое значение `emoji`.
    - При `remove: true` удаляется реакция с указанным эмодзи.
  </Accordion>

  <Accordion title="Feishu/Lark">
    - Используйте инструмент `feishu_reaction` с действиями `add`, `remove` и `list`.
    - Для добавления/удаления требуется `emoji_type`, для удаления также нужен `reaction_id`.
  </Accordion>

  <Accordion title="Signal">
    - Уведомления о входящих реакциях регулируются параметром `channels.signal.reactionNotifications`: значение `"off"` отключает их, `"own"` (по умолчанию) отправляет события, когда пользователи реагируют на сообщения бота, а `"all"` отправляет события для всех реакций.
  </Accordion>
</AccordionGroup>

## Уровень реакций

Конфигурация `reactionLevel` для каждого канала определяет, насколько активно агент использует реакции. Возможные значения обычно: `off`, `ack`, `minimal` или `extensive`.

- [reactionLevel для Telegram](/channels/telegram#reaction-notifications) — `channels.telegram.reactionLevel`
- [reactionLevel для WhatsApp](/channels/whatsapp#reactions) — `channels.whatsapp.reactionLevel`

Настройте `reactionLevel` для отдельных каналов, чтобы отрегулировать активность реакций агента на сообщениях в каждой платформе.

## Связанные материалы

- [Agent Send](/tools/agent-send) — инструмент `message`, включающий `react`
- [Channels](/channels) — конфигурация для конкретных каналов