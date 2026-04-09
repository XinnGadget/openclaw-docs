 ---
summary: "Сервис управления браузером + команды действий"
read_when:
  - Добавление автоматизации браузера под управлением агента
  - Отладка ситуации, когда OpenClaw мешает работе вашего Chrome
  - Реализация настроек браузера и жизненного цикла в приложении для macOS
title: "Браузер (под управлением OpenClaw)"
---

# Браузер (под управлением OpenClaw)

OpenClaw может запускать **выделенный профиль Chrome/Brave/Edge/Chromium**, которым управляет агент.
Он изолирован от вашего личного браузера и управляется через небольшой локальный сервис управления внутри Gateway (только loopback).

Для начинающих:

- Представьте это как **отдельный браузер, доступный только агенту**.
- Профиль `openclaw` **не** затрагивает ваш личный профиль браузера.
- Агент может **открывать вкладки, читать страницы, кликать и вводить текст** в безопасной среде.
- Встроенный профиль `user` подключается к вашей реальной авторизованной сессии Chrome через Chrome MCP.

## Что вы получаете

- Отдельный профиль браузера с именем **openclaw** (по умолчанию с оранжевым акцентом).
- Детерминированное управление вкладками (список/открытие/фокус/закрытие).
- Действия агента (клик/ввод/перетаскивание/выделение), снимки состояния, скриншоты, PDF-файлы.
- Опциональная поддержка нескольких профилей (`openclaw`, `work`, `remote` и т. д.).

Этот браузер — **не** ваш повседневный инструмент. Это безопасная изолированная среда для автоматизации и проверки действий агента.

## Быстрый старт

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

Если вы получаете сообщение "Браузер отключён", включите его в конфигурации (см. ниже) и перезапустите Gateway.

Если команда `openclaw browser` полностью отсутствует или агент сообщает, что инструмент браузера недоступен, перейдите к разделу [Отсутствует команда или инструмент браузера](/tools/browser#missing-browser-command-or-tool).

## Управление плагинами

Инструмент `browser` по умолчанию — это встроенный плагин, который поставляется включённым. Это означает, что вы можете отключить или заменить его, не удаляя остальную часть системы плагинов OpenClaw:

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

Отключите встроенный плагин перед установкой другого плагина, предоставляющего тот же инструмент `browser`. Для работы браузера по умолчанию необходимы оба параметра:

- `plugins.entries.browser.enabled` не отключён;
- `browser.enabled=true`.

Если вы отключите только плагин, встроенный CLI браузера (`openclaw browser`), метод Gateway (`browser.request`), инструмент агента и служба управления браузером по умолчанию исчезнут вместе. Ваша конфигурация `browser.*` останется нетронутой — её сможет использовать заменяющий плагин.

Встроенный плагин браузера теперь также отвечает за реализацию среды выполнения браузера. В ядре остаются только вспомогательные компоненты Plugin SDK и экспорты для обеспечения совместимости со старыми путями импорта. На практике удаление или замена пакета плагина браузера приводит к удалению набора функций браузера, а не к сохранению второй среды выполнения, принадлежащей ядру.

Изменения конфигурации браузера по-прежнему требуют перезапуска Gateway, чтобы встроенный плагин мог перерегистрировать службу браузера с новыми настройками.

## Отсутствует команда или инструмент браузера

Если после обновления `openclaw browser` внезапно становится неизвестной командой или агент сообщает, что инструмент браузера отсутствует, наиболее распространённая причина — ограничивающий список `plugins.allow`, в который не включён `browser`.

Пример некорректной конфигурации:

```json5
{
  plugins: {
    allow: ["telegram"],
  },
}
```

Исправьте это, добавив `browser` в белый список плагинов:

```json5
{
  plugins: {
    allow: ["telegram", "browser"],
  },
}
```

Важные замечания:

- `browser.enabled=true` само по себе недостаточно, если задан `plugins.allow`.
- `plugins.entries.browser.enabled=true` также недостаточно само по себе, если задан `plugins.allow`.
- `tools.alsoAllow: ["browser"]` **не** загружает встроенный плагин браузера. Он только корректирует политику инструментов после того, как плагин уже загружен.
- Если вам не нужен ограничивающий белый список плагинов, удаление `plugins.allow` также восстанавливает поведение встроенного браузера по умолчанию.

Типичные симптомы:

- `openclaw browser` — неизвестная команда.
- Отсутствует `browser.request`.
- Агент сообщает, что инструмент браузера недоступен или отсутствует.

## Профили: `openclaw` против `user`

- `openclaw`: управляемый, изолированный браузер (расширения не требуются).
- `user`: встроенный профиль подключения Chrome MCP для вашей **реальной авторизованной сессии Chrome**.

Для вызовов инструмента браузера агентом:

- По умолчанию используется изолированный браузер `openclaw`.
- Предпочитайте `profile="user"`, когда важны существующие авторизованные сессии, а пользователь находится за компьютером, чтобы подтвердить запрос на подключение.
- `profile` — явное переопределение, когда вам нужен определённый режим работы браузера.

Установите `browser.defaultProfile: "openclaw"`, если хотите, чтобы режим управления использовался по умолчанию.

## Конфигурация

Настройки браузера находятся в `~/.openclaw/openclaw.json`.

```json5
{
  browser: {
    enabled: true, // по умолчанию: true
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: true, // режим доверенной сети по умолчанию
      // allowPrivateNetwork: true, // устаревший псевдоним
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    // cdpUrl: "http://127.0.0.1:18792", // устаревшее переопределение для одного профиля
    remoteCdpTimeoutMs: 1500, // таймаут HTTP для удалённого CDP (мс)
    remoteCdpHandshakeTimeoutMs: 3000, // таймаут рукопожатия WebSocket для удалённого CDP (мс)
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

Примечания:

- Служба управления браузером привязывается к loopback на порту, производном от `gateway.port` (по умолчанию: `18791`, то есть gateway + 2).
- Если вы переопределяете порт Gateway (`gateway.port` или `OPENCLAW_GATEWAY_PORT`), производные порты браузера смещаются, чтобы оставаться в том же "семействе".
- `cdpUrl` по умолчанию использует управляемый локальный порт CDP, если не задан.
- `remoteCdpTimeoutMs` применяется к проверкам доступности удалённого (не loopback) CDP.
- `remoteCdpHandshakeTimeoutMs` применяется к проверкам доступности WebSocket удалённого CDP.
- Навигация браузера/открытие вкладок защищено от SSRF перед навигацией и повторно проверяется с наилучшими усилиями для окончательного URL `http(s)` после навигации.
- В строгом режиме SSRF проверка также распространяется на обнаружение/зондирование конечных точек удалённого CDP (`cdpUrl`, включая запросы `/json/version`).
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork` по умолчанию имеет значение `true` (модель доверенной сети). Установите значение `false` для строгого просмотра только в публичной сети.
- `browser.ssrfPolicy.allowPrivateNetwork` поддерживается как устаревший псевдоним для совместимости.
- `attachOnly: true` означает "никогда не запускать локальный браузер; подключаться только если он уже запущен".
- `color` и `color` для каждого профиля окрашивают интерфейс браузера, чтобы вы могли видеть, какой профиль активен.
- Профиль по умолчанию — `openclaw` (автономный браузер под управлением OpenClaw). Используйте `defaultProfile: "user"`, чтобы выбрать авторизованный пользовательский браузер.
- Порядок автоматического определения: системный браузер по умолчанию, если он основан на Chromium; в противном случае Chrome → Brave → Edge → Chromium → Chrome Canary.
- Локальные профили `openclaw` автоматически назначают `cdpPort`/`cdpUrl` — устанавливайте их только для удалённого CDP.
- `driver: "existing-session"` использует Chrome DevTools MCP вместо необработанного CDP. Не устанавливайте `cdpUrl` для этого драйвера.
- Установите `browser.profiles.<name>.userDataDir`, если профиль существующей сессии должен подключаться к нестандартному профилю пользователя Chromium, например Brave или Edge.

## Использование Brave (или другого браузера на базе Chromium)

Если ваш **браузер по умолчанию** основан на Chromium (Chrome/Brave/Edge и т. д.), OpenClaw использует его автоматически. Установите `browser.executablePath`, чтобы переопределить автоматическое определение:

Пример CLI:

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

## Локальное и удалённое управление

- **Локальное управление (по умолчанию):** Gateway запускает службу управления loopback и может запустить локальный браузер.
- **Удалённое управление (узел узла):** запустите узел узла на машине с браузером; Gateway проксирует действия браузера на него.
- **Удалённый CDP:** установите `browser.profiles.<name>.cdpUrl` (или `browser.cdpUrl`), чтобы подключиться к удалённому браузеру на базе Chromium. В этом случае OpenClaw не будет запускать локальный браузер.

Поведение при остановке зависит от режима профиля:

- локальные управляемые профили: `openclaw browser stop` останавливает процесс браузера, запущенный OpenClaw;
- профили с подключением только и профили удалённого CDP: `openclaw browser stop` закрывает активную сессию управления и снимает переопределения эмуляции Playwright/CDP (область просмотра, цветовая схема, локали, часовой пояс, автономный режим и т. д.), даже если OpenClaw не запускал процесс браузера.

URL удалённого CDP могут включать аутентификацию:

- токены запроса (например, `https://provider.example?token=<token>`);
- HTTP-аутентификацию Basic (например, `https://user:pass@provider.example`).

OpenClaw сохраняет аутентификацию при обращении к конечным точкам `/json/*` и при подключении к WebSocket CDP. Предпочитайте переменные окружения или менеджеры секретов для токенов вместо их фиксации в файлах конфигурации.

## Прокси браузера узла (по умолчанию без конфигурации)

Если вы запускаете **узел узла** на машине с браузером, OpenClaw может автоматически перенаправлять вызовы инструментов браузера на этот узел без дополнительной настройки браузера. Это путь по умолчанию для удалённых шлюзов.

Примечания:

- Узел узла предоставляет свой локальный сервер управления браузером через **команду прокси**.
- Профили берутся из собственной конфигурации `browser.profiles` узла (так же, как локально).
- `nodeHost.browserProxy.allowProfiles` необязателен. Оставьте его пустым для поведения по умолчанию (устаревшего): все настроенные профили остаются доступными через прокси, включая маршруты создания/удаления профилей.
- Если вы установите `nodeHost.browserProxy.allowProfiles`, OpenClaw будет рассматривать это как границу с минимальными привилегиями: можно нацеливаться только на профили из белого списка, а маршруты создания/удаления постоянных профилей блокируются на поверхности прокси.
- Отключите, если вам это не нужно:
  - На узле: `nodeHost.browserProxy.enabled=false`
  - На шлюзе: `gateway.nodes.browser.mode="off"`

## Browserless (размещённый удалённый CDP)

[Browserless](https://browserless.io) — это размещённый сервис Chromium, который предоставляет URL-адреса подключения CDP через HTTPS и WebSocket. OpenClaw может использовать любой вариант, но для удалённого профиля браузера самый простой вариант — прямой URL WebSocket из документации по подключению Browserless.

Пример:

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

Примечания:

- Замените `<BROWSERLESS_API_KEY>` на ваш реальный токен Browserless.
- Выберите конечную точку региона, соответствующую вашей учётной записи Browserless (см. их документацию).
- Если Browserless предоставляет базовый URL HTTPS, вы можете либо преобразовать его в `wss://` для прямого подключения CDP, либо оставить URL HTTPS и позволить OpenClaw обнаружить `/json/version`.

## Поставщики прямого WebSocket CDP

Некоторые размещённые браузерные сервисы предоставляют **прямую конечную точку WebSocket** вместо стандартного обнаружения CDP на основе HTTP (`/json/version`). OpenClaw поддерживает оба варианта:

- **Конечные точки HTTP(S)** — OpenClaw вызывает `/json/version`, чтобы обнаружить URL отладчика WebSocket, затем подключается.
- **Конечные точки WebSocket** (`ws://` / `wss://`) — OpenClaw подключается напрямую, пропуская `/json/version`. Используйте это для сервисов, таких как [Browserless](https://browserless.io), [Browserbase](https://www.browserbase.com), или любого поставщика, который предоставляет URL WebSocket.

### Browserbase

[Browserbase](https://www.browserbase.com) — это облачная платформа для запуска безголовых браузеров со встроенной функцией решения CAPTCHA, режимом скрытности и резидентными прокси.

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

Примечания:

- [Зарегистрируйтесь](https://www.browserbase.com/sign-up) и скопируйте свой **API-ключ** с [панели обзора](https://www.browserbase.com/overview).
- Замените `<BROWSERBASE_API_KEY>` на ваш реальный API-ключ Browserbase.
- Browserbase автоматически создаёт сессию браузера при подключении WebSocket, поэтому ручной шаг создания сессии не требуется.
- Бесплатный тариф позволяет использовать одну одновременную сессию и один час работы браузера в месяц. См. [цены](https://www.browserbase.com/pricing) для ограничений платных планов.
- См. [документацию Browserbase](https://docs.browserbase.com) для полного справочника API, руководств по SDK и примеров интеграции.

## Безопасность

Основные идеи:

- Управление браузером ограничено loopback; доступ проходит через аутентификацию Gateway или сопоставление узлов.
- Автономный HTTP API браузера loopback использует **только аутентификацию с общим секретом**: токен-носитель Gateway, `x-openclaw-password` или HTTP Basic auth с настроенным паролем Gateway.
- Заголовки идентификации Tailscale Serve и `gateway.auth.mode: "trusted-proxy"` **не** аутентифицируют этот автономный API браузера loopback.
- Если управление браузером включено и аутентификация с общим секретом не настроена, OpenClaw автоматически генерирует `gateway.auth.token` при запуске и сохраняет его в конфигурации.
- OpenClaw **не** автоматически генерирует этот токен, если `gateway.auth.mode` уже имеет значение `password`, `none` или `trusted-proxy`.
- Держите Gateway и любые узлы узлов в частной сети (Tailscale); избегайте публичного доступа.
- Относитесь к URL/токенам удалённого CDP как к секретам; предпочитайте переменные окружения или менеджер секретов.

Советы по удалённому CDP:

- Предпочитайте зашифрованные конечные точки (HTTPS или WSS) и недолговечные токены, где это возможно.
- Избегайте встраивания долгоживущих токенов непосредственно в файлы конфигурации.

## Профили (многобраузерность)

OpenClaw поддерживает несколько именованных профилей (конфигураций маршрутизации). Профили могут быть:

- **под управлением OpenClaw**: выделенный экземпляр браузера на базе Chromium с собственным каталогом пользовательских данных и портом CDP;
- **удалённый**: явный URL CDP (браузер на базе Chromium, работающий в другом месте);
- **существующая сессия**: ваш существующий профиль Chrome через автоматическое подключение Chrome DevTools MCP.

По умолчанию:

- Профиль `openclaw` создаётся автоматически, если отсутствует.
- Профиль `user` встроен для подключения существующей сессии через Chrome MCP.
- Профили существующих сессий требуют явного включения за пределами `user`; создавайте их с помощью `--driver existing-session`.
- Локальные порты CDP выделяются из диапазона **18800–18899** по умолчанию.
- При удалении профиля его локальный каталог данных перемещается в корзину.

Все конечные точки управления принимают `?profile=<name>`; в CLI используется `--browser-profile`.

## Существующая сессия через Chrome DevTools MCP

OpenClaw также может подключаться к запущенному браузеру на базе Chromium через официальный сервер Chrome DevTools MCP. Это повторно использует вкладки и состояние авторизации, уже открытые в этом профиле браузера.

Официальные справочные материалы и ссылки по настройке:

- [Chrome для разработчиков: используйте Chrome DevTools MCP с вашей сессией браузера](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)
- [README Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)

Встроенный профиль:

- `user`

Дополнительно: создайте свой собственный профиль существующей сессии, если вам нужно другое имя, цвет или каталог данных браузера.

Поведение по умолчанию:

- Встроенный профиль `user` использует автоматическое подключение Chrome MCP, нацеленное на профиль Google Chrome по умолчанию.

Используйте `userDataDir` для Brave, Edge, Chromium или нестандартного профиля Chrome:

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

Затем в соответствующем браузере:

1. Откройте страницу проверки этого браузера для удалённой отладки.
2. Включите удалённую отладку.
3. Оставьте браузер запущенным и подтвердите запрос на подключение, когда OpenClaw подключается.

Общие страницы проверки:

- Chrome: `chrome://inspect/#remote-debugging`
- Brave: `brave://inspect/#remote-debugging`
- Edge: `edge://inspect/#remote-debugging`

Тест подключения в реальном времени:

```bash
openclaw browser --browser-profile user start
openclaw browser --browser-profile user status
openclaw browser --browser-profile user tabs
openclaw browser --browser-profile user snapshot --format ai
```

Как выглядит успех:

- `status` показывает `driver: existing-session`
- `status` показывает `transport: chrome-mcp`
- `status` показывает `running: true`
- `tabs` выводит список уже открытых вкладок браузера
- `snapshot` возвращает ссылки из выбранной активной вкладки

Что проверить, если подключение не работает:

- целевой браузер на базе Chromium версии `144+`
- удалённая отладка включена на странице проверки этого браузера
- браузер показал запрос на согласие на подключение, и вы его приняли
- `openclaw doctor` переносит старую конфигурацию браузера на основе расширений и проверяет, что Chrome установлен локально для профилей автоматического подключения по умолчанию, но не может включить удалённую отладку на стороне браузера для вас

Использование агентом:

- Используйте `profile="user"`, когда вам нужно состояние авторизованного браузера пользователя.
- Если вы используете пользовательский профиль существующей сессии, передайте это явное имя профиля.
- Выбирайте этот режим только тогда, когда пользователь находится за компьютером, чтобы подтвердить запрос на подключение.
- Gateway или узел узла может запустить `npx chrome-devtools-mcp@latest --autoConnect`

Примечания:

- Этот путь более рискован, чем изолированный профиль `openclaw`, поскольку может действовать внутри вашей авторизованной сессии браузера.
- OpenClaw не запускает браузер для этого драйвера; он подключается только к существующей сессии.
- OpenClaw использует официальный поток Chrome DevTools MCP `--autoConnect`. Если задан `userDataDir`, OpenClaw передаёт его, чтобы нацелиться на этот явный каталог пользовательских данных Chromium.
- Скриншоты для существующих сессий поддерживают захват страниц и захват элементов по ссылкам из снимков, но не CSS-селекторы `--element`.
- Скриншоты страниц для существующих сессий работают без Playwright через Chrome MCP. Скриншоты элементов на основе ссылок (`--ref`) также работают там, но `--full-page` нельзя комбинировать с `--ref` или `--element`.
- Действия для существующих сессий всё ещё более ограничены, чем для управляемого браузера:
  - `click`, `type`, `hover`, `scrollIntoView`, `drag` и `select` требуют ссылок из снимков вместо CSS-селекторов;
  - `click` — только левая кнопка (без переопределений кнопок или модификаторов);
  - `type` не поддерживает `slowly=true`; используйте `fill` или `press`;
  - `press` не поддерживает `delayMs`;
  - `hover`, `scrollIntoView`, `drag`, `select`, `fill` и `evaluate` не поддерживают переопределение таймаута для каждого вызова;
  - `select` в настоящее время поддерживает только одно значение.
- `wait --url` для существующих сессий поддерживает точные, подстрочные и шаблонные совпадения, как и другие драйверы браузера. `wait --load networkidle` пока не поддерживается.
- Перехваты загрузки для существующих сессий требуют `ref` или `inputRef`, поддерживают один файл за раз и не поддерживают таргетинг CSS `element`.
- Перехваты диалогов для существующих сессий не поддерживают переопределение таймаута.
- Некоторые функции по-прежнему требуют пути управляемого браузера, включая пакетные действия, экспорт PDF, перехват загрузок и `responsebody`.
- Существующая сессия локальна для хоста. Если Chrome находится на другой машине или в другом сетевом пространстве имён, используйте удалённый CDP или узел узла вместо этого.

## Гарантии изоляции

- **Выделенный каталог пользовательских данных**: никогда не затрагивает ваш личный профиль браузера.
- **Выделенные порты**: избегает порта `9222`, чтобы предотвратить конфликты с рабочими процессами разработки.
- **Детерминированное управление вкладками**: нацеливание на вкладки по `targetId`, а не на "последнюю вкладку".

## Выбор браузера

При локальном запуске OpenClaw выбирает первый доступный:

1. Chrome
2. Brave
3. Edge
4. Chromium
5. Chrome Canary

Вы можете переопределить это с помощью `browser.executablePath`.

Платформы:

- macOS: проверяет `/Applications` и `~/Applications`.
- Linux: ищет `google-chrome`, `brave`, `microsoft-edge`, `chromium` и т. д.
- Windows: проверяет распространённые места установки.

## API управления (необязательно)

Только для локальных интеграций Gateway предоставляет небольшой HTTP API loopback:

- Статус/запуск/остановка: `GET /`, `POST /start`, `POST /stop`
- Вкладки: `GET /tabs`, `POST /tabs/open`, `POST /tabs/focus`, `DELETE /tabs/:targetId`
- Снимок/скриншот: `GET /snapshot`, `POST /screenshot`
- Действия: `POST /navigate`, `POST /act`
- Перехваты: `POST /hooks/file-chooser`, `POST /hooks/dialog`
- Загрузки: `POST /download`, `POST /wait/download`
- Отладка: `GET /console`, `POST /pdf`
- Отладка: `GET /errors`, `GET /requests`, `POST /trace/start`, `POST /trace/stop`, `POST /highlight`
- Сеть: `POST /response/body`
- Состояние: `GET /cookies`, `POST /cookies/set`, `POST /cookies/clear`
- Состояние: `GET /storage/:kind`, `POST /storage/:kind/set`, `POST /storage/:kind/clear`
- Настройки: `POST /set/offline`, `POST /set/headers`, `POST /set/credentials`, `POST /set/geolocation`, `POST /set/media`, `POST /set/timezone`, `POST /set/locale`, `POST /set/device`

Все конечные точки принимают `?profile=<name>`.

Если настроена аутентификация Gateway с общим секретом, маршруты HTTP браузера также требуют аутентификации:

- `Authorization: Bearer <gateway token>`
- `x-openclaw-password: <gateway password>` или HTTP Basic auth с этим паролем

Примечания:

- Этот автономный API браузера loopback **не** использует заголовки идентификации доверенного прокси или Tailscale Serve.
- Если `gateway.auth.mode` имеет значение `none` или `trusted-proxy`, эти маршруты браузера loopback не наследуют эти режимы с идентификацией; держите их только для loopback.

### Требование Playwright

Некоторые функции (navigate/act/AI snapshot/role snapshot, скриншоты элементов, PDF) требуют Playwright. Если Playwright не установлен, эти конечные точки возвращают чёткую ошибку 501.

Что работает без Playwright:

- ARIA-снимки
- Скриншоты страниц для управляемого браузера `openclaw`, когда доступно WebSocket CDP для каждой вкладки
- Скриншоты страниц для профилей `existing-session` / Chrome MCP
- Скриншоты на основе ссылок (`--ref`) из вывода снимка для `existing-session`

Что по-прежнему требует Playwright:

- `navigate`
- `act`
- AI-снимки / role-снимки
- Скриншоты элементов с CSS-селекторами (`--element`)
- Полный экспорт PDF браузера

Скриншоты элементов также отклоняют `--full-page`; маршрут возвращает `fullPage is not supported for element screenshots`.

Если вы видите `Playwright is not available in this gateway build`, установите полный пакет Playwright (не `playwright-core`) и перезапустите шлюз или переустановите OpenClaw с поддержкой браузера.

#### Установка Playwright в Docker

Если ваш Gateway работает в Docker, избегайте `npx playwright` (конфликты переопределения npm). Используйте встроенный CLI вместо этого:

```bash
docker compose run --rm openclaw-cli \
  node /app/node_modules/playwright-core/cli.js install chromium
```

Чтобы сохранить загрузки браузера, установите `PLAYWRIGHT_BROWSERS_PATH` (например, `/home/node/.cache/ms-playwright`) и убедитесь, что `/home/node` сохраняется через `OPENCLAW_HOME_VOLUME` или примонтированный том. См. [Docker](/install/docker).

## Как это работает (внутреннее)

Высокоуровневый поток:

- Небольшой **сервер управления** принимает HTTP-запросы.
- Он подключается к браузерам на базе Chromium (Chrome/Brave/Edge/Chromium) через **CDP**.
- Для расширенных действий (клик/ввод/снимок/PDF) он использует **Playwright** поверх CDP.
- Когда Playwright отсутствует, доступны только операции без Playwright.

Этот дизайн поддерживает стабильный, детерминированный интерфейс для агента, позволяя вам менять локальные/удалённые браузеры и профили.

## Краткий справочник CLI

Все команды принимают `--browser-profile <name>` для нацеливания на определённый профиль. Все команды также принимают `--json` для машиночитаемого вывода (стабильные полезные нагрузки).

Основы:

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

Проверка:

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

Примечание о жизненном цикле:

- Для профилей с подключением только и удалённого CDP `openclaw browser stop` по-прежнему является правильной командой очистки после тестов. Она закрывает активную сессию управления и очищает временные переопределения эмуляции вместо того, чтобы убивать базовый браузер.
- `openclaw browser errors --clear`
- `openclaw browser requests --filter api --clear`
- `openclaw browser pdf`
- `openclaw browser responsebody "**/api" --max-chars 5000`

Действия:

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

Состояние:

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

Примечания:

- `upload` и `dialog` — **подготовительные** вызовы; запускайте их перед кликом/нажатием, которое запускает выбор файла/диалог.
- Пути вывода загрузок и трассировок ограничены временными корнями OpenClaw:
  - трассировки: `/tmp/openclaw` (запасной вариант: `${os.tmpdir()}/openclaw`)
  - загрузки: `/tmp/openclaw/downloads` (запасной вариант: `${os.tmpdir()}/openclaw/downloads`)
- Пути загрузок ограничены временным корнем загрузок OpenClaw:
  - загрузки: `/tmp/openclaw/uploads` (запасной вариант: `${os.tmpdir()}/openclaw/uploads`)
- `upload` также может устанавливать входные данные файла напрямую через `--input-ref` или `--element`.
- `snapshot`:
  - `--format ai` (по умолчанию, когда установлен Playwright): возвращает AI-снимок с числовыми ссылками (`aria-ref="<n>"`).
  - `--format aria`: возвращает дерево доступности (без ссылок; только для проверки).
  - `--efficient` (или `--mode efficient`): компактный предустановленный снимок роли (интерактивный + компактный + глубина + меньшее максимальное количество символов).
  - Конфигурация по умолчанию (только инструмент/CLI): установите `browser.snapshotDefaults.mode: "efficient"`, чтобы использовать эффективные снимки, когда вызывающая сторона не передаёт режим (см. [Конфигурация Gateway](/gateway/configuration-reference#browser)).
  - Параметры снимка роли (`--interactive`, `--compact`, `--depth`, `--selector`) принудительно создают снимок на основе роли со ссылками, такими как `ref=e12`.
  - `--frame "<iframe selector>"` ограничивает снимки роли iframe (в паре со ссылками роли, такими как `e12`).
  - `--interactive` выводит плоский, удобный для выбора список интерактивных элементов (лучше всего подходит для выполнения действий).
  - `--labels` добавляет скриншот области просмотра с наложенными метками ссылок (выводит `MEDIA:<path>`).
- `click`/`type` и т. д. требуют `ref` из `snapshot` (либо числовой `12`, либо ссылки роли `e12`). CSS-селекторы намеренно не поддерживаются для действий.

## Снимки и ссылки

OpenClaw поддерживает два стиля "снимков":

- **AI-снимок (числовые ссылки)**: `openclaw browser snapshot` (по умолчанию; `--format ai`)
  - Вывод: текстовый снимок, включающий числовые ссылки.
  - Действия: `openclaw browser click 12`, `openclaw browser type 23 "hello"`.
  - Внутри ссылка разрешается