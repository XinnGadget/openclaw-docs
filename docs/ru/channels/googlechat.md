---
summary: "Статус поддержки приложения Google Chat, возможности и конфигурация"
read_when:
  - Работа над функциями канала Google Chat
title: "Google Chat"
---

# Google Chat (Chat API)

Статус: готов к работе с личными сообщениями (DM) и пространствами через вебхуки Google Chat API (только HTTP).

## Быстрая настройка (для начинающих)

1. Создайте проект в Google Cloud и включите **Google Chat API**:
   - Перейдите по ссылке: [Google Chat API Credentials](https://console.cloud.google.com/apis/api/chat.googleapis.com/credentials).
   - Включите API, если оно ещё не активировано.
2. Создайте **учётную запись службы (Service Account)**:
   - Нажмите **Create Credentials** > **Service Account**.
   - Присвойте ей любое имя (например, `openclaw-chat`).
   - Оставьте разрешения пустыми (нажмите **Continue**).
   - Оставьте список субъектов с доступом пустым (нажмите **Done**).
3. Создайте и скачайте **JSON-ключ**:
   - В списке учётных записей служб выберите только что созданную.
   - Перейдите на вкладку **Keys**.
   - Нажмите **Add Key** > **Create new key**.
   - Выберите **JSON** и нажмите **Create**.
4. Сохраните скачанный JSON-файл на хосте шлюза (например, `~/.openclaw/googlechat-service-account.json`).
5. Создайте приложение Google Chat в [Google Cloud Console Chat Configuration](https://console.cloud.google.com/apis/api/chat.googleapis.com/hangouts-chat):
   - Заполните раздел **Application info**:
     - **App name** (название приложения): например, `OpenClaw`.
     - **Avatar URL** (URL аватара): например, `https://openclaw.ai/logo.png`.
     - **Description** (описание): например, `Personal AI Assistant`.
   - Включите **Interactive features** (интерактивные функции).
   - В разделе **Functionality** (функциональность) отметьте **Join spaces and group conversations** (присоединяться к пространствам и групповым чатам).
   - В разделе **Connection settings** (настройки подключения) выберите **HTTP endpoint URL**.
   - В разделе **Triggers** (триггеры) выберите **Use a common HTTP endpoint URL for all triggers** (использовать общий URL HTTP-конечной точки для всех триггеров) и укажите публичный URL вашего шлюза с добавлением `/googlechat`.
     - _Совет: выполните команду `openclaw status`, чтобы узнать публичный URL вашего шлюза._
   - В разделе **Visibility** (видимость) отметьте **Make this Chat app available to specific people and groups in &lt;Your Domain&gt;** (сделать это приложение Chat доступным для определённых людей и групп в &lt;вашем домене&gt;).
   - Введите свой адрес электронной почты (например, `user@example.com`) в текстовое поле.
   - Нажмите **Save** внизу страницы.
6. **Включите статус приложения**:
   - После сохранения **обновите страницу**.
   - Найдите раздел **App status** (статус приложения) (обычно вверху или внизу после сохранения).
   - Измените статус на **Live — available to users** (в эфире — доступно пользователям).
   - Снова нажмите **Save**.
7. Настройте OpenClaw, указав путь к учётной записи службы и аудиторию вебхука:
   - Переменная окружения: `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE=/path/to/service-account.json`.
   - Или конфигурация: `channels.googlechat.serviceAccountFile: "/path/to/service-account.json"`.
8. Укажите тип и значение аудитории вебхука (должны соответствовать конфигурации вашего приложения Chat).
9. Запустите шлюз. Google Chat будет отправлять POST-запросы на ваш путь вебхука.

## Добавление в Google Chat

После запуска шлюза и добавления вашего адреса электронной почты в список видимости:

1. Перейдите на сайт [Google Chat](https://chat.google.com/).
2. Нажмите на значок **+** (плюс) рядом с **Direct Messages** (личные сообщения).
3. В строке поиска (где обычно добавляют людей) введите **название приложения**, которое вы указали в Google Cloud Console.
   - **Примечание**: бот _не_ появится в списке "Marketplace", поскольку это частное приложение. Вам нужно искать его по имени.
4. Выберите своего бота из результатов поиска.
5. Нажмите **Add** (добавить) или **Chat** (чат), чтобы начать диалог один на один.
6. Отправьте сообщение "Hello", чтобы активировать помощника!

## Публичный URL (только для вебхуков)

Для вебхуков Google Chat требуется публичная HTTPS-конечная точка. В целях безопасности **экспонируйте в интернет только путь `/googlechat`**. Оставьте панель управления OpenClaw и другие чувствительные конечные точки в вашей частной сети.

### Вариант A: Tailscale Funnel (рекомендуется)

Используйте Tailscale Serve для частной панели управления и Funnel для публичного пути вебхука. Это позволит оставить `/` приватным, экспонируя только `/googlechat`.

1. **Проверьте, к какому адресу привязан ваш шлюз:**

   ```bash
   ss -tlnp | grep 18789
   ```

   Запишите IP-адрес (например, `127.0.0.1`, `0.0.0.0` или ваш Tailscale IP, например, `100.x.x.x`).

2. **Экспонируйте панель управления только для tailnet (порт 8443):**

   ```bash
   # Если привязан к localhost (127.0.0.1 или 0.0.0.0):
   tailscale serve --bg --https 8443 http://127.0.0.1:18789

   # Если привязан только к Tailscale IP (например, 100.106.161.80):
   tailscale serve --bg --https 8443 http://100.106.161.80:18789
   ```

3. **Экспонируйте публично только путь вебхука:**

   ```bash
   # Если привязан к localhost (127.0.0.1 или 0.0.0.0):
   tailscale funnel --bg --set-path /googlechat http://127.0.0.1:18789/googlechat

   # Если привязан только к Tailscale IP (например, 100.106.161.80):
   tailscale funnel --bg --set-path /googlechat http://100.106.161.80:18789/googlechat
   ```

4. **Авторизуйте узел для доступа к Funnel:**
   Если появится запрос, перейдите по URL авторизации, указанному в выводе, чтобы включить Funnel для этого узла в политике вашего tailnet.

5. **Проверьте конфигурацию:**

   ```bash
   tailscale serve status
   tailscale funnel status
   ```

Ваш публичный URL вебхука будет выглядеть так:
`https://<node-name>.<tailnet>.ts.net/googlechat`

Ваша частная панель управления останется доступной только в tailnet:
`https://<node-name>.<tailnet>.ts.net:8443/`

Используйте публичный URL (без `:8443`) в конфигурации приложения Google Chat.

> Примечание: эта конфигурация сохраняется после перезагрузки. Чтобы удалить её позже, выполните команды `tailscale funnel reset` и `tailscale serve reset`.

### Вариант B: Обратный прокси (Caddy)

Если вы используете обратный прокси, например Caddy, проксируйте только определённый путь:

```caddy
your-domain.com {
    reverse_proxy /googlechat* localhost:18789
}
```

При такой конфигурации любой запрос к `your-domain.com/` будет игнорироваться или возвращаться с ошибкой 404, а запрос к `your-domain.com/googlechat` будет безопасно перенаправляться в OpenClaw.

### Вариант C: Cloudflare Tunnel

Настройте правила входа в туннель, чтобы маршрутизировать только путь вебхука:

- **Path** (путь): `/googlechat` → `http://localhost:18789/googlechat`
- **Default Rule** (правило по умолчанию): HTTP 404 (Not Found)

## Как это работает

1. Google Chat отправляет POST-запросы вебхука на шлюз. Каждый запрос содержит заголовок `Authorization: Bearer <token>`.
   - OpenClaw проверяет аутентификацию по токену до чтения/парсинга полного тела вебхука, если заголовок присутствует.
   - Запросы Google Workspace Add-on, содержащие `authorizationEventObject.systemIdToken` в теле, поддерживаются с более строгой предварительной аутентификацией по бюджету тела.
2. OpenClaw проверяет токен по настроенным `audienceType` + `audience`:
   - `audienceType: "app-url"` → аудитория