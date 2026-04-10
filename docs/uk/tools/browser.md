---
read_when:
    - Додавання автоматизації браузера, керованої агентом
    - Налагодження, чому openclaw заважає роботі вашого Chrome
    - Реалізація налаштувань браузера та його життєвого циклу в застосунку macOS
summary: Інтегрований сервіс керування браузером + команди дій
title: Браузер (керований OpenClaw)
x-i18n:
    generated_at: "2026-04-10T03:56:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: cd3424f62178bbf25923b8bc8e4d9f70e330f35428d01fe153574e5fa45d7604
    source_path: tools/browser.md
    workflow: 15
---

# Браузер (керований openclaw)

OpenClaw може запускати **окремий профіль Chrome/Brave/Edge/Chromium**, яким керує агент.
Він ізольований від вашого особистого браузера та керується через невеликий локальний
сервіс керування всередині Gateway (лише loopback).

Погляд для початківців:

- Думайте про нього як про **окремий браузер лише для агента**.
- Профіль `openclaw` **не** торкається профілю вашого особистого браузера.
- Агент може **відкривати вкладки, читати сторінки, натискати та вводити текст** у безпечному середовищі.
- Вбудований профіль `user` підключається до вашої справжньої авторизованої сесії Chrome через Chrome MCP.

## Що ви отримуєте

- Окремий профіль браузера з назвою **openclaw** (помаранчевий акцент за замовчуванням).
- Детерміноване керування вкладками (список/відкрити/сфокусувати/закрити).
- Дії агента (натискання/введення/перетягування/вибір), знімки стану, знімки екрана, PDF.
- Необов’язкова підтримка кількох профілів (`openclaw`, `work`, `remote`, ...).

Цей браузер **не** є вашим щоденним браузером. Це безпечна, ізольована поверхня для
автоматизації та перевірки агентом.

## Швидкий старт

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

Якщо ви бачите “Browser disabled”, увімкніть його в конфігурації (див. нижче) і перезапустіть
Gateway.

