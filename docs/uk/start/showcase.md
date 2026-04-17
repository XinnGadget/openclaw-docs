---
description: Real-world OpenClaw projects from the community
read_when:
    - Шукаєте реальні приклади використання OpenClaw
    - Оновлення добірки проєктів спільноти
summary: Проєкти та інтеграції, створені спільнотою на базі OpenClaw
title: Вітрина
x-i18n:
    generated_at: "2026-04-14T13:43:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: 797d0b85c9eca920240c79d870eb9636216714f3eba871c5ebd0f7f40cf7bbf1
    source_path: start/showcase.md
    workflow: 15
---

<!-- markdownlint-disable MD033 -->

# Вітрина

<div className="showcase-hero">
  <p className="showcase-kicker">Створено в чатах, терміналах, браузерах і вітальнях</p>
  <p className="showcase-lead">
    Проєкти OpenClaw — це не іграшкові демо. Люди запускають цикли перегляду PR, мобільні застосунки, домашню автоматизацію,
    голосові системи, devtools і workflows з великим обсягом пам’яті з каналів, якими вони вже користуються.
  </p>
  <div className="showcase-actions">
    <a href="#videos">Дивитися демо</a>
    <a href="#fresh-from-discord">Переглянути проєкти</a>
    <a href="https://discord.gg/clawd">Поділитися своїм</a>
  </div>
  <div className="showcase-highlights">
    <div className="showcase-highlight">
      <strong>Збірки, нативні для чату</strong>
      <span>Telegram, WhatsApp, Discord, Beeper, вебчат і workflows з пріоритетом термінала.</span>
    </div>
    <div className="showcase-highlight">
      <strong>Справжня автоматизація</strong>
      <span>Бронювання, покупки, підтримка, звітність і керування браузером без очікування на API.</span>
    </div>
    <div className="showcase-highlight">
      <strong>Локальний + фізичний світ</strong>
      <span>Принтери, пилососи, камери, дані про здоров’я, домашні системи та особисті бази знань.</span>
    </div>
  </div>
</div>

