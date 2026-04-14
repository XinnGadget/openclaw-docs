---
read_when:
    - Додавання автоматизації браузера, керованої агентом
    - Налагодження, чому openclaw заважає вашому власному Chrome
    - Реалізація налаштувань браузера + життєвого циклу в застосунку macOS
summary: Інтегрований сервіс керування браузером + команди дій
title: Браузер (керований OpenClaw)
x-i18n:
    generated_at: "2026-04-14T08:32:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: ae9ef725f544d4236d229f498c7187871c69bd18d31069b30a7e67fac53166a2
    source_path: tools/browser.md
    workflow: 15
---

# Браузер (керований openclaw)

OpenClaw може запускати **окремий профіль Chrome/Brave/Edge/Chromium**, яким керує агент.
Він ізольований від вашого особистого браузера та керується через невеликий локальний
сервіс керування всередині Gateway (лише loopback).

Пояснення для початківців:

- Сприймайте це як **окремий браузер лише для агента**.
- Профіль `openclaw` **не** взаємодіє з вашим особистим профілем браузера.
- Агент може **відкривати вкладки, читати сторінки, натискати та вводити текст** у безпечному середовищі.
- Вбудований профіль `user` підключається до вашої реальної сесії Chrome, у якій виконано вхід, через Chrome MCP.

## Що ви отримуєте

- Окремий профіль браузера з назвою **openclaw** (типово з помаранчевим акцентом).
- Детерміноване керування вкладками (список/відкриття/фокус/закриття).
- Дії агента (натискання/введення/перетягування/вибір), знімки стану, знімки екрана, PDF.
- Необов’язкова підтримка кількох профілів (`openclaw`, `work`, `remote`, ...).

Цей браузер **не** призначений для вашого щоденного використання. Це безпечна, ізольована поверхня для
автоматизації та перевірки агентом.

## Швидкий початок

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

Якщо ви бачите повідомлення “Browser disabled”, увімкніть браузер у конфігурації (див. нижче) і перезапустіть
Gateway.