Якщо `openclaw browser` взагалі відсутня або агент каже, що інструмент браузера
недоступний, перейдіть до [Відсутня команда браузера або інструмент](/uk/tools/browser#missing-browser-command-or-tool).

## Керування плагіном

Інструмент `browser` за замовчуванням тепер є вбудованим плагіном, який постачається увімкненим
за замовчуванням. Це означає, що ви можете вимкнути або замінити його, не прибираючи решту
системи плагінів OpenClaw:

```json5
{
  plugins: {
    entries: {
      browser: {
        enabled: false,
      },
    },
  },
}
```

Вимкніть вбудований плагін перед встановленням іншого плагіна, який надає ту саму
назву інструмента `browser`. Стандартний режим браузера потребує обох умов:

- `plugins.entries.browser.enabled` не вимкнено
- `browser.enabled=true`

Якщо ви вимкнете лише плагін, вбудований CLI браузера (`openclaw browser`),
метод gateway (`browser.request`), інструмент агента та стандартний сервіс
керування браузером зникнуть одночасно. Ваш конфіг `browser.*` залишиться недоторканим,
щоб його міг повторно використати замінний плагін.

Вбудований плагін браузера тепер також володіє реалізацією середовища виконання браузера.
Ядро зберігає лише спільні допоміжні засоби Plugin SDK та сумісні повторні експорти для
старіших внутрішніх шляхів імпорту. На практиці це означає, що видалення або заміна пакета
плагіна браузера прибирає набір функцій браузера, а не залишає позаду друге середовище
виконання, що належить ядру.

Зміни конфігурації браузера все ще потребують перезапуску Gateway, щоб вбудований плагін
міг повторно зареєструвати свій сервіс браузера з новими налаштуваннями.

## Відсутня команда браузера або інструмент

Якщо після оновлення `openclaw browser` раптово стала невідомою командою або
агент повідомляє, що інструмент браузера відсутній, найпоширенішою причиною є
обмежувальний список `plugins.allow`, який не містить `browser`.

Приклад некоректної конфігурації:

```json5
{
  plugins: {
    allow: ["telegram"],
  },
}
```

Виправте це, додавши `browser` до allowlist плагінів:

```json5
{
  plugins: {
    allow: ["telegram", "browser"],
  },
}
```

Важливі примітки:

- Самого `browser.enabled=true` недостатньо, якщо задано `plugins.allow`.
- Самого `plugins.entries.browser.enabled=true` також недостатньо, якщо задано `plugins.allow`.
- `tools.alsoAllow: ["browser"]` **не** завантажує вбудований плагін браузера. Воно лише коригує політику інструментів після того, як плагін уже завантажено.
- Якщо вам не потрібен обмежувальний allowlist плагінів, видалення `plugins.allow` також відновлює стандартну поведінку вбудованого браузера.

Типові симптоми:

- `openclaw browser` є невідомою командою.
- `browser.request` відсутній.
- Агент повідомляє, що інструмент браузера недоступний або відсутній.

## Профілі: `openclaw` vs `user`

- `openclaw`: керований, ізольований браузер (розширення не потрібне).
- `user`: вбудований профіль підключення Chrome MCP до вашої **справжньої авторизованої сесії Chrome**.

Для викликів інструмента браузера агентом:

- За замовчуванням: використовується ізольований браузер `openclaw`.
- Віддавайте перевагу `profile="user"`, коли важливі наявні авторизовані сесії, і користувач
  перебуває за комп’ютером, щоб натиснути/підтвердити будь-який запит на підключення.
- `profile` — це явне перевизначення, коли вам потрібен конкретний режим браузера.

Установіть `browser.defaultProfile: "openclaw"`, якщо хочете, щоб керований режим був типовим.

## Конфігурація

Налаштування браузера зберігаються в `~/.openclaw/openclaw.json`.

```json5
{
  browser: {
    enabled: true, // default: true
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: true, // default trusted-network mode
      // allowPrivateNetwork: true, // legacy alias
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    // cdpUrl: "http://127.0.0.1:18792", // legacy single-profile override
    remoteCdpTimeoutMs: 1500, // remote CDP HTTP timeout (ms)
    remoteCdpHandshakeTimeoutMs: 3000, // remote CDP WebSocket handshake timeout (ms)
    defaultProfile: "openclaw",
    color: "#FF4500",
    headless: false,
    noSandbox: false,
    attachOnly: false,
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      user: {
        driver: "existing-session",
        attachOnly: true,
        color: "#00AA00",
      },
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
  },
}
```

Примітки:

- Сервіс керування браузером прив’язується до loopback на порту, похідному від `gateway.port`
  (за замовчуванням: `18791`, тобто gateway + 2).
- Якщо ви перевизначите порт Gateway (`gateway.port` або `OPENCLAW_GATEWAY_PORT`),
  похідні порти браузера змістяться, щоб залишатися в тій самій «сім’ї».
- Якщо `cdpUrl` не задано, за замовчуванням використовується локальний CDP-порт керованого браузера.
- `remoteCdpTimeoutMs` застосовується до перевірок доступності віддаленого (не-loopback) CDP.
- `remoteCdpHandshakeTimeoutMs` застосовується до перевірок доступності віддаленого CDP WebSocket.
- Навігація браузера/відкриття вкладок захищені від SSRF перед переходом і повторно перевіряються в режимі best-effort на фінальному `http(s)` URL після переходу.
- У суворому режимі SSRF також перевіряються виявлення/зондування віддалених CDP-ендпоінтів (`cdpUrl`, зокрема запити `/json/version`).
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork` за замовчуванням має значення `true` (модель довіреної мережі). Установіть `false` для суворого перегляду лише публічних ресурсів.
- `browser.ssrfPolicy.allowPrivateNetwork` залишається підтримуваним як застарілий псевдонім для сумісності.
- `attachOnly: true` означає: «ніколи не запускати локальний браузер; лише підключатися, якщо він уже запущений».
- `color` і `color` для окремого профілю тонують інтерфейс браузера, щоб ви бачили, який профіль активний.
- Профілем за замовчуванням є `openclaw` (окремий браузер, керований OpenClaw). Використайте `defaultProfile: "user"`, щоб увімкнути браузер користувача з авторизованою сесією.
- Порядок автовизначення: системний браузер за замовчуванням, якщо він на базі Chromium; інакше Chrome → Brave → Edge → Chromium → Chrome Canary.
- Локальним профілям `openclaw` автоматично призначаються `cdpPort`/`cdpUrl` — задавайте їх лише для віддаленого CDP.
- `driver: "existing-session"` використовує Chrome DevTools MCP замість сирого CDP. Не
  задавайте `cdpUrl` для цього драйвера.
- Установіть `browser.profiles.<name>.userDataDir`, якщо профіль existing-session
  має підключатися до нестандартного профілю користувача Chromium, наприклад Brave або Edge.

## Використання Brave (або іншого браузера на базі Chromium)

Якщо вашим **системним браузером за замовчуванням** є браузер на базі Chromium (Chrome/Brave/Edge тощо),
OpenClaw використовує його автоматично. Задайте `browser.executablePath`, щоб перевизначити
автовизначення:

Приклад CLI:

```bash
openclaw config set browser.executablePath "/usr/bin/google-chrome"
```

```json5
// macOS
{
  browser: {
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
  }
}

// Windows
{
  browser: {
    executablePath: "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
  }
}

// Linux
{
  browser: {
    executablePath: "/usr/bin/brave-browser"
  }
}
```

## Локальне та віддалене керування

- **Локальне керування (за замовчуванням):** Gateway запускає loopback-сервіс керування і може запускати локальний браузер.
- **Віддалене керування (вузол-хост):** запустіть вузол-хост на машині, де є браузер; Gateway проксуватиме дії браузера до нього.
- **Віддалений CDP:** задайте `browser.profiles.<name>.cdpUrl` (або `browser.cdpUrl`), щоб
  підключитися до віддаленого браузера на базі Chromium. У цьому випадку OpenClaw не запускатиме локальний браузер.

Поведінка під час зупинки відрізняється залежно від режиму профілю:

- локальні керовані профілі: `openclaw browser stop` зупиняє процес браузера, який
  запустив OpenClaw
- профілі лише для підключення та віддаленого CDP: `openclaw browser stop` закриває активну
  сесію керування та звільняє перевизначення емуляції Playwright/CDP (viewport,
  колірна схема, локаль, часовий пояс, офлайн-режим та подібний стан), навіть
  якщо OpenClaw не запускав жодного процесу браузера

URL віддаленого CDP можуть містити автентифікацію:

- Токени в рядку запиту (наприклад, `https://provider.example?token=<token>`)
- HTTP Basic auth (наприклад, `https://user:pass@provider.example`)

OpenClaw зберігає автентифікаційні дані під час виклику ендпоінтів `/json/*` і під час підключення
до CDP WebSocket. Для токенів краще використовувати змінні середовища або менеджери секретів,
а не комітити їх у файли конфігурації.

## Проксі браузера вузла (zero-config за замовчуванням)

Якщо ви запускаєте **вузол-хост** на машині, де є ваш браузер, OpenClaw може
автоматично маршрутизувати виклики інструмента браузера до цього вузла без будь-якої додаткової конфігурації браузера.
Це типовий шлях для віддалених gateway.

Примітки:

- Вузол-хост надає свій локальний сервер керування браузером через **команду проксі**.
- Профілі беруться з власного конфігу `browser.profiles` вузла (так само, як і локально).
- `nodeHost.browserProxy.allowProfiles` — необов’язковий параметр. Залиште його порожнім для застарілої/типової поведінки: усі налаштовані профілі залишаються доступними через проксі, включно з маршрутами створення/видалення профілів.
- Якщо ви задасте `nodeHost.browserProxy.allowProfiles`, OpenClaw сприйматиме це як межу мінімально необхідних привілеїв: можна буде звертатися лише до профілів з allowlist, а маршрути створення/видалення постійних профілів будуть заблоковані на поверхні проксі.
- Вимкнення, якщо це не потрібно:
  - На вузлі: `nodeHost.browserProxy.enabled=false`
  - На gateway: `gateway.nodes.browser.mode="off"`

## Browserless (розміщений віддалений CDP)

[Browserless](https://browserless.io) — це розміщений сервіс Chromium, який надає
URL підключення CDP через HTTPS і WebSocket. OpenClaw може використовувати будь-яку форму, але
для профілю віддаленого браузера найпростішим варіантом є прямий URL WebSocket
із документації Browserless щодо підключення.

Приклад:

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "browserless",
    remoteCdpTimeoutMs: 2000,
    remoteCdpHandshakeTimeoutMs: 4000,
    profiles: {
      browserless: {
        cdpUrl: "wss://production-sfo.browserless.io?token=<BROWSERLESS_API_KEY>",
        color: "#00AA00",
      },
    },
  },
}
```

Примітки:

- Замініть `<BROWSERLESS_API_KEY>` на ваш реальний токен Browserless.
- Виберіть регіональний ендпоінт, який відповідає вашому обліковому запису Browserless (див. їхню документацію).
- Якщо Browserless надає вам базовий URL HTTPS, ви можете або перетворити його на
  `wss://` для прямого CDP-підключення, або залишити HTTPS URL і дозволити OpenClaw
  виявити `/json/version`.