<Info>
**Хочете, щоб вас додали?** Поділіться своїм проєктом у [#self-promotion on Discord](https://discord.gg/clawd) або [позначте @openclaw у X](https://x.com/openclaw).
</Info>

<div className="showcase-jump-links">
  <a href="#videos">Відео</a>
  <a href="#fresh-from-discord">Свіже з Discord</a>
  <a href="#automation-workflows">Автоматизація</a>
  <a href="#knowledge-memory">Пам’ять</a>
  <a href="#voice-phone">Голос і телефон</a>
  <a href="#infrastructure-deployment">Інфраструктура</a>
  <a href="#home-hardware">Дім і обладнання</a>
  <a href="#community-projects">Спільнота</a>
  <a href="#submit-your-project">Надіслати проєкт</a>
</div>

<h2 id="videos">Відео</h2>

<p className="showcase-section-intro">
  Почніть звідси, якщо хочете найкоротший шлях від «що це таке?» до «гаразд, я зрозумів».
</p>

<div className="showcase-video-grid">
  <div className="showcase-video-card">
    <div className="showcase-video-shell">
      <iframe
        src="https://www.youtube-nocookie.com/embed/SaWSPZoPX34"
        title="OpenClaw: The self-hosted AI that Siri should have been (Full setup)"
        loading="lazy"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowFullScreen
      />
    </div>
    <h3>Повний огляд налаштування</h3>
    <p>VelvetShark, 28 хвилин. Встановлення, онбординг і запуск першого робочого помічника від початку до кінця.</p>
    <a href="https://www.youtube.com/watch?v=SaWSPZoPX34">Дивитися на YouTube</a>
  </div>

  <div className="showcase-video-card">
    <div className="showcase-video-shell">
      <iframe
        src="https://www.youtube-nocookie.com/embed/mMSKQvlmFuQ"
        title="OpenClaw showcase video"
        loading="lazy"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowFullScreen
      />
    </div>
    <h3>Добірка проєктів спільноти</h3>
    <p>Швидший огляд реальних проєктів, інтерфейсів і workflows, побудованих навколо OpenClaw.</p>
    <a href="https://www.youtube.com/watch?v=mMSKQvlmFuQ">Дивитися на YouTube</a>
  </div>

  <div className="showcase-video-card">
    <div className="showcase-video-shell">
      <iframe
        src="https://www.youtube-nocookie.com/embed/5kkIJNUGFho"
        title="OpenClaw community showcase"
        loading="lazy"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowFullScreen
      />
    </div>
    <h3>Проєкти з реального світу</h3>
    <p>Приклади від спільноти — від циклів розробки, нативних для чату, до обладнання та персональної автоматизації.</p>
    <a href="https://www.youtube.com/watch?v=5kkIJNUGFho">Дивитися на YouTube</a>
  </div>
</div>

<h2 id="fresh-from-discord">Свіже з Discord</h2>

<p className="showcase-section-intro">
  Нещодавні яскраві приклади у сферах програмування, devtools, мобільних застосунків і створення продуктів, нативних для чату.
</p>

<CardGroup cols={2}>

<Card title="Перегляд PR → Відгук у Telegram" icon="code-pull-request" href="https://x.com/i/status/2010878524543131691">
  **@bangnokia** • `review` `github` `telegram`

OpenCode завершує зміну → відкриває PR → OpenClaw переглядає diff і відповідає в Telegram «незначними пропозиціями» разом із чітким вердиктом щодо злиття (включно з критичними виправленнями, які треба застосувати спочатку).

  <img src="/assets/showcase/pr-review-telegram.jpg" alt="Відгук OpenClaw на перегляд PR, доставлений у Telegram" />
</Card>

<Card title="Навичка винного льоху за лічені хвилини" icon="wine-glass" href="https://x.com/i/status/2010916352454791216">
  **@prades_maxime** • `skills` `local` `csv`

Попросили «Robby» (@openclaw) створити локальну навичку для винного льоху. Вона запитує приклад експорту CSV і місце для його зберігання, а потім швидко створює/тестує навичку (у прикладі — 962 пляшки).

  <img src="/assets/showcase/wine-cellar-skill.jpg" alt="OpenClaw створює локальну навичку винного льоху з CSV" />
</Card>

<Card title="Автопілот покупок у Tesco" icon="cart-shopping" href="https://x.com/i/status/2009724862470689131">
  **@marchattonhere** • `automation` `browser` `shopping`

Щотижневий план харчування → постійні покупки → бронювання слота доставки → підтвердження замовлення. Жодних API, лише керування браузером.

  <img src="/assets/showcase/tesco-shop.jpg" alt="Автоматизація покупок у Tesco через чат" />
</Card>

<Card title="SNAG: зі скриншота в Markdown" icon="scissors" href="https://github.com/am-will/snag">
  **@am-will** • `devtools` `screenshots` `markdown`

Гаряча клавіша для області екрана → Gemini vision → миттєвий Markdown у вашому буфері обміну.

  <img src="/assets/showcase/snag.png" alt="Інструмент SNAG для перетворення скриншотів у Markdown" />
</Card>

<Card title="Agents UI" icon="window-maximize" href="https://releaseflow.net/kitze/agents-ui">
  **@kitze** • `ui` `skills` `sync`

Десктопний застосунок для керування Skills/командами в Agents, Claude, Codex і OpenClaw.

  <img src="/assets/showcase/agents-ui.jpg" alt="Застосунок Agents UI" />
</Card>

<Card title="Голосові повідомлення Telegram (papla.media)" icon="microphone" href="https://papla.media/docs">
  **Спільнота** • `voice` `tts` `telegram`

Обгортає TTS від papla.media і надсилає результати як голосові повідомлення Telegram (без дратівливого автовідтворення).

  <img src="/assets/showcase/papla-tts.jpg" alt="Вивід TTS як голосове повідомлення Telegram" />
</Card>

<Card title="CodexMonitor" icon="eye" href="https://clawhub.ai/odrobnik/codexmonitor">
  **@odrobnik** • `devtools` `codex` `brew`

Допоміжний інструмент, який встановлюється через Homebrew, для перегляду/інспекції/моніторингу локальних сесій OpenAI Codex (CLI + VS Code).

  <img src="/assets/showcase/codexmonitor.png" alt="CodexMonitor у ClawHub" />
</Card>

<Card title="Керування 3D-принтером Bambu" icon="print" href="https://clawhub.ai/tobiasbischoff/bambu-cli">
  **@tobiasbischoff** • `hardware` `3d-printing` `skill`

Керуйте та діагностуйте принтери BambuLab: статус, завдання, камера, AMS, калібрування тощо.

  <img src="/assets/showcase/bambu-cli.png" alt="Навичка Bambu CLI у ClawHub" />
</Card>

<Card title="Віденський транспорт (Wiener Linien)" icon="train" href="https://clawhub.ai/hjanuschka/wienerlinien">
  **@hjanuschka** • `travel` `transport` `skill`

Відправлення в реальному часі, збої, статус ліфтів і маршрути для громадського транспорту Відня.

  <img src="/assets/showcase/wienerlinien.png" alt="Навичка Wiener Linien у ClawHub" />
</Card>

<Card title="Шкільні обіди ParentPay" icon="utensils">
  **@George5562** • `automation` `browser` `parenting`

Автоматизоване бронювання шкільних обідів у Великій Британії через ParentPay. Використовує координати миші для надійного натискання клітинок таблиці.
</Card>

<Card title="Завантаження в R2 (Send Me My Files)" icon="cloud-arrow-up" href="https://clawhub.ai/skills/r2-upload">
  **@julianengel** • `files` `r2` `presigned-urls`

Завантаження до Cloudflare R2/S3 і створення безпечних presigned-посилань для завантаження. Ідеально для віддалених інстансів OpenClaw.
</Card>

<Card title="iOS-застосунок через Telegram" icon="mobile">
  **@coard** • `ios` `xcode` `testflight`

Повноцінний iOS-застосунок із мапами та записом голосу, розгорнутий у TestFlight повністю через чат у Telegram.

  <img src="/assets/showcase/ios-testflight.jpg" alt="iOS-застосунок у TestFlight" />
</Card>

<Card title="Помічник для здоров’я з Oura Ring" icon="heart-pulse">
  **@AS** • `health` `oura` `calendar`

Персональний AI-помічник для здоров’я, що інтегрує дані Oura ring із календарем, зустрічами та графіком тренувань.

  <img src="/assets/showcase/oura-health.png" alt="Помічник для здоров’я з Oura ring" />
</Card>
<Card title="Команда мрії Kev (14+ агентів)" icon="robot" href="https://github.com/adam91holt/orchestrated-ai-articles">
  **@adam91holt** • `multi-agent` `orchestration` `architecture` `manifesto`

14+ агентів під одним Gateway, де оркестратор Opus 4.5 делегує завдання працівникам Codex. Докладний [технічний опис](https://github.com/adam91holt/orchestrated-ai-articles), що охоплює склад Dream Team, вибір моделей, ізоляцію, Webhook, Heartbeat і потоки делегування. [Clawdspace](https://github.com/adam91holt/clawdspace) для ізоляції агентів. [Допис у блозі](https://adams-ai-journey.ghost.io/2026-the-year-of-the-orchestrator/).
</Card>

<Card title="Linear CLI" icon="terminal" href="https://github.com/Finesssee/linear-cli">
  **@NessZerra** • `devtools` `linear` `cli` `issues`

CLI для Linear, що інтегрується з агентними workflows (Claude Code, OpenClaw). Керуйте issue, проєктами та workflows з термінала. Перший зовнішній PR уже злитий!
</Card>

<Card title="Beeper CLI" icon="message" href="https://github.com/blqke/beepcli">
  **@jules** • `messaging` `beeper` `cli` `automation`

Читайте, надсилайте та архівуйте повідомлення через Beeper Desktop. Використовує локальний MCP API Beeper, щоб агенти могли керувати всіма вашими чатами (iMessage, WhatsApp тощо) в одному місці.
</Card>

</CardGroup>

<h2 id="automation-workflows">Автоматизація й workflows</h2>

<p className="showcase-section-intro">
  Планування, керування браузером, цикли підтримки та та сторона продукту, де він «просто робить завдання за мене».
</p>

<CardGroup cols={2}>

<Card title="Керування очищувачем повітря Winix" icon="wind" href="https://x.com/antonplex/status/2010518442471006253">
  **@antonplex** • `automation` `hardware` `air-quality`

Claude Code виявив і підтвердив елементи керування очищувачем, а потім OpenClaw перебирає керування для підтримання якості повітря в кімнаті.

  <img src="/assets/showcase/winix-air-purifier.jpg" alt="Керування очищувачем повітря Winix через OpenClaw" />
</Card>

<Card title="Гарні знімки неба з камери" icon="camera" href="https://x.com/signalgaining/status/2010523120604746151">
  **@signalgaining** • `automation` `camera` `skill` `images`

Запускається камерою на даху: попросіть OpenClaw зробити фото неба щоразу, коли воно виглядає гарно — він спроєктував навичку й зробив знімок.

  <img src="/assets/showcase/roof-camera-sky.jpg" alt="Знімок неба з даху, зроблений OpenClaw" />
</Card>

<Card title="Візуальна сцена для ранкового брифінгу" icon="robot" href="https://x.com/buddyhadry/status/2010005331925954739">
  **@buddyhadry** • `automation` `briefing` `images` `telegram`

Запланований prompt щоранку генерує одне зображення «сцени» (погода, завдання, дата, улюблений допис/цитата) через персоналізований образ OpenClaw.
</Card>

<Card title="Бронювання корту для паделу" icon="calendar-check" href="https://github.com/joshp123/padel-cli">
  **@joshp123** • `automation` `booking` `cli`
  
  Перевірка доступності Playtomic + CLI для бронювання. Більше ніколи не пропускайте вільний корт.
  
  <img src="/assets/showcase/padel-screenshot.jpg" alt="Скриншот padel-cli" />
</Card>

<Card title="Збір бухгалтерських документів" icon="file-invoice-dollar">
  **Спільнота** • `automation` `email` `pdf`
  
  Збирає PDF з електронної пошти, готує документи для податкового консультанта. Щомісячна бухгалтерія на автопілоті.
</Card>

<Card title="Режим розробки з дивана" icon="couch" href="https://davekiss.com">
  **@davekiss** • `telegram` `website` `migration` `astro`

Перебудував увесь особистий сайт через Telegram, поки дивився Netflix — Notion → Astro, перенесено 18 дописів, DNS на Cloudflare. Жодного разу не відкривав ноутбук.
</Card>

<Card title="Агент для пошуку роботи" icon="briefcase">
  **@attol8** • `automation` `api` `skill`

Шукає вакансії, зіставляє їх із ключовими словами з CV і повертає релевантні можливості з посиланнями. Створено за 30 хвилин з використанням JSearch API.
</Card>

<Card title="Конструктор Jira Skill" icon="diagram-project" href="https://x.com/jdrhyne/status/2008336434827002232">
  **@jdrhyne** • `automation` `jira` `skill` `devtools`

OpenClaw підключився до Jira, а потім згенерував нову навичку на льоту (ще до того, як вона з’явилася в ClawHub).
</Card>

<Card title="Todoist Skill через Telegram" icon="list-check" href="https://x.com/iamsubhrajyoti/status/2009949389884920153">
  **@iamsubhrajyoti** • `automation` `todoist` `skill` `telegram`

Автоматизував завдання Todoist і змусив OpenClaw згенерувати навичку безпосередньо в чаті Telegram.
</Card>

<Card title="Аналіз у TradingView" icon="chart-line">
  **@bheem1798** • `finance` `browser` `automation`

Входить у TradingView через автоматизацію браузера, робить скриншоти графіків і виконує технічний аналіз на вимогу. API не потрібен — лише керування браузером.
</Card>

<Card title="Автопідтримка в Slack" icon="slack">
  **@henrymascot** • `slack` `automation` `support`

Стежить за корпоративним каналом Slack, корисно відповідає та пересилає сповіщення в Telegram. Автономно виправив production-баг у розгорнутому застосунку без жодного запиту.
</Card>

</CardGroup>

<h2 id="knowledge-memory">Знання й пам’ять</h2>

<p className="showcase-section-intro">
  Системи, які індексують, шукають, запам’ятовують і міркують на основі особистих або командних знань.
</p>

<CardGroup cols={2}>

<Card title="Вивчення китайської з xuezh" icon="language" href="https://github.com/joshp123/xuezh">
  **@joshp123** • `learning` `voice` `skill`
  
  Рушій для вивчення китайської з відгуками щодо вимови та навчальними workflows через OpenClaw.
  
  <img src="/assets/showcase/xuezh-pronunciation.jpeg" alt="Відгук щодо вимови в xuezh" />
</Card>

<Card title="Сховище пам’яті WhatsApp" icon="vault">
  **Спільнота** • `memory` `transcription` `indexing`
  
  Імпортує повні експорти WhatsApp, транскрибує понад 1 тис. голосових повідомлень, звіряє їх із git log і виводить пов’язані markdown-звіти.
</Card>

<Card title="Семантичний пошук Karakeep" icon="magnifying-glass" href="https://github.com/jamesbrooksco/karakeep-semantic-search">
  **@jamesbrooksco** • `search` `vector` `bookmarks`
  
  Додає векторний пошук до закладок Karakeep за допомогою Qdrant + ембедингів OpenAI/Ollama.
</Card>

<Card title="Пам’ять Inside-Out-2" icon="brain">
  **Спільнота** • `memory` `beliefs` `self-model`
  
  Окремий менеджер пам’яті, який перетворює файли сесій на спогади → переконання → еволюційну модель себе.
</Card>

</CardGroup>

<h2 id="voice-phone">Голос і телефон</h2>

<p className="showcase-section-intro">
  Голосові точки входу, телефонні мости та workflows із великим обсягом транскрибування.
</p>

<CardGroup cols={2}>

<Card title="Телефонний міст Clawdia" icon="phone" href="https://github.com/alejandroOPI/clawdia-bridge">
  **@alejandroOPI** • `voice` `vapi` `bridge`
  
  Голосовий помічник Vapi ↔ HTTP-міст OpenClaw. Майже реальний час під час телефонних дзвінків з вашим агентом.
</Card>

<Card title="Транскрибування через OpenRouter" icon="microphone" href="https://clawhub.ai/obviyus/openrouter-transcribe">
  **@obviyus** • `transcription` `multilingual` `skill`

Багатомовне транскрибування аудіо через OpenRouter (Gemini тощо). Доступно в ClawHub.
</Card>

</CardGroup>

<h2 id="infrastructure-deployment">Інфраструктура й розгортання</h2>

<p className="showcase-section-intro">
  Пакування, розгортання та інтеграції, які спрощують запуск і розширення OpenClaw.
</p>

<CardGroup cols={2}>

<Card title="Доповнення для Home Assistant" icon="home" href="https://github.com/ngutman/openclaw-ha-addon">
  **@ngutman** • `homeassistant` `docker` `raspberry-pi`
  
  Gateway OpenClaw, що працює на Home Assistant OS, із підтримкою SSH-тунелю та постійним станом.
</Card>

<Card title="Навичка Home Assistant" icon="toggle-on" href="https://clawhub.ai/skills/homeassistant">
  **ClawHub** • `homeassistant` `skill` `automation`
  
  Керуйте й автоматизуйте пристрої Home Assistant природною мовою.
</Card>

<Card title="Пакування Nix" icon="snowflake" href="https://github.com/openclaw/nix-openclaw">
  **@openclaw** • `nix` `packaging` `deployment`
  
  Готова до використання nix-версія конфігурації OpenClaw для відтворюваних розгортань.
</Card>

<Card title="Календар CalDAV" icon="calendar" href="https://clawhub.ai/skills/caldav-calendar">
  **ClawHub** • `calendar` `caldav` `skill`
  
  Навичка календаря на базі khal/vdirsyncer. Самостійно розміщена інтеграція календаря.
</Card>

</CardGroup>

<h2 id="home-hardware">Дім і обладнання</h2>

<p className="showcase-section-intro">
  Фізичний бік OpenClaw: домівки, сенсори, камери, пилососи та інші пристрої.
</p>

<CardGroup cols={2}>

<Card title="Автоматизація GoHome" icon="house-signal" href="https://github.com/joshp123/gohome">
  **@joshp123** • `home` `nix` `grafana`
  
  Домашня автоматизація, нативна для Nix, з OpenClaw як інтерфейсом, а також красивими панелями Grafana.
  
  <img src="/assets/showcase/gohome-grafana.png" alt="Панель Grafana для GoHome" />
</Card>

<Card title="Пилосос Roborock" icon="robot" href="https://github.com/joshp123/gohome/tree/main/plugins/roborock">
  **@joshp123** • `vacuum` `iot` `plugin`
  
  Керуйте роботом-пилососом Roborock за допомогою природної розмови.
  
  <img src="/assets/showcase/roborock-screenshot.jpg" alt="Статус Roborock" />
</Card>

</CardGroup>

<h2 id="community-projects">Проєкти спільноти</h2>

<p className="showcase-section-intro">
  Речі, що виросли за межі одного workflow у ширші продукти або екосистеми.
</p>

<CardGroup cols={2}>

<Card title="Маркетплейс StarSwap" icon="star" href="https://star-swap.com/">
  **Спільнота** • `marketplace` `astronomy` `webapp`
  
  Повноцінний маркетплейс астрономічного обладнання. Створений за допомогою/навколо екосистеми OpenClaw.
</Card>

</CardGroup>

---

<h2 id="submit-your-project">Надіслати свій проєкт</h2>

<p className="showcase-section-intro">
  Якщо ви створюєте щось цікаве з OpenClaw, надсилайте. Якісні скриншоти й конкретні результати дуже допомагають.
</p>

Маєте чим поділитися? Ми будемо раді показати це!

<Steps>
  <Step title="Поділіться">
    Напишіть у [#self-promotion on Discord](https://discord.gg/clawd) або [твітніть @openclaw](https://x.com/openclaw)
  </Step>
  <Step title="Додайте подробиці">
    Розкажіть, що це робить, додайте посилання на репозиторій/демо, поділіться скриншотом, якщо він у вас є
  </Step>
  <Step title="Потрапте у добірку">
    Ми додамо найяскравіші проєкти на цю сторінку
  </Step>
</Steps>