Якщо команда `openclaw browser` взагалі відсутня або агент повідомляє, що
інструмент браузера недоступний, перейдіть до [Відсутня команда або інструмент браузера](/uk/tools/browser#missing-browser-command-or-tool).

## Керування Plugin

Типовий інструмент `browser` тепер є вбудованим Plugin, який постачається увімкненим
типово. Це означає, що ви можете вимкнути або замінити його, не видаляючи решту
системи Plugin в OpenClaw:

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

Вимкніть вбудований Plugin перед установленням іншого Plugin, який надає
той самий інструмент `browser`. Типова робота браузера потребує обох умов:

- `plugins.entries.browser.enabled` не вимкнено
- `browser.enabled=true`

Якщо ви вимкнете лише Plugin, вбудований CLI браузера (`openclaw browser`),
метод Gateway (`browser.request`), інструмент агента та типовий сервіс
керування браузером зникнуть одночасно. Ваша конфігурація `browser.*` залишиться
недоторканою, щоб її міг повторно використати замінний Plugin.

Вбудований Plugin браузера тепер також володіє реалізацією середовища виконання браузера.
У ядрі залишаються лише спільні допоміжні засоби Plugin SDK та сумісні re-export для
старих внутрішніх шляхів імпорту. На практиці це означає, що видалення або заміна пакета Plugin браузера
прибирає набір можливостей браузера, а не залишає друге середовище виконання, яким володіє ядро.

Зміни конфігурації браузера, як і раніше, вимагають перезапуску Gateway, щоб вбудований Plugin
міг повторно зареєструвати свій сервіс браузера з новими налаштуваннями.

## Відсутня команда або інструмент браузера

Якщо після оновлення `openclaw browser` раптом стала невідомою командою або
агент повідомляє, що інструмент браузера відсутній, найпоширеніша причина — це
обмежувальний список `plugins.allow`, у якому немає `browser`.

Приклад некоректної конфігурації:

```json5
{
  plugins: {
    allow: ["telegram"],
  },
}
```

Виправлення: додайте `browser` до списку дозволених Plugin:

```json5
{
  plugins: {
    allow: ["telegram", "browser"],
  },
}
```

Важливі примітки:

- Одного `browser.enabled=true` недостатньо, якщо задано `plugins.allow`.
- Одного `plugins.entries.browser.enabled=true` також недостатньо, якщо задано `plugins.allow`.
- `tools.alsoAllow: ["browser"]` **не** завантажує вбудований Plugin браузера. Це лише коригує політику інструментів після того, як Plugin уже завантажено.
- Якщо вам не потрібен обмежувальний список дозволених Plugin, видалення `plugins.allow` також відновлює типову поведінку вбудованого браузера.

Типові симптоми:

- `openclaw browser` є невідомою командою.
- `browser.request` відсутній.
- Агент повідомляє, що інструмент браузера недоступний або відсутній.

## Профілі: `openclaw` і `user`

- `openclaw`: керований, ізольований браузер (розширення не потрібне).
- `user`: вбудований профіль підключення Chrome MCP до вашої **реальної сесії Chrome**
  з виконаним входом.

Для викликів інструмента браузера агентом:

- Типово: використовується ізольований браузер `openclaw`.
- Віддавайте перевагу `profile="user"`, коли важливі наявні сесії з виконаним входом і користувач
  перебуває за комп’ютером, щоб натиснути/підтвердити будь-який запит на підключення.
- `profile` — це явний параметр перевизначення, коли вам потрібен конкретний режим браузера.

Установіть `browser.defaultProfile: "openclaw"`, якщо хочете, щоб керований режим був типовим.

## Конфігурація

Налаштування браузера зберігаються в `~/.openclaw/openclaw.json`.

```json5
{
  browser: {
    enabled: true, // типово: true
    ssrfPolicy: {
      // dangerouslyAllowPrivateNetwork: true, // вмикайте лише для довіреного доступу до приватної мережі
      // allowPrivateNetwork: true, // застарілий псевдонім
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    // cdpUrl: "http://127.0.0.1:18792", // застаріле перевизначення для одного профілю
    remoteCdpTimeoutMs: 1500, // HTTP-тайм-аут віддаленого CDP (мс)
    remoteCdpHandshakeTimeoutMs: 3000, // тайм-аут WebSocket-handshake віддаленого CDP (мс)
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

- Сервіс керування браузером прив’язується до loopback на порті, похідному від `gateway.port`
  (типово: `18791`, тобто порт Gateway + 2).
- Якщо ви перевизначите порт Gateway (`gateway.port` або `OPENCLAW_GATEWAY_PORT`),
  похідні порти браузера змістяться, щоб залишатися в тій самій «родині».
- `cdpUrl` типово використовує керований локальний порт CDP, якщо його не задано.
- `remoteCdpTimeoutMs` застосовується до перевірок доступності віддаленого CDP (не-loopback).
- `remoteCdpHandshakeTimeoutMs` застосовується до перевірок доступності WebSocket віддаленого CDP.
- Навігація браузера/відкриття вкладки захищені від SSRF перед переходом і повторно перевіряються в режимі best-effort для фінального `http(s)` URL після переходу.
- У строгому режимі SSRF також перевіряються виявлення/зондування віддалених кінцевих точок CDP (`cdpUrl`, включно з пошуками `/json/version`).
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork` типово вимкнено. Установлюйте `true` лише тоді, коли ви свідомо довіряєте доступу браузера до приватної мережі.
- `browser.ssrfPolicy.allowPrivateNetwork` залишається підтримуваним як застарілий псевдонім для сумісності.
- `attachOnly: true` означає «ніколи не запускати локальний браузер; лише підключатися, якщо він уже запущений».
- `color` і `color` для кожного профілю тонують інтерфейс браузера, щоб ви могли бачити, який профіль активний.
- Типовий профіль — `openclaw` (окремий браузер під керуванням OpenClaw). Використовуйте `defaultProfile: "user"`, щоб перейти до браузера користувача з виконаним входом.
- Порядок автовизначення: системний типовий браузер, якщо він на базі Chromium; інакше Chrome → Brave → Edge → Chromium → Chrome Canary.
- Для локальних профілів `openclaw` `cdpPort`/`cdpUrl` призначаються автоматично — задавайте їх лише для віддаленого CDP.
- `driver: "existing-session"` використовує Chrome DevTools MCP замість сирого CDP. Не
  задавайте `cdpUrl` для цього драйвера.
- Установіть `browser.profiles.<name>.userDataDir`, якщо профіль existing-session
  має підключатися до нетипового користувацького профілю Chromium, наприклад Brave або Edge.

## Використання Brave (або іншого браузера на базі Chromium)

Якщо ваш **системний типовий** браузер побудований на Chromium (Chrome/Brave/Edge тощо),
OpenClaw використовує його автоматично. Установіть `browser.executablePath`, щоб перевизначити
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

- **Локальне керування (типово):** Gateway запускає сервіс керування loopback і може запускати локальний браузер.
- **Віддалене керування (вузол host):** запустіть вузол host на машині, де є браузер; Gateway проксуватиме до нього дії браузера.
- **Віддалений CDP:** задайте `browser.profiles.<name>.cdpUrl` (або `browser.cdpUrl`), щоб
  підключитися до віддаленого браузера на базі Chromium. У цьому разі OpenClaw не запускатиме локальний браузер.

Поведінка зупинки відрізняється залежно від режиму профілю:

- локальні керовані профілі: `openclaw browser stop` зупиняє процес браузера, який
  запустив OpenClaw
- профілі лише з підключенням і профілі віддаленого CDP: `openclaw browser stop` закриває активну
  сесію керування та скидає перевизначення емуляції Playwright/CDP (viewport,
  колірну схему, локаль, часовий пояс, офлайн-режим та подібний стан), навіть
  якщо OpenClaw не запускав жодного процесу браузера

URL віддаленого CDP можуть містити автентифікацію:

- Токени в параметрах запиту (наприклад, `https://provider.example?token=<token>`)
- HTTP Basic auth (наприклад, `https://user:pass@provider.example`)

OpenClaw зберігає автентифікацію під час викликів кінцевих точок `/json/*` і під час підключення
до WebSocket CDP. Для токенів краще використовувати змінні середовища або менеджери секретів, а не
зберігати їх у файлах конфігурації.

## Node-проксі браузера (типовий режим без конфігурації)

Якщо ви запускаєте **вузол host** на машині, де є ваш браузер, OpenClaw може
автоматично маршрутизувати виклики інструмента браузера до цього вузла без жодної додаткової конфігурації браузера.
Це типовий шлях для віддалених Gateway.

Примітки:

- Вузол host надає доступ до свого локального сервера керування браузером через **проксі-команду**.
- Профілі беруться з власної конфігурації вузла `browser.profiles` (так само, як локально).
- `nodeHost.browserProxy.allowProfiles` є необов’язковим. Якщо залишити його порожнім, діятиме застаріла/типова поведінка: усі налаштовані профілі залишатимуться доступними через проксі, включно з маршрутами створення/видалення профілів.
- Якщо ви задасте `nodeHost.browserProxy.allowProfiles`, OpenClaw трактуватиме це як межу найменших привілеїв: можна буде звертатися лише до профілів зі списку дозволених, а маршрути створення/видалення постійних профілів буде заблоковано на поверхні проксі.
- Вимкнення, якщо це вам не потрібно:
  - На вузлі: `nodeHost.browserProxy.enabled=false`
  - На gateway: `gateway.nodes.browser.mode="off"`

## Browserless (хостований віддалений CDP)

[Browserless](https://browserless.io) — це хостований сервіс Chromium, який надає
URL підключення CDP через HTTPS і WebSocket. OpenClaw може використовувати обидва формати, але
для віддаленого профілю браузера найпростішим варіантом є прямий URL WebSocket
з документації підключення Browserless.

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
- Виберіть регіональну кінцеву точку, яка відповідає вашому обліковому запису Browserless (див. їхню документацію).
- Якщо Browserless надає вам базовий URL HTTPS, ви можете або перетворити його на
  `wss://` для прямого підключення CDP, або залишити URL HTTPS і дозволити OpenClaw
  виявити `/json/version`.

## Постачальники прямого WebSocket CDP

Деякі хостовані браузерні сервіси надають **пряму кінцеву точку WebSocket** замість
стандартного виявлення CDP на основі HTTP (`/json/version`). OpenClaw підтримує обидва варіанти:

- **Кінцеві точки HTTP(S)** — OpenClaw викликає `/json/version`, щоб виявити
  URL WebSocket debugger, а потім підключається.
- **Кінцеві точки WebSocket** (`ws://` / `wss://`) — OpenClaw підключається напряму,
  пропускаючи `/json/version`. Використовуйте це для таких сервісів, як
  [Browserless](https://browserless.io),
  [Browserbase](https://www.browserbase.com), або будь-якого постачальника, який надає вам
  URL WebSocket.

### Browserbase

[Browserbase](https://www.browserbase.com) — це хмарна платформа для запуску
headless-браузерів із вбудованим розв’язуванням CAPTCHA, stealth mode і residential
proxy.

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
  з [панелі керування Overview](https://www.browserbase.com/overview).
- Замініть `<BROWSERBASE_API_KEY>` на ваш реальний API key Browserbase.
- Browserbase автоматично створює сесію браузера під час підключення WebSocket, тому
  окремий крок ручного створення сесії не потрібен.
- Безкоштовний тариф дозволяє одну одночасну сесію та одну годину браузера на місяць.
  Обмеження платних планів дивіться в розділі [pricing](https://www.browserbase.com/pricing).
- Повний довідник API, посібники з SDK та приклади інтеграції дивіться в [документації Browserbase](https://docs.browserbase.com).

## Безпека

Ключові ідеї:

- Керування браузером доступне лише через loopback; доступ проходить через автентифікацію Gateway або прив’язку вузла.
- Окремий loopback HTTP API браузера використовує **лише автентифікацію спільним секретом**:
  bearer auth токеном gateway, `x-openclaw-password` або HTTP Basic auth із
  налаштованим паролем gateway.
- Заголовки ідентичності Tailscale Serve та `gateway.auth.mode: "trusted-proxy"`
  **не** автентифікують цей окремий loopback API браузера.
- Якщо керування браузером увімкнено і не налаштовано жодної автентифікації спільним секретом, OpenClaw
  автоматично генерує `gateway.auth.token` під час запуску та зберігає його в конфігурації.
- OpenClaw **не** генерує цей токен автоматично, якщо `gateway.auth.mode` вже має значення
  `password`, `none` або `trusted-proxy`.
- Тримайте Gateway і будь-які вузли host у приватній мережі (Tailscale); уникайте публічної доступності.
- Розглядайте URL/токени віддаленого CDP як секрети; віддавайте перевагу змінним середовища або менеджеру секретів.

Поради щодо віддаленого CDP:

- За можливості віддавайте перевагу зашифрованим кінцевим точкам (HTTPS або WSS) і токенам із коротким строком дії.
- Уникайте вбудовування довгоживучих токенів безпосередньо у файли конфігурації.

## Профілі (кілька браузерів)

OpenClaw підтримує кілька іменованих профілів (конфігурацій маршрутизації). Профілі можуть бути такими:

- **керовані openclaw**: окремий екземпляр браузера на базі Chromium із власним каталогом користувацьких даних + портом CDP
- **віддалені**: явно заданий URL CDP (браузер на базі Chromium, що працює деінде)
- **наявна сесія**: ваш наявний профіль Chrome через автопідключення Chrome DevTools MCP

Типові значення:

- Профіль `openclaw` створюється автоматично, якщо його немає.
- Профіль `user` є вбудованим для підключення наявної сесії Chrome MCP.
- Профілі наявної сесії, крім `user`, є опціональними; створюйте їх за допомогою `--driver existing-session`.
- Локальні порти CDP типово виділяються з діапазону **18800–18899**.
- Під час видалення профілю його локальний каталог даних переміщується до Кошика.

Усі кінцеві точки керування приймають `?profile=<name>`; CLI використовує `--browser-profile`.

## Existing-session через Chrome DevTools MCP

OpenClaw також може підключатися до запущеного профілю браузера на базі Chromium через
офіційний сервер Chrome DevTools MCP. Це дозволяє повторно використовувати вкладки та стан входу,
які вже відкриті в цьому профілі браузера.

Офіційні довідкові матеріали та налаштування:

- [Chrome for Developers: Use Chrome DevTools MCP with your browser session](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)
- [Chrome DevTools MCP README](https://github.com/ChromeDevTools/chrome-devtools-mcp)

Вбудований профіль:

- `user`

Необов’язково: створіть власний профіль existing-session, якщо хочете
іншу назву, колір або каталог даних браузера.

Типова поведінка:

- Вбудований профіль `user` використовує автопідключення Chrome MCP, яке націлюється на
  типовий локальний профіль Google Chrome.

Використовуйте `userDataDir` для Brave, Edge, Chromium або нетипового профілю Chrome:

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
3. Залиште браузер запущеним і підтвердьте запит на підключення, коли OpenClaw під’єднається.

Поширені сторінки inspect:

- Chrome: `chrome://inspect/#remote-debugging`
- Brave: `brave://inspect/#remote-debugging`
- Edge: `edge://inspect/#remote-debugging`

Живий smoke test підключення:

```bash
openclaw browser --browser-profile user start
openclaw browser --browser-profile user status
openclaw browser --browser-profile user tabs
openclaw browser --browser-profile user snapshot --format ai
```

Ознаки успіху:

- `status` показує `driver: existing-session`
- `status` показує `transport: chrome-mcp`
- `status` показує `running: true`
- `tabs` перелічує вже відкриті вкладки вашого браузера
- `snapshot` повертає ref з вибраної живої вкладки

Що перевірити, якщо підключення не працює:

- цільовий браузер на базі Chromium має версію `144+`
- у сторінці inspect цього браузера ввімкнено віддалене налагодження
- браузер показав запит на підтвердження підключення, і ви його прийняли
- `openclaw doctor` мігрує стару конфігурацію браузера на основі розширення та перевіряє, що
  Chrome локально встановлено для типових профілів автопідключення, але він не може
  увімкнути віддалене налагодження в самому браузері за вас

Використання агентом:

- Використовуйте `profile="user"`, коли потрібен стан браузера користувача з виконаним входом.
- Якщо ви використовуєте власний профіль existing-session, передайте явну назву цього профілю.
- Вибирайте цей режим лише тоді, коли користувач перебуває за комп’ютером, щоб підтвердити
  запит на підключення.
- Gateway або вузол host може запускати `npx chrome-devtools-mcp@latest --autoConnect`

Примітки:

- Цей шлях є ризикованішим, ніж ізольований профіль `openclaw`, оскільки він може
  діяти всередині вашої сесії браузера, у якій виконано вхід.
- OpenClaw не запускає браузер для цього драйвера; він підключається
  лише до наявної сесії.
- Тут OpenClaw використовує офіційний потік Chrome DevTools MCP `--autoConnect`. Якщо
  задано `userDataDir`, OpenClaw передає його далі, щоб націлитися саме на цей
  каталог користувацьких даних Chromium.
- Знімки екрана existing-session підтримують знімки сторінки та знімки елементів за `--ref`
  зі виводу snapshot, але не CSS-селектори `--element`.
- Знімки екрана сторінки existing-session працюють без Playwright через Chrome MCP.
  Знімки елементів за ref (`--ref`) там також працюють, але `--full-page`
  не можна поєднувати з `--ref` або `--element`.
- Дії existing-session усе ще більш обмежені, ніж у керованому браузері:
  - `click`, `type`, `hover`, `scrollIntoView`, `drag` і `select` потребують
    ref зі snapshot замість CSS-селекторів
  - `click` підтримує лише ліву кнопку миші (без перевизначення кнопок або модифікаторів)
  - `type` не підтримує `slowly=true`; використовуйте `fill` або `press`
  - `press` не підтримує `delayMs`
  - `hover`, `scrollIntoView`, `drag`, `select`, `fill` і `evaluate` не
    підтримують перевизначення тайм-ауту для окремого виклику
  - `select` наразі підтримує лише одне значення
- Existing-session `wait --url` підтримує точні, підрядкові та glob-шаблони,
  як і інші драйвери браузера. `wait --load networkidle` поки не підтримується.
- Хуки завантаження файлів existing-session вимагають `ref` або `inputRef`, підтримують один файл за раз і не підтримують націлення через CSS `element`.
- Хуки діалогів existing-session не підтримують перевизначення тайм-ауту.
- Деякі можливості все ще потребують керованого браузера, зокрема пакетні
  дії, експорт PDF, перехоплення завантажень і `responsebody`.
- Existing-session є локальним для host. Якщо Chrome працює на іншій машині або
  в іншому мережевому просторі імен, використовуйте віддалений CDP або вузол host.

## Гарантії ізоляції

- **Окремий каталог користувацьких даних**: ніколи не торкається вашого особистого профілю браузера.
- **Окремі порти**: уникає `9222`, щоб не створювати конфліктів із процесами розробки.
- **Детерміноване керування вкладками**: націлення на вкладки за `targetId`, а не за принципом «остання вкладка».

## Вибір браузера

Під час локального запуску OpenClaw вибирає перший доступний:

1. Chrome
2. Brave
3. Edge
4. Chromium
5. Chrome Canary

Ви можете перевизначити це через `browser.executablePath`.

Платформи:

- macOS: перевіряються `/Applications` і `~/Applications`.
- Linux: шукаються `google-chrome`, `brave`, `microsoft-edge`, `chromium` тощо.
- Windows: перевіряються типові місця встановлення.

## API керування (необов’язково)

Лише для локальних інтеграцій Gateway надає невеликий loopback HTTP API:

- Стан/запуск/зупинка: `GET /`, `POST /start`, `POST /stop`
- Вкладки: `GET /tabs`, `POST /tabs/open`, `POST /tabs/focus`, `DELETE /tabs/:targetId`
- Snapshot/screenshot: `GET /snapshot`, `POST /screenshot`
- Дії: `POST /navigate`, `POST /act`
- Хуки: `POST /hooks/file-chooser`, `POST /hooks/dialog`
- Завантаження: `POST /download`, `POST /wait/download`
- Налагодження: `GET /console`, `POST /pdf`
- Налагодження: `GET /errors`, `GET /requests`, `POST /trace/start`, `POST /trace/stop`, `POST /highlight`
- Мережа: `POST /response/body`
- Стан: `GET /cookies`, `POST /cookies/set`, `POST /cookies/clear`
- Стан: `GET /storage/:kind`, `POST /storage/:kind/set`, `POST /storage/:kind/clear`
- Налаштування: `POST /set/offline`, `POST /set/headers`, `POST /set/credentials`, `POST /set/geolocation`, `POST /set/media`, `POST /set/timezone`, `POST /set/locale`, `POST /set/device`

Усі кінцеві точки приймають `?profile=<name>`.

Якщо налаштовано автентифікацію gateway зі спільним секретом, маршрути HTTP браузера також вимагають автентифікації:

- `Authorization: Bearer <gateway token>`
- `x-openclaw-password: <gateway password>` або HTTP Basic auth із цим паролем

Примітки:

- Цей окремий loopback API браузера **не** використовує `trusted-proxy` або
  заголовки ідентичності Tailscale Serve.
- Якщо `gateway.auth.mode` має значення `none` або `trusted-proxy`, ці loopback-маршрути браузера
  не успадковують режими з ідентичністю; залишайте їх доступними лише через loopback.

### Контракт помилок `/act`

`POST /act` використовує структуровану відповідь про помилку для валідації на рівні маршруту та
збоїв політик:

```json
{ "error": "<message>", "code": "ACT_*" }
```

Поточні значення `code`:

- `ACT_KIND_REQUIRED` (HTTP 400): `kind` відсутній або не розпізнаний.
- `ACT_INVALID_REQUEST` (HTTP 400): нормалізація або валідація payload дії не пройшла.
- `ACT_SELECTOR_UNSUPPORTED` (HTTP 400): `selector` використано з непідтримуваним типом дії.
- `ACT_EVALUATE_DISABLED` (HTTP 403): `evaluate` (або `wait --fn`) вимкнено конфігурацією.
- `ACT_TARGET_ID_MISMATCH` (HTTP 403): `targetId` верхнього рівня або пакетний `targetId` конфліктує з ціллю запиту.
- `ACT_EXISTING_SESSION_UNSUPPORTED` (HTTP 501): дія не підтримується для профілів existing-session.

Інші збої під час виконання все ще можуть повертати `{ "error": "<message>" }` без
поля `code`.

### Вимога Playwright

Для деяких можливостей (navigate/act/AI snapshot/role snapshot, знімки елементів,
PDF) потрібен Playwright. Якщо Playwright не встановлено, ці кінцеві точки повертають
зрозумілу помилку 501.

Що все ще працює без Playwright:

- ARIA snapshot
- Знімки екрана сторінки для керованого браузера `openclaw`, коли доступний WebSocket
  CDP для кожної вкладки
- Знімки екрана сторінки для профілів `existing-session` / Chrome MCP
- Знімки `existing-session` на основі ref (`--ref`) зі виводу snapshot

Що все ще потребує Playwright:

- `navigate`
- `act`
- AI snapshot / role snapshot
- знімки елементів за CSS-селектором (`--element`)
- повний експорт PDF браузера

Знімки елементів також відхиляють `--full-page`; маршрут повертає `fullPage is
not supported for element screenshots`.

Якщо ви бачите `Playwright is not available in this gateway build`, установіть повний
пакет Playwright (не `playwright-core`) і перезапустіть gateway або перевстановіть
OpenClaw із підтримкою браузера.

#### Установлення Playwright у Docker

Якщо ваш Gateway працює в Docker, уникайте `npx playwright` (конфлікти перевизначень npm).
Натомість використовуйте вбудований CLI:

```bash
docker compose run --rm openclaw-cli \
  node /app/node_modules/playwright-core/cli.js install chromium
```

Щоб зберігати завантаження браузера, задайте `PLAYWRIGHT_BROWSERS_PATH` (наприклад,
`/home/node/.cache/ms-playwright`) і переконайтеся, що `/home/node` зберігається через
`OPENCLAW_HOME_VOLUME` або bind mount. Див. [Docker](/uk/install/docker).

## Як це працює (внутрішньо)

Потік на високому рівні:

- Невеликий **сервер керування** приймає HTTP-запити.
- Він підключається до браузерів на базі Chromium (Chrome/Brave/Edge/Chromium) через **CDP**.
- Для розширених дій (click/type/snapshot/PDF) він використовує **Playwright** поверх
  CDP.
- Якщо Playwright відсутній, доступні лише операції без Playwright.

Ця архітектура зберігає для агента стабільний, детермінований інтерфейс і водночас дозволяє
вам змінювати локальні/віддалені браузери та профілі.

## Короткий довідник CLI

Усі команди приймають `--browser-profile <name>` для націлювання на конкретний профіль.
Усі команди також приймають `--json` для машинозчитуваного виводу (стабільні payload).

Основне:

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

Перевірка:

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

Примітка про життєвий цикл:

- Для профілів лише з підключенням і профілів віддаленого CDP `openclaw browser stop` усе ще є
  правильною командою очищення після тестів. Вона закриває активну сесію керування та
  скидає тимчасові перевизначення емуляції замість завершення базового
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

- `upload` і `dialog` — це виклики **попереднього озброєння**; запускайте їх перед click/press,
  який активує вибір файлу/діалог.
- Шляхи виводу для завантажень і trace обмежені тимчасовими кореневими каталогами OpenClaw:
  - traces: `/tmp/openclaw` (резервний варіант: `${os.tmpdir()}/openclaw`)
  - downloads: `/tmp/openclaw/downloads` (резервний варіант: `${os.tmpdir()}/openclaw/downloads`)
- Шляхи upload обмежені кореневим тимчасовим каталогом upload OpenClaw:
  - uploads: `/tmp/openclaw/uploads` (резервний варіант: `${os.tmpdir()}/openclaw/uploads`)
- `upload` також може безпосередньо задавати файлові input через `--input-ref` або `--element`.
- `snapshot`:
  - `--format ai` (типово, коли Playwright установлено): повертає AI snapshot із числовими ref (`aria-ref="<n>"`).
  - `--format aria`: повертає дерево доступності (без ref; лише для перевірки).
  - `--efficient` (або `--mode efficient`): компактний пресет role snapshot (interactive + compact + depth + менший maxChars).
  - Типове значення конфігурації (лише tool/CLI): установіть `browser.snapshotDefaults.mode: "efficient"`, щоб використовувати efficient snapshot, коли викликач не передає режим (див. [Конфігурація Gateway](/uk/gateway/configuration-reference#browser)).
  - Параметри role snapshot (`--interactive`, `--compact`, `--depth`, `--selector`) примусово вмикають role-based snapshot із ref на кшталт `ref=e12`.
  - `--frame "<iframe selector>"` обмежує role snapshot конкретним iframe (у парі з role ref на кшталт `e12`).
  - `--interactive` виводить плаский, зручний для вибору список інтерактивних елементів (найкраще для керування діями).
  - `--labels` додає знімок екрана лише області viewport із накладеними мітками ref (виводить `MEDIA:<path>`).
- `click`/`type`/тощо потребують `ref` зі `snapshot` (або числовий `12`, або role ref `e12`).
  CSS-селектори навмисно не підтримуються для дій.

## Snapshot і ref

OpenClaw підтримує два стилі “snapshot”:

- **AI snapshot (числові ref)**: `openclaw browser snapshot` (типово; `--format ai`)
  - Вивід: текстовий snapshot, що містить числові ref.
  - Дії: `openclaw browser click 12`, `openclaw browser type 23 "hello"`.
  - Внутрішньо ref розв’язується через `aria-ref` Playwright.

- **Role snapshot (role ref на кшталт `e12`)**: `openclaw browser snapshot --interactive` (або `--compact`, `--depth`, `--selector`, `--frame`)
  - Вивід: список/дерево на основі ролей із `[ref=e12]` (і необов’язково `[nth=1]`).
  - Дії: `openclaw browser click e12`, `openclaw browser highlight e12`.
  - Внутрішньо ref розв’язується через `getByRole(...)` (плюс `nth()` для дублікатів).
  - Додайте `--labels`, щоб включити знімок екрана viewport із накладеними мітками `e12`.

Поведінка ref:

- Ref **не є стабільними між переходами**; якщо щось не спрацювало, знову виконайте `snapshot` і використайте новий ref.
- Якщо role snapshot було зроблено з `--frame`, role ref обмежуються цим iframe до наступного role snapshot.

## Розширені можливості wait

Можна чекати не лише час/текст:

- Очікування URL (підтримуються glob, як у Playwright):
  - `openclaw browser wait --url "**/dash"`
- Очікування стану завантаження:
  - `openclaw browser wait --load networkidle`
- Очікування JS-предиката:
  - `openclaw browser wait --fn "window.ready===true"`
- Очікування видимості селектора:
  - `openclaw browser wait "#main"`

Це можна комбінувати:

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
2. Використайте `click <ref>` / `type <ref>` (в інтерактивному режимі віддавайте перевагу role ref)
3. Якщо все одно не працює: `openclaw browser highlight <ref>`, щоб побачити, на що націлюється Playwright
4. Якщо сторінка поводиться дивно:
   - `openclaw browser errors --clear`
   - `openclaw browser requests --filter api --clear`
5. Для глибокого налагодження: запишіть trace:
   - `openclaw browser trace start`
   - відтворіть проблему
   - `openclaw browser trace stop` (виведе `TRACE:<path>`)

## JSON-вивід

`--json` призначений для сценаріїв і структурованих інструментів.

Приклади:

```bash
openclaw browser status --json
openclaw browser snapshot --interactive --json
openclaw browser requests --filter api --json
openclaw browser cookies --json
```

Role snapshot у JSON містять `refs` плюс невеликий блок `stats` (lines/chars/refs/interactive), щоб інструменти могли оцінювати розмір і щільність payload.

## Параметри стану та середовища

Вони корисні для сценаріїв «змусь сайт поводитися як X»:

- Cookies: `cookies`, `cookies set`, `cookies clear`
- Storage: `storage local|session get|set|clear`
- Offline: `set offline on|off`
- Headers: `set headers --headers-json '{"X-Debug":"1"}'` (застарілий `set headers --json '{"X-Debug":"1"}'` залишається підтримуваним)
- HTTP basic auth: `set credentials user pass` (або `--clear`)
- Геолокація: `set geo <lat> <lon> --origin "https://example.com"` (або `--clear`)
- Media: `set media dark|light|no-preference|none`
- Часовий пояс / локаль: `set timezone ...`, `set locale ...`
- Пристрій / viewport:
  - `set device "iPhone 14"` (preset пристроїв Playwright)
  - `set viewport 1280 720`

## Безпека та приватність

- Профіль браузера openclaw може містити сесії з виконаним входом; розглядайте його як чутливий.
- `browser act kind=evaluate` / `openclaw browser evaluate` і `wait --fn`
  виконують довільний JavaScript у контексті сторінки. Prompt injection може спрямувати
  це. Вимкніть через `browser.evaluateEnabled=false`, якщо вам це не потрібно.
- Для входу та приміток щодо антибот-захисту (X/Twitter тощо) див. [Вхід у браузері + публікація в X/Twitter](/uk/tools/browser-login).
- Тримайте Gateway/вузол host приватними (лише loopback або tailnet).
- Кінцеві точки віддаленого CDP мають широкі можливості; тунелюйте та захищайте їх.

Приклад strict mode (типово блокує приватні/внутрішні адресати):

```json5
{
  browser: {
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: false,
      hostnameAllowlist: ["*.example.com", "example.com"],
      allowedHostnames: ["localhost"], // необов’язковий точний дозвіл
    },
  },
}
```

## Усунення несправностей

Для проблем, специфічних для Linux (особливо snap Chromium), див.
[Усунення несправностей браузера](/uk/tools/browser-linux-troubleshooting).

Для сценаріїв із розділеними host WSL2 Gateway + Windows Chrome див.
[Усунення несправностей WSL2 + Windows + віддалений Chrome CDP](/uk/tools/browser-wsl2-windows-remote-cdp-troubleshooting).

### Збій запуску CDP проти блокування SSRF навігації

Це різні класи збоїв, і вони вказують на різні шляхи коду.

- **Збій запуску або готовності CDP** означає, що OpenClaw не може підтвердити, що control plane браузера працює справно.
- **Блокування SSRF навігації** означає, що control plane браузера працює справно, але ціль переходу сторінки відхиляється політикою.

Поширені приклади:

- Збій запуску або готовності CDP:
  - `Chrome CDP websocket for profile "openclaw" is not reachable after start`
  - `Remote CDP for profile "<name>" is not reachable at <cdpUrl>`
- Блокування SSRF навігації:
  - `open`, `navigate`, snapshot або потоки відкриття вкладок завершуються помилкою політики браузера/мережі, тоді як `start` і `tabs` усе ще працюють

Використайте цю мінімальну послідовність, щоб відрізнити одне від іншого:

```bash
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw tabs
openclaw browser --browser-profile openclaw open https://example.com
```

Як читати результати:

- Якщо `start` завершується помилкою `not reachable after start`, спочатку усувайте проблему готовності CDP.
- Якщо `start` виконується успішно, але `tabs` завершується помилкою, control plane усе ще працює некоректно. Розглядайте це як проблему доступності CDP, а не проблему навігації сторінкою.
- Якщо `start` і `tabs` виконуються успішно, але `open` або `navigate` завершується помилкою, control plane браузера працює, а збій пов’язаний із політикою навігації або цільовою сторінкою.
- Якщо `start`, `tabs` і `open` усі виконуються успішно, базовий шлях керування керованим браузером працює справно.

Важливі деталі поведінки:

- Конфігурація браузера типово використовує fail-closed об’єкт політики SSRF, навіть якщо ви не налаштовуєте `browser.ssrfPolicy`.
- Для локального loopback керованого профілю `openclaw` перевірки справності CDP навмисно пропускають застосування SSRF-перевірки доступності браузера для власного локального control plane OpenClaw.
- Захист навігації є окремим механізмом. Успішний результат `start` або `tabs` не означає, що пізніша ціль `open` або `navigate` буде дозволена.

Рекомендації з безпеки:

- **Не** послаблюйте політику SSRF браузера типово.
- Віддавайте перевагу вузьким виняткам для host, таким як `hostnameAllowlist` або `allowedHostnames`, замість широкого доступу до приватної мережі.
- Використовуйте `dangerouslyAllowPrivateNetwork: true` лише в навмисно довірених середовищах, де доступ браузера до приватної мережі потрібен і перевірений.

Приклад: навігацію заблоковано, control plane працює справно

- `start` виконується успішно
- `tabs` виконується успішно
- `open http://internal.example` завершується помилкою

Зазвичай це означає, що запуск браузера працює нормально, а ціль навігації потребує перегляду політики.

Приклад: запуск заблоковано ще до того, як навігація стає важливою

- `start` завершується помилкою `not reachable after start`
- `tabs` також завершується помилкою або не може бути виконано

Це вказує на запуск браузера або доступність CDP, а не на проблему зі списком дозволених URL сторінок.

## Інструменти агента + як працює керування

Агент отримує **один інструмент** для автоматизації браузера:

- `browser` — status/start/stop/tabs/open/focus/close/snapshot/screenshot/navigate/act

Як це зіставляється:

- `browser snapshot` повертає стабільне дерево UI (AI або ARIA).
- `browser act` використовує ID `ref` зі snapshot для click/type/drag/select.
- `browser screenshot` захоплює пікселі (усю сторінку або елемент).
- `browser` приймає:
  - `profile` для вибору іменованого профілю браузера (openclaw, chrome або віддалений CDP).
  - `target` (`sandbox` | `host` | `node`) для вибору, де розміщено браузер.
  - У sandbox-сесіях `target: "host"` вимагає `agents.defaults.sandbox.browser.allowHostControl=true`.
  - Якщо `target` не вказано: sandbox-сесії типово використовують `sandbox`, несandbox-сесії типово використовують `host`.
  - Якщо підключено вузол із підтримкою браузера, інструмент може автоматично маршрутизуватися до нього, якщо ви не зафіксуєте `target="host"` або `target="node"`.

Це зберігає детермінованість агента та допомагає уникати крихких селекторів.

## Пов’язане

- [Огляд інструментів](/uk/tools) — усі доступні інструменти агента
- [Sandboxing](/uk/gateway/sandboxing) — керування браузером у sandbox-середовищах
- [Безпека](/uk/gateway/security) — ризики керування браузером і посилення захисту