## Провайдери прямого WebSocket CDP

Деякі розміщені сервіси браузерів надають **прямий ендпоінт WebSocket** замість
стандартного виявлення CDP на основі HTTP (`/json/version`). OpenClaw підтримує обидва варіанти:

- **Ендпоінти HTTP(S)** — OpenClaw викликає `/json/version`, щоб виявити URL
  WebSocket debugger, а потім підключається.
- **Ендпоінти WebSocket** (`ws://` / `wss://`) — OpenClaw підключається напряму,
  пропускаючи `/json/version`. Використовуйте це для сервісів на кшталт
  [Browserless](https://browserless.io),
  [Browserbase](https://www.browserbase.com) або будь-якого провайдера, який надає вам
  URL WebSocket.

### Browserbase

[Browserbase](https://www.browserbase.com) — це хмарна платформа для запуску
headless-браузерів із вбудованим розв’язанням CAPTCHA, stealth mode та резидентними
проксі.

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "browserbase",
    remoteCdpTimeoutMs: 3000,
    remoteCdpHandshakeTimeoutMs: 5000,
    profiles: {
      browserbase: {
        cdpUrl: "wss://connect.browserbase.com?apiKey=<BROWSERBASE_API_KEY>",
        color: "#F97316",
      },
    },
  },
}
```

Примітки:

- [Зареєструйтеся](https://www.browserbase.com/sign-up) і скопіюйте свій **API Key**
  з [панелі Overview](https://www.browserbase.com/overview).
- Замініть `<BROWSERBASE_API_KEY>` на ваш справжній API key Browserbase.
- Browserbase автоматично створює сесію браузера під час підключення WebSocket, тому
  ручний крок створення сесії не потрібен.
- Безкоштовний тариф дозволяє одну одночасну сесію та одну годину браузера на місяць.
  Див. [pricing](https://www.browserbase.com/pricing) для обмежень платних планів.
- Див. [документацію Browserbase](https://docs.browserbase.com) для повного
  довідника API, посібників із SDK та прикладів інтеграції.

## Безпека

Ключові ідеї:

- Керування браузером доступне лише через loopback; доступ проходить через автентифікацію Gateway або сполучення вузлів.
- Окремий loopback HTTP API браузера використовує **лише автентифікацію спільним секретом**:
  bearer auth токена gateway, `x-openclaw-password` або HTTP Basic auth із
  налаштованим паролем gateway.
- Заголовки ідентифікації Tailscale Serve і `gateway.auth.mode: "trusted-proxy"`
  **не** автентифікують цей окремий loopback API браузера.
- Якщо керування браузером увімкнене і не налаштовано жодної автентифікації спільним секретом, OpenClaw
  автоматично генерує `gateway.auth.token` під час запуску і зберігає його в конфігурації.
- OpenClaw **не** генерує цей токен автоматично, якщо `gateway.auth.mode` вже має значення
  `password`, `none` або `trusted-proxy`.
- Тримайте Gateway і будь-які вузли-хости в приватній мережі (Tailscale); уникайте публічного доступу.
- Розглядайте URL/токени віддаленого CDP як секрети; надавайте перевагу змінним середовища або менеджеру секретів.

Поради щодо віддаленого CDP:

- За можливості надавайте перевагу зашифрованим ендпоінтам (HTTPS або WSS) і короткоживучим токенам.
- Уникайте вбудовування довгоживучих токенів безпосередньо у файли конфігурації.

## Профілі (кілька браузерів)

OpenClaw підтримує кілька іменованих профілів (конфігурацій маршрутизації). Профілі можуть бути:

- **керовані openclaw**: окремий екземпляр браузера на базі Chromium із власним каталогом даних користувача + CDP-портом
- **віддалені**: явний URL CDP (браузер на базі Chromium, що працює деінде)
- **наявна сесія**: ваш наявний профіль Chrome через автопідключення Chrome DevTools MCP

Значення за замовчуванням:

- Профіль `openclaw` створюється автоматично, якщо відсутній.
- Профіль `user` є вбудованим для підключення existing-session через Chrome MCP.
- Профілі existing-session, окрім `user`, є opt-in; створюйте їх за допомогою `--driver existing-session`.
- Локальні CDP-порти за замовчуванням виділяються з діапазону **18800–18899**.
- Видалення профілю переміщує його локальний каталог даних до Кошика.

Усі ендпоінти керування приймають `?profile=<name>`; CLI використовує `--browser-profile`.

## Existing-session через Chrome DevTools MCP

OpenClaw також може підключатися до запущеного профілю браузера на базі Chromium через
офіційний сервер Chrome DevTools MCP. Це повторно використовує вкладки та стан входу,
які вже відкриті в цьому профілі браузера.

Офіційні матеріали та довідкові посилання з налаштування:

- [Chrome for Developers: Use Chrome DevTools MCP with your browser session](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)
- [Chrome DevTools MCP README](https://github.com/ChromeDevTools/chrome-devtools-mcp)

Вбудований профіль:

- `user`

Необов’язково: створіть власний профіль existing-session, якщо вам потрібна
інша назва, колір або каталог даних браузера.

Поведінка за замовчуванням:

- Вбудований профіль `user` використовує автопідключення Chrome MCP, яке націлюється на
  стандартний локальний профіль Google Chrome.

Використовуйте `userDataDir` для Brave, Edge, Chromium або нестандартного профілю Chrome:

```json5
{
  browser: {
    profiles: {
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
    },
  },
}
```

Потім у відповідному браузері:

1. Відкрийте сторінку inspect цього браузера для віддаленого налагодження.
2. Увімкніть віддалене налагодження.
3. Залиште браузер запущеним і підтвердьте запит на підключення, коли OpenClaw підключатиметься.

Поширені сторінки inspect:

- Chrome: `chrome://inspect/#remote-debugging`
- Brave: `brave://inspect/#remote-debugging`
- Edge: `edge://inspect/#remote-debugging`

Перевірка live attach:

```bash
openclaw browser --browser-profile user start
openclaw browser --browser-profile user status
openclaw browser --browser-profile user tabs
openclaw browser --browser-profile user snapshot --format ai
```

Як виглядає успіх:

- `status` показує `driver: existing-session`
- `status` показує `transport: chrome-mcp`
- `status` показує `running: true`
- `tabs` показує список уже відкритих вкладок браузера
- `snapshot` повертає ref з вибраної активної вкладки

Що перевірити, якщо підключення не працює:

- цільовий браузер на базі Chromium має версію `144+`
- у сторінці inspect цього браузера увімкнено віддалене налагодження
- браузер показав запит на підключення, і ви його прийняли
- `openclaw doctor` мігрує стару конфігурацію браузера на основі розширення і перевіряє, що
  Chrome локально встановлено для стандартних профілів автопідключення, але не може
  увімкнути віддалене налагодження на боці браузера за вас

Використання агентом:

- Використовуйте `profile="user"`, коли потрібен стан авторизованого браузера користувача.
- Якщо ви використовуєте власний профіль existing-session, передайте явну назву цього профілю.
- Вибирайте цей режим лише тоді, коли користувач перебуває за комп’ютером, щоб підтвердити
  запит на підключення.
- Gateway або вузол-хост може запускати `npx chrome-devtools-mcp@latest --autoConnect`

Примітки:

- Цей шлях має вищий ризик, ніж ізольований профіль `openclaw`, оскільки він може
  виконувати дії у вашій авторизованій сесії браузера.
- OpenClaw не запускає браузер для цього драйвера; він підключається лише до
  вже наявної сесії.
- Тут OpenClaw використовує офіційний потік Chrome DevTools MCP `--autoConnect`. Якщо
  задано `userDataDir`, OpenClaw передає його далі, щоб націлитися на цей явний
  каталог даних користувача Chromium.
- Знімки екрана для existing-session підтримують захоплення сторінки та захоплення елементів через `--ref`
  зі виводу snapshot, але не CSS-селектори `--element`.
- Знімки екрана сторінки existing-session працюють без Playwright через Chrome MCP.
  Знімки екрана елементів на основі ref (`--ref`) там також працюють, але `--full-page`
  не можна поєднувати з `--ref` або `--element`.
- Дії existing-session все ще більш обмежені, ніж у керованому
  режимі браузера:
  - `click`, `type`, `hover`, `scrollIntoView`, `drag` і `select` потребують
    ref зі snapshot замість CSS-селекторів
  - `click` підтримує лише ліву кнопку миші (без перевизначення кнопок або модифікаторів)
  - `type` не підтримує `slowly=true`; використовуйте `fill` або `press`
  - `press` не підтримує `delayMs`
  - `hover`, `scrollIntoView`, `drag`, `select`, `fill` і `evaluate` не
    підтримують перевизначення timeout для окремого виклику
  - `select` наразі підтримує лише одне значення
- Existing-session `wait --url` підтримує точні, часткові та glob-шаблони
  як і інші драйвери браузера. `wait --load networkidle` ще не підтримується.
- Хуки завантаження файлів existing-session вимагають `ref` або `inputRef`, підтримують один файл за раз і не підтримують націлювання через CSS `element`.
- Хуки діалогів existing-session не підтримують перевизначення timeout.
- Деякі можливості все ще потребують керованого режиму браузера, зокрема пакетні
  дії, експорт PDF, перехоплення завантажень і `responsebody`.
- Existing-session є локальним для хоста. Якщо Chrome працює на іншій машині або
  в іншому мережевому просторі імен, натомість використовуйте віддалений CDP або вузол-хост.

## Гарантії ізоляції

- **Окремий каталог даних користувача**: ніколи не торкається профілю вашого особистого браузера.
- **Окремі порти**: уникає `9222`, щоб запобігти конфліктам із робочими процесами розробки.
- **Детерміноване керування вкладками**: націлювання на вкладки за `targetId`, а не за принципом «остання вкладка».

## Вибір браузера

Під час локального запуску OpenClaw обирає перший доступний:

1. Chrome
2. Brave
3. Edge
4. Chromium
5. Chrome Canary

Ви можете перевизначити це через `browser.executablePath`.

Платформи:

- macOS: перевіряє `/Applications` і `~/Applications`.
- Linux: шукає `google-chrome`, `brave`, `microsoft-edge`, `chromium` тощо.
- Windows: перевіряє типові місця встановлення.

## API керування (необов’язково)

Лише для локальних інтеграцій Gateway надає невеликий loopback HTTP API:

- Стан/запуск/зупинка: `GET /`, `POST /start`, `POST /stop`
- Вкладки: `GET /tabs`, `POST /tabs/open`, `POST /tabs/focus`, `DELETE /tabs/:targetId`
- Snapshot/знімок екрана: `GET /snapshot`, `POST /screenshot`
- Дії: `POST /navigate`, `POST /act`
- Хуки: `POST /hooks/file-chooser`, `POST /hooks/dialog`
- Завантаження: `POST /download`, `POST /wait/download`
- Налагодження: `GET /console`, `POST /pdf`
- Налагодження: `GET /errors`, `GET /requests`, `POST /trace/start`, `POST /trace/stop`, `POST /highlight`
- Мережа: `POST /response/body`
- Стан: `GET /cookies`, `POST /cookies/set`, `POST /cookies/clear`
- Стан: `GET /storage/:kind`, `POST /storage/:kind/set`, `POST /storage/:kind/clear`
- Налаштування: `POST /set/offline`, `POST /set/headers`, `POST /set/credentials`, `POST /set/geolocation`, `POST /set/media`, `POST /set/timezone`, `POST /set/locale`, `POST /set/device`

Усі ендпоінти приймають `?profile=<name>`.

Якщо налаштовано автентифікацію gateway зі спільним секретом, HTTP-маршрути браузера також вимагають автентифікації:

- `Authorization: Bearer <gateway token>`
- `x-openclaw-password: <gateway password>` або HTTP Basic auth із цим паролем

Примітки:

- Цей окремий loopback API браузера **не** споживає trusted-proxy або
  заголовки ідентифікації Tailscale Serve.
- Якщо `gateway.auth.mode` має значення `none` або `trusted-proxy`, ці loopback-маршрути браузера
  не успадковують ці режими з передачею ідентичності; залишайте їх доступними лише через loopback.

### Контракт помилок `/act`

`POST /act` використовує структуровану відповідь помилки для валідації на рівні маршруту та
збоїв політики:

```json
{ "error": "<message>", "code": "ACT_*" }
```

Поточні значення `code`:

- `ACT_KIND_REQUIRED` (HTTP 400): `kind` відсутній або не розпізнаний.
- `ACT_INVALID_REQUEST` (HTTP 400): payload дії не пройшов нормалізацію або валідацію.
- `ACT_SELECTOR_UNSUPPORTED` (HTTP 400): `selector` було використано з непідтримуваним типом дії.
- `ACT_EVALUATE_DISABLED` (HTTP 403): `evaluate` (або `wait --fn`) вимкнено конфігурацією.
- `ACT_TARGET_ID_MISMATCH` (HTTP 403): верхньорівневий або пакетний `targetId` конфліктує з цільовим targetId запиту.
- `ACT_EXISTING_SESSION_UNSUPPORTED` (HTTP 501): дія не підтримується для профілів existing-session.

Інші збої під час виконання все ще можуть повертати `{ "error": "<message>" }` без
поля `code`.

### Вимога Playwright

Деякі можливості (navigate/act/AI snapshot/role snapshot, знімки екрана елементів,
PDF) потребують Playwright. Якщо Playwright не встановлено, ці ендпоінти повертають
чітку помилку 501.

Що все ще працює без Playwright:

- ARIA snapshot
- Знімки екрана сторінки для керованого браузера `openclaw`, коли доступний
  WebSocket CDP для окремої вкладки
- Знімки екрана сторінки для профілів `existing-session` / Chrome MCP
- Знімки екрана existing-session на основі `--ref` з виводу snapshot

Що все ще потребує Playwright:

- `navigate`
- `act`
- AI snapshot / role snapshot
- Знімки екрана елементів через CSS-селектор (`--element`)
- Повний експорт PDF браузера

Знімки екрана елементів також не приймають `--full-page`; маршрут повертає `fullPage is
not supported for element screenshots`.

Якщо ви бачите `Playwright is not available in this gateway build`, установіть повний
пакет Playwright (не `playwright-core`) і перезапустіть gateway або перевстановіть
OpenClaw з підтримкою браузера.

#### Установлення Playwright у Docker

Якщо ваш Gateway працює в Docker, уникайте `npx playwright` (конфлікти npm override).
Натомість використовуйте вбудований CLI:

```bash
docker compose run --rm openclaw-cli \
  node /app/node_modules/playwright-core/cli.js install chromium
```

Щоб зберігати завантажені браузери, задайте `PLAYWRIGHT_BROWSERS_PATH` (наприклад,
`/home/node/.cache/ms-playwright`) і переконайтеся, що `/home/node` зберігається через
`OPENCLAW_HOME_VOLUME` або bind mount. Див. [Docker](/uk/install/docker).

## Як це працює (внутрішньо)

Потік на високому рівні:

- Невеликий **сервер керування** приймає HTTP-запити.
- Він підключається до браузерів на базі Chromium (Chrome/Brave/Edge/Chromium) через **CDP**.
- Для розширених дій (натискання/введення/snapshot/PDF) він використовує **Playwright** поверх
  CDP.
- Коли Playwright відсутній, доступні лише операції без Playwright.

Така архітектура зберігає для агента стабільний, детермінований інтерфейс і водночас дає змогу
вам змінювати локальні/віддалені браузери та профілі.

## Швидкий довідник CLI

Усі команди приймають `--browser-profile <name>` для націлювання на конкретний профіль.
Усі команди також приймають `--json` для машиночитаного виводу (стабільні payload).

Базові команди:

- `openclaw browser status`
- `openclaw browser start`
- `openclaw browser stop`
- `openclaw browser tabs`
- `openclaw browser tab`
- `openclaw browser tab new`
- `openclaw browser tab select 2`
- `openclaw browser tab close 2`
- `openclaw browser open https://example.com`
- `openclaw browser focus abcd1234`
- `openclaw browser close abcd1234`

Перевірка стану:

- `openclaw browser screenshot`
- `openclaw browser screenshot --full-page`
- `openclaw browser screenshot --ref 12`
- `openclaw browser screenshot --ref e12`
- `openclaw browser snapshot`
- `openclaw browser snapshot --format aria --limit 200`
- `openclaw browser snapshot --interactive --compact --depth 6`
- `openclaw browser snapshot --efficient`
- `openclaw browser snapshot --labels`
- `openclaw browser snapshot --selector "#main" --interactive`
- `openclaw browser snapshot --frame "iframe#main" --interactive`
- `openclaw browser console --level error`

Примітка щодо життєвого циклу:

- Для профілів лише для підключення та віддаленого CDP `openclaw browser stop` усе ще є
  правильною командою очищення після тестів. Вона закриває активну сесію керування та
  очищує тимчасові перевизначення емуляції замість завершення базового
  браузера.
- `openclaw browser errors --clear`
- `openclaw browser requests --filter api --clear`
- `openclaw browser pdf`
- `openclaw browser responsebody "**/api" --max-chars 5000`

Дії:

- `openclaw browser navigate https://example.com`
- `openclaw browser resize 1280 720`
- `openclaw browser click 12 --double`
- `openclaw browser click e12 --double`
- `openclaw browser type 23 "hello" --submit`
- `openclaw browser press Enter`
- `openclaw browser hover 44`
- `openclaw browser scrollintoview e12`
- `openclaw browser drag 10 11`
- `openclaw browser select 9 OptionA OptionB`
- `openclaw browser download e12 report.pdf`
- `openclaw browser waitfordownload report.pdf`
- `openclaw browser upload /tmp/openclaw/uploads/file.pdf`
- `openclaw browser fill --fields '[{"ref":"1","type":"text","value":"Ada"}]'`
- `openclaw browser dialog --accept`
- `openclaw browser wait --text "Done"`
- `openclaw browser wait "#main" --url "**/dash" --load networkidle --fn "window.ready===true"`
- `openclaw browser evaluate --fn '(el) => el.textContent' --ref 7`
- `openclaw browser highlight e12`
- `openclaw browser trace start`
- `openclaw browser trace stop`

Стан:

- `openclaw browser cookies`
- `openclaw browser cookies set session abc123 --url "https://example.com"`
- `openclaw browser cookies clear`
- `openclaw browser storage local get`
- `openclaw browser storage local set theme dark`
- `openclaw browser storage session clear`
- `openclaw browser set offline on`
- `openclaw browser set headers --headers-json '{"X-Debug":"1"}'`
- `openclaw browser set credentials user pass`
- `openclaw browser set credentials --clear`
- `openclaw browser set geo 37.7749 -122.4194 --origin "https://example.com"`
- `openclaw browser set geo --clear`
- `openclaw browser set media dark`
- `openclaw browser set timezone America/New_York`
- `openclaw browser set locale en-US`
- `openclaw browser set device "iPhone 14"`

Примітки:

- `upload` і `dialog` — це виклики **попереднього озброєння**; запускайте їх перед натисканням/командою
  `press`, яка викликає вибір файлу/діалог.
- Шляхи виводу download і trace обмежені тимчасовими кореневими каталогами OpenClaw:
  - traces: `/tmp/openclaw` (резервний варіант: `${os.tmpdir()}/openclaw`)
  - downloads: `/tmp/openclaw/downloads` (резервний варіант: `${os.tmpdir()}/openclaw/downloads`)
- Шляхи upload обмежені тимчасовим кореневим каталогом завантажень OpenClaw:
  - uploads: `/tmp/openclaw/uploads` (резервний варіант: `${os.tmpdir()}/openclaw/uploads`)
- `upload` також може напряму задавати input file через `--input-ref` або `--element`.
- `snapshot`:
  - `--format ai` (за замовчуванням, коли встановлено Playwright): повертає AI snapshot із числовими ref (`aria-ref="<n>"`).
  - `--format aria`: повертає дерево доступності (без ref; лише для перевірки).
  - `--efficient` (або `--mode efficient`): компактний preset role snapshot (interactive + compact + depth + нижчий maxChars).
  - Значення конфігурації за замовчуванням (лише tool/CLI): установіть `browser.snapshotDefaults.mode: "efficient"`, щоб використовувати efficient snapshots, коли викликач не передає режим (див. [Конфігурація Gateway](/uk/gateway/configuration-reference#browser)).
  - Параметри role snapshot (`--interactive`, `--compact`, `--depth`, `--selector`) примусово вмикають role-based snapshot із ref на кшталт `ref=e12`.
  - `--frame "<iframe selector>"` обмежує role snapshots цим iframe (працює в парі з role ref на кшталт `e12`).
  - `--interactive` виводить плоский, зручний для вибору список інтерактивних елементів (найкраще для виконання дій).
  - `--labels` додає знімок екрана лише області перегляду з накладеними мітками ref (виводить `MEDIA:<path>`).
- `click`/`type`/тощо потребують `ref` із `snapshot` (або числовий `12`, або role ref `e12`).
  CSS-селектори навмисно не підтримуються для дій.

## Snapshot і ref

OpenClaw підтримує два стилі “snapshot”:

- **AI snapshot (числові ref)**: `openclaw browser snapshot` (за замовчуванням; `--format ai`)
  - Вивід: текстовий snapshot, який містить числові ref.
  - Дії: `openclaw browser click 12`, `openclaw browser type 23 "hello"`.
  - Внутрішньо ref визначається через `aria-ref` у Playwright.

- **Role snapshot (role ref на кшталт `e12`)**: `openclaw browser snapshot --interactive` (або `--compact`, `--depth`, `--selector`, `--frame`)
  - Вивід: список/дерево на основі ролей із `[ref=e12]` (і необов’язковим `[nth=1]`).
  - Дії: `openclaw browser click e12`, `openclaw browser highlight e12`.
  - Внутрішньо ref визначається через `getByRole(...)` (плюс `nth()` для дублікатів).
  - Додайте `--labels`, щоб включити знімок екрана області перегляду з накладеними мітками `e12`.

Поведінка ref:

- Ref **не є стабільними між переходами**; якщо щось не спрацювало, повторно запустіть `snapshot` і використайте новий ref.
- Якщо role snapshot було зроблено з `--frame`, role ref обмежуються цим iframe до наступного role snapshot.

## Додаткові можливості wait

Можна чекати не лише час/текст:

- Очікування URL (підтримуються glob-шаблони Playwright):
  - `openclaw browser wait --url "**/dash"`
- Очікування стану завантаження:
  - `openclaw browser wait --load networkidle`
- Очікування JS-предиката:
  - `openclaw browser wait --fn "window.ready===true"`
- Очікування, поки селектор стане видимим:
  - `openclaw browser wait "#main"`

Їх можна поєднувати:

```bash
openclaw browser wait "#main" \
  --url "**/dash" \
  --load networkidle \
  --fn "window.ready===true" \
  --timeout-ms 15000
```

## Робочі процеси налагодження

Коли дія не спрацьовує (наприклад, “not visible”, “strict mode violation”, “covered”):

1. `openclaw browser snapshot --interactive`
2. Використайте `click <ref>` / `type <ref>` (у режимі interactive віддавайте перевагу role ref)
3. Якщо все одно не працює: `openclaw browser highlight <ref>`, щоб побачити, на що націлюється Playwright
4. Якщо сторінка поводиться дивно:
   - `openclaw browser errors --clear`
   - `openclaw browser requests --filter api --clear`
5. Для глибокого налагодження: запишіть trace:
   - `openclaw browser trace start`
   - відтворіть проблему
   - `openclaw browser trace stop` (виводить `TRACE:<path>`)

## Вивід JSON

`--json` призначений для скриптів і структурованих інструментів.

Приклади:

```bash
openclaw browser status --json
openclaw browser snapshot --interactive --json
openclaw browser requests --filter api --json
openclaw browser cookies --json
```

Role snapshots у JSON містять `refs` і невеликий блок `stats` (lines/chars/refs/interactive), щоб інструменти могли оцінювати розмір і щільність payload.

## Параметри стану та середовища

Вони корисні для сценаріїв «змусити сайт поводитися як X»:

- Cookies: `cookies`, `cookies set`, `cookies clear`
- Storage: `storage local|session get|set|clear`
- Offline: `set offline on|off`
- Headers: `set headers --headers-json '{"X-Debug":"1"}'` (застарілий `set headers --json '{"X-Debug":"1"}'` усе ще підтримується)
- HTTP basic auth: `set credentials user pass` (або `--clear`)
- Геолокація: `set geo <lat> <lon> --origin "https://example.com"` (або `--clear`)
- Media: `set media dark|light|no-preference|none`
- Часовий пояс / локаль: `set timezone ...`, `set locale ...`
- Пристрій / область перегляду:
  - `set device "iPhone 14"` (preset пристроїв Playwright)
  - `set viewport 1280 720`

## Безпека та приватність

- Профіль браузера openclaw може містити авторизовані сесії; вважайте його чутливим.
- `browser act kind=evaluate` / `openclaw browser evaluate` і `wait --fn`
  виконують довільний JavaScript у контексті сторінки. Prompt injection може
  впливати на це. Вимкніть через `browser.evaluateEnabled=false`, якщо вам це не потрібно.
- Для входу в систему та приміток щодо anti-bot (X/Twitter тощо) див. [Вхід у браузері + публікація в X/Twitter](/uk/tools/browser-login).
- Тримайте Gateway/вузол-хост приватними (лише loopback або tailnet-only).
- Ендпоінти віддаленого CDP мають широкі можливості; тунелюйте та захищайте їх.

Приклад strict mode (блокувати приватні/внутрішні адресати за замовчуванням):

```json5
{
  browser: {
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: false,
      hostnameAllowlist: ["*.example.com", "example.com"],
      allowedHostnames: ["localhost"], // optional exact allow
    },
  },
}
```

## Усунення неполадок

Для проблем, специфічних для Linux (особливо snap Chromium), див.
[Усунення неполадок браузера](/uk/tools/browser-linux-troubleshooting).

Для конфігурацій із розділеними хостами WSL2 Gateway + Windows Chrome див.
[Усунення неполадок WSL2 + Windows + віддалений Chrome CDP](/uk/tools/browser-wsl2-windows-remote-cdp-troubleshooting).

## Інструменти агента + як працює керування

Агент отримує **один інструмент** для автоматизації браузера:

- `browser` — status/start/stop/tabs/open/focus/close/snapshot/screenshot/navigate/act

Як це відображається:

- `browser snapshot` повертає стабільне дерево UI (AI або ARIA).
- `browser act` використовує ID `ref` зі snapshot для click/type/drag/select.
- `browser screenshot` захоплює пікселі (усю сторінку або елемент).
- `browser` приймає:
  - `profile` для вибору іменованого профілю браузера (openclaw, chrome або віддалений CDP).
  - `target` (`sandbox` | `host` | `node`) для вибору, де розташовано браузер.
  - У sandbox-сеансах `target: "host"` вимагає `agents.defaults.sandbox.browser.allowHostControl=true`.
  - Якщо `target` не вказано: sandbox-сеанси за замовчуванням використовують `sandbox`, сеанси без sandbox — `host`.
  - Якщо підключено вузол із підтримкою браузера, інструмент може автоматично маршрутизуватися до нього, якщо ви не зафіксували `target="host"` або `target="node"`.

Це зберігає детермінованість агента та допомагає уникати крихких селекторів.

## Пов’язане

- [Огляд інструментів](/uk/tools) — усі доступні інструменти агента
- [Ізоляція sandbox](/uk/gateway/sandboxing) — керування браузером у sandbox-середовищах
- [Безпека](/uk/gateway/security) — ризики керування браузером і заходи захисту
