---
read_when:
    - Додавання функцій, що розширюють доступ або автоматизацію
summary: Міркування щодо безпеки та модель загроз для запуску AI Gateway із доступом до оболонки
title: Безпека
x-i18n:
    generated_at: "2026-04-12T18:22:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7f3ef693813b696be2e24bcc333c8ee177fa56c3cb06c5fac12a0bd220a29917
    source_path: gateway/security/index.md
    workflow: 15
---

# Безпека

<Warning>
**Модель довіри персонального асистента:** ці рекомендації виходять із припущення про одну межу довіри оператора на один Gateway (модель одного користувача / персонального асистента).
OpenClaw **не** є безпечною межею для ворожого багатокористувацького середовища, у якому кілька зловмисних користувачів ділять одного агента/Gateway.
Якщо вам потрібна робота зі змішаною довірою або в умовах ворожих користувачів, розділіть межі довіри (окремий Gateway + облікові дані, в ідеалі також окремі користувачі ОС/хости).
</Warning>

**На цій сторінці:** [Модель довіри](#scope-first-personal-assistant-security-model) | [Швидкий аудит](#quick-check-openclaw-security-audit) | [Посилений базовий захист](#hardened-baseline-in-60-seconds) | [Модель доступу DM](#dm-access-model-pairing-allowlist-open-disabled) | [Посилення конфігурації](#configuration-hardening-examples) | [Реагування на інциденти](#incident-response)

## Спочатку про межі: модель безпеки персонального асистента

Рекомендації з безпеки OpenClaw ґрунтуються на розгортанні **персонального асистента**: одна межа довіри оператора, потенційно багато агентів.

- Підтримувана модель безпеки: один користувач/межа довіри на Gateway (бажано один користувач ОС/хост/VPS на межу).
- Модель, яка не підтримується як межа безпеки: один спільний Gateway/агент, яким користуються взаємно недовірені або ворожі користувачі.
- Якщо потрібна ізоляція від ворожих користувачів, розділіть за межами довіри (окремий Gateway + облікові дані, а в ідеалі також окремі користувачі ОС/хости).
- Якщо кілька недовірених користувачів можуть надсилати повідомлення одному агенту з увімкненими інструментами, вважайте, що всі вони спільно використовують однакові делеговані повноваження цього агента щодо інструментів.

Ця сторінка пояснює посилення захисту **в межах цієї моделі**. Вона не стверджує наявність ворожої багатокористувацької ізоляції в одному спільному Gateway.

## Швидка перевірка: `openclaw security audit`

Див. також: [Формальна верифікація (моделі безпеки)](/uk/security/formal-verification)

Регулярно запускайте це (особливо після змін конфігурації або відкриття мережевих поверхонь):

```bash
openclaw security audit
openclaw security audit --deep
openclaw security audit --fix
openclaw security audit --json
```

`security audit --fix` навмисно залишається вузько спрямованою командою: вона перемикає поширені відкриті групові політики на allowlist, відновлює `logging.redactSensitive: "tools"`, посилює дозволи для state/config/include-file і використовує скидання ACL Windows замість POSIX `chmod` під час роботи у Windows.

Команда позначає типові небезпечні конфігурації (відкритий доступ до автентифікації Gateway, відкритий доступ до керування браузером, розширені allowlist, дозволи файлової системи, надто поблажливі схвалення exec і відкритий доступ до інструментів через канали).

OpenClaw — це і продукт, і експеримент: ви підключаєте поведінку frontier-моделей до реальних поверхонь обміну повідомленнями та реальних інструментів. **Ідеально безпечної конфігурації не існує.** Мета — усвідомлено визначити:

- хто може спілкуватися з вашим ботом;
- де боту дозволено діяти;
- до чого бот може торкатися.

Починайте з мінімального доступу, який ще дозволяє працювати, і розширюйте його лише в міру зростання впевненості.

### Розгортання та довіра до хоста

OpenClaw припускає, що хост і межа конфігурації є довіреними:

- Якщо хтось може змінювати стан/конфігурацію хоста Gateway (`~/.openclaw`, включно з `openclaw.json`), вважайте його довіреним оператором.
- Запуск одного Gateway для кількох взаємно недовірених/ворожих операторів **не є рекомендованою конфігурацією**.
- Для команд зі змішаним рівнем довіри розділяйте межі довіри за допомогою окремих Gateway (або щонайменше окремих користувачів ОС/хостів).
- Рекомендований типовий варіант: один користувач на машину/хост (або VPS), один gateway для цього користувача та один або кілька агентів у цьому gateway.
- У межах одного екземпляра Gateway автентифікований операторський доступ — це довірена роль площини керування, а не роль окремого користувача-орендаря.
- Ідентифікатори сеансу (`sessionKey`, session IDs, labels) — це селектори маршрутизації, а не токени авторизації.
- Якщо кілька людей можуть надсилати повідомлення одному агенту з увімкненими інструментами, кожен із них може керувати однаковим набором дозволів. Ізоляція сеансів/пам’яті на рівні користувача допомагає приватності, але не перетворює спільного агента на авторизацію хоста на рівні окремого користувача.

### Спільний Slack workspace: реальний ризик

Якщо «будь-хто в Slack може написати боту», основний ризик — це делеговані повноваження інструментів:

- будь-який дозволений відправник може ініціювати виклики інструментів (`exec`, браузер, мережеві/файлові інструменти) у межах політики агента;
- ін’єкція підказок/вмісту від одного відправника може спричинити дії, що впливають на спільний стан, пристрої або результати;
- якщо один спільний агент має доступ до чутливих облікових даних/файлів, будь-який дозволений відправник потенційно може ініціювати їх ексфільтрацію через використання інструментів.

Для командних робочих процесів використовуйте окремі агенти/Gateway з мінімальним набором інструментів; агентів із персональними даними тримайте приватними.

### Спільний агент у компанії: прийнятний шаблон

Це прийнятно, коли всі користувачі такого агента належать до однієї межі довіри (наприклад, одна команда в компанії), а сам агент суворо обмежений бізнес-контекстом.

- запускайте його на виділеній машині/VM/контейнері;
- використовуйте виділеного користувача ОС + окремий браузер/профіль/акаунти для цього середовища;
- не входьте в цьому середовищі до особистих Apple/Google-акаунтів чи особистих профілів браузера/менеджера паролів.

Якщо ви змішуєте особисті й корпоративні ідентичності в одному середовищі, ви руйнуєте розділення та підвищуєте ризик витоку персональних даних.

## Концепція довіри між Gateway і Node

Розглядайте Gateway і Node як єдиний домен довіри оператора, але з різними ролями:

- **Gateway** — це площина керування та поверхня політик (`gateway.auth`, політика інструментів, маршрутизація).
- **Node** — це поверхня віддаленого виконання, пов’язана з цим Gateway (команди, дії на пристрої, локальні можливості хоста).
- Викликач, автентифікований у Gateway, є довіреним у межах Gateway. Після pairing дії Node вважаються довіреними операторськими діями на цьому Node.
- `sessionKey` — це вибір маршрутизації/контексту, а не автентифікація окремого користувача.
- Схвалення exec (allowlist + ask) — це запобіжники для намірів оператора, а не ізоляція від ворожих багатокористувацьких сценаріїв.
- Типова поведінка OpenClaw для довірених конфігурацій з одним оператором полягає в тому, що виконання на хості через `gateway`/`node` дозволене без запитів на схвалення (`security="full"`, `ask="off"`, якщо ви не посилите політику). Це навмисне UX-рішення, а не вразливість саме по собі.
- Схвалення exec прив’язуються до точного контексту запиту та, наскільки можливо, до прямих локальних файлових операндів; вони не моделюють семантично кожен шлях завантаження runtime/інтерпретатора. Для сильних меж використовуйте sandboxing та ізоляцію хоста.

Якщо вам потрібна ізоляція від ворожих користувачів, розділяйте межі довіри за користувачем ОС/хостом і запускайте окремі Gateway.

## Матриця меж довіри

Використовуйте це як швидку модель під час оцінки ризику:

| Межа або контроль                                        | Що це означає                                    | Типове хибне тлумачення                                                    |
| -------------------------------------------------------- | ------------------------------------------------ | -------------------------------------------------------------------------- |
| `gateway.auth` (token/password/trusted-proxy/device auth) | Автентифікує викликачів до API Gateway           | «Щоб бути безпечною, система потребує підпису кожного повідомлення в кожному кадрі» |
| `sessionKey`                                             | Ключ маршрутизації для вибору контексту/сеансу   | «Ключ сеансу — це межа автентифікації користувача»                         |
| Запобіжники для prompt/content                           | Зменшують ризик зловживання моделлю              | «Одна лише prompt injection уже доводить обхід автентифікації»             |
| `canvas.eval` / browser evaluate                         | Навмисна операторська можливість, коли увімкнена | «Будь-який примітив JS eval автоматично є вразливістю в цій моделі довіри» |
| Локальна TUI-оболонка `!`                                | Явно ініційоване оператором локальне виконання   | «Локальна зручна shell-команда — це віддалена ін’єкція»                    |
| Pairing Node і команди Node                              | Віддалене виконання на рівні оператора на пов’язаних пристроях | «Керування віддаленим пристроєм слід за замовчуванням трактувати як доступ недовіреного користувача» |

## Не є вразливостями за задумом

Про ці шаблони часто повідомляють, але зазвичай їх закривають без дій, якщо не показано реальний обхід межі:

- Ланцюги, що складаються лише з prompt injection, без обходу політики/автентифікації/sandbox.
- Твердження, що припускають вороже багатокористувацьке використання на одному спільному хості/конфігурації.
- Твердження, які класифікують звичайний операторський доступ на читання (наприклад `sessions.list`/`sessions.preview`/`chat.history`) як IDOR у конфігурації зі спільним gateway.
- Висновки щодо розгортань лише на localhost (наприклад HSTS для gateway, доступного лише через loopback).
- Повідомлення про підпис вхідних webhook Discord для вхідних шляхів, яких немає в цьому репозиторії.
- Повідомлення, які трактують метадані pairing Node як прихований другий рівень схвалення кожної команди для `system.run`, хоча реальною межею виконання все ще є глобальна політика команд Node у gateway плюс власні схвалення exec самого Node.
- Повідомлення про «відсутність авторизації на рівні користувача», які трактують `sessionKey` як токен автентифікації.

## Контрольний список для дослідника перед відкриттям GHSA

Перш ніж відкривати GHSA, перевірте все з наведеного нижче:

1. Відтворення все ще працює на останньому `main` або в останньому релізі.
2. Повідомлення містить точний шлях у коді (`file`, function, line range) і перевірену версію/коміт.
3. Вплив перетинає задокументовану межу довіри (а не лише prompt injection).
4. Заявлена проблема не входить до [Out of Scope](https://github.com/openclaw/openclaw/blob/main/SECURITY.md#out-of-scope).
5. Наявні advisory уже перевірені на дублікати (за потреби використовуйте канонічний GHSA повторно).
6. Припущення щодо розгортання явно описані (loopback/local чи exposed, довірені чи недовірені оператори).

## Посилений базовий захист за 60 секунд

Спочатку використовуйте цей базовий профіль, а потім вибірково знову вмикайте інструменти для довірених агентів:

```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",
    auth: { mode: "token", token: "replace-with-long-random-token" },
  },
  session: {
    dmScope: "per-channel-peer",
  },
  tools: {
    profile: "messaging",
    deny: ["group:automation", "group:runtime", "group:fs", "sessions_spawn", "sessions_send"],
    fs: { workspaceOnly: true },
    exec: { security: "deny", ask: "always" },
    elevated: { enabled: false },
  },
  channels: {
    whatsapp: { dmPolicy: "pairing", groups: { "*": { requireMention: true } } },
  },
}
```

Це залишає Gateway доступним лише локально, ізолює DM і за замовчуванням вимикає інструменти площини керування/runtime.

## Швидке правило для спільної вхідної скриньки

Якщо більше ніж одна людина може надсилати DM вашому боту:

- Установіть `session.dmScope: "per-channel-peer"` (або `"per-account-channel-peer"` для каналів із кількома акаунтами).
- Використовуйте `dmPolicy: "pairing"` або суворі allowlist.
- Ніколи не поєднуйте спільні DM із широким доступом до інструментів.
- Це посилює захист кооперативних/спільних вхідних скриньок, але не призначене для ворожої коорендної ізоляції, коли користувачі мають спільний доступ на запис до хоста/конфігурації.

## Модель видимості контексту

OpenClaw розділяє два поняття:

- **Авторизація запуску**: хто може запускати агента (`dmPolicy`, `groupPolicy`, allowlist, обмеження згадуваннями).
- **Видимість контексту**: який додатковий контекст вбудовується у вхід моделі (тіло відповіді, процитований текст, історія гілки, метадані пересилання).

Allowlist контролюють запуск і авторизацію команд. Налаштування `contextVisibility` визначає, як фільтрується додатковий контекст (процитовані відповіді, корені гілок, отримана історія):

- `contextVisibility: "all"` (типове значення) зберігає додатковий контекст у тому вигляді, у якому його отримано.
- `contextVisibility: "allowlist"` фільтрує додатковий контекст за відправниками, дозволеними активними перевірками allowlist.
- `contextVisibility: "allowlist_quote"` працює як `allowlist`, але все ж зберігає одну явну процитовану відповідь.

Установлюйте `contextVisibility` для каналу або для кімнати/розмови. Докладніше про налаштування див. у [Групові чати](/uk/channels/groups#context-visibility-and-allowlists).

Рекомендації для triage advisory:

- Твердження, які лише показують, що «модель може бачити процитований або історичний текст від відправників поза allowlist», є висновками щодо посилення захисту, які можна усунути за допомогою `contextVisibility`, а не самі по собі обходом межі автентифікації чи sandbox.
- Щоб мати безпековий вплив, повідомлення все одно повинні демонструвати обхід межі довіри (автентифікація, політика, sandbox, схвалення або інша задокументована межа).

## Що перевіряє аудит (на високому рівні)

- **Вхідний доступ** (політики DM, групові політики, allowlist): чи можуть сторонні люди запускати бота?
- **Радіус ураження інструментів** (розширені інструменти + відкриті кімнати): чи може prompt injection перетворитися на дії в оболонці/з файлами/мережею?
- **Дрейф схвалення exec** (`security=full`, `autoAllowSkills`, allowlist інтерпретаторів без `strictInlineEval`): чи запобіжники host-exec усе ще працюють так, як ви очікуєте?
  - `security="full"` — це широке попередження про режим безпеки, а не доказ помилки. Це обраний варіант за замовчуванням для довірених конфігурацій персонального асистента; посилюйте його лише тоді, коли ваша модель загроз вимагає схвалення або запобіжників allowlist.
- **Мережевий доступ** (bind/auth Gateway, Tailscale Serve/Funnel, слабкі/короткі токени автентифікації).
- **Доступ до керування браузером** (віддалені Node, relay-порти, віддалені кінцеві точки CDP).
- **Гігієна локального диска** (дозволи, symlink, include конфігурації, шляхи «синхронізованих папок»).
- **Плагіни** (розширення існують без явного allowlist).
- **Дрейф політик/помилки конфігурації** (налаштування sandbox docker задані, але режим sandbox вимкнений; неефективні шаблони `gateway.nodes.denyCommands`, тому що зіставлення виконується лише за точною назвою команди (наприклад `system.run`) і не аналізує текст оболонки; небезпечні записи `gateway.nodes.allowCommands`; глобальний `tools.profile="minimal"` перевизначено профілями окремих агентів; інструменти розширень Plugin доступні через надто поблажливу політику інструментів).
- **Дрейф очікувань runtime** (наприклад, припущення, що неявний exec і далі означає `sandbox`, хоча `tools.exec.host` тепер за замовчуванням має значення `auto`, або явне встановлення `tools.exec.host="sandbox"` при вимкненому режимі sandbox).
- **Гігієна моделей** (попередження, якщо налаштовані моделі виглядають застарілими; не є жорстким блокуванням).

Якщо ви запускаєте `--deep`, OpenClaw також намагається виконати best-effort live-перевірку Gateway.

## Карта зберігання облікових даних

Використовуйте це під час аудиту доступу або коли вирішуєте, що резервувати:

- **WhatsApp**: `~/.openclaw/credentials/whatsapp/<accountId>/creds.json`
- **Токен Telegram-бота**: config/env або `channels.telegram.tokenFile` (лише звичайний файл; symlink відхиляються)
- **Токен Discord-бота**: config/env або SecretRef (постачальники env/file/exec)
- **Токени Slack**: config/env (`channels.slack.*`)
- **Allowlist pairing**:
  - `~/.openclaw/credentials/<channel>-allowFrom.json` (типовий акаунт)
  - `~/.openclaw/credentials/<channel>-<accountId>-allowFrom.json` (нетипові акаунти)
- **Профілі автентифікації моделей**: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- **Файл із payload секретів (необов’язково)**: `~/.openclaw/secrets.json`
- **Імпорт застарілого OAuth**: `~/.openclaw/credentials/oauth.json`

## Контрольний список аудиту безпеки

Коли аудит виводить висновки, дотримуйтеся такого порядку пріоритетів:

1. **Усе, що є “open” + увімкнені інструменти**: спочатку обмежте DM/групи (pairing/allowlist), потім посильте політику інструментів/sandboxing.
2. **Публічний мережевий доступ** (bind у LAN, Funnel, відсутність auth): виправляйте негайно.
3. **Віддалений доступ до керування браузером**: ставтеся до цього як до операторського доступу (лише tailnet, навмисне pair Node, уникайте публічного доступу).
4. **Дозволи**: переконайтеся, що state/config/credentials/auth недоступні для читання групою або всіма.
5. **Плагіни/розширення**: завантажуйте лише те, чому ви явно довіряєте.
6. **Вибір моделі**: для будь-якого бота з інструментами віддавайте перевагу сучасним моделям, загартованим проти інструкційних атак.

## Глосарій аудиту безпеки

Найбільш показові значення `checkId`, які ви, найімовірніше, побачите в реальних розгортаннях (список не є вичерпним):

| `checkId`                                                     | Серйозність   | Чому це важливо                                                                      | Основний ключ/шлях для виправлення                                                                    | Авто-виправлення |
| ------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------- | ---------------- |
| `fs.state_dir.perms_world_writable`                           | critical      | Інші користувачі/процеси можуть змінювати весь стан OpenClaw                         | дозволи файлової системи для `~/.openclaw`                                                            | так              |
| `fs.state_dir.perms_group_writable`                           | warn          | Користувачі групи можуть змінювати весь стан OpenClaw                                | дозволи файлової системи для `~/.openclaw`                                                            | так              |
| `fs.state_dir.perms_readable`                                 | warn          | Каталог стану доступний для читання іншими                                           | дозволи файлової системи для `~/.openclaw`                                                            | так              |
| `fs.state_dir.symlink`                                        | warn          | Ціль каталогу стану стає іншою межею довіри                                          | структура файлової системи каталогу стану                                                             | ні               |
| `fs.config.perms_writable`                                    | critical      | Інші можуть змінювати політику auth/tool/config                                      | дозволи файлової системи для `~/.openclaw/openclaw.json`                                              | так              |
| `fs.config.symlink`                                           | warn          | Ціль файлу конфігурації стає іншою межею довіри                                      | структура файлової системи файлу конфігурації                                                         | ні               |
| `fs.config.perms_group_readable`                              | warn          | Користувачі групи можуть читати токени/налаштування з конфігурації                   | дозволи файлової системи для файлу конфігурації                                                       | так              |
| `fs.config.perms_world_readable`                              | critical      | Конфігурація може розкривати токени/налаштування                                     | дозволи файлової системи для файлу конфігурації                                                       | так              |
| `fs.config_include.perms_writable`                            | critical      | Файл include конфігурації може бути змінений іншими                                  | дозволи для include-файлу, на який посилається `openclaw.json`                                        | так              |
| `fs.config_include.perms_group_readable`                      | warn          | Користувачі групи можуть читати включені секрети/налаштування                        | дозволи для include-файлу, на який посилається `openclaw.json`                                        | так              |
| `fs.config_include.perms_world_readable`                      | critical      | Включені секрети/налаштування доступні для читання всім                              | дозволи для include-файлу, на який посилається `openclaw.json`                                        | так              |
| `fs.auth_profiles.perms_writable`                             | critical      | Інші можуть впроваджувати або підміняти збережені облікові дані моделей              | дозволи для `agents/<agentId>/agent/auth-profiles.json`                                               | так              |
| `fs.auth_profiles.perms_readable`                             | warn          | Інші можуть читати API-ключі та OAuth-токени                                         | дозволи для `agents/<agentId>/agent/auth-profiles.json`                                               | так              |
| `fs.credentials_dir.perms_writable`                           | critical      | Інші можуть змінювати стан pairing/облікових даних каналів                           | дозволи файлової системи для `~/.openclaw/credentials`                                                | так              |
| `fs.credentials_dir.perms_readable`                           | warn          | Інші можуть читати стан облікових даних каналів                                      | дозволи файлової системи для `~/.openclaw/credentials`                                                | так              |
| `fs.sessions_store.perms_readable`                            | warn          | Інші можуть читати транскрипти/метадані сеансів                                      | дозволи сховища сеансів                                                                               | так              |
| `fs.log_file.perms_readable`                                  | warn          | Інші можуть читати журнали, де дані замасковані, але все ще чутливі                  | дозволи для файлу журналу gateway                                                                     | так              |
| `fs.synced_dir`                                               | warn          | Стан/конфігурація в iCloud/Dropbox/Drive розширюють ризик витоку токенів/транскриптів | перенесіть конфігурацію/стан із синхронізованих папок                                                 | ні               |
| `gateway.bind_no_auth`                                        | critical      | Віддалений bind без спільного секрету                                                | `gateway.bind`, `gateway.auth.*`                                                                      | ні               |
| `gateway.loopback_no_auth`                                    | critical      | Loopback за reverse proxy може стати неавтентифікованим                              | `gateway.auth.*`, налаштування proxy                                                                  | ні               |
| `gateway.trusted_proxies_missing`                             | warn          | Заголовки reverse proxy присутні, але не позначені як trusted                        | `gateway.trustedProxies`                                                                              | ні               |
| `gateway.http.no_auth`                                        | warn/critical | HTTP API Gateway доступні з `auth.mode="none"`                                       | `gateway.auth.mode`, `gateway.http.endpoints.*`                                                       | ні               |
| `gateway.http.session_key_override_enabled`                   | info          | Викликачі HTTP API можуть перевизначати `sessionKey`                                 | `gateway.http.allowSessionKeyOverride`                                                                | ні               |
| `gateway.tools_invoke_http.dangerous_allow`                   | warn/critical | Повторно вмикає небезпечні інструменти через HTTP API                                | `gateway.tools.allow`                                                                                 | ні               |
| `gateway.nodes.allow_commands_dangerous`                      | warn/critical | Вмикає команди Node з високим впливом (camera/screen/contacts/calendar/SMS)          | `gateway.nodes.allowCommands`                                                                         | ні               |
| `gateway.nodes.deny_commands_ineffective`                     | warn          | Записи deny, схожі на шаблони, не зіставляються з текстом оболонки або групами       | `gateway.nodes.denyCommands`                                                                          | ні               |
| `gateway.tailscale_funnel`                                    | critical      | Публічний доступ з інтернету                                                         | `gateway.tailscale.mode`                                                                              | ні               |
| `gateway.tailscale_serve`                                     | info          | Доступ через tailnet увімкнено через Serve                                           | `gateway.tailscale.mode`                                                                              | ні               |
| `gateway.control_ui.allowed_origins_required`                 | critical      | Control UI поза loopback без явного allowlist джерел браузера                        | `gateway.controlUi.allowedOrigins`                                                                    | ні               |
| `gateway.control_ui.allowed_origins_wildcard`                 | warn/critical | `allowedOrigins=["*"]` вимикає allowlist джерел браузера                             | `gateway.controlUi.allowedOrigins`                                                                    | ні               |
| `gateway.control_ui.host_header_origin_fallback`              | warn/critical | Вмикає fallback походження через заголовок Host (послаблення захисту від DNS rebinding) | `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback`                                       | ні               |
| `gateway.control_ui.insecure_auth`                            | warn          | Увімкнено перемикач сумісності insecure-auth                                         | `gateway.controlUi.allowInsecureAuth`                                                                 | ні               |
| `gateway.control_ui.device_auth_disabled`                     | critical      | Вимикає перевірку ідентичності пристрою                                              | `gateway.controlUi.dangerouslyDisableDeviceAuth`                                                      | ні               |
| `gateway.real_ip_fallback_enabled`                            | warn/critical | Довіра до fallback `X-Real-IP` може дозволити підробку source-IP через помилкову конфігурацію proxy | `gateway.allowRealIpFallback`, `gateway.trustedProxies`                                   | ні               |
| `gateway.token_too_short`                                     | warn          | Короткий спільний токен легше підібрати перебором                                    | `gateway.auth.token`                                                                                  | ні               |
| `gateway.auth_no_rate_limit`                                  | warn          | Відкрита auth без rate limiting підвищує ризик brute-force                           | `gateway.auth.rateLimit`                                                                              | ні               |
| `gateway.trusted_proxy_auth`                                  | critical      | Ідентичність proxy тепер стає межею auth                                             | `gateway.auth.mode="trusted-proxy"`                                                                   | ні               |
| `gateway.trusted_proxy_no_proxies`                            | critical      | Автентифікація trusted-proxy без IP-адрес trusted proxy є небезпечною                | `gateway.trustedProxies`                                                                              | ні               |
| `gateway.trusted_proxy_no_user_header`                        | critical      | Автентифікація trusted-proxy не може безпечно визначити ідентичність користувача     | `gateway.auth.trustedProxy.userHeader`                                                                | ні               |
| `gateway.trusted_proxy_no_allowlist`                          | warn          | Автентифікація trusted-proxy приймає будь-якого автентифікованого користувача upstream | `gateway.auth.trustedProxy.allowUsers`                                                             | ні               |
| `gateway.probe_auth_secretref_unavailable`                    | warn          | Глибока перевірка не змогла розв’язати auth SecretRef у цьому шляху команди          | джерело auth для deep-probe / доступність SecretRef                                                  | ні               |
| `gateway.probe_failed`                                        | warn/critical | Live-перевірка Gateway завершилася невдачею                                          | доступність/автентифікація gateway                                                                   | ні               |
| `discovery.mdns_full_mode`                                    | warn/critical | Повний режим mDNS рекламує метадані `cliPath`/`sshPort` у локальній мережі           | `discovery.mdns.mode`, `gateway.bind`                                                                | ні               |
| `config.insecure_or_dangerous_flags`                          | warn          | Увімкнено будь-які небезпечні/незахищені debug-прапори                               | кілька ключів (див. деталі висновку)                                                                 | ні               |
| `config.secrets.gateway_password_in_config`                   | warn          | Пароль Gateway зберігається безпосередньо в конфігурації                             | `gateway.auth.password`                                                                              | ні               |
| `config.secrets.hooks_token_in_config`                        | warn          | Bearer-токен hook зберігається безпосередньо в конфігурації                          | `hooks.token`                                                                                        | ні               |
| `hooks.token_reuse_gateway_token`                             | critical      | Токен входу hook також відкриває доступ до auth Gateway                              | `hooks.token`, `gateway.auth.token`                                                                  | ні               |
| `hooks.token_too_short`                                       | warn          | Полегшує brute force для входу hook                                                  | `hooks.token`                                                                                        | ні               |
| `hooks.default_session_key_unset`                             | warn          | Агент hook виконує fan out у згенеровані сеанси для кожного запиту                   | `hooks.defaultSessionKey`                                                                            | ні               |
| `hooks.allowed_agent_ids_unrestricted`                        | warn/critical | Автентифіковані викликачі hook можуть маршрутизувати до будь-якого налаштованого агента | `hooks.allowedAgentIds`                                                                           | ні               |
| `hooks.request_session_key_enabled`                           | warn/critical | Зовнішній викликач може вибирати `sessionKey`                                        | `hooks.allowRequestSessionKey`                                                                       | ні               |
| `hooks.request_session_key_prefixes_missing`                  | warn/critical | Немає обмеження на форму зовнішніх ключів сеансу                                     | `hooks.allowedSessionKeyPrefixes`                                                                    | ні               |
| `hooks.path_root`                                             | critical      | Шлях hook — `/`, що полегшує колізії або помилкову маршрутизацію входу               | `hooks.path`                                                                                         | ні               |
| `hooks.installs_unpinned_npm_specs`                           | warn          | Записи встановлення hook не прив’язані до незмінних npm-специфікацій                 | метадані встановлення hook                                                                           | ні               |
| `hooks.installs_missing_integrity`                            | warn          | У записах встановлення hook відсутні метадані integrity                              | метадані встановлення hook                                                                           | ні               |
| `hooks.installs_version_drift`                                | warn          | Записи встановлення hook розходяться зі встановленими пакетами                       | метадані встановлення hook                                                                           | ні               |
| `logging.redact_off`                                          | warn          | Чутливі значення витікають у журнали/статус                                          | `logging.redactSensitive`                                                                            | так              |
| `browser.control_invalid_config`                              | warn          | Конфігурація керування браузером недійсна ще до runtime                              | `browser.*`                                                                                          | ні               |
| `browser.control_no_auth`                                     | critical      | Керування браузером відкрите без auth через token/password                           | `gateway.auth.*`                                                                                     | ні               |
| `browser.remote_cdp_http`                                     | warn          | Віддалений CDP через звичайний HTTP не має транспортного шифрування                  | профіль браузера `cdpUrl`                                                                            | ні               |
| `browser.remote_cdp_private_host`                             | warn          | Віддалений CDP націлений на приватний/внутрішній хост                                | профіль браузера `cdpUrl`, `browser.ssrfPolicy.*`                                                    | ні               |
| `sandbox.docker_config_mode_off`                              | warn          | Конфігурація Docker sandbox присутня, але неактивна                                  | `agents.*.sandbox.mode`                                                                              | ні               |
| `sandbox.bind_mount_non_absolute`                             | warn          | Відносні bind mount можуть розв’язуватися непередбачувано                            | `agents.*.sandbox.docker.binds[]`                                                                    | ні               |
| `sandbox.dangerous_bind_mount`                                | critical      | Ціль bind mount sandbox вказує на заблоковані системні шляхи, облікові дані або шляхи сокета Docker | `agents.*.sandbox.docker.binds[]`                                                        | ні               |
| `sandbox.dangerous_network_mode`                              | critical      | Мережа Docker sandbox використовує режим `host` або `container:*` із приєднанням до простору імен | `agents.*.sandbox.docker.network`                                                         | ні               |
| `sandbox.dangerous_seccomp_profile`                           | critical      | Профіль seccomp sandbox послаблює ізоляцію контейнера                                | `agents.*.sandbox.docker.securityOpt`                                                                | ні               |
| `sandbox.dangerous_apparmor_profile`                          | critical      | Профіль AppArmor sandbox послаблює ізоляцію контейнера                               | `agents.*.sandbox.docker.securityOpt`                                                                | ні               |
| `sandbox.browser_cdp_bridge_unrestricted`                     | warn          | Міст CDP браузера в sandbox відкритий без обмеження діапазону джерел                 | `sandbox.browser.cdpSourceRange`                                                                     | ні               |
| `sandbox.browser_container.non_loopback_publish`              | critical      | Наявний контейнер браузера публікує CDP на інтерфейсах поза loopback                 | конфігурація publish контейнера браузера sandbox                                                     | ні               |
| `sandbox.browser_container.hash_label_missing`                | warn          | Наявний контейнер браузера створено до поточних міток хеша конфігурації              | `openclaw sandbox recreate --browser --all`                                                          | ні               |
| `sandbox.browser_container.hash_epoch_stale`                  | warn          | Наявний контейнер браузера створено до поточної епохи конфігурації браузера          | `openclaw sandbox recreate --browser --all`                                                          | ні               |
| `tools.exec.host_sandbox_no_sandbox_defaults`                 | warn          | `exec host=sandbox` безпечно завершується відмовою, якщо sandbox вимкнено            | `tools.exec.host`, `agents.defaults.sandbox.mode`                                                    | ні               |
| `tools.exec.host_sandbox_no_sandbox_agents`                   | warn          | Для агента `exec host=sandbox` безпечно завершується відмовою, якщо sandbox вимкнено | `agents.list[].tools.exec.host`, `agents.list[].sandbox.mode`                                        | ні               |
| `tools.exec.security_full_configured`                         | warn/critical | Host exec працює з `security="full"`                                                 | `tools.exec.security`, `agents.list[].tools.exec.security`                                           | ні               |
| `tools.exec.auto_allow_skills_enabled`                        | warn          | Схвалення exec неявно довіряють skill bins                                           | `~/.openclaw/exec-approvals.json`                                                                    | ні               |
| `tools.exec.allowlist_interpreter_without_strict_inline_eval` | warn          | Allowlist інтерпретаторів дозволяють inline eval без примусового повторного схвалення | `tools.exec.strictInlineEval`, `agents.list[].tools.exec.strictInlineEval`, allowlist схвалень exec | ні               |
| `tools.exec.safe_bins_interpreter_unprofiled`                 | warn          | Біни інтерпретаторів/runtime у `safeBins` без явних профілів розширюють ризик exec   | `tools.exec.safeBins`, `tools.exec.safeBinProfiles`, `agents.list[].tools.exec.*`                    | ні               |
| `tools.exec.safe_bins_broad_behavior`                         | warn          | Інструменти з широкою поведінкою в `safeBins` послаблюють модель довіри низького ризику для фільтра stdin | `tools.exec.safeBins`, `agents.list[].tools.exec.safeBins`                               | ні               |
| `tools.exec.safe_bin_trusted_dirs_risky`                      | warn          | `safeBinTrustedDirs` містить змінювані або ризикові каталоги                         | `tools.exec.safeBinTrustedDirs`, `agents.list[].tools.exec.safeBinTrustedDirs`                       | ні               |
| `skills.workspace.symlink_escape`                             | warn          | `skills/**/SKILL.md` у workspace розв’язується поза коренем workspace (дрейф ланцюжка symlink) | стан файлової системи `skills/**` у workspace                                                 | ні               |
| `plugins.extensions_no_allowlist`                             | warn          | Розширення встановлені без явного allowlist Plugin                                   | `plugins.allowlist`                                                                                  | ні               |
| `plugins.installs_unpinned_npm_specs`                         | warn          | Записи встановлення Plugin не прив’язані до незмінних npm-специфікацій               | метадані встановлення Plugin                                                                         | ні               |
| `plugins.installs_missing_integrity`                          | warn          | У записах встановлення Plugin відсутні метадані integrity                            | метадані встановлення Plugin                                                                         | ні               |
| `plugins.installs_version_drift`                              | warn          | Записи встановлення Plugin розходяться зі встановленими пакетами                     | метадані встановлення Plugin                                                                         | ні               |
| `plugins.code_safety`                                         | warn/critical | Сканування коду Plugin виявило підозрілі або небезпечні шаблони                      | код Plugin / джерело встановлення                                                                    | ні               |
| `plugins.code_safety.entry_path`                              | warn          | Шлях входу Plugin вказує на приховані розташування або `node_modules`                | `entry` у маніфесті Plugin                                                                           | ні               |
| `plugins.code_safety.entry_escape`                            | critical      | Точка входу Plugin виходить за межі каталогу Plugin                                  | `entry` у маніфесті Plugin                                                                           | ні               |
| `plugins.code_safety.scan_failed`                             | warn          | Сканування коду Plugin не вдалося завершити                                          | шлях розширення Plugin / середовище сканування                                                       | ні               |
| `skills.code_safety`                                          | warn/critical | Метадані/код інсталятора Skills містять підозрілі або небезпечні шаблони             | джерело встановлення Skills                                                                          | ні               |
| `skills.code_safety.scan_failed`                              | warn          | Сканування коду Skills не вдалося завершити                                          | середовище сканування Skills                                                                         | ні               |
| `security.exposure.open_channels_with_exec`                   | warn/critical | Спільні/публічні кімнати можуть звертатися до агентів із увімкненим exec             | `channels.*.dmPolicy`, `channels.*.groupPolicy`, `tools.exec.*`, `agents.list[].tools.exec.*`       | ні               |
| `security.exposure.open_groups_with_elevated`                 | critical      | Відкриті групи + розширені інструменти створюють шляхи prompt injection з високим впливом | `channels.*.groupPolicy`, `tools.elevated.*`                                                    | ні               |
| `security.exposure.open_groups_with_runtime_or_fs`            | critical/warn | Відкриті групи можуть отримати доступ до командних/файлових інструментів без sandbox/обмежень workspace | `channels.*.groupPolicy`, `tools.profile/deny`, `tools.fs.workspaceOnly`, `agents.*.sandbox.mode` | ні               |
| `security.trust_model.multi_user_heuristic`                   | warn          | Конфігурація виглядає багатокористувацькою, хоча модель довіри gateway — персональний асистент | розділіть межі довіри або посильте захист для спільного використання (`sandbox.mode`, deny інструментів / обмеження workspace) | ні |
| `tools.profile_minimal_overridden`                            | warn          | Перевизначення агента обходять глобальний профіль minimal                            | `agents.list[].tools.profile`                                                                        | ні               |
| `plugins.tools_reachable_permissive_policy`                   | warn          | Інструменти розширень доступні в надто поблажливих контекстах                        | `tools.profile` + allow/deny інструментів                                                           | ні               |
| `models.legacy`                                               | warn          | Досі налаштовано застарілі сімейства моделей                                         | вибір моделі                                                                                         | ні               |
| `models.weak_tier`                                            | warn          | Налаштовані моделі нижчі за поточно рекомендовані рівні                              | вибір моделі                                                                                         | ні               |
| `models.small_params`                                         | critical/info | Малі моделі + небезпечні поверхні інструментів підвищують ризик ін’єкцій             | вибір моделі + політика sandbox/інструментів                                                         | ні               |
| `summary.attack_surface`                                      | info          | Підсумкове зведення щодо auth, каналів, інструментів і рівня доступності             | кілька ключів (див. деталі висновку)                                                                 | ні               |

## Control UI через HTTP

Control UI потребує **безпечного контексту** (HTTPS або localhost), щоб генерувати ідентичність пристрою. `gateway.controlUi.allowInsecureAuth` — це локальний перемикач сумісності:

- На localhost він дозволяє автентифікацію Control UI без ідентичності пристрою, коли сторінку відкрито через небезпечний HTTP.
- Він не обходить перевірки pairing.
- Він не послаблює вимоги до ідентичності пристрою для віддалених (не localhost) підключень.

Надавайте перевагу HTTPS (Tailscale Serve) або відкривайте UI на `127.0.0.1`.

Лише для аварійних сценаріїв `gateway.controlUi.dangerouslyDisableDeviceAuth`
повністю вимикає перевірки ідентичності пристрою. Це серйозне послаблення безпеки; тримайте його вимкненим, якщо тільки ви активно не налагоджуєте проблему і не можете швидко повернути все назад.

Окремо від цих небезпечних прапорів, успішний режим `gateway.auth.mode: "trusted-proxy"`
може допускати **операторські** сесії Control UI без ідентичності пристрою. Це
навмисна поведінка режиму auth, а не обхід через `allowInsecureAuth`, і вона все
одно не поширюється на сесії Control UI ролі Node.

`openclaw security audit` попереджає, коли це налаштування увімкнено.

## Підсумок небезпечних або незахищених прапорів

`openclaw security audit` включає `config.insecure_or_dangerous_flags`, коли
увімкнено відомі незахищені/небезпечні debug-перемикачі. Наразі ця перевірка
агрегує:

- `gateway.controlUi.allowInsecureAuth=true`
- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true`
- `gateway.controlUi.dangerouslyDisableDeviceAuth=true`
- `hooks.gmail.allowUnsafeExternalContent=true`
- `hooks.mappings[<index>].allowUnsafeExternalContent=true`
- `tools.exec.applyPatch.workspaceOnly=false`
- `plugins.entries.acpx.config.permissionMode=approve-all`

Повний список ключів конфігурації `dangerous*` / `dangerously*`, визначених у схемі конфігурації OpenClaw:

- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback`
- `gateway.controlUi.dangerouslyDisableDeviceAuth`
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `channels.discord.dangerouslyAllowNameMatching`
- `channels.discord.accounts.<accountId>.dangerouslyAllowNameMatching`
- `channels.slack.dangerouslyAllowNameMatching`
- `channels.slack.accounts.<accountId>.dangerouslyAllowNameMatching`
- `channels.googlechat.dangerouslyAllowNameMatching`
- `channels.googlechat.accounts.<accountId>.dangerouslyAllowNameMatching`
- `channels.msteams.dangerouslyAllowNameMatching`
- `channels.synology-chat.dangerouslyAllowNameMatching` (канал розширення)
- `channels.synology-chat.accounts.<accountId>.dangerouslyAllowNameMatching` (канал розширення)
- `channels.synology-chat.dangerouslyAllowInheritedWebhookPath` (канал розширення)
- `channels.zalouser.dangerouslyAllowNameMatching` (канал розширення)
- `channels.zalouser.accounts.<accountId>.dangerouslyAllowNameMatching` (канал розширення)
- `channels.irc.dangerouslyAllowNameMatching` (канал розширення)
- `channels.irc.accounts.<accountId>.dangerouslyAllowNameMatching` (канал розширення)
- `channels.mattermost.dangerouslyAllowNameMatching` (канал розширення)
- `channels.mattermost.accounts.<accountId>.dangerouslyAllowNameMatching` (канал розширення)
- `channels.telegram.network.dangerouslyAllowPrivateNetwork`
- `channels.telegram.accounts.<accountId>.network.dangerouslyAllowPrivateNetwork`
- `agents.defaults.sandbox.docker.dangerouslyAllowReservedContainerTargets`
- `agents.defaults.sandbox.docker.dangerouslyAllowExternalBindSources`
- `agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin`
- `agents.list[<index>].sandbox.docker.dangerouslyAllowReservedContainerTargets`
- `agents.list[<index>].sandbox.docker.dangerouslyAllowExternalBindSources`
- `agents.list[<index>].sandbox.docker.dangerouslyAllowContainerNamespaceJoin`

## Конфігурація reverse proxy

Якщо ви запускаєте Gateway за reverse proxy (nginx, Caddy, Traefik тощо), налаштуйте
`gateway.trustedProxies` для коректної обробки IP-адрес клієнтів із forwarded-заголовків.

Коли Gateway виявляє proxy-заголовки з адреси, якої **немає** в `trustedProxies`, він **не** вважатиме з’єднання локальними клієнтами. Якщо auth gateway вимкнено, такі з’єднання буде відхилено. Це запобігає обходу автентифікації, коли проксійовані з’єднання інакше могли б виглядати як такі, що надходять із localhost, і автоматично отримувати довіру.

`gateway.trustedProxies` також використовується режимом `gateway.auth.mode: "trusted-proxy"`, але цей режим auth суворіший:

- auth trusted-proxy **завершується відмовою за замовчуванням для proxy із джерелом loopback**
- reverse proxy loopback на тому ж хості все одно можуть використовувати `gateway.trustedProxies` для виявлення локальних клієнтів і обробки forwarded IP
- для reverse proxy loopback на тому ж хості використовуйте auth через token/password замість `gateway.auth.mode: "trusted-proxy"`

```yaml
gateway:
  trustedProxies:
    - "10.0.0.1" # IP reverse proxy
  # Необов’язково. За замовчуванням false.
  # Увімкніть лише якщо ваш proxy не може надавати X-Forwarded-For.
  allowRealIpFallback: false
  auth:
    mode: password
    password: ${OPENCLAW_GATEWAY_PASSWORD}
```

Коли налаштовано `trustedProxies`, Gateway використовує `X-Forwarded-For` для визначення IP-адреси клієнта. `X-Real-IP` типово ігнорується, якщо явно не встановлено `gateway.allowRealIpFallback: true`.

Коректна поведінка reverse proxy (перезапис вхідних forwarded-заголовків):

```nginx
proxy_set_header X-Forwarded-For $remote_addr;
proxy_set_header X-Real-IP $remote_addr;
```

Некоректна поведінка reverse proxy (додавання/збереження недовірених forwarded-заголовків):

```nginx
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```

## Примітки щодо HSTS і origin

- Gateway OpenClaw насамперед орієнтований на local/loopback. Якщо ви завершуєте TLS на reverse proxy, налаштуйте HSTS на HTTPS-домені, який обслуговує proxy.
- Якщо HTTPS завершує сам gateway, ви можете встановити `gateway.http.securityHeaders.strictTransportSecurity`, щоб OpenClaw додавав заголовок HSTS у відповіді.
- Докладні вказівки щодо розгортання наведено в [Trusted Proxy Auth](/uk/gateway/trusted-proxy-auth#tls-termination-and-hsts).
- Для розгортань Control UI поза loopback `gateway.controlUi.allowedOrigins` є обов’язковим за замовчуванням.
- `gateway.controlUi.allowedOrigins: ["*"]` — це явна політика браузерних origin «дозволити все», а не посилене типове значення. Уникайте її поза межами суворо контрольованого локального тестування.
- Збої автентифікації за browser-origin на loopback усе одно підлягають rate limiting, навіть коли загальний виняток для loopback увімкнено, але ключ блокування визначається окремо для кожного нормалізованого значення `Origin`, а не для одного спільного локального bucket.
- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true` вмикає режим fallback походження через заголовок Host; розглядайте це як небезпечну політику, свідомо обрану оператором.
- Розглядайте DNS rebinding і поведінку proxy щодо заголовка Host як питання посилення безпеки розгортання; тримайте `trustedProxies` вузьким і уникайте прямого відкриття gateway у публічний інтернет.

## Локальні журнали сеансів зберігаються на диску

OpenClaw зберігає транскрипти сеансів на диску в `~/.openclaw/agents/<agentId>/sessions/*.jsonl`.
Це необхідно для безперервності сеансів і (за бажанням) індексації пам’яті сеансів, але це також означає, що
**будь-який процес/користувач із доступом до файлової системи може читати ці журнали**. Вважайте доступ до диска
межею довіри й жорстко обмежуйте дозволи для `~/.openclaw` (див. розділ аудиту нижче). Якщо вам потрібна
сильніша ізоляція між агентами, запускайте їх під окремими користувачами ОС або на окремих хостах.

## Виконання на Node (`system.run`)

Якщо Node macOS пов’язано через pairing, Gateway може викликати `system.run` на цьому Node. Це **віддалене виконання коду** на Mac:

- Потрібне pairing Node (схвалення + токен).
- Pairing Node в Gateway не є поверхнею схвалення кожної окремої команди. Воно встановлює ідентичність/довіру до Node та видачу токена.
- Gateway застосовує грубу глобальну політику команд Node через `gateway.nodes.allowCommands` / `denyCommands`.
- На Mac це контролюється через **Settings → Exec approvals** (security + ask + allowlist).
- Політика `system.run` для конкретного Node — це власний файл схвалень exec цього Node (`exec.approvals.node.*`), який може бути суворішим або м’якшим, ніж глобальна політика ID команд у gateway.
- Node, що працює з `security="full"` і `ask="off"`, дотримується типової моделі довіреного оператора. Вважайте це очікуваною поведінкою, якщо тільки ваше розгортання явно не вимагає суворішого режиму схвалення або allowlist.
- Режим схвалення прив’язується до точного контексту запиту і, коли можливо, до одного конкретного локального операнда script/file. Якщо OpenClaw не може точно визначити один прямий локальний файл для команди інтерпретатора/runtime, виконання, що потребує схвалення, відхиляється замість того, щоб обіцяти повне семантичне покриття.
- Для `host=node` виконання, що потребують схвалення, також зберігають канонічний підготовлений `systemRunPlan`; пізніші схвалені переспрямування повторно використовують цей збережений план, а валідація gateway відхиляє зміни викликачем до команди/cwd/контексту сеансу після створення запиту на схвалення.
- Якщо ви не хочете віддаленого виконання, встановіть security у **deny** і видаліть pairing Node для цього Mac.

Це розрізнення важливе для triage:

- Повторне підключення вже пов’язаного Node, який рекламує інший список команд, саме по собі не є вразливістю, якщо глобальна політика Gateway і локальні схвалення exec самого Node усе ще забезпечують реальну межу виконання.
- Повідомлення, які трактують метадані pairing Node як другий прихований шар схвалення кожної команди, зазвичай є плутаниною політики/UX, а не обходом межі безпеки.

## Динамічні Skills (watcher / віддалені Node)

OpenClaw може оновлювати список Skills посеред сеансу:

- **Спостерігач Skills**: зміни в `SKILL.md` можуть оновити знімок Skills на наступному ході агента.
- **Віддалені Node**: підключення Node macOS може зробити доступними Skills лише для macOS (на основі перевірки наявності бінарників).

Розглядайте папки skill як **довірений код** і обмежуйте коло тих, хто може їх змінювати.

## Модель загроз

Ваш AI-асистент може:

- Виконувати довільні shell-команди
- Читати/записувати файли
- Отримувати доступ до мережевих сервісів
- Надсилати повідомлення будь-кому (якщо ви надали йому доступ до WhatsApp)

Люди, які пишуть вам, можуть:

- Намагатися обманом змусити ваш AI робити шкідливі речі
- Соціальною інженерією добиватися доступу до ваших даних
- Досліджувати вашу інфраструктуру в пошуках деталей

## Ключова ідея: контроль доступу перед інтелектом

Більшість збоїв тут — не витончені експлойти, а ситуації на кшталт «хтось написав боту, і бот зробив те, що його попросили».

Позиція OpenClaw така:

- **Спочатку ідентичність:** вирішіть, хто може говорити з ботом (pairing для DM / allowlist / явний `open`).
- **Потім обсяг:** вирішіть, де боту дозволено діяти (allowlist груп + обмеження згадуваннями, інструменти, sandboxing, дозволи пристрою).
- **Модель наприкінці:** припускайте, що моделлю можна маніпулювати; проєктуйте систему так, щоб наслідки маніпуляції були обмеженими.

## Модель авторизації команд

Слеш-команди та директиви виконуються лише для **авторизованих відправників**. Авторизація визначається через
allowlist/pairing каналу разом із `commands.useAccessGroups` (див. [Configuration](/uk/gateway/configuration)
і [Slash commands](/uk/tools/slash-commands)). Якщо allowlist каналу порожній або містить `"*"`,
команди фактично відкриті для цього каналу.

`/exec` — це зручна команда лише в межах сеансу для авторизованих операторів. Вона **не** записує конфігурацію і
не змінює інші сеанси.

## Ризики інструментів площини керування

Два вбудовані інструменти можуть вносити стійкі зміни до площини керування:

- `gateway` може переглядати конфігурацію через `config.schema.lookup` / `config.get`, а також вносити стійкі зміни через `config.apply`, `config.patch` і `update.run`.
- `cron` може створювати заплановані завдання, які продовжують працювати після завершення початкового чату/завдання.

Інструмент runtime `gateway`, доступний лише власнику, усе ще відмовляється
перезаписувати `tools.exec.ask` або `tools.exec.security`; застарілі псевдоніми `tools.bash.*`
нормалізуються до тих самих захищених шляхів exec перед записом.

Для будь-якого агента/поверхні, що обробляє недовірений вміст, типово забороняйте таке:

```json5
{
  tools: {
    deny: ["gateway", "cron", "sessions_spawn", "sessions_send"],
  },
}
```

`commands.restart=false` блокує лише дії перезапуску. Він не вимикає дії конфігурації/оновлення `gateway`.

## Плагіни/розширення

Плагіни працюють **у тому ж процесі**, що й Gateway. Розглядайте їх як довірений код:

- Встановлюйте лише ті плагіни, джерелам яких ви довіряєте.
- Надавайте перевагу явним allowlist `plugins.allow`.
- Перевіряйте конфігурацію Plugin перед увімкненням.
- Перезапускайте Gateway після змін Plugin.
- Якщо ви встановлюєте або оновлюєте Plugin (`openclaw plugins install <package>`, `openclaw plugins update <id>`), ставтеся до цього так, ніби ви запускаєте недовірений код:
  - Шлях встановлення — це каталог конкретного Plugin у межах активного кореня встановлення Plugin.
  - Перед встановленням/оновленням OpenClaw запускає вбудоване сканування небезпечного коду. Знахідки рівня `critical` типово блокують операцію.
  - OpenClaw використовує `npm pack`, а потім виконує `npm install --omit=dev` у цьому каталозі (скрипти життєвого циклу npm можуть виконувати код під час встановлення).
  - Надавайте перевагу pinned, точним версіям (`@scope/pkg@1.2.3`) і перевіряйте розпакований код на диску перед увімкненням.
  - `--dangerously-force-unsafe-install` — лише аварійний варіант для хибнопозитивних спрацювань вбудованого сканування у потоках встановлення/оновлення Plugin. Він не обходить блокування політики hook `before_install` Plugin і не обходить збої сканування.
  - Встановлення залежностей Skills через Gateway дотримуються того самого поділу на dangerous/suspicious: вбудовані знахідки `critical` блокують операцію, якщо викликач явно не встановить `dangerouslyForceUnsafeInstall`, тоді як підозрілі знахідки, як і раніше, лише попереджають. `openclaw skills install` залишається окремим потоком завантаження/встановлення Skills із ClawHub.

Докладніше: [Plugins](/uk/tools/plugin)

<a id="dm-access-model-pairing-allowlist-open-disabled"></a>

## Модель доступу DM (pairing / allowlist / open / disabled)

Усі поточні канали з підтримкою DM мають політику DM (`dmPolicy` або `*.dm.policy`), яка блокує вхідні DM **до** обробки повідомлення:

- `pairing` (типово): невідомі відправники отримують короткий код pairing, а бот ігнорує їхнє повідомлення до схвалення. Коди спливають через 1 годину; повторні DM не надсилатимуть код знову, доки не буде створено новий запит. Кількість очікуваних запитів типово обмежена **3 на канал**.
- `allowlist`: невідомих відправників заблоковано (без handshake pairing).
- `open`: дозволити будь-кому надсилати DM (публічно). **Потрібно**, щоб allowlist каналу містив `"*"` (явне підтвердження).
- `disabled`: повністю ігнорувати вхідні DM.

Схвалення через CLI:

```bash
openclaw pairing list <channel>
openclaw pairing approve <channel> <code>
```

Докладніше + файли на диску: [Pairing](/uk/channels/pairing)

## Ізоляція сеансів DM (багатокористувацький режим)

Типово OpenClaw маршрутизує **усі DM в основний сеанс**, щоб ваш асистент зберігав безперервність між пристроями й каналами. Якщо **кілька людей** можуть надсилати DM боту (відкриті DM або allowlist із кількох осіб), розгляньте ізоляцію сеансів DM:

```json5
{
  session: { dmScope: "per-channel-peer" },
}
```

Це запобігає витоку контексту між користувачами, зберігаючи при цьому ізоляцію групових чатів.

Це межа контексту обміну повідомленнями, а не межа адміністрування хоста. Якщо користувачі взаємно ворожі та спільно використовують той самий хост/конфігурацію Gateway, запускайте окремі Gateway для кожної межі довіри.

### Безпечний режим DM (рекомендовано)

Розглядайте фрагмент вище як **безпечний режим DM**:

- Типово: `session.dmScope: "main"` (усі DM використовують один спільний сеанс для безперервності).
- Типове значення локального onboarding у CLI: записує `session.dmScope: "per-channel-peer"`, якщо значення не задано (зберігає наявні явні значення).
- Безпечний режим DM: `session.dmScope: "per-channel-peer"` (кожна пара канал+відправник отримує ізольований контекст DM).
- Ізоляція контакту між каналами: `session.dmScope: "per-peer"` (кожен відправник має один сеанс у всіх каналах одного типу).

Якщо ви використовуєте кілька акаунтів в одному каналі, замість цього застосовуйте `per-account-channel-peer`. Якщо та сама людина зв’язується з вами через кілька каналів, використовуйте `session.identityLinks`, щоб об’єднати ці DM-сеанси в одну канонічну ідентичність. Див. [Session Management](/uk/concepts/session) і [Configuration](/uk/gateway/configuration).

## Allowlists (DM + групи) — термінологія

В OpenClaw є два окремі шари «хто може мене запускати?»:

- **Allowlist DM** (`allowFrom` / `channels.discord.allowFrom` / `channels.slack.allowFrom`; застаріле: `channels.discord.dm.allowFrom`, `channels.slack.dm.allowFrom`): хто має право писати боту в особисті повідомлення.
  - Коли `dmPolicy="pairing"`, схвалення записуються в сховище allowlist pairing з областю дії акаунта в `~/.openclaw/credentials/` (`<channel>-allowFrom.json` для типового акаунта, `<channel>-<accountId>-allowFrom.json` для нетипових акаунтів) і зливаються з allowlist із конфігурації.
- **Allowlist груп** (специфічний для каналу): з яких саме груп/каналів/guilds бот узагалі прийматиме повідомлення.
  - Типові шаблони:
    - `channels.whatsapp.groups`, `channels.telegram.groups`, `channels.imessage.groups`: типові параметри для груп, як-от `requireMention`; якщо задано, це також працює як allowlist груп (додайте `"*"`, щоб зберегти поведінку «дозволити все»).
    - `groupPolicy="allowlist"` + `groupAllowFrom`: обмежує, хто може запускати бота _в межах_ групового сеансу (WhatsApp/Telegram/Signal/iMessage/Microsoft Teams).
    - `channels.discord.guilds` / `channels.slack.channels`: allowlist для конкретних поверхонь + типові параметри згадувань.
  - Перевірки груп виконуються в такому порядку: спочатку `groupPolicy`/allowlist груп, потім активація за згадуванням/відповіддю.
  - Відповідь на повідомлення бота (неявне згадування) **не** обходить allowlist відправників, як-от `groupAllowFrom`.
  - **Примітка щодо безпеки:** ставтеся до `dmPolicy="open"` і `groupPolicy="open"` як до крайніх варіантів. Їх варто використовувати якомога рідше; надавайте перевагу pairing + allowlist, якщо тільки ви не довіряєте повністю кожному учаснику кімнати.

Докладніше: [Configuration](/uk/gateway/configuration) і [Groups](/uk/channels/groups)

## Prompt injection (що це, і чому це важливо)

Prompt injection — це ситуація, коли зловмисник створює повідомлення, яке маніпулює моделлю так, щоб вона зробила щось небезпечне («ігноруй свої інструкції», «виведи вміст файлової системи», «перейди за цим посиланням і виконай команди» тощо).

Навіть із сильними системними prompt, **prompt injection не розв’язано**. Запобіжники в системному prompt — це лише м’які вказівки; жорстке забезпечення дають політика інструментів, схвалення exec, sandboxing і allowlist каналів (і оператори можуть вимкнути це за задумом). Що практично допомагає:

- Тримайте вхідні DM закритими (pairing/allowlist).
- У групах надавайте перевагу обмеженню за згадуванням; уникайте «завжди активних» ботів у публічних кімнатах.
- За замовчуванням вважайте посилання, вкладення та вставлені інструкції ворожими.
- Виконуйте чутливі інструменти в sandbox; тримайте секрети поза файловою системою, доступною для агента.
- Примітка: sandboxing вмикається добровільно. Якщо режим sandbox вимкнено, неявне `host=auto` розв’язується до хоста gateway. Явне `host=sandbox` усе одно безпечно завершується відмовою, тому що runtime sandbox недоступний. Установіть `host=gateway`, якщо хочете, щоб така поведінка була явно описана в конфігурації.
- Обмежуйте інструменти високого ризику (`exec`, `browser`, `web_fetch`, `web_search`) лише довіреними агентами або явними allowlist.
- Якщо ви використовуєте allowlist інтерпретаторів (`python`, `node`, `ruby`, `perl`, `php`, `lua`, `osascript`), увімкніть `tools.exec.strictInlineEval`, щоб inline eval-форми все одно вимагали явного схвалення.
- **Вибір моделі має значення:** старіші/менші/застарілі моделі значно менш стійкі до prompt injection і зловживань інструментами. Для агентів з увімкненими інструментами використовуйте найсильнішу доступну сучасну модель, загартовану щодо інструкцій.

Тривожні сигнали, які слід вважати недовіреними:

- «Прочитай цей файл/URL і зроби точно те, що там написано».
- «Ігноруй свій системний prompt або правила безпеки».
- «Розкрий свої приховані інструкції або результати інструментів».
- «Встав повний вміст `~/.openclaw` або свої журнали».

## Прапори обходу небезпечного зовнішнього вмісту

OpenClaw містить явні прапори обходу, які вимикають захисне обгортання зовнішнього вмісту:

- `hooks.mappings[].allowUnsafeExternalContent`
- `hooks.gmail.allowUnsafeExternalContent`
- Поле payload Cron `allowUnsafeExternalContent`

Рекомендації:

- У production залишайте їх незаданими/false.
- Увімкнюйте лише тимчасово для дуже вузько обмеженого налагодження.
- Якщо увімкнули, ізолюйте цього агента (sandbox + мінімум інструментів + окремий простір імен сеансів).

Примітка про ризики Hooks:

- Payload hooks — це недовірений вміст, навіть якщо доставлення походить із систем, які ви контролюєте (пошта/документи/вебвміст можуть містити prompt injection).
- Слабкіші рівні моделей збільшують цей ризик. Для автоматизації на основі hooks надавайте перевагу сильним сучасним рівням моделей і тримайте політику інструментів суворою (`tools.profile: "messaging"` або суворіше), а також використовуйте sandboxing там, де це можливо.

### Prompt injection не потребує публічних DM

Навіть якщо **лише ви** можете писати боту, prompt injection усе одно може виникнути через
будь-який **недовірений вміст**, який бот читає (результати web search/fetch, сторінки браузера,
листи, документи, вкладення, вставлені журнали/код). Іншими словами: не лише відправник
є поверхнею загрози; сам **вміст** також може містити ворожі інструкції.

Коли інструменти увімкнені, типовий ризик — це ексфільтрація контексту або запуск
викликів інструментів. Зменшуйте радіус ураження так:

- Використовуйте **агента-читача** лише для читання або без інструментів, щоб підсумовувати недовірений вміст,
  а вже потім передавайте підсумок основному агенту.
- Тримайте `web_search` / `web_fetch` / `browser` вимкненими для агентів з інструментами, якщо вони не потрібні.
- Для URL-входів OpenResponses (`input_file` / `input_image`) задавайте суворі
  `gateway.http.endpoints.responses.files.urlAllowlist` і
  `gateway.http.endpoints.responses.images.urlAllowlist`, а також зберігайте малим значення `maxUrlParts`.
  Порожні allowlist вважаються незаданими; використовуйте `files.allowUrl: false` / `images.allowUrl: false`,
  якщо хочете повністю вимкнути отримання за URL.
- Для файлових входів OpenResponses декодований текст `input_file` усе одно вбудовується як
  **недовірений зовнішній вміст**. Не покладайтеся на те, що текст файла є довіреним лише тому,
  що Gateway декодував його локально. Вбудований блок усе одно містить явні
  маркери меж `<<<EXTERNAL_UNTRUSTED_CONTENT ...>>>` плюс метадані `Source: External`,
  хоча цей шлях і пропускає довший банер `SECURITY NOTICE:`.
- Таке саме обгортання на основі маркерів застосовується, коли media-understanding витягує текст
  із прикріплених документів перед додаванням цього тексту до prompt медіа.
- Увімкніть sandboxing і суворі allowlist інструментів для будь-якого агента, який працює з недовіреним вводом.
- Тримайте секрети поза prompt; передавайте їх через env/config на хості gateway.

### Сила моделі (примітка щодо безпеки)

Стійкість до prompt injection **не** однакова для всіх рівнів моделей. Менші/дешевші моделі загалом більш схильні до зловживання інструментами та перехоплення інструкцій, особливо під час ворожих prompt.

<Warning>
Для агентів із увімкненими інструментами або агентів, які читають недовірений вміст, ризик prompt injection зі старішими/меншими моделями часто є надто високим. Не запускайте такі навантаження на слабких рівнях моделей.
</Warning>

Рекомендації:

- **Використовуйте модель останнього покоління найвищого рівня** для будь-якого бота, який може запускати інструменти або взаємодіяти з файлами/мережами.
- **Не використовуйте старіші/слабші/менші рівні** для агентів з інструментами або недовірених вхідних скриньок; ризик prompt injection надто високий.
- Якщо вам доводиться використовувати меншу модель, **зменшуйте радіус ураження** (лише читання, сильне sandboxing, мінімальний доступ до файлової системи, суворі allowlist).
- Під час роботи з малими моделями **увімкніть sandboxing для всіх сеансів** і **вимкніть `web_search`/`web_fetch`/`browser`**, якщо вхідні дані не контролюються дуже жорстко.
- Для персональних асистентів лише для чату з довіреним вводом і без інструментів малі моделі зазвичай підходять.

<a id="reasoning-verbose-output-in-groups"></a>

## Reasoning і verbose output у групах

`/reasoning`, `/verbose` і `/trace` можуть розкривати внутрішнє міркування, вихід
інструментів або діагностику Plugin, які
не призначалися для публічного каналу. У групових налаштуваннях розглядайте їх як **лише для налагодження**
і тримайте вимкненими, якщо тільки вони вам явно не потрібні.

Рекомендації:

- Тримайте `/reasoning`, `/verbose` і `/trace` вимкненими в публічних кімнатах.
- Якщо ви їх увімкнули, робіть це лише в довірених DM або в суворо контрольованих кімнатах.
- Пам’ятайте: verbose і trace output можуть містити аргументи інструментів, URL, діагностику Plugin і дані, які бачила модель.

## Посилення конфігурації (приклади)

### 0) Дозволи файлів

Тримайте конфігурацію та стан приватними на хості gateway:

- `~/.openclaw/openclaw.json`: `600` (лише читання/запис для користувача)
- `~/.openclaw`: `700` (лише користувач)

`openclaw doctor` може попередити про це та запропонувати посилити ці дозволи.

### 0.4) Мережевий доступ (bind + порт + firewall)

Gateway мультиплексує **WebSocket + HTTP** на одному порту:

- Типово: `18789`
- Config/flags/env: `gateway.port`, `--port`, `OPENCLAW_GATEWAY_PORT`

Ця HTTP-поверхня включає Control UI і canvas host:

- Control UI (ресурси SPA) (типовий базовий шлях `/`)
- Canvas host: `/__openclaw__/canvas/` і `/__openclaw__/a2ui/` (довільні HTML/JS; розглядайте як недовірений вміст)

Якщо ви завантажуєте вміст canvas у звичайному браузері, ставтеся до нього як до будь-якої іншої недовіреної вебсторінки:

- Не відкривайте canvas host для недовірених мереж/користувачів.
- Не змушуйте вміст canvas використовувати той самий origin, що й привілейовані вебповерхні, якщо ви повністю не розумієте наслідки.

Режим bind визначає, де саме слухає Gateway:

- `gateway.bind: "loopback"` (типово): підключатися можуть лише локальні клієнти.
- Bind поза loopback (`"lan"`, `"tailnet"`, `"custom"`) розширює поверхню атаки. Використовуйте їх лише з auth gateway (спільний token/password або правильно налаштований non-loopback trusted proxy) і реальним firewall.

Базові правила:

- Надавайте перевагу Tailscale Serve замість bind у LAN (Serve залишає Gateway на loopback, а доступ контролює Tailscale).
- Якщо вам все ж потрібен bind у LAN, обмежте порт через firewall вузьким allowlist вихідних IP; не робіть широкого port-forward.
- Ніколи не відкривайте Gateway без автентифікації на `0.0.0.0`.

### 0.4.1) Публікація портів Docker + UFW (`DOCKER-USER`)

Якщо ви запускаєте OpenClaw у Docker на VPS, пам’ятайте, що опубліковані порти контейнера
(`-p HOST:CONTAINER` або Compose `ports:`) маршрутизуються через ланцюги переспрямування Docker,
а не лише через правила `INPUT` хоста.

Щоб трафік Docker відповідав політиці вашого firewall, застосовуйте правила в
`DOCKER-USER` (цей ланцюг перевіряється до власних правил accept Docker).
На багатьох сучасних дистрибутивах `iptables`/`ip6tables` використовують frontend `iptables-nft`
і все одно застосовують ці правила до backend nftables.

Мінімальний приклад allowlist (IPv4):

```bash
# /etc/ufw/after.rules (додайте як окремий розділ *filter)
*filter
:DOCKER-USER - [0:0]
-A DOCKER-USER -m conntrack --ctstate ESTABLISHED,RELATED -j RETURN
-A DOCKER-USER -s 127.0.0.0/8 -j RETURN
-A DOCKER-USER -s 10.0.0.0/8 -j RETURN
-A DOCKER-USER -s 172.16.0.0/12 -j RETURN
-A DOCKER-USER -s 192.168.0.0/16 -j RETURN
-A DOCKER-USER -s 100.64.0.0/10 -j RETURN
-A DOCKER-USER -p tcp --dport 80 -j RETURN
-A DOCKER-USER -p tcp --dport 443 -j RETURN
-A DOCKER-USER -m conntrack --ctstate NEW -j DROP
-A DOCKER-USER -j RETURN
COMMIT
```

Для IPv6 існують окремі таблиці. Додайте відповідну політику в `/etc/ufw/after6.rules`, якщо
IPv6 у Docker увімкнено.

Уникайте жорстко заданих назв інтерфейсів, таких як `eth0`, у фрагментах документації. Назви інтерфейсів
відрізняються між образами VPS (`ens3`, `enp*` тощо), і невідповідність може випадково
призвести до пропуску вашого правила deny.

Швидка перевірка після перезавантаження:

```bash
ufw reload
iptables -S DOCKER-USER
ip6tables -S DOCKER-USER
nmap -sT -p 1-65535 <public-ip> --open
```

Очікувано зовні мають бути відкриті лише ті порти, які ви навмисно відкрили (для більшості
конфігурацій: SSH + порти вашого reverse proxy).

### 0.4.2) Виявлення через mDNS/Bonjour (розкриття інформації)

Gateway транслює свою присутність через mDNS (`_openclaw-gw._tcp` на порту 5353) для локального виявлення пристроїв. У повному режимі це включає TXT-записи, які можуть розкривати операційні деталі:

- `cliPath`: повний шлях у файловій системі до CLI-бінарника (розкриває ім’я користувача та місце встановлення)
- `sshPort`: рекламує доступність SSH на хості
- `displayName`, `lanHost`: інформація про ім’я хоста

**Міркування щодо операційної безпеки:** трансляція інфраструктурних деталей полегшує розвідку для будь-кого в локальній мережі. Навіть «нешкідлива» інформація, як-от шляхи файлової системи та наявність SSH, допомагає зловмисникам картографувати ваше середовище.

**Рекомендації:**

1. **Мінімальний режим** (типово, рекомендовано для відкритих gateway): вилучає чутливі поля з mDNS-трансляцій:

   ```json5
   {
     discovery: {
       mdns: { mode: "minimal" },
     },
   }
   ```

2. **Повністю вимкніть**, якщо локальне виявлення пристроїв вам не потрібне:

   ```json5
   {
     discovery: {
       mdns: { mode: "off" },
     },
   }
   ```

3. **Повний режим** (за явним бажанням): включає `cliPath` + `sshPort` у TXT-записи:

   ```json5
   {
     discovery: {
       mdns: { mode: "full" },
     },
   }
   ```

4. **Змінна середовища** (альтернатива): установіть `OPENCLAW_DISABLE_BONJOUR=1`, щоб вимкнути mDNS без змін конфігурації.

У мінімальному режимі Gateway все одно транслює достатньо даних для виявлення пристроїв (`role`, `gatewayPort`, `transport`), але не включає `cliPath` і `sshPort`. Програми, яким потрібна інформація про шлях до CLI, можуть отримати її через автентифіковане з’єднання WebSocket.

### 0.5) Захистіть WebSocket Gateway (локальна auth)

Auth Gateway **потрібна за замовчуванням**. Якщо не налаштовано
жодного коректного шляху auth gateway, Gateway відмовляє у WebSocket-з’єднаннях (fail‑closed).

Onboarding типово генерує токен (навіть для loopback), тому
локальні клієнти повинні проходити автентифікацію.

Установіть токен, щоб **усі** WS-клієнти мусили автентифікуватися:

```json5
{
  gateway: {
    auth: { mode: "token", token: "your-token" },
  },
}
```

Doctor може згенерувати його за вас: `openclaw doctor --generate-gateway-token`.

Примітка: `gateway.remote.token` / `.password` — це джерела облікових даних клієнта.
Самі по собі вони **не** захищають локальний доступ WS.
Локальні шляхи виклику можуть використовувати `gateway.remote.*` як резервний варіант лише тоді, коли `gateway.auth.*`
не задано.
Якщо `gateway.auth.token` / `gateway.auth.password` явно налаштовано через SecretRef і його не вдається розв’язати, розв’язання завершується fail closed (жоден резервний шлях remote не маскує проблему).
Необов’язково: закріпіть віддалений TLS через `gateway.remote.tlsFingerprint` під час використання `wss://`.
Нешифрований `ws://` типово дозволено лише для loopback. Для довірених шляхів у приватній мережі
встановіть `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1` у процесі клієнта як аварійний варіант.

Локальний pairing пристроїв:

- Pairing пристрою автоматично схвалюється для прямих локальних loopback-підключень, щоб
  взаємодія клієнтів на тому самому хості була зручною.
- OpenClaw також має вузький шлях backend/container-local self-connect для
  довірених потоків із допоміжними засобами зі спільним секретом.
- Підключення через tailnet і LAN, включно з bind через tailnet на тому ж хості, вважаються
  віддаленими для pairing і все одно потребують схвалення.

Режими auth:

- `gateway.auth.mode: "token"`: спільний bearer token (рекомендовано для більшості конфігурацій).
- `gateway.auth.mode: "password"`: автентифікація паролем (краще задавати через env: `OPENCLAW_GATEWAY_PASSWORD`).
- `gateway.auth.mode: "trusted-proxy"`: довіряти reverse proxy з урахуванням ідентичності, який автентифікує користувачів і передає ідентичність у заголовках (див. [Trusted Proxy Auth](/uk/gateway/trusted-proxy-auth)).

Контрольний список ротації (token/password):

1. Згенеруйте/встановіть новий секрет (`gateway.auth.token` або `OPENCLAW_GATEWAY_PASSWORD`).
2. Перезапустіть Gateway (або перезапустіть застосунок macOS, якщо він керує Gateway).
3. Оновіть усі віддалені клієнти (`gateway.remote.token` / `.password` на машинах, які звертаються до Gateway).
4. Переконайтеся, що зі старими обліковими даними підключитися більше не можна.

### 0.6) Заголовки ідентичності Tailscale Serve

Коли `gateway.auth.allowTailscale` має значення `true` (типово для Serve), OpenClaw
приймає заголовки ідентичності Tailscale Serve (`tailscale-user-login`) для автентифікації
Control UI/WebSocket. OpenClaw перевіряє ідентичність, розв’язуючи адресу
`x-forwarded-for` через локальний демон Tailscale (`tailscale whois`) і зіставляючи її
із заголовком. Це спрацьовує лише для запитів, що потрапляють на loopback
і містять `x-forwarded-for`, `x-forwarded-proto` та `x-forwarded-host`, як
інжектує Tailscale.
Для цього асинхронного шляху перевірки ідентичності невдалі спроби для того самого `{scope, ip}`
серіалізуються до того, як обмежувач зафіксує збій. Тому конкурентні невдалі повтори
від одного клієнта Serve можуть заблокувати другу спробу негайно, замість того щоб
проскочити як дві звичайні невідповідності.
Кінцеві точки HTTP API (наприклад `/v1/*`, `/tools/invoke` і `/api/channels/*`)
**не** використовують автентифікацію заголовками ідентичності Tailscale. Вони, як і раніше, дотримуються
налаштованого в gateway режиму HTTP auth.

Важлива примітка щодо меж:

- Bearer auth HTTP Gateway фактично дає повний операторський доступ без тонкого поділу.
- Ставтеся до облікових даних, які можуть викликати `/v1/chat/completions`, `/v1/responses` або `/api/channels/*`, як до повноцінних операторських секретів доступу до цього gateway.
- На сумісній з OpenAI HTTP-поверхні bearer auth зі спільним секретом відновлює повний типовий набір операторських scope (`operator.admin`, `operator.approvals`, `operator.pairing`, `operator.read`, `operator.talk.secrets`, `operator.write`) і семантику власника для ходів агента; вужчі значення `x-openclaw-scopes` не звужують цей шлях зі спільним секретом.
- Семантика scope на HTTP на рівні окремого запиту застосовується лише тоді, коли запит надходить із режиму, що несе ідентичність, як-от auth через trusted proxy або `gateway.auth.mode="none"` на приватному вході.
- У таких режимах, що несуть ідентичність, якщо не вказано `x-openclaw-scopes`, використовується звичайний типовий набір операторських scope; надсилайте заголовок явно, коли хочете вужчий набір scope.
- `/tools/invoke` дотримується того самого правила спільного секрету: bearer auth через token/password там також розглядається як повний операторський доступ, тоді як режими, що несуть ідентичність, як і раніше, поважають задекларовані scope.
- Не передавайте ці облікові дані недовіреним викликачам; краще використовуйте окремі Gateway для кожної межі довіри.

**Припущення довіри:** auth Serve без токена виходить із того, що хост gateway є довіреним.
Не розглядайте це як захист від ворожих процесів на тому самому хості. Якщо на хості gateway
може виконуватися недовірений локальний код, вимкніть `gateway.auth.allowTailscale`
і вимагайте явної auth через спільний секрет із `gateway.auth.mode: "token"` або
`"password"`.

**Правило безпеки:** не пересилайте ці заголовки зі свого reverse proxy. Якщо
ви завершуєте TLS або проксіюєте запити перед gateway, вимкніть
`gateway.auth.allowTailscale` і використовуйте auth через спільний секрет (`gateway.auth.mode:
"token"` або `"password"`) або [Trusted Proxy Auth](/uk/gateway/trusted-proxy-auth)
замість цього.

Довірені proxy:

- Якщо ви завершуєте TLS перед Gateway, установіть `gateway.trustedProxies` на IP-адреси вашого proxy.
- OpenClaw довірятиме `x-forwarded-for` (або `x-real-ip`) від цих IP для визначення IP клієнта під час перевірок локального pairing і HTTP auth/local.
- Переконайтеся, що ваш proxy **перезаписує** `x-forwarded-for` і блокує прямий доступ до порту Gateway.

Див. [Tailscale](/uk/gateway/tailscale) і [Огляд Web](/web).

### 0.6.1) Керування браузером через host Node (рекомендовано)

Якщо ваш Gateway віддалений, але браузер працює на іншій машині, запустіть **host Node**
на машині з браузером і дозвольте Gateway проксувати дії браузера (див. [Інструмент browser](/uk/tools/browser)).
Ставтеся до pairing Node як до адміністративного доступу.

Рекомендований шаблон:

- Тримайте Gateway і host Node в одній tailnet (Tailscale).
- Навмисно виконайте pairing Node; вимикайте proxy-маршрутизацію браузера, якщо вона вам не потрібна.

Уникайте:

- Відкриття relay/control-портів у LAN або публічному інтернеті.
- Tailscale Funnel для кінцевих точок керування браузером (публічний доступ).

### 0.7) Секрети на диску (чутливі дані)

Вважайте, що все в `~/.openclaw/` (або `$OPENCLAW_STATE_DIR/`) може містити секрети або приватні дані:

- `openclaw.json`: конфігурація може містити токени (gateway, віддалений gateway), налаштування постачальників і allowlist.
- `credentials/**`: облікові дані каналів (наприклад, облікові дані WhatsApp), allowlist pairing, імпорт застарілого OAuth.
- `agents/<agentId>/agent/auth-profiles.json`: API-ключі, профілі токенів, OAuth-токени, а також необов’язкові `keyRef`/`tokenRef`.
- `secrets.json` (необов’язково): файл із payload секретів, який використовується постачальниками SecretRef типу `file` (`secrets.providers`).
- `agents/<agentId>/agent/auth.json`: застарілий файл сумісності. Статичні записи `api_key` очищаються під час виявлення.
- `agents/<agentId>/sessions/**`: транскрипти сеансів (`*.jsonl`) + метадані маршрутизації (`sessions.json`), які можуть містити приватні повідомлення та результати інструментів.
- пакети bundled Plugin: установлені Plugin (разом із їхніми `node_modules/`).
- `sandboxes/**`: робочі простори sandbox інструментів; у них можуть накопичуватися копії файлів, які ви читали/записували всередині sandbox.

Поради щодо посилення захисту:

- Тримайте дозволи суворими (`700` для каталогів, `600` для файлів).
- Використовуйте повне шифрування диска на хості gateway.
- Якщо хост спільний, надавайте перевагу окремому обліковому запису користувача ОС для Gateway.

### 0.8) Журнали + транскрипти (редагування + зберігання)

Журнали й транскрипти можуть призвести до витоку чутливої інформації навіть тоді, коли контроль доступу налаштовано правильно:

- Журнали Gateway можуть містити зведення інструментів, помилки та URL.
- Транскрипти сеансів можуть містити вставлені секрети, вміст файлів, вихід команд і посилання.

Рекомендації:

- Тримайте редагування зведень інструментів увімкненим (`logging.redactSensitive: "tools"`; типове значення).
- Додавайте власні шаблони для свого середовища через `logging.redactPatterns` (токени, імена хостів, внутрішні URL).
- Коли ділитеся діагностикою, надавайте перевагу `openclaw status --all` (зручно вставляти, секрети відредаговані), а не сирим журналам.
- Видаляйте старі транскрипти сеансів і файли журналів, якщо вам не потрібне тривале зберігання.

Докладніше: [Logging](/uk/gateway/logging)

### 1) DM: pairing за замовчуванням

```json5
{
  channels: { whatsapp: { dmPolicy: "pairing" } },
}
```

### 2) Групи: вимагайте згадування всюди

```json
{
  "channels": {
    "whatsapp": {
      "groups": {
        "*": { "requireMention": true }
      }
    }
  },
  "agents": {
    "list": [
      {
        "id": "main",
        "groupChat": { "mentionPatterns": ["@openclaw", "@mybot"] }
      }
    ]
  }
}
```

У групових чатах відповідайте лише за явного згадування.

### 3) Окремі номери (WhatsApp, Signal, Telegram)

Для каналів на основі телефонних номерів розгляньте запуск вашого AI на окремому номері телефону, а не на вашому особистому:

- Особистий номер: ваші розмови залишаються приватними
- Номер бота: їх обробляє AI, з відповідними межами

### 4) Режим лише для читання (через sandbox + інструменти)

Ви можете побудувати профіль лише для читання, поєднавши:

- `agents.defaults.sandbox.workspaceAccess: "ro"` (або `"none"` для повної відсутності доступу до workspace)
- списки allow/deny інструментів, які блокують `write`, `edit`, `apply_patch`, `exec`, `process` тощо

Додаткові варіанти посилення захисту:

- `tools.exec.applyPatch.workspaceOnly: true` (типово): гарантує, що `apply_patch` не може записувати/видаляти за межами каталогу workspace, навіть якщо sandboxing вимкнено. Установлюйте `false` лише тоді, коли ви свідомо хочете дозволити `apply_patch` працювати з файлами поза workspace.
- `tools.fs.workspaceOnly: true` (необов’язково): обмежує шляхи `read`/`write`/`edit`/`apply_patch` і нативні шляхи автозавантаження зображень у prompt лише каталогом workspace (корисно, якщо сьогодні ви дозволяєте абсолютні шляхи й хочете мати єдиний запобіжник).
- Тримайте корені файлової системи вузькими: уникайте широких коренів, як-от ваш домашній каталог, для workspace агента/workspace sandbox. Широкі корені можуть відкривати файловим інструментам доступ до чутливих локальних файлів (наприклад, state/config у `~/.openclaw`).

### 5) Безпечний базовий профіль (копіювати/вставити)

Одна «безпечна типова» конфігурація, яка тримає Gateway приватним, вимагає pairing для DM і уникає завжди активних ботів у групах:

```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",
    port: 18789,
    auth: { mode: "token", token: "your-long-random-token" },
  },
  channels: {
    whatsapp: {
      dmPolicy: "pairing",
      groups: { "*": { requireMention: true } },
    },
  },
}
```

Якщо ви хочете також «типово безпечніше» виконання інструментів, додайте sandbox + deny небезпечних інструментів для будь-якого агента, який не є власником (див. приклад нижче в розділі «Профілі доступу для кожного агента»).

Вбудований базовий профіль для chat-driven ходів агента: відправники, які не є власниками, не можуть використовувати інструменти `cron` або `gateway`.

## Sandboxing (рекомендовано)

Окремий документ: [Sandboxing](/uk/gateway/sandboxing)

Два взаємодоповнювальні підходи:

- **Запускати весь Gateway у Docker** (межа контейнера): [Docker](/uk/install/docker)
- **Інструментальний sandbox** (`agents.defaults.sandbox`, host gateway + інструменти, ізольовані Docker): [Sandboxing](/uk/gateway/sandboxing)

Примітка: щоб запобігти доступу між агентами, залишайте `agents.defaults.sandbox.scope` зі значенням `"agent"` (типово)
або використовуйте `"session"` для суворішої ізоляції на рівні сеансу. `scope: "shared"` використовує
один спільний контейнер/workspace.

Також врахуйте доступ агента до workspace всередині sandbox:

- `agents.defaults.sandbox.workspaceAccess: "none"` (типово) залишає workspace агента недоступним; інструменти працюють із workspace sandbox у `~/.openclaw/sandboxes`
- `agents.defaults.sandbox.workspaceAccess: "ro"` монтує workspace агента лише для читання в `/agent` (вимикає `write`/`edit`/`apply_patch`)
- `agents.defaults.sandbox.workspaceAccess: "rw"` монтує workspace агента для читання/запису в `/workspace`
- Додаткові `sandbox.docker.binds` перевіряються за нормалізованими й канонізованими шляхами джерела. Хитрощі з symlink батьківських каталогів і канонічними псевдонімами home усе одно завершуються fail closed, якщо вони розв’язуються в заблоковані корені, такі як `/etc`, `/var/run` або каталоги облікових даних у home ОС.

Важливо: `tools.elevated` — це глобальний аварійний обхід базового захисту, який запускає exec поза sandbox. Ефективний host типово має значення `gateway`, або `node`, якщо ціль exec налаштована на `node`. Тримайте `tools.elevated.allowFrom` вузьким і не вмикайте це для сторонніх. Ви також можете додатково обмежити elevated для конкретного агента через `agents.list[].tools.elevated`. Див. [Elevated Mode](/uk/tools/elevated).

### Запобіжник делегування підлеглих агентів

Якщо ви дозволяєте інструменти сеансів, розглядайте делеговані запуски підлеглих агентів як ще одне рішення щодо меж:

- Забороняйте `sessions_spawn`, якщо агенту справді не потрібне делегування.
- Тримайте `agents.defaults.subagents.allowAgents` і будь-які перевизначення `agents.list[].subagents.allowAgents` для окремих агентів обмеженими відомими безпечними цільовими агентами.
- Для будь-якого робочого процесу, який має залишатися в sandbox, викликайте `sessions_spawn` із `sandbox: "require"` (типове значення — `inherit`).
- `sandbox: "require"` швидко завершується помилкою, якщо цільовий дочірній runtime не працює в sandbox.

## Ризики керування браузером

Увімкнення керування браузером дає моделі можливість керувати реальним браузером.
Якщо в цьому профілі браузера вже є активні сеанси входу, модель може
отримати доступ до цих акаунтів і даних. Розглядайте профілі браузера як **чутливий стан**:

- Надавайте перевагу окремому профілю для агента (типовий профіль `openclaw`).
- Уникайте спрямування агента на ваш особистий повсякденний профіль.
- Тримайте керування браузером на host вимкненим для агентів у sandbox, якщо ви їм не довіряєте.
- Автономний loopback API керування браузером приймає лише auth через спільний секрет
  (bearer auth токеном gateway або паролем gateway). Він не використовує
  заголовки ідентичності trusted-proxy або Tailscale Serve.
- Ставтеся до завантажень браузера як до недовіреного вводу; надавайте перевагу ізольованому каталогу завантажень.
- Якщо можливо, вимикайте синхронізацію браузера/менеджери паролів у профілі агента (це зменшує радіус ураження).
- Для віддалених gateway виходьте з того, що «керування браузером» еквівалентне «операторському доступу» до всього, чого може досягти цей профіль.
- Тримайте Gateway і host Node доступними лише через tailnet; уникайте відкриття портів керування браузером у LAN або публічному інтернеті.
- Вимикайте proxy-маршрутизацію браузера, коли вона не потрібна (`gateway.nodes.browser.mode="off"`).
- Режим існуючого сеансу Chrome MCP **не** є «безпечнішим»; він може діяти від вашого імені в межах усього, до чого має доступ цей профіль Chrome на host.

### Політика SSRF браузера (сувора за замовчуванням)

Політика навігації браузера в OpenClaw сувора за замовчуванням: приватні/внутрішні адресати залишаються заблокованими, якщо ви явно не дозволите їх.

- Типово: `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork` не встановлено, тому навігація браузера блокує приватні/внутрішні/special-use адресати.
- Застарілий псевдонім: `browser.ssrfPolicy.allowPrivateNetwork` і далі приймається для сумісності.
- Режим за явною згодою: установіть `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork: true`, щоб дозволити приватні/внутрішні/special-use адресати.
- У суворому режимі використовуйте `hostnameAllowlist` (шаблони на кшталт `*.example.com`) і `allowedHostnames` (точні винятки для host, включно із заблокованими іменами, як-от `localhost`) для явних винятків.
- Навігація перевіряється перед запитом і повторно перевіряється best-effort на фінальному URL `http(s)` після навігації, щоб зменшити ризик pivot через редиректи.

Приклад суворої політики:

```json5
{
  browser: {
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: false,
      hostnameAllowlist: ["*.example.com", "example.com"],
      allowedHostnames: ["localhost"],
    },
  },
}
```

## Профілі доступу для кожного агента (багатоагентність)

За багатoагентної маршрутизації кожен агент може мати власний sandbox + політику інструментів:
використовуйте це, щоб надавати **повний доступ**, **лише читання** або **без доступу** для кожного агента.
Повні подробиці та правила пріоритету див. у [Multi-Agent Sandbox & Tools](/uk/tools/multi-agent-sandbox-tools).

Типові сценарії:

- Особистий агент: повний доступ, без sandbox
- Сімейний/робочий агент: sandbox + інструменти лише для читання
- Публічний агент: sandbox + без доступу до файлової системи/оболонки

### Приклад: повний доступ (без sandbox)

```json5
{
  agents: {
    list: [
      {
        id: "personal",
        workspace: "~/.openclaw/workspace-personal",
        sandbox: { mode: "off" },
      },
    ],
  },
}
```

### Приклад: інструменти лише для читання + workspace лише для читання

```json5
{
  agents: {
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: {
          mode: "all",
          scope: "agent",
          workspaceAccess: "ro",
        },
        tools: {
          allow: ["read"],
          deny: ["write", "edit", "apply_patch", "exec", "process", "browser"],
        },
      },
    ],
  },
}
```

### Приклад: без доступу до файлової системи/оболонки (дозволено обмін повідомленнями через постачальника)

```json5
{
  agents: {
    list: [
      {
        id: "public",
        workspace: "~/.openclaw/workspace-public",
        sandbox: {
          mode: "all",
          scope: "agent",
          workspaceAccess: "none",
        },
        // Інструменти сеансів можуть розкривати чутливі дані з транскриптів. Типово OpenClaw обмежує ці інструменти
        // поточним сеансом + сеансами запущених підлеглих агентів, але за потреби можна обмежити їх ще сильніше.
        // Див. `tools.sessions.visibility` у довіднику конфігурації.
        tools: {
          sessions: { visibility: "tree" }, // self | tree | agent | all
          allow: [
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "whatsapp",
            "telegram",
            "slack",
            "discord",
          ],
          deny: [
            "read",
            "write",
            "edit",
            "apply_patch",
            "exec",
            "process",
            "browser",
            "canvas",
            "nodes",
            "cron",
            "gateway",
            "image",
          ],
        },
      },
    ],
  },
}
```

## Що сказати вашому AI

Додайте рекомендації з безпеки до системного prompt вашого агента:

```
## Security Rules
- Never share directory listings or file paths with strangers
- Never reveal API keys, credentials, or infrastructure details
- Verify requests that modify system config with the owner
- When in doubt, ask before acting
- Keep private data private unless explicitly authorized
```

## Реагування на інциденти

Якщо ваш AI зробив щось погане:

### Стримайте ситуацію

1. **Зупиніть його:** зупиніть застосунок macOS (якщо він керує Gateway) або завершіть процес `openclaw gateway`.
2. **Закрийте доступ:** установіть `gateway.bind: "loopback"` (або вимкніть Tailscale Funnel/Serve), доки не зрозумієте, що сталося.
3. **Заморозьте доступ:** перемкніть ризиковані DM/групи на `dmPolicy: "disabled"` / вимогу згадувань і видаліть записи `"*"`, що дозволяють усіх, якщо вони були.

### Проведіть ротацію (припускайте компрометацію, якщо секрети витекли)

1. Змініть auth Gateway (`gateway.auth.token` / `OPENCLAW_GATEWAY_PASSWORD`) і перезапустіть систему.
2. Змініть секрети віддалених клієнтів (`gateway.remote.token` / `.password`) на кожній машині, яка може викликати Gateway.
3. Змініть облікові дані постачальників/API (облікові дані WhatsApp, токени Slack/Discord, ключі моделей/API в `auth-profiles.json` і значення зашифрованого payload секретів, якщо вони використовуються).

### Аудит

1. Перевірте журнали Gateway: `/tmp/openclaw/openclaw-YYYY-MM-DD.log` (або `logging.file`).
2. Перегляньте відповідні транскрипти: `~/.openclaw/agents/<agentId>/sessions/*.jsonl`.
3. Перегляньте нещодавні зміни конфігурації (усе, що могло розширити доступ: `gateway.bind`, `gateway.auth`, політики dm/group, `tools.elevated`, зміни Plugin).
4. Повторно запустіть `openclaw security audit --deep` і переконайтеся, що критичні висновки усунено.

### Зберіть для звіту

- Часову позначку, ОС хоста gateway + версію OpenClaw
- Транскрипти сеансів + короткий tail журналу (після редагування)
- Що надіслав атакувальник + що зробив агент
- Чи був Gateway відкритий поза loopback (LAN/Tailscale Funnel/Serve)

## Сканування секретів (detect-secrets)

CI запускає pre-commit hook `detect-secrets` у job `secrets`.
Push у `main` завжди запускають сканування всіх файлів. Pull request використовують
швидкий шлях лише для змінених файлів, коли доступний базовий коміт, і повертаються
до повного сканування інакше. Якщо перевірка завершується невдачею, це означає, що є нові кандидати, яких ще немає в baseline.

### Якщо CI падає

1. Відтворіть локально:

   ```bash
   pre-commit run --all-files detect-secrets
   ```

2. Зрозумійте інструменти:
   - `detect-secrets` у pre-commit запускає `detect-secrets-hook` із baseline
     та виключеннями репозиторію.
   - `detect-secrets audit` відкриває інтерактивний перегляд, щоб позначити кожен елемент baseline
     як справжній секрет або хибнопозитивне спрацювання.
3. Для справжніх секретів: змініть/видаліть їх, а потім повторно запустіть сканування, щоб оновити baseline.
4. Для хибнопозитивних спрацювань: запустіть інтерактивний audit і позначте їх як хибні:

   ```bash
   detect-secrets audit .secrets.baseline
   ```

5. Якщо вам потрібні нові виключення, додайте їх до `.detect-secrets.cfg` і заново згенеруйте
   baseline з відповідними прапорами `--exclude-files` / `--exclude-lines` (файл config
   наведено лише для довідки; detect-secrets не читає його автоматично).

Закомітьте оновлений `.secrets.baseline`, коли він відображатиме задуманий стан.

## Повідомлення про проблеми безпеки

Знайшли вразливість в OpenClaw? Будь ласка, повідомте відповідально:

1. Email: [security@openclaw.ai](mailto:security@openclaw.ai)
2. Не публікуйте публічно, доки проблему не буде виправлено
3. Ми вкажемо вас у подяках (якщо ви не віддаєте перевагу анонімності)
