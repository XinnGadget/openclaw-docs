---
summary: "Обзор бота Feishu, его функции и настройка"
read_when:
  - Вы хотите подключить бота Feishu/Lark
  - Вы настраиваете канал Feishu
title: Feishu
---

# Бот Feishu

Feishu (Lark) — платформа для командного общения, которую компании используют для обмена сообщениями и совместной работы. Этот плагин подключает OpenClaw к боту Feishu/Lark с помощью подписки на события через WebSocket платформы — так сообщения можно получать без публикации публичного URL вебхука.

---

## Встроенный плагин

Плагин Feishu входит в текущие версии OpenClaw, поэтому отдельная установка плагина не требуется.

Если вы используете более старую сборку или пользовательскую установку, в которую не включён встроенный плагин Feishu, установите его вручную:

```bash
openclaw plugins install @openclaw/feishu
```

---

## Быстрый старт

Есть два способа добавить канал Feishu:

### Способ 1: настройка при первом запуске (рекомендуется)

Если вы только что установили OpenClaw, запустите настройку при первом запуске:

```bash
openclaw onboard
```

Мастер проведёт вас через следующие шаги:

1. Создание приложения Feishu и получение учётных данных.
2. Настройка учётных данных приложения в OpenClaw.
3. Запуск шлюза.

✅ **После настройки** проверьте статус шлюза:

- `openclaw gateway status`
- `openclaw logs --follow`

### Способ 2: настройка через CLI

Если вы уже выполнили первоначальную установку, добавьте канал через CLI:

```bash
openclaw channels add
```

Выберите **Feishu**, затем введите App ID и App Secret.

✅ **После настройки** управляйте шлюзом:

- `openclaw gateway status`
- `openclaw gateway restart`
- `openclaw logs --follow`

---

## Шаг 1: создание приложения Feishu

### 1. Откройте платформу Feishu Open Platform

Перейдите на [Feishu Open Platform](https://open.feishu.cn/app) и войдите в систему.

Для арендаторов Lark (глобальная версия) используйте [https://open.larksuite.com/app](https://open.larksuite.com/app) и установите `domain: "lark"` в конфигурации Feishu.

### 2. Создайте приложение

1. Нажмите **Create enterprise app** ("Создать корпоративное приложение").
2. Заполните название и описание приложения.
3. Выберите иконку приложения.

![Создание корпоративного приложения](/images/feishu-step2-create-app.png)

### 3. Скопируйте учётные данные

В разделе **Credentials & Basic Info** ("Учётные данные и основная информация") скопируйте:

- **App ID** (формат: `cli_xxx`);
- **App Secret**.

❗ **Важно:** сохраняйте App Secret в секрете.

![Получение учётных данных](/images/feishu-step3-credentials.png)

### 4. Настройте разрешения

В разделе **Permissions** ("Разрешения") нажмите **Batch import** ("Пакетный импорт") и вставьте:

```json
{
  "scopes": {
    "tenant": [
      "aily:file:read",
      "aily:file:write",
      "application:application.app_message_stats.overview:readonly",
      "application:application:self_manage",
      "application:bot.menu:write",
      "cardkit:card:read",
      "cardkit:card:write",
      "contact:user.employee_id:readonly",
      "corehr:file:download",
      "event:ip_list",
      "im:chat.access_event.bot_p2p_chat:read",
      "im:chat.members:bot_access",
      "im:message",
      "im:message.group_at_msg:readonly",
      "im:message.p2p_msg:readonly",
      "im:message:readonly",
      "im:message:send_as_bot",
      "im:resource"
    ],
    "user": ["aily:file:read", "aily:file:write", "im:chat.access_event.bot_p2p_chat:read"]
  }
}
```

![Настройка разрешений](/images/feishu-step4-permissions.png)

### 5. Включите возможности бота

В разделе **App Capability** ("Возможности приложения") → **Bot** ("Бот"):

1. Включите возможности бота.
2. Задайте имя бота.

![Включение возможностей бота](/images/feishu-step5-bot-capability.png)

### 6. Настройте подписку на события

⚠️ **Важно:** перед настройкой подписки на события убедитесь, что:

1. Вы уже выполнили команду `openclaw channels add` для Feishu.
2. Шлюз запущен (`openclaw gateway status`).

В разделе **Event Subscription** ("Подписка на события"):

1. Выберите **Use long connection to receive events** ("Использовать длительное подключение для получения событий") (WebSocket).
2. Добавьте событие: `im.message.receive_v1`.
3. (Опционально) Для рабочих процессов с комментариями в Drive также добавьте: `drive.notice.comment_add_v1`.

⚠️ Если шлюз не запущен, настройка длительного подключения может не сохраниться.

![Настройка подписки на события](/images/feishu-step6-event-subscription.png)

### 7. Опубликуйте приложение

1. Создайте версию в разделе **Version Management & Release** ("Управление версиями и выпуск").
2. Отправьте на проверку и опубликуйте.
3. Дождитесь одобрения администратора (для корпоративных приложений обычно действует автоматическое одобрение).

---

## Шаг 2: настройка OpenClaw

### Настройка с помощью мастера (рекомендуется)

```bash
openclaw channels add
```

Выберите **Feishu** и вставьте App ID и App Secret.

### Настройка через конфигурационный файл

Отредактируйте файл `~/.openclaw/openclaw.json`:

```json5
{
  channels: {
    feishu: {
      enabled: true,
      dmPolicy: "pairing",
      accounts: {
        main: {
          appId: "cli_xxx",
          appSecret: "xxx",
          name: "Мой ИИ-ассистент",
        },
      },
    },
  },
}
```

Если вы используете `connectionMode: "webhook"`, задайте значения `verificationToken` и `encryptKey`. Сервер вебхуков Feishu по умолчанию привязывается к `127.0.0.1`; задайте `webhookHost` только в том случае, если вам намеренно нужен другой адрес привязки.

#### Verification Token и Encrypt Key (режим вебхука)

При использовании режима вебхука задайте значения `channels.feishu.verificationToken` и `channels.feishu.encryptKey` в конфигурации. Чтобы получить эти значения:

1. В Feishu Open Platform откройте своё приложение.
2. Перейдите в раздел **Development** → **Events & Callbacks** ("Разработка" → "События и обратные вызовы").
3. Откройте вкладку **Encryption** ("Шифрование").
4. Скопируйте **Verification Token** ("Токен верификации") и **Encrypt Key** ("Ключ шифрования").

На скриншоте ниже показано, где найти **Verification Token**. **Encrypt Key** указан в том же разделе **Encryption**.

![Расположение Verification Token](/images/feishu-verification-token.png)

### Настройка через переменные окружения

```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
```

### Домен Lark (глобальный)

Если ваш арендатор использует Lark (международная версия), задайте домен как `lark` (или полную строку домена). Вы можете задать его в `channels.feishu.domain` или для каждой учётной записи (`channels.feishu.accounts.<id>.domain`).

```json5
{
  channels: {
    feishu: {
      domain: "lark",
      accounts: {
        main: {
          appId: "cli_xxx",
          appSecret: "xxx",
        },
      },
    },
  },
}
```

### Флаги оптимизации квоты

Вы можете снизить использование API Feishu с помощью двух необязательных флагов:

- `typingIndicator` (по умолчанию `true`): если задано `false`, пропускаются вызовы реакций набора текста.
- `resolveSenderNames` (по умолчанию `true`): если задано `false`, пропускаются вызовы поиска профиля отправителя.

Задайте их на верхнем уровне или для каждой учётной записи:

```json5
{
  channels: {
    feishu: {
      typingIndicator: false,
      resolveSenderNames: false,