---
read_when:
    - Робота над функціями каналу Microsoft Teams
summary: Статус підтримки бота Microsoft Teams, можливості та налаштування
title: Microsoft Teams
x-i18n:
    generated_at: "2026-04-11T18:30:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3e6841a618fb030e4c2029b3652d45dedd516392e2ae17309ff46b93648ffb79
    source_path: channels/msteams.md
    workflow: 15
---

# Microsoft Teams

> «Залиште надію всі, хто сюди входить».

Оновлено: 2026-03-25

Статус: підтримуються текстові повідомлення + вкладення в DM; надсилання файлів у каналах/групах потребує `sharePointSiteId` + дозволів Graph (див. [Надсилання файлів у групових чатах](#sending-files-in-group-chats)). Опитування надсилаються через Adaptive Cards. Дії з повідомленнями надають явний `upload-file` для надсилань, що починаються з файлу.

## Вбудований плагін

Microsoft Teams постачається як вбудований плагін у поточних релізах OpenClaw, тож у звичайній пакетованій збірці окреме встановлення не потрібне.

Якщо ви використовуєте старішу збірку або власне встановлення без вбудованого Teams,
встановіть його вручну:

```bash
openclaw plugins install @openclaw/msteams
```

Локальний checkout (під час запуску з git-репозиторію):

```bash
openclaw plugins install ./path/to/local/msteams-plugin
```

Докладніше: [Плагіни](/uk/tools/plugin)

## Швидке налаштування (для початківців)

1. Переконайтеся, що плагін Microsoft Teams доступний.
   - У поточних пакетованих релізах OpenClaw він уже вбудований.
   - У старіших/власних встановленнях його можна додати вручну командами вище.
2. Створіть **Azure Bot** (App ID + client secret + tenant ID).
3. Налаштуйте OpenClaw із цими обліковими даними.
4. Відкрийте `/api/messages` (типово порт 3978) через публічну URL-адресу або тунель.
5. Установіть пакет застосунку Teams і запустіть gateway.

Мінімальна конфігурація (client secret):

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      appPassword: "<APP_PASSWORD>",
      tenantId: "<TENANT_ID>",
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

Для production-розгортань розгляньте використання [federated authentication](#federated-authentication-certificate--managed-identity) (сертифікат або managed identity) замість client secret.

Примітка: групові чати типово заблоковані (`channels.msteams.groupPolicy: "allowlist"`). Щоб дозволити відповіді в групах, задайте `channels.msteams.groupAllowFrom` (або використайте `groupPolicy: "open"`, щоб дозволити будь-якого учасника, із вимогою згадки).

## Цілі

- Спілкуватися з OpenClaw через Teams DM, групові чати або канали.
- Зберігати детерміновану маршрутизацію: відповіді завжди повертаються в канал, з якого вони надійшли.
- Типово використовувати безпечну поведінку каналів (потрібні згадки, якщо не налаштовано інакше).

## Запис у конфігурацію

Типово Microsoft Teams має право записувати оновлення конфігурації, ініційовані через `/config set|unset` (потрібно `commands.config: true`).

Вимкнути можна так:

```json5
{
  channels: { msteams: { configWrites: false } },
}
```

## Керування доступом (DM + групи)

**Доступ у DM**

- Типово: `channels.msteams.dmPolicy = "pairing"`. Невідомі відправники ігноруються до схвалення.
- `channels.msteams.allowFrom` має використовувати стабільні AAD object ID.
- UPN/display name можуть змінюватися; пряме зіставлення типово вимкнене й вмикається лише через `channels.msteams.dangerouslyAllowNameMatching: true`.
- Майстер налаштування може зіставляти імена з ID через Microsoft Graph, якщо облікові дані це дозволяють.

**Груповий доступ**

- Типово: `channels.msteams.groupPolicy = "allowlist"` (заблоковано, доки ви не додасте `groupAllowFrom`). Використовуйте `channels.defaults.groupPolicy`, щоб перевизначити типове значення, якщо його не задано.
- `channels.msteams.groupAllowFrom` визначає, які відправники можуть ініціювати дії в групових чатах/каналах (із fallback на `channels.msteams.allowFrom`).
- Встановіть `groupPolicy: "open"`, щоб дозволити будь-якого учасника (типово все одно потрібна згадка).
- Щоб дозволити **жодних каналів**, задайте `channels.msteams.groupPolicy: "disabled"`.

Приклад:

```json5
{
  channels: {
    msteams: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["user@org.com"],
    },
  },
}
```

**Teams + allowlist каналів**

- Обмежуйте відповіді в групах/каналах, перелічивши teams і channels у `channels.msteams.teams`.
- Як ключі слід використовувати стабільні team ID і channel conversation ID.
- Коли `groupPolicy="allowlist"` і присутній teams allowlist, приймаються лише перелічені teams/channels (із вимогою згадки).
- Майстер налаштування приймає записи `Team/Channel` і зберігає їх за вас.
- Під час запуску OpenClaw зіставляє імена team/channel і user в allowlist з ID (коли це дозволяють дозволи Graph)
  і записує це зіставлення в лог; невизначені імена team/channel зберігаються як введені, але типово ігноруються для маршрутизації, якщо не ввімкнено `channels.msteams.dangerouslyAllowNameMatching: true`.

Приклад:

```json5
{
  channels: {
    msteams: {
      groupPolicy: "allowlist",
      teams: {
        "My Team": {
          channels: {
            General: { requireMention: true },
          },
        },
      },
    },
  },
}
```

## Як це працює

1. Переконайтеся, що плагін Microsoft Teams доступний.
   - У поточних пакетованих релізах OpenClaw він уже вбудований.
   - У старіших/власних встановленнях його можна додати вручну командами вище.
2. Створіть **Azure Bot** (App ID + secret + tenant ID).
3. Зберіть **пакет застосунку Teams**, який посилається на бота та включає наведені нижче дозволи RSC.
4. Завантажте/встановіть застосунок Teams у команду (або в особисту область для DM).
5. Налаштуйте `msteams` у `~/.openclaw/openclaw.json` (або змінні середовища) і запустіть gateway.
6. Gateway типово слухає webhook-трафік Bot Framework на `/api/messages`.

## Налаштування Azure Bot (передумови)

Перш ніж налаштовувати OpenClaw, потрібно створити ресурс Azure Bot.

### Крок 1: Створіть Azure Bot

1. Перейдіть до [Create Azure Bot](https://portal.azure.com/#create/Microsoft.AzureBot)
2. Заповніть вкладку **Basics**:

   | Поле               | Значення                                                 |
   | ------------------ | -------------------------------------------------------- |
   | **Bot handle**     | Назва вашого бота, наприклад `openclaw-msteams` (має бути унікальною) |
   | **Subscription**   | Виберіть вашу Azure subscription                         |
   | **Resource group** | Створіть нову або використайте наявну                    |
   | **Pricing tier**   | **Free** для розробки/тестування                         |
   | **Type of App**    | **Single Tenant** (рекомендовано — див. примітку нижче)  |
   | **Creation type**  | **Create new Microsoft App ID**                          |

> **Повідомлення про припинення підтримки:** створення нових multi-tenant ботів було припинено після 2025-07-31. Для нових ботів використовуйте **Single Tenant**.

3. Натисніть **Review + create** → **Create** (зачекайте ~1–2 хвилини)

### Крок 2: Отримайте облікові дані

1. Перейдіть до ресурсу Azure Bot → **Configuration**
2. Скопіюйте **Microsoft App ID** → це ваш `appId`
3. Натисніть **Manage Password** → перейдіть до App Registration
4. У **Certificates & secrets** → **New client secret** → скопіюйте **Value** → це ваш `appPassword`
5. Перейдіть до **Overview** → скопіюйте **Directory (tenant) ID** → це ваш `tenantId`

### Крок 3: Налаштуйте endpoint повідомлень

1. У Azure Bot → **Configuration**
2. Установіть **Messaging endpoint** на вашу webhook URL-адресу:
   - Production: `https://your-domain.com/api/messages`
   - Локальна розробка: використовуйте тунель (див. [Локальна розробка](#local-development-tunneling) нижче)

### Крок 4: Увімкніть канал Teams

1. У Azure Bot → **Channels**
2. Натисніть **Microsoft Teams** → Configure → Save
3. Прийміть Terms of Service

## Federated Authentication (сертифікат + Managed Identity)

> Додано в 2026.3.24

Для production-розгортань OpenClaw підтримує **federated authentication** як безпечнішу альтернативу client secret. Доступні два методи:

### Варіант A: автентифікація на основі сертифіката

Використовуйте PEM-сертифікат, зареєстрований у реєстрації застосунку Entra ID.

**Налаштування:**

1. Згенеруйте або отримайте сертифікат (формат PEM із приватним ключем).
2. У Entra ID → App Registration → **Certificates & secrets** → **Certificates** → завантажте публічний сертифікат.

**Конфігурація:**

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      tenantId: "<TENANT_ID>",
      authType: "federated",
      certificatePath: "/path/to/cert.pem",
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

**Змінні середовища:**

- `MSTEAMS_AUTH_TYPE=federated`
- `MSTEAMS_CERTIFICATE_PATH=/path/to/cert.pem`

### Варіант B: Azure Managed Identity

Використовуйте Azure Managed Identity для автентифікації без пароля. Це ідеально підходить для розгортань в інфраструктурі Azure (AKS, App Service, Azure VM), де доступна managed identity.

**Як це працює:**

1. Bot pod/VM має managed identity (system-assigned або user-assigned).
2. **Federated identity credential** пов’язує managed identity з реєстрацією застосунку Entra ID.
3. Під час виконання OpenClaw використовує `@azure/identity`, щоб отримати токени з endpoint Azure IMDS (`169.254.169.254`).
4. Токен передається в Teams SDK для автентифікації бота.

**Передумови:**

- Інфраструктура Azure з увімкненою managed identity (AKS workload identity, App Service, VM)
- Створений federated identity credential у реєстрації застосунку Entra ID
- Мережевий доступ до IMDS (`169.254.169.254:80`) з pod/VM

**Конфігурація (system-assigned managed identity):**

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      tenantId: "<TENANT_ID>",
      authType: "federated",
      useManagedIdentity: true,
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

**Конфігурація (user-assigned managed identity):**

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      tenantId: "<TENANT_ID>",
      authType: "federated",
      useManagedIdentity: true,
      managedIdentityClientId: "<MI_CLIENT_ID>",
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

**Змінні середовища:**

- `MSTEAMS_AUTH_TYPE=federated`
- `MSTEAMS_USE_MANAGED_IDENTITY=true`
- `MSTEAMS_MANAGED_IDENTITY_CLIENT_ID=<client-id>` (лише для user-assigned)

### Налаштування AKS Workload Identity

Для розгортань AKS із використанням workload identity:

1. **Увімкніть workload identity** у вашому кластері AKS.
2. **Створіть federated identity credential** у реєстрації застосунку Entra ID:

   ```bash
   az ad app federated-credential create --id <APP_OBJECT_ID> --parameters '{
     "name": "my-bot-workload-identity",
     "issuer": "<AKS_OIDC_ISSUER_URL>",
     "subject": "system:serviceaccount:<NAMESPACE>:<SERVICE_ACCOUNT>",
     "audiences": ["api://AzureADTokenExchange"]
   }'
   ```

3. **Додайте анотацію до Kubernetes service account** з app client ID:

   ```yaml
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: my-bot-sa
     annotations:
       azure.workload.identity/client-id: "<APP_CLIENT_ID>"
   ```

4. **Додайте мітку pod** для ін’єкції workload identity:

   ```yaml
   metadata:
     labels:
       azure.workload.identity/use: "true"
   ```

5. **Переконайтеся в наявності мережевого доступу** до IMDS (`169.254.169.254`) — якщо ви використовуєте NetworkPolicy, додайте правило egress, яке дозволяє трафік до `169.254.169.254/32` на порт 80.

### Порівняння типів автентифікації

| Метод                | Конфігурація                                   | Переваги                            | Недоліки                               |
| -------------------- | ---------------------------------------------- | ----------------------------------- | -------------------------------------- |
| **Client secret**    | `appPassword`                                  | Просте налаштування                 | Потрібна ротація секретів, менш безпечно |
| **Certificate**      | `authType: "federated"` + `certificatePath`    | Немає спільного секрету в мережі    | Додаткові витрати на керування сертифікатами |
| **Managed Identity** | `authType: "federated"` + `useManagedIdentity` | Без пароля, не потрібно керувати секретами | Потрібна інфраструктура Azure          |

**Типова поведінка:** якщо `authType` не задано, OpenClaw типово використовує автентифікацію через client secret. Наявні конфігурації продовжують працювати без змін.

## Локальна розробка (тунелювання)

Teams не може звертатися до `localhost`. Для локальної розробки використовуйте тунель:

**Варіант A: ngrok**

```bash
ngrok http 3978
# Скопіюйте https URL, наприклад https://abc123.ngrok.io
# Установіть messaging endpoint на: https://abc123.ngrok.io/api/messages
```

**Варіант B: Tailscale Funnel**

```bash
tailscale funnel 3978
# Використайте вашу URL-адресу Tailscale funnel як messaging endpoint
```

## Teams Developer Portal (альтернатива)

Замість ручного створення manifest ZIP ви можете скористатися [Teams Developer Portal](https://dev.teams.microsoft.com/apps):

1. Натисніть **+ New app**
2. Заповніть базову інформацію (назва, опис, інформація про розробника)
3. Перейдіть до **App features** → **Bot**
4. Виберіть **Enter a bot ID manually** і вставте App ID вашого Azure Bot
5. Позначте області: **Personal**, **Team**, **Group Chat**
6. Натисніть **Distribute** → **Download app package**
7. У Teams: **Apps** → **Manage your apps** → **Upload a custom app** → виберіть ZIP

Часто це простіше, ніж вручну редагувати JSON-маніфести.

## Тестування бота

**Варіант A: Azure Web Chat (спочатку перевірте webhook)**

1. У Azure Portal → ваш ресурс Azure Bot → **Test in Web Chat**
2. Надішліть повідомлення — ви маєте побачити відповідь
3. Це підтверджує, що ваш endpoint webhook працює до налаштування Teams

**Варіант B: Teams (після встановлення застосунку)**

1. Установіть застосунок Teams (sideload або org catalog)
2. Знайдіть бота в Teams і надішліть DM
3. Перевірте логи gateway на наявність вхідної activity

## Налаштування (мінімальне, лише текст)

1. **Переконайтеся, що плагін Microsoft Teams доступний**
   - У поточних пакетованих релізах OpenClaw він уже вбудований.
   - У старіших/власних встановленнях його можна додати вручну:
     - З npm: `openclaw plugins install @openclaw/msteams`
     - Із локального checkout: `openclaw plugins install ./path/to/local/msteams-plugin`

2. **Реєстрація бота**
   - Створіть Azure Bot (див. вище) і занотуйте:
     - App ID
     - Client secret (App password)
     - Tenant ID (single-tenant)

3. **Маніфест застосунку Teams**
   - Додайте запис `bot` із `botId = <App ID>`.
   - Області: `personal`, `team`, `groupChat`.
   - `supportsFiles: true` (обов’язково для обробки файлів в особистій області).
   - Додайте дозволи RSC (нижче).
   - Створіть іконки: `outline.png` (32x32) і `color.png` (192x192).
   - Заархівуйте всі три файли разом: `manifest.json`, `outline.png`, `color.png`.

4. **Налаштуйте OpenClaw**

   ```json5
   {
     channels: {
       msteams: {
         enabled: true,
         appId: "<APP_ID>",
         appPassword: "<APP_PASSWORD>",
         tenantId: "<TENANT_ID>",
         webhook: { port: 3978, path: "/api/messages" },
       },
     },
   }
   ```

   Ви також можете використовувати змінні середовища замість ключів конфігурації:
   - `MSTEAMS_APP_ID`
   - `MSTEAMS_APP_PASSWORD`
   - `MSTEAMS_TENANT_ID`
   - `MSTEAMS_AUTH_TYPE` (необов’язково: `"secret"` або `"federated"`)
   - `MSTEAMS_CERTIFICATE_PATH` (federated + certificate)
   - `MSTEAMS_CERTIFICATE_THUMBPRINT` (необов’язково, не потрібен для автентифікації)
   - `MSTEAMS_USE_MANAGED_IDENTITY` (federated + managed identity)
   - `MSTEAMS_MANAGED_IDENTITY_CLIENT_ID` (лише для user-assigned MI)

5. **Endpoint бота**
   - Установіть Azure Bot Messaging Endpoint на:
     - `https://<host>:3978/api/messages` (або ваш вибраний path/port).

6. **Запустіть gateway**
   - Канал Teams запускається автоматично, коли доступний вбудований або вручну встановлений плагін і існує конфігурація `msteams` з обліковими даними.

## Дія member info

OpenClaw надає для Microsoft Teams дію `member-info`, що працює через Graph, щоб агенти й автоматизації могли напряму отримувати дані про учасників каналу (display name, email, role) з Microsoft Graph.

Вимоги:

- Дозвіл RSC `Member.Read.Group` (уже є в рекомендованому маніфесті)
- Для lookups між командами: дозвіл Application `User.Read.All` у Graph з admin consent

Дія керується через `channels.msteams.actions.memberInfo` (типово: увімкнена, коли доступні облікові дані Graph).

## Контекст історії

- `channels.msteams.historyLimit` визначає, скільки останніх повідомлень каналу/групи загортається в prompt.
- Використовується fallback до `messages.groupChat.historyLimit`. Установіть `0`, щоб вимкнути (типово 50).
- Отримана історія thread фільтрується за allowlist відправників (`allowFrom` / `groupAllowFrom`), тож заповнення контексту thread включає лише повідомлення від дозволених відправників.
- Цитований контекст вкладень (`ReplyTo*`, похідний від Teams reply HTML) зараз передається як отримано.
- Іншими словами, allowlist визначають, хто може активувати агента; сьогодні фільтруються лише окремі шляхи додаткового контексту.
- Історію DM можна обмежити через `channels.msteams.dmHistoryLimit` (ходи користувача). Перевизначення для окремих користувачів: `channels.msteams.dms["<user_id>"].historyLimit`.

## Поточні дозволи Teams RSC (маніфест)

Це **наявні resourceSpecific permissions** у нашому маніфесті застосунку Teams. Вони застосовуються лише в тій команді/чаті, де встановлено застосунок.

**Для каналів (область команди):**

- `ChannelMessage.Read.Group` (Application) - отримання тексту всіх повідомлень каналу без @mention
- `ChannelMessage.Send.Group` (Application)
- `Member.Read.Group` (Application)
- `Owner.Read.Group` (Application)
- `ChannelSettings.Read.Group` (Application)
- `TeamMember.Read.Group` (Application)
- `TeamSettings.Read.Group` (Application)

**Для групових чатів:**

- `ChatMessage.Read.Chat` (Application) - отримання всіх повідомлень групового чату без @mention

## Приклад маніфесту Teams (із прихованими даними)

Мінімальний, коректний приклад з обов’язковими полями. Замініть ID та URL.

```json5
{
  $schema: "https://developer.microsoft.com/en-us/json-schemas/teams/v1.23/MicrosoftTeams.schema.json",
  manifestVersion: "1.23",
  version: "1.0.0",
  id: "00000000-0000-0000-0000-000000000000",
  name: { short: "OpenClaw" },
  developer: {
    name: "Your Org",
    websiteUrl: "https://example.com",
    privacyUrl: "https://example.com/privacy",
    termsOfUseUrl: "https://example.com/terms",
  },
  description: { short: "OpenClaw in Teams", full: "OpenClaw in Teams" },
  icons: { outline: "outline.png", color: "color.png" },
  accentColor: "#5B6DEF",
  bots: [
    {
      botId: "11111111-1111-1111-1111-111111111111",
      scopes: ["personal", "team", "groupChat"],
      isNotificationOnly: false,
      supportsCalling: false,
      supportsVideo: false,
      supportsFiles: true,
    },
  ],
  webApplicationInfo: {
    id: "11111111-1111-1111-1111-111111111111",
  },
  authorization: {
    permissions: {
      resourceSpecific: [
        { name: "ChannelMessage.Read.Group", type: "Application" },
        { name: "ChannelMessage.Send.Group", type: "Application" },
        { name: "Member.Read.Group", type: "Application" },
        { name: "Owner.Read.Group", type: "Application" },
        { name: "ChannelSettings.Read.Group", type: "Application" },
        { name: "TeamMember.Read.Group", type: "Application" },
        { name: "TeamSettings.Read.Group", type: "Application" },
        { name: "ChatMessage.Read.Chat", type: "Application" },
      ],
    },
  },
}
```

### Застереження щодо маніфесту (обов’язкові поля)

- `bots[].botId` **має** збігатися з Azure Bot App ID.
- `webApplicationInfo.id` **має** збігатися з Azure Bot App ID.
- `bots[].scopes` мають включати області, які ви плануєте використовувати (`personal`, `team`, `groupChat`).
- `bots[].supportsFiles: true` є обов’язковим для обробки файлів в особистій області.
- `authorization.permissions.resourceSpecific` має включати channel read/send, якщо ви хочете трафік каналів.

### Оновлення наявного застосунку

Щоб оновити вже встановлений застосунок Teams (наприклад, щоб додати дозволи RSC):

1. Оновіть ваш `manifest.json` новими налаштуваннями
2. **Збільшіть поле `version`** (наприклад, `1.0.0` → `1.1.0`)
3. **Повторно заархівуйте** маніфест з іконками (`manifest.json`, `outline.png`, `color.png`)
4. Завантажте новий zip:
   - **Варіант A (Teams Admin Center):** Teams Admin Center → Teams apps → Manage apps → знайдіть ваш застосунок → Upload new version
   - **Варіант B (Sideload):** У Teams → Apps → Manage your apps → Upload a custom app
5. **Для каналів команд:** повторно встановіть застосунок у кожній команді, щоб нові дозволи набули чинності
6. **Повністю закрийте й знову запустіть Teams** (а не просто закрийте вікно), щоб очистити кешовані метадані застосунку

## Можливості: лише RSC чи Graph

### З **лише Teams RSC** (застосунок встановлено, без дозволів Graph API)

Працює:

- Читання **текстового** вмісту повідомлень каналу.
- Надсилання **текстового** вмісту повідомлень каналу.
- Отримання вкладень файлів у **особистих повідомленнях (DM)**.

НЕ працює:

- **Вміст зображень або файлів** у каналах/групах (payload містить лише HTML-заглушку).
- Завантаження вкладень, що зберігаються в SharePoint/OneDrive.
- Читання історії повідомлень (поза межами live webhook event).

### З **Teams RSC + дозволами Microsoft Graph Application**

Додається:

- Завантаження hosted content (зображень, вставлених у повідомлення).
- Завантаження вкладень файлів, що зберігаються в SharePoint/OneDrive.
- Читання історії повідомлень каналів/чатів через Graph.

### RSC і Graph API

| Можливість              | Дозволи RSC          | Graph API                           |
| ----------------------- | -------------------- | ----------------------------------- |
| **Повідомлення в реальному часі** | Так (через webhook) | Ні (лише polling)                   |
| **Історичні повідомлення** | Ні                   | Так (можна отримувати історію)      |
| **Складність налаштування** | Лише маніфест застосунку | Потрібні admin consent + token flow |
| **Працює офлайн**       | Ні (має бути запущено) | Так (можна запитувати будь-коли)    |

**Підсумок:** RSC потрібен для прослуховування в реальному часі; Graph API — для історичного доступу. Щоб надолужувати пропущені повідомлення під час офлайн-режиму, потрібен Graph API з `ChannelMessage.Read.All` (потрібен admin consent).

## Медіа й історія з Graph (обов’язково для каналів)

Якщо вам потрібні зображення/файли в **каналах** або ви хочете отримувати **історію повідомлень**, потрібно ввімкнути дозволи Microsoft Graph і надати admin consent.

1. У **App Registration** Entra ID (Azure AD) додайте **Application permissions** Microsoft Graph:
   - `ChannelMessage.Read.All` (вкладення каналів + історія)
   - `Chat.Read.All` або `ChatMessage.Read.All` (групові чати)
2. **Надайте admin consent** для tenant.
3. Збільшіть **версію маніфесту** застосунку Teams, повторно завантажте його й **повторно встановіть застосунок у Teams**.
4. **Повністю закрийте й знову запустіть Teams**, щоб очистити кешовані метадані застосунку.

**Додатковий дозвіл для згадок користувачів:** @mentions користувачів працюють одразу для користувачів у поточній розмові. Однак якщо ви хочете динамічно шукати й згадувати користувачів, які **не перебувають у поточній розмові**, додайте дозвіл `User.Read.All` (Application) і надайте admin consent.

## Відомі обмеження

### Тайм-аути webhook

Teams доставляє повідомлення через HTTP webhook. Якщо обробка триває надто довго (наприклад, через повільні відповіді LLM), ви можете побачити:

- тайм-аути gateway
- повторні спроби доставки повідомлення з боку Teams (що спричиняє дублікати)
- втрачені відповіді

OpenClaw обробляє це, швидко повертаючи відповідь і надсилаючи відповіді проактивно, але дуже повільні відповіді все одно можуть спричиняти проблеми.

### Форматування

Markdown у Teams більш обмежений, ніж у Slack чи Discord:

- Базове форматування працює: **жирний**, _курсив_, `code`, посилання
- Складний markdown (таблиці, вкладені списки) може відображатися некоректно
- Adaptive Cards підтримуються для опитувань і довільного надсилання карток (див. нижче)

## Конфігурація

Ключові параметри (спільні шаблони каналів див. у `/gateway/configuration`):

- `channels.msteams.enabled`: увімкнути/вимкнути канал.
- `channels.msteams.appId`, `channels.msteams.appPassword`, `channels.msteams.tenantId`: облікові дані бота.
- `channels.msteams.webhook.port` (типово `3978`)
- `channels.msteams.webhook.path` (типово `/api/messages`)
- `channels.msteams.dmPolicy`: `pairing | allowlist | open | disabled` (типово: pairing)
- `channels.msteams.allowFrom`: allowlist для DM (рекомендовано AAD object ID). Майстер під час налаштування зіставляє імена з ID, коли доступний доступ до Graph.
- `channels.msteams.dangerouslyAllowNameMatching`: аварійний перемикач для повторного ввімкнення зіставлення за змінними UPN/display name і прямої маршрутизації за назвами team/channel.
- `channels.msteams.textChunkLimit`: розмір фрагмента вихідного тексту.
- `channels.msteams.chunkMode`: `length` (типово) або `newline`, щоб розбивати за порожніми рядками (межами абзаців) перед розбиттям за довжиною.
- `channels.msteams.mediaAllowHosts`: allowlist хостів для вхідних вкладень (типово домени Microsoft/Teams).
- `channels.msteams.mediaAuthAllowHosts`: allowlist для додавання заголовків Authorization під час повторних спроб завантаження медіа (типово хости Graph + Bot Framework).
- `channels.msteams.requireMention`: вимагати @mention у каналах/групах (типово true).
- `channels.msteams.replyStyle`: `thread | top-level` (див. [Стиль відповіді](#reply-style-threads-vs-posts)).
- `channels.msteams.teams.<teamId>.replyStyle`: перевизначення для окремої команди.
- `channels.msteams.teams.<teamId>.requireMention`: перевизначення для окремої команди.
- `channels.msteams.teams.<teamId>.tools`: типові перевизначення політики інструментів для окремої команди (`allow`/`deny`/`alsoAllow`), які використовуються, якщо для каналу немає перевизначення.
- `channels.msteams.teams.<teamId>.toolsBySender`: типові перевизначення політики інструментів для окремої команди й відправника (`"*"` wildcard підтримується).
- `channels.msteams.teams.<teamId>.channels.<conversationId>.replyStyle`: перевизначення для окремого каналу.
- `channels.msteams.teams.<teamId>.channels.<conversationId>.requireMention`: перевизначення для окремого каналу.
- `channels.msteams.teams.<teamId>.channels.<conversationId>.tools`: перевизначення політики інструментів для окремого каналу (`allow`/`deny`/`alsoAllow`).
- `channels.msteams.teams.<teamId>.channels.<conversationId>.toolsBySender`: перевизначення політики інструментів для окремого каналу й відправника (`"*"` wildcard підтримується).
- Ключі `toolsBySender` мають використовувати явні префікси:
  `id:`, `e164:`, `username:`, `name:` (застарілі ключі без префікса все ще зіставляються лише з `id:`).
- `channels.msteams.actions.memberInfo`: увімкнути або вимкнути дію member info через Graph (типово: увімкнено, коли доступні облікові дані Graph).
- `channels.msteams.authType`: тип автентифікації — `"secret"` (типово) або `"federated"`.
- `channels.msteams.certificatePath`: шлях до файлу PEM-сертифіката (federated + certificate auth).
- `channels.msteams.certificateThumbprint`: відбиток сертифіката (необов’язково, не потрібен для автентифікації).
- `channels.msteams.useManagedIdentity`: увімкнути автентифікацію через managed identity (режим federated).
- `channels.msteams.managedIdentityClientId`: client ID для user-assigned managed identity.
- `channels.msteams.sharePointSiteId`: SharePoint site ID для надсилання файлів у групових чатах/каналах (див. [Надсилання файлів у групових чатах](#sending-files-in-group-chats)).

## Маршрутизація та сесії

- Ключі сесій відповідають стандартному формату агента (див. [/concepts/session](/uk/concepts/session)):
  - Прямі повідомлення використовують основну сесію (`agent:<agentId>:<mainKey>`).
  - Повідомлення каналу/групи використовують conversation id:
    - `agent:<agentId>:msteams:channel:<conversationId>`
    - `agent:<agentId>:msteams:group:<conversationId>`

## Стиль відповіді: threads чи posts

Teams нещодавно запровадив два стилі UI каналів поверх тієї самої базової моделі даних:

| Стиль                   | Опис                                                      | Рекомендований `replyStyle` |
| ----------------------- | --------------------------------------------------------- | --------------------------- |
| **Posts** (класичний)   | Повідомлення відображаються як картки з thread-відповідями під ними | `thread` (типово)           |
| **Threads** (як у Slack) | Повідомлення йдуть лінійно, більше схоже на Slack         | `top-level`                 |

**Проблема:** API Teams не показує, який стиль UI використовує канал. Якщо використати неправильний `replyStyle`:

- `thread` у каналі зі стилем Threads → відповіді виглядатимуть незграбно вкладеними
- `top-level` у каналі зі стилем Posts → відповіді відображатимуться як окремі повідомлення верхнього рівня, а не в thread

**Рішення:** налаштуйте `replyStyle` для кожного каналу залежно від того, як налаштовано канал:

```json5
{
  channels: {
    msteams: {
      replyStyle: "thread",
      teams: {
        "19:abc...@thread.tacv2": {
          channels: {
            "19:xyz...@thread.tacv2": {
              replyStyle: "top-level",
            },
          },
        },
      },
    },
  },
}
```

## Вкладення та зображення

**Поточні обмеження:**

- **DM:** зображення та вкладення файлів працюють через Teams bot file API.
- **Канали/групи:** вкладення зберігаються в сховищі M365 (SharePoint/OneDrive). Payload webhook містить лише HTML-заглушку, а не фактичні байти файлу. **Для завантаження вкладень каналів потрібні дозволи Graph API**.
- Для явних надсилань, що починаються з файлу, використовуйте `action=upload-file` з `media` / `filePath` / `path`; необов’язковий `message` стає супровідним текстом/коментарем, а `filename` перевизначає ім’я завантаженого файлу.

Без дозволів Graph повідомлення каналів із зображеннями отримуватимуться лише як текст (вміст зображення недоступний боту).
Типово OpenClaw завантажує медіа лише з хостів Microsoft/Teams. Перевизначте це через `channels.msteams.mediaAllowHosts` (використайте `["*"]`, щоб дозволити будь-який хост).
Заголовки Authorization додаються лише для хостів у `channels.msteams.mediaAuthAllowHosts` (типово хости Graph + Bot Framework). Тримайте цей список суворим (уникайте multi-tenant суфіксів).

## Надсилання файлів у групових чатах

Боти можуть надсилати файли в DM за допомогою потоку FileConsentCard (вбудовано). Однак **надсилання файлів у групових чатах/каналах** потребує додаткового налаштування:

| Контекст                 | Як надсилаються файли                      | Потрібне налаштування                              |
| ------------------------ | ------------------------------------------ | -------------------------------------------------- |
| **DM**                   | FileConsentCard → користувач підтверджує → бот завантажує | Працює одразу                                      |
| **Групові чати/канали**  | Завантаження до SharePoint → посилання для спільного доступу | Потрібні `sharePointSiteId` + дозволи Graph        |
| **Зображення (будь-який контекст)** | Вбудовано як Base64                     | Працює одразу                                      |

### Чому груповим чатам потрібен SharePoint

Боти не мають особистого диска OneDrive (endpoint Graph API `/me/drive` не працює для application identities). Щоб надсилати файли в групових чатах/каналах, бот завантажує їх на **сайт SharePoint** і створює посилання для спільного доступу.

### Налаштування

1. **Додайте дозволи Graph API** в Entra ID (Azure AD) → App Registration:
   - `Sites.ReadWrite.All` (Application) - завантаження файлів у SharePoint
   - `Chat.Read.All` (Application) - необов’язково, вмикає посилання спільного доступу для окремих користувачів

2. **Надайте admin consent** для tenant.

3. **Отримайте SharePoint site ID:**

   ```bash
   # Через Graph Explorer або curl із дійсним токеном:
   curl -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/{hostname}:/{site-path}"

   # Приклад: для сайту за адресою "contoso.sharepoint.com/sites/BotFiles"
   curl -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/contoso.sharepoint.com:/sites/BotFiles"

   # Відповідь містить: "id": "contoso.sharepoint.com,guid1,guid2"
   ```

4. **Налаштуйте OpenClaw:**

   ```json5
   {
     channels: {
       msteams: {
         // ... інша конфігурація ...
         sharePointSiteId: "contoso.sharepoint.com,guid1,guid2",
       },
     },
   }
   ```

### Поведінка спільного доступу

| Дозвіл                                    | Поведінка спільного доступу                              |
| ----------------------------------------- | -------------------------------------------------------- |
| `Sites.ReadWrite.All` лише                | Посилання спільного доступу для всієї організації (доступ має будь-хто в організації) |
| `Sites.ReadWrite.All` + `Chat.Read.All`   | Посилання спільного доступу для окремих користувачів (доступ мають лише учасники чату) |

Спільний доступ для окремих користувачів безпечніший, оскільки лише учасники чату можуть отримати доступ до файлу. Якщо дозволу `Chat.Read.All` немає, бот повертається до спільного доступу для всієї організації.

### Поведінка fallback

| Сценарій                                          | Результат                                           |
| ------------------------------------------------- | --------------------------------------------------- |
| Груповий чат + файл + налаштовано `sharePointSiteId` | Завантаження у SharePoint, надсилання посилання спільного доступу |
| Груповий чат + файл + без `sharePointSiteId`      | Спроба завантаження в OneDrive (може не вдатися), надсилається лише текст |
| Особистий чат + файл                              | Потік FileConsentCard (працює без SharePoint)       |
| Будь-який контекст + зображення                   | Вбудовано як Base64 (працює без SharePoint)         |

### Місце зберігання файлів

Завантажені файли зберігаються в папці `/OpenClawShared/` у стандартній бібліотеці документів налаштованого сайту SharePoint.

## Опитування (Adaptive Cards)

OpenClaw надсилає опитування Teams як Adaptive Cards (вбудованого Teams poll API немає).

- CLI: `openclaw message poll --channel msteams --target conversation:<id> ...`
- Голоси записуються gateway у `~/.openclaw/msteams-polls.json`.
- Щоб записувати голоси, gateway має залишатися онлайн.
- Опитування поки що не публікують підсумки результатів автоматично (за потреби перевіряйте файл сховища).

## Adaptive Cards (довільні)

Надсилайте будь-який JSON Adaptive Card користувачам або розмовам Teams за допомогою інструмента `message` або CLI.

Параметр `card` приймає JSON-об’єкт Adaptive Card. Коли передано `card`, текст повідомлення необов’язковий.

**Інструмент агента:**

```json5
{
  action: "send",
  channel: "msteams",
  target: "user:<id>",
  card: {
    type: "AdaptiveCard",
    version: "1.5",
    body: [{ type: "TextBlock", text: "Hello!" }],
  },
}
```

**CLI:**

```bash
openclaw message send --channel msteams \
  --target "conversation:19:abc...@thread.tacv2" \
  --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Hello!"}]}'
```

Див. [документацію Adaptive Cards](https://adaptivecards.io/) щодо схеми карток і прикладів. Докладніше про формати цілей див. у [Формати цілей](#target-formats) нижче.

## Формати цілей

Цілі MSTeams використовують префікси, щоб розрізняти користувачів і розмови:

| Тип цілі              | Формат                           | Приклад                                             |
| --------------------- | -------------------------------- | --------------------------------------------------- |
| Користувач (за ID)    | `user:<aad-object-id>`           | `user:40a1a0ed-4ff2-4164-a219-55518990c197`         |
| Користувач (за ім’ям) | `user:<display-name>`            | `user:John Smith` (потрібен Graph API)              |
| Група/канал           | `conversation:<conversation-id>` | `conversation:19:abc123...@thread.tacv2`            |
| Група/канал (raw)     | `<conversation-id>`              | `19:abc123...@thread.tacv2` (якщо містить `@thread`) |

**Приклади CLI:**

```bash
# Надіслати користувачу за ID
openclaw message send --channel msteams --target "user:40a1a0ed-..." --message "Hello"

# Надіслати користувачу за display name (викликає lookup через Graph API)
openclaw message send --channel msteams --target "user:John Smith" --message "Hello"

# Надіслати в груповий чат або канал
openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" --message "Hello"

# Надіслати Adaptive Card у розмову
openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" \
  --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Hello"}]}'
```

**Приклади інструмента агента:**

```json5
{
  action: "send",
  channel: "msteams",
  target: "user:John Smith",
  message: "Hello!",
}
```

```json5
{
  action: "send",
  channel: "msteams",
  target: "conversation:19:abc...@thread.tacv2",
  card: {
    type: "AdaptiveCard",
    version: "1.5",
    body: [{ type: "TextBlock", text: "Hello" }],
  },
}
```

Примітка: без префікса `user:` імена типово трактуються як цілі групи/команди. Завжди використовуйте `user:`, коли адресуєте людей за display name.

## Проактивні повідомлення

- Проактивні повідомлення можливі лише **після** взаємодії користувача, оскільки саме тоді ми зберігаємо посилання на розмову.
- Див. `/gateway/configuration` щодо `dmPolicy` і обмеження через allowlist.

## ID команди та каналу (поширена пастка)

Параметр запиту `groupId` в URL Teams — це **НЕ** team ID, який використовується для конфігурації. Натомість витягайте ID зі шляху URL:

**URL команди:**

```
https://teams.microsoft.com/l/team/19%3ABk4j...%40thread.tacv2/conversations?groupId=...
                                    └────────────────────────────┘
                                    Team ID (виконайте URL-декодування)
```

**URL каналу:**

```
https://teams.microsoft.com/l/channel/19%3A15bc...%40thread.tacv2/ChannelName?groupId=...
                                      └─────────────────────────┘
                                      Channel ID (виконайте URL-декодування)
```

**Для конфігурації:**

- Team ID = сегмент шляху після `/team/` (URL-декодований, наприклад `19:Bk4j...@thread.tacv2`)
- Channel ID = сегмент шляху після `/channel/` (URL-декодований)
- Параметр запиту `groupId` **ігноруйте**

## Приватні канали

Боти мають обмежену підтримку в приватних каналах:

| Функція                      | Стандартні канали | Приватні канали      |
| ---------------------------- | ----------------- | -------------------- |
| Встановлення бота            | Так               | Обмежено             |
| Повідомлення в реальному часі (webhook) | Так       | Може не працювати    |
| Дозволи RSC                  | Так               | Можуть поводитися інакше |
| @mentions                    | Так               | Якщо бот доступний   |
| Історія через Graph API      | Так               | Так (із дозволами)   |

**Обхідні варіанти, якщо приватні канали не працюють:**

1. Використовуйте стандартні канали для взаємодії з ботом
2. Використовуйте DM — користувачі завжди можуть писати боту напряму
3. Використовуйте Graph API для історичного доступу (потрібен `ChannelMessage.Read.All`)

## Усунення несправностей

### Поширені проблеми

- **У каналах не відображаються зображення:** бракує дозволів Graph або admin consent. Повторно встановіть застосунок Teams і повністю закрийте/знову відкрийте Teams.
- **Немає відповідей у каналі:** типово потрібні згадки; установіть `channels.msteams.requireMention=false` або налаштуйте це для конкретної команди/каналу.
- **Невідповідність версій (Teams все ще показує старий маніфест):** видаліть і знову додайте застосунок та повністю перезапустіть Teams для оновлення.
- **401 Unauthorized від webhook:** очікувано під час ручного тестування без Azure JWT — це означає, що endpoint доступний, але автентифікація не пройдена. Для коректної перевірки використовуйте Azure Web Chat.

### Помилки завантаження маніфесту

- **"Icon file cannot be empty":** маніфест посилається на файли іконок розміром 0 байт. Створіть коректні PNG-іконки (`outline.png` 32x32, `color.png` 192x192).
- **"webApplicationInfo.Id already in use":** застосунок усе ще встановлений в іншій команді/чаті. Спочатку знайдіть і видаліть його або зачекайте 5–10 хвилин на поширення змін.
- **"Something went wrong" під час завантаження:** натомість виконайте завантаження через [https://admin.teams.microsoft.com](https://admin.teams.microsoft.com), відкрийте DevTools браузера (F12) → вкладка Network і перевірте тіло відповіді, щоб побачити фактичну помилку.
- **Не вдається sideload:** спробуйте "Upload an app to your org's app catalog" замість "Upload a custom app" — це часто обходить обмеження sideload.

### Дозволи RSC не працюють

1. Переконайтеся, що `webApplicationInfo.id` точно збігається з App ID вашого бота
2. Повторно завантажте застосунок і перевстановіть його в команді/чаті
3. Перевірте, чи адміністратор вашої організації не заблокував дозволи RSC
4. Підтвердьте, що ви використовуєте правильну область: `ChannelMessage.Read.Group` для команд, `ChatMessage.Read.Chat` для групових чатів

## Посилання

- [Create Azure Bot](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-quickstart-registration) - посібник із налаштування Azure Bot
- [Teams Developer Portal](https://dev.teams.microsoft.com/apps) - створення й керування застосунками Teams
- [Teams app manifest schema](https://learn.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema)
- [Receive channel messages with RSC](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/channel-messages-with-rsc)
- [RSC permissions reference](https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/rsc/resource-specific-consent)
- [Teams bot file handling](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/bots-filesv4) (для каналу/групи потрібен Graph)
- [Proactive messaging](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/send-proactive-messages)

## Пов’язане

- [Огляд каналів](/uk/channels) — усі підтримувані канали
- [Pairing](/uk/channels/pairing) — автентифікація DM і потік pairing
- [Групи](/uk/channels/groups) — поведінка групового чату та обмеження за згадками
- [Маршрутизація каналів](/uk/channels/channel-routing) — маршрутизація сесій для повідомлень
- [Безпека](/uk/gateway/security) — модель доступу та посилення захисту
