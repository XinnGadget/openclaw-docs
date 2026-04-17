---
read_when:
    - Відповіді на поширені запитання щодо налаштування, встановлення, онбордингу або підтримки під час виконання
    - Тріаж проблем, про які повідомляють користувачі, перед глибшим налагодженням
summary: Часті запитання про налаштування, конфігурацію та використання OpenClaw
title: Часті запитання
x-i18n:
    generated_at: "2026-04-12T18:22:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: d2a78d0fea9596625cc2753e6dc8cc42c2379a3a0c91729265eee0261fe53eaa
    source_path: help/faq.md
    workflow: 15
---

# Часті запитання

Швидкі відповіді плюс глибше усунення проблем для реальних сценаріїв налаштування (локальна розробка, VPS, multi-agent, OAuth/API-ключі, резервне перемикання моделей). Для діагностики під час виконання див. [Усунення проблем](/uk/gateway/troubleshooting). Повний довідник із конфігурації див. у [Конфігурація](/uk/gateway/configuration).

## Перші 60 секунд, якщо щось зламалося

1. **Швидкий статус (перша перевірка)**

   ```bash
   openclaw status
   ```

   Швидке локальне зведення: ОС + оновлення, доступність gateway/сервісу, agents/sessions, конфігурація провайдера + проблеми під час виконання (коли gateway доступний).

2. **Звіт, який можна вставити та поділитися ним**

   ```bash
   openclaw status --all
   ```

   Діагностика в режимі лише читання з хвостом логу (токени замасковано).

3. **Стан демона + порту**

   ```bash
   openclaw gateway status
   ```

   Показує runtime supervisor порівняно з досяжністю RPC, цільову URL-адресу probe і те, яку конфігурацію сервіс, імовірно, використовував.

4. **Глибокі probe-перевірки**

   ```bash
   openclaw status --deep
   ```

   Запускає live probe-перевірку стану gateway, зокрема перевірки channel, якщо це підтримується
   (потрібен доступний gateway). Див. [Health](/uk/gateway/health).

5. **Переглянути хвіст останнього логу**

   ```bash
   openclaw logs --follow
   ```

   Якщо RPC недоступний, використайте як запасний варіант:

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   Файлові логи відокремлені від сервісних логів; див. [Logging](/uk/logging) і [Усунення проблем](/uk/gateway/troubleshooting).

6. **Запустити doctor (виправлення)**

   ```bash
   openclaw doctor
   ```

   Виправляє/мігрує config/state + запускає перевірки стану. Див. [Doctor](/uk/gateway/doctor).

7. **Знімок gateway**

   ```bash
   openclaw health --json
   openclaw health --verbose   # показує цільову URL-адресу + шлях до config у разі помилок
   ```

   Запитує повний знімок у запущеного gateway (лише WS). Див. [Health](/uk/gateway/health).

## Швидкий старт і початкове налаштування

<AccordionGroup>
  <Accordion title="Я застряг, найшвидший спосіб зрушити з місця">
    Використайте локальний AI-агент, який може **бачити вашу машину**. Це набагато ефективніше, ніж питати
    в Discord, тому що більшість випадків "я застряг" — це **локальні проблеми конфігурації або середовища**,
    які віддалені помічники не можуть перевірити.

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    Ці інструменти можуть читати репозиторій, виконувати команди, перевіряти логи й допомагати виправити
    налаштування на рівні машини (PATH, сервіси, дозволи, файли автентифікації). Дайте їм **повну checkout-копію вихідного коду**
    через hackable (git) install:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Це встановлює OpenClaw **із git checkout**, тож агент може читати код + документацію та
    міркувати на основі точної версії, яку ви використовуєте. Ви завжди можете пізніше повернутися до stable,
    повторно запустивши інсталятор без `--install-method git`.

    Порада: попросіть агента **спланувати й контролювати** виправлення (крок за кроком), а потім виконати лише
    потрібні команди. Це зберігає зміни невеликими й полегшує аудит.

    Якщо ви виявили справжню помилку або виправлення, будь ласка, створіть GitHub issue або надішліть PR:
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    Почніть із цих команд (діліться виводом, коли просите про допомогу):

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    Що вони роблять:

    - `openclaw status`: швидкий знімок стану gateway/agent + базова config.
    - `openclaw models status`: перевіряє auth провайдера + доступність моделей.
    - `openclaw doctor`: перевіряє та виправляє поширені проблеми config/state.

    Інші корисні перевірки CLI: `openclaw status --all`, `openclaw logs --follow`,
    `openclaw gateway status`, `openclaw health --verbose`.

    Швидкий цикл налагодження: [Перші 60 секунд, якщо щось зламалося](#перші-60-секунд-якщо-щось-зламалося).
    Документація зі встановлення: [Install](/uk/install), [Прапорці інсталятора](/uk/install/installer), [Оновлення](/uk/install/updating).

  </Accordion>

  <Accordion title="Heartbeat постійно пропускається. Що означають причини пропуску?">
    Поширені причини пропуску Heartbeat:

    - `quiet-hours`: поза налаштованим вікном active-hours
    - `empty-heartbeat-file`: `HEARTBEAT.md` існує, але містить лише порожній каркас або лише заголовки
    - `no-tasks-due`: режим завдань `HEARTBEAT.md` активний, але жоден з інтервалів завдань ще не настав
    - `alerts-disabled`: уся видимість heartbeat вимкнена (`showOk`, `showAlerts` і `useIndicator` усі вимкнені)

    У режимі завдань часові позначки настання оновлюються лише після завершення
    реального запуску heartbeat. Пропущені запуски не позначають завдання як виконані.

    Документація: [Heartbeat](/uk/gateway/heartbeat), [Автоматизація та завдання](/uk/automation).

  </Accordion>

  <Accordion title="Рекомендований спосіб встановити й налаштувати OpenClaw">
    Репозиторій рекомендує запуск із вихідного коду та використання onboarding:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    Майстер також може автоматично зібрати ресурси UI. Після onboarding зазвичай Gateway запускається на порту **18789**.

    Із вихідного коду (contributors/dev):

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # автоматично встановлює залежності UI під час першого запуску
    openclaw onboard
    ```

    Якщо у вас ще немає глобального встановлення, запустіть через `pnpm openclaw onboard`.

  </Accordion>

  <Accordion title="Як відкрити dashboard після onboarding?">
    Майстер відкриває браузер із чистою URL-адресою dashboard (без токенів) одразу після onboarding, а також виводить посилання в підсумку. Залиште цю вкладку відкритою; якщо вона не запустилася, скопіюйте й вставте надруковану URL-адресу на тій самій машині.
  </Accordion>

  <Accordion title="Як автентифікувати dashboard на localhost і віддалено?">
    **Localhost (та сама машина):**

    - Відкрийте `http://127.0.0.1:18789/`.
    - Якщо запитується автентифікація shared secret, вставте налаштований токен або пароль у налаштуваннях Control UI.
    - Джерело токена: `gateway.auth.token` (або `OPENCLAW_GATEWAY_TOKEN`).
    - Джерело пароля: `gateway.auth.password` (або `OPENCLAW_GATEWAY_PASSWORD`).
    - Якщо shared secret ще не налаштовано, згенеруйте токен командою `openclaw doctor --generate-gateway-token`.

    **Не на localhost:**

    - **Tailscale Serve** (рекомендовано): залиште прив’язку до loopback, виконайте `openclaw gateway --tailscale serve`, відкрийте `https://<magicdns>/`. Якщо `gateway.auth.allowTailscale` має значення `true`, заголовки ідентичності задовольняють автентифікацію Control UI/WebSocket (без вставляння shared secret, за умови довіреного хоста gateway); HTTP API усе одно вимагають автентифікацію shared secret, якщо ви навмисно не використовуєте private-ingress `none` або trusted-proxy HTTP auth.
      Некоректні одночасні спроби автентифікації Serve від одного клієнта серіалізуються до того, як обмежувач failed-auth їх зафіксує, тому друга невдала повторна спроба вже може показати `retry later`.
    - **Прив’язка до tailnet**: виконайте `openclaw gateway --bind tailnet --token "<token>"` (або налаштуйте автентифікацію паролем), відкрийте `http://<tailscale-ip>:18789/`, а потім вставте відповідний shared secret у налаштування dashboard.
    - **Зворотний proxy з урахуванням ідентичності**: залиште Gateway за trusted proxy без loopback-прив’язки, налаштуйте `gateway.auth.mode: "trusted-proxy"`, а потім відкрийте URL-адресу proxy.
    - **SSH tunnel**: `ssh -N -L 18789:127.0.0.1:18789 user@host`, після чого відкрийте `http://127.0.0.1:18789/`. Автентифікація shared secret усе ще застосовується через tunnel; якщо буде запит, вставте налаштований токен або пароль.

    Див. [Dashboard](/web/dashboard) і [Веб-поверхні](/web) для режимів прив’язки та деталей автентифікації.

  </Accordion>

  <Accordion title="Чому є дві конфігурації затвердження exec для chat approvals?">
    Вони керують різними рівнями:

    - `approvals.exec`: пересилає запити на затвердження до chat destinations
    - `channels.<channel>.execApprovals`: робить цей channel нативним approval-клієнтом для exec approvals

    Політика host exec все одно залишається справжнім бар’єром затвердження. Конфігурація чату лише визначає, куди
    надходять запити на затвердження і як люди можуть на них відповідати.

    У більшості налаштувань вам **не** потрібні обидві:

    - Якщо chat уже підтримує команди й відповіді, `/approve` у тому самому чаті працює через спільний шлях.
    - Якщо підтримуваний нативний channel може безпечно визначити осіб, які затверджують, OpenClaw тепер автоматично вмикає нативні approvals із пріоритетом DM, коли `channels.<channel>.execApprovals.enabled` не задано або має значення `"auto"`.
    - Коли доступні нативні approval cards/buttons, цей нативний UI є основним шляхом; агент має включати ручну команду `/approve`, лише якщо результат інструмента каже, що chat approvals недоступні або ручне затвердження — єдиний шлях.
    - Використовуйте `approvals.exec` лише тоді, коли запити також потрібно пересилати до інших чатів або явних ops rooms.
    - Використовуйте `channels.<channel>.execApprovals.target: "channel"` або `"both"` лише тоді, коли ви явно хочете, щоб запити на затвердження публікувалися назад у вихідну room/topic.
    - Затвердження Plugin знову ж окремі: за замовчуванням вони використовують `/approve` у тому самому чаті, необов’язкове пересилання `approvals.plugin`, і лише деякі нативні channels додатково зберігають нативну обробку затверджень Plugin.

    Коротко: пересилання — для маршрутизації, конфігурація нативного клієнта — для більш зручного channel-specific UX.
    Див. [Exec Approvals](/uk/tools/exec-approvals).

  </Accordion>

  <Accordion title="Яке runtime мені потрібне?">
    Потрібен Node **>= 22**. Рекомендується `pnpm`. Bun **не рекомендується** для Gateway.
  </Accordion>

  <Accordion title="Чи працює це на Raspberry Pi?">
    Так. Gateway легкий — у документації вказано, що для персонального використання достатньо **512MB-1GB RAM**, **1 core** і приблизно **500MB**
    дискового простору, а також зазначено, що **Raspberry Pi 4 може його запускати**.

    Якщо вам потрібен додатковий запас (логи, медіа, інші сервіси), **рекомендується 2GB**, але це
    не жорсткий мінімум.

    Порада: невеликий Pi/VPS може хостити Gateway, а ви можете під’єднати **nodes** на ноутбуці/телефоні для
    локального екрана/камери/canvas або виконання команд. Див. [Nodes](/uk/nodes).

  </Accordion>

  <Accordion title="Чи є поради для встановлення на Raspberry Pi?">
    Коротко: це працює, але очікуйте шорсткостей.

    - Використовуйте **64-bit** ОС і Node >= 22.
    - Віддавайте перевагу **hackable (git) install**, щоб бачити логи й швидко оновлюватися.
    - Починайте без channels/skills, а потім додавайте їх по одному.
    - Якщо натрапите на дивні проблеми з бінарниками, зазвичай це проблема **ARM compatibility**.

    Документація: [Linux](/uk/platforms/linux), [Install](/uk/install).

  </Accordion>

  <Accordion title="Застряє на wake up my friend / onboarding не вилуплюється. Що робити?">
    Цей екран залежить від того, чи доступний і автентифікований Gateway. TUI також автоматично надсилає
    "Wake up, my friend!" під час першого hatch. Якщо ви бачите цей рядок **без відповіді**
    і токени залишаються на 0, agent так і не запустився.

    1. Перезапустіть Gateway:

    ```bash
    openclaw gateway restart
    ```

    2. Перевірте статус + auth:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. Якщо все ще зависає, виконайте:

    ```bash
    openclaw doctor
    ```

    Якщо Gateway віддалений, переконайтеся, що tunnel/Tailscale-з’єднання активне і що UI
    вказує на правильний Gateway. Див. [Віддалений доступ](/uk/gateway/remote).

  </Accordion>

  <Accordion title="Чи можу я перенести своє налаштування на нову машину (Mac mini), не проходячи onboarding заново?">
    Так. Скопіюйте **каталог state** і **workspace**, а потім один раз запустіть Doctor. Це
    збереже вашого бота **точно таким самим** (memory, історія session, auth і
    стан channel), якщо ви скопіюєте **обидва** розташування:

    1. Встановіть OpenClaw на нову машину.
    2. Скопіюйте `$OPENCLAW_STATE_DIR` (типово: `~/.openclaw`) зі старої машини.
    3. Скопіюйте ваш workspace (типово: `~/.openclaw/workspace`).
    4. Виконайте `openclaw doctor` і перезапустіть сервіс Gateway.

    Це зберігає config, профілі auth, облікові дані WhatsApp, sessions і memory. Якщо ви працюєте
    у віддаленому режимі, пам’ятайте, що session store і workspace належать хосту gateway.

    **Важливо:** якщо ви лише commit/push свій workspace до GitHub, ви створюєте
    резервну копію **memory + bootstrap-файлів**, але **не** історії session чи auth. Вони зберігаються
    у `~/.openclaw/` (наприклад, `~/.openclaw/agents/<agentId>/sessions/`).

    Пов’язане: [Міграція](/uk/install/migrating), [Де що зберігається на диску](#де-що-зберігається-на-диску),
    [Робочий простір agent](/uk/concepts/agent-workspace), [Doctor](/uk/gateway/doctor),
    [Віддалений режим](/uk/gateway/remote).

  </Accordion>

  <Accordion title="Де подивитися, що нового в останній версії?">
    Перегляньте changelog на GitHub:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Найновіші записи — угорі. Якщо верхній розділ позначено як **Unreleased**, наступний датований
    розділ — це остання випущена версія. Записи згруповано за **Highlights**, **Changes** і
    **Fixes** (плюс розділи з документацією/інші за потреби).

  </Accordion>

  <Accordion title="Не вдається відкрити docs.openclaw.ai (помилка SSL)">
    Деякі з’єднання Comcast/Xfinity помилково блокують `docs.openclaw.ai` через Xfinity
    Advanced Security. Вимкніть її або додайте `docs.openclaw.ai` до allowlist, а потім повторіть спробу.
    Будь ласка, допоможіть нам розблокувати сайт, повідомивши тут: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status).

    Якщо ви все ще не можете відкрити сайт, документація дзеркально доступна на GitHub:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="Різниця між stable і beta">
    **Stable** і **beta** — це **npm dist-tags**, а не окремі гілки коду:

    - `latest` = stable
    - `beta` = рання збірка для тестування

    Зазвичай stable-реліз спочатку потрапляє в **beta**, а потім явний
    крок просування переміщує цю саму версію до `latest`. Maintainers також можуть
    за потреби публікувати одразу в `latest`. Саме тому beta і stable можуть
    вказувати на **ту саму версію** після просування.

    Подивитися, що змінилося:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Однорядкові команди для встановлення і різницю між beta та dev див. в accordion нижче.

  </Accordion>

  <Accordion title="Як установити beta-версію і яка різниця між beta та dev?">
    **Beta** — це npm dist-tag `beta` (після просування може збігатися з `latest`).
    **Dev** — це рухома вершина `main` (git); під час публікації використовується npm dist-tag `dev`.

    Однорядкові команди (macOS/Linux):

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Інсталятор для Windows (PowerShell):
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    Докладніше: [Канали розробки](/uk/install/development-channels) і [Прапорці інсталятора](/uk/install/installer).

  </Accordion>

  <Accordion title="Як спробувати найсвіжіші збірки?">
    Є два варіанти:

    1. **Dev channel (git checkout):**

    ```bash
    openclaw update --channel dev
    ```

    Це перемикає вас на гілку `main` і оновлює з вихідного коду.

    2. **Hackable install (із сайту інсталятора):**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Це дає вам локальний репозиторій, який можна редагувати, а потім оновлювати через git.

    Якщо ви віддаєте перевагу чистому ручному clone, використайте:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    Документація: [Update](/cli/update), [Канали розробки](/uk/install/development-channels),
    [Install](/uk/install).

  </Accordion>

  <Accordion title="Скільки зазвичай триває встановлення й onboarding?">
    Приблизний орієнтир:

    - **Встановлення:** 2–5 хвилин
    - **Onboarding:** 5–15 хвилин залежно від того, скільки channels/models ви налаштовуєте

    Якщо все зависає, див. [Інсталятор завис?](#швидкий-старт-і-початкове-налаштування)
    і швидкий цикл налагодження в [Я застряг](#швидкий-старт-і-початкове-налаштування).

  </Accordion>

  <Accordion title="Інсталятор завис? Як отримати більше зворотного зв’язку?">
    Повторно запустіть інсталятор із **докладним виводом**:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    Установлення beta з докладним виводом:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    Для hackable (git) install:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    Еквівалент для Windows (PowerShell):

    ```powershell
    # install.ps1 поки що не має окремого прапорця -Verbose.
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    Більше варіантів: [Прапорці інсталятора](/uk/install/installer).

  </Accordion>

  <Accordion title="Під час встановлення у Windows пише git not found або openclaw not recognized">
    Дві поширені проблеми у Windows:

    **1) помилка npm spawn git / git not found**

    - Установіть **Git for Windows** і переконайтеся, що `git` є у вашому PATH.
    - Закрийте й знову відкрийте PowerShell, а потім повторно запустіть інсталятор.

    **2) після встановлення `openclaw` not recognized**

    - Ваш глобальний каталог npm bin відсутній у PATH.
    - Перевірте шлях:

      ```powershell
      npm config get prefix
      ```

    - Додайте цей каталог до вашого користувацького PATH (у Windows суфікс `\bin` не потрібен; у більшості систем це `%AppData%\npm`).
    - Після оновлення PATH закрийте й знову відкрийте PowerShell.

    Якщо ви хочете максимально плавне налаштування у Windows, використовуйте **WSL2** замість нативного Windows.
    Документація: [Windows](/uk/platforms/windows).

  </Accordion>

  <Accordion title="У Windows вивід exec показує спотворений китайський текст — що робити?">
    Зазвичай це невідповідність кодової сторінки консолі в нативних оболонках Windows.

    Симптоми:

    - вивід `system.run`/`exec` показує китайський текст як mojibake
    - та сама команда виглядає нормально в іншому профілі термінала

    Швидкий обхідний шлях у PowerShell:

    ```powershell
    chcp 65001
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    ```

    Потім перезапустіть Gateway і повторіть команду:

    ```powershell
    openclaw gateway restart
    ```

    Якщо це все ще відтворюється в останній версії OpenClaw, відстежуйте/повідомляйте тут:

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="Документація не відповіла на моє запитання — як отримати кращу відповідь?">
    Використайте **hackable (git) install**, щоб мати локально повний вихідний код і документацію, а потім запитайте
    свого бота (або Claude/Codex) _з цієї папки_, щоб він міг читати репозиторій і точно відповісти.

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Докладніше: [Install](/uk/install) і [Прапорці інсталятора](/uk/install/installer).

  </Accordion>

  <Accordion title="Як установити OpenClaw на Linux?">
    Коротка відповідь: дотримуйтеся інструкції для Linux, а потім запустіть onboarding.

    - Швидкий шлях для Linux + встановлення сервісу: [Linux](/uk/platforms/linux).
    - Повний покроковий посібник: [Початок роботи](/uk/start/getting-started).
    - Інсталятор + оновлення: [Встановлення й оновлення](/uk/install/updating).

  </Accordion>

  <Accordion title="Як установити OpenClaw на VPS?">
    Підійде будь-який Linux VPS. Установіть на сервері, а потім використовуйте SSH/Tailscale для доступу до Gateway.

    Посібники: [exe.dev](/uk/install/exe-dev), [Hetzner](/uk/install/hetzner), [Fly.io](/uk/install/fly).
    Віддалений доступ: [Gateway remote](/uk/gateway/remote).

  </Accordion>

  <Accordion title="Де посібники зі встановлення в хмарі/VPS?">
    У нас є **хаб хостингу** з поширеними провайдерами. Виберіть один і дотримуйтеся інструкції:

    - [VPS hosting](/uk/vps) (усі провайдери в одному місці)
    - [Fly.io](/uk/install/fly)
    - [Hetzner](/uk/install/hetzner)
    - [exe.dev](/uk/install/exe-dev)

    Як це працює в хмарі: **Gateway працює на сервері**, а ви звертаєтеся до нього
    з ноутбука/телефона через Control UI (або Tailscale/SSH). Ваші state + workspace
    зберігаються на сервері, тож вважайте хост джерелом істини та робіть його резервні копії.

    Ви можете під’єднувати **nodes** (Mac/iOS/Android/headless) до цього хмарного Gateway, щоб отримувати доступ до
    локального екрана/камери/canvas або запускати команди на ноутбуці, водночас
    тримаючи Gateway у хмарі.

    Хаб: [Platforms](/uk/platforms). Віддалений доступ: [Gateway remote](/uk/gateway/remote).
    Nodes: [Nodes](/uk/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="Чи можу я попросити OpenClaw оновити самого себе?">
    Коротка відповідь: **можливо, але не рекомендується**. Під час оновлення може перезапуститися
    Gateway (що розірве активну session), може знадобитися чистий git checkout, а також
    може з’явитися запит на підтвердження. Безпечніше запускати оновлення з оболонки як оператор.

    Використовуйте CLI:

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    Якщо автоматизація через agent все ж потрібна:

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    Документація: [Update](/cli/update), [Оновлення](/uk/install/updating).

  </Accordion>

  <Accordion title="Що насправді робить onboarding?">
    `openclaw onboard` — рекомендований шлях налаштування. У **локальному режимі** він проводить вас через:

    - **Налаштування model/auth** (OAuth провайдера, API-ключі, токен налаштування Anthropic, а також варіанти локальних моделей, як-от LM Studio)
    - Розташування **workspace** + bootstrap-файли
    - **Налаштування Gateway** (bind/port/auth/tailscale)
    - **Channels** (WhatsApp, Telegram, Discord, Mattermost, Signal, iMessage, а також bundled channel plugins, як-от QQ Bot)
    - **Встановлення демона** (LaunchAgent на macOS; user unit systemd на Linux/WSL2)
    - **Перевірки стану** і вибір **Skills**

    Він також попереджає, якщо налаштована model невідома або для неї відсутня auth.

  </Accordion>

  <Accordion title="Чи потрібна мені підписка Claude або OpenAI, щоб це запустити?">
    Ні. Ви можете запускати OpenClaw з **API-ключами** (Anthropic/OpenAI/інші) або з
    **лише локальними моделями**, щоб ваші дані залишалися на вашому пристрої. Підписки (Claude
    Pro/Max або OpenAI Codex) — це необов’язкові способи автентифікації цих провайдерів.

    Для Anthropic в OpenClaw практичний поділ такий:

    - **API-ключ Anthropic**: звичайна оплата Anthropic API
    - **Автентифікація Claude CLI / підпискою Claude в OpenClaw**: співробітники Anthropic
      повідомили нам, що таке використання знову дозволене, і OpenClaw розглядає використання `claude -p`
      як санкціоноване для цієї інтеграції, якщо Anthropic не опублікує нову
      політику

    Для довготривалих хостів gateway API-ключі Anthropic усе ще є
    більш передбачуваним варіантом. OAuth OpenAI Codex явно підтримується для зовнішніх
    інструментів на кшталт OpenClaw.

    OpenClaw також підтримує інші розміщені варіанти у стилі підписки, зокрема
    **Qwen Cloud Coding Plan**, **MiniMax Coding Plan** і
    **Z.AI / GLM Coding Plan**.

    Документація: [Anthropic](/uk/providers/anthropic), [OpenAI](/uk/providers/openai),
    [Qwen Cloud](/uk/providers/qwen),
    [MiniMax](/uk/providers/minimax), [GLM Models](/uk/providers/glm),
    [Локальні моделі](/uk/gateway/local-models), [Models](/uk/concepts/models).

  </Accordion>

  <Accordion title="Чи можу я використовувати підписку Claude Max без API-ключа?">
    Так.

    Співробітники Anthropic повідомили нам, що використання Claude CLI у стилі OpenClaw знову дозволене, тож
    OpenClaw вважає auth через підписку Claude та використання `claude -p` санкціонованими
    для цієї інтеграції, якщо Anthropic не опублікує нову політику. Якщо вам потрібне
    найпередбачуваніше налаштування на стороні сервера, натомість використовуйте API-ключ Anthropic.

  </Accordion>

  <Accordion title="Чи підтримуєте ви auth через підписку Claude (Claude Pro або Max)?">
    Так.

    Співробітники Anthropic повідомили нам, що таке використання знову дозволене, тож OpenClaw вважає
    повторне використання Claude CLI та використання `claude -p` санкціонованими для цієї інтеграції,
    якщо Anthropic не опублікує нову політику.

    Токен налаштування Anthropic все ще доступний як підтримуваний шлях токена OpenClaw, але тепер OpenClaw надає перевагу повторному використанню Claude CLI та `claude -p`, коли це можливо.
    Для production або multi-user навантажень auth через API-ключ Anthropic усе ще є
    безпечнішим і передбачуванішим вибором. Якщо вас цікавлять інші розміщені варіанти
    у стилі підписки в OpenClaw, див. [OpenAI](/uk/providers/openai), [Qwen / Model
    Cloud](/uk/providers/qwen), [MiniMax](/uk/providers/minimax) і [GLM
    Models](/uk/providers/glm).

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="Чому я бачу HTTP 429 rate_limit_error від Anthropic?">
Це означає, що вашу **квоту/ліміт швидкості Anthropic** вичерпано для поточного вікна. Якщо ви
використовуєте **Claude CLI**, дочекайтеся скидання вікна або оновіть свій план. Якщо ви
використовуєте **API-ключ Anthropic**, перевірте Anthropic Console
щодо використання/білінгу та за потреби збільште ліміти.

    Якщо повідомлення конкретно таке:
    `Extra usage is required for long context requests`, запит намагається використовувати
    1M context beta Anthropic (`context1m: true`). Це працює лише тоді, коли ваші
    облікові дані мають право на білінг long-context (білінг за API-ключем або
    шлях входу Claude в OpenClaw з увімкненим Extra Usage).

    Порада: задайте **резервну model**, щоб OpenClaw міг продовжувати відповідати, поки провайдер обмежений rate limit.
    Див. [Models](/cli/models), [OAuth](/uk/concepts/oauth) і
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/uk/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context).

  </Accordion>

  <Accordion title="Чи підтримується AWS Bedrock?">
    Так. OpenClaw має bundled провайдер **Amazon Bedrock (Converse)**. За наявності AWS env markers OpenClaw може автоматично виявити потоковий/текстовий каталог Bedrock і об’єднати його як неявного провайдера `amazon-bedrock`; інакше ви можете явно ввімкнути `plugins.entries.amazon-bedrock.config.discovery.enabled` або додати запис ручного провайдера. Див. [Amazon Bedrock](/uk/providers/bedrock) і [Провайдери моделей](/uk/providers/models). Якщо ви віддаєте перевагу керованому потоку ключів, OpenAI-compatible proxy перед Bedrock теж залишається коректним варіантом.
  </Accordion>

  <Accordion title="Як працює auth Codex?">
    OpenClaw підтримує **OpenAI Code (Codex)** через OAuth (вхід через ChatGPT). Onboarding може запустити OAuth-потік і за потреби встановить модель за замовчуванням `openai-codex/gpt-5.4`. Див. [Провайдери моделей](/uk/concepts/model-providers) і [Onboarding (CLI)](/uk/start/wizard).
  </Accordion>

  <Accordion title="Чому ChatGPT GPT-5.4 не розблоковує openai/gpt-5.4 в OpenClaw?">
    OpenClaw розглядає ці два шляхи окремо:

    - `openai-codex/gpt-5.4` = OAuth ChatGPT/Codex
    - `openai/gpt-5.4` = прямий API OpenAI Platform

    В OpenClaw вхід ChatGPT/Codex прив’язано до маршруту `openai-codex/*`,
    а не до прямого маршруту `openai/*`. Якщо вам потрібен прямий API-шлях у
    OpenClaw, задайте `OPENAI_API_KEY` (або еквівалентну config провайдера OpenAI).
    Якщо вам потрібен вхід ChatGPT/Codex в OpenClaw, використовуйте `openai-codex/*`.

  </Accordion>

  <Accordion title="Чому ліміти Codex OAuth можуть відрізнятися від ChatGPT web?">
    `openai-codex/*` використовує маршрут Codex OAuth, і його доступні вікна квот
    керуються OpenAI та залежать від плану. На практиці ці ліміти можуть відрізнятися від
    досвіду використання сайту/застосунку ChatGPT, навіть якщо обидва прив’язані до одного облікового запису.

    OpenClaw може показувати поточні видимі вікна використання/квот провайдера в
    `openclaw models status`, але не вигадує й не нормалізує
    права доступу ChatGPT web до прямого доступу API. Якщо вам потрібен прямий шлях білінгу/лімітів OpenAI Platform,
    використовуйте `openai/*` з API-ключем.

  </Accordion>

  <Accordion title="Чи підтримуєте ви auth через підписку OpenAI (Codex OAuth)?">
    Так. OpenClaw повністю підтримує **OAuth підписки OpenAI Code (Codex)**.
    OpenAI явно дозволяє використання OAuth-підписки в зовнішніх інструментах/робочих процесах
    на кшталт OpenClaw. Onboarding може запустити OAuth-потік за вас.

    Див. [OAuth](/uk/concepts/oauth), [Провайдери моделей](/uk/concepts/model-providers) і [Onboarding (CLI)](/uk/start/wizard).

  </Accordion>

  <Accordion title="Як налаштувати Gemini CLI OAuth?">
    Gemini CLI використовує **потік auth Plugin**, а не client id чи secret у `openclaw.json`.

    Кроки:

    1. Установіть Gemini CLI локально, щоб `gemini` був у `PATH`
       - Homebrew: `brew install gemini-cli`
       - npm: `npm install -g @google/gemini-cli`
    2. Увімкніть Plugin: `openclaw plugins enable google`
    3. Увійдіть: `openclaw models auth login --provider google-gemini-cli --set-default`
    4. Модель за замовчуванням після входу: `google-gemini-cli/gemini-3-flash-preview`
    5. Якщо запити не працюють, задайте `GOOGLE_CLOUD_PROJECT` або `GOOGLE_CLOUD_PROJECT_ID` на хості gateway

    Це зберігає OAuth-токени в auth profiles на хості gateway. Докладніше: [Провайдери моделей](/uk/concepts/model-providers).

  </Accordion>

  <Accordion title="Чи підходить локальна model для звичайних чатів?">
    Зазвичай ні. OpenClaw потребує великого контексту + сильної безпеки; малі картки обрізають і допускають витоки. Якщо вже потрібно, запускайте **найбільшу** збірку model, яку можете локально (LM Studio), і див. [/gateway/local-models](/uk/gateway/local-models). Менші/квантовані models підвищують ризик prompt injection — див. [Security](/uk/gateway/security).
  </Accordion>

  <Accordion title="Як утримувати трафік до hosted models у певному регіоні?">
    Вибирайте endpoints, прив’язані до регіону. OpenRouter надає варіанти з хостингом у США для MiniMax, Kimi та GLM; вибирайте варіант із хостингом у США, щоб зберігати дані в межах регіону. Ви все одно можете вказувати Anthropic/OpenAI поруч із ними, використовуючи `models.mode: "merge"`, щоб резервні варіанти залишалися доступними, водночас дотримуючись вибраного провайдера з прив’язкою до регіону.
  </Accordion>

  <Accordion title="Чи треба купувати Mac Mini, щоб установити це?">
    Ні. OpenClaw працює на macOS або Linux (Windows через WSL2). Mac mini не обов’язковий — деякі люди
    купують його як завжди ввімкнений хост, але також підійде невеликий VPS, домашній сервер або пристрій рівня Raspberry Pi.

    Mac потрібен лише **для інструментів тільки для macOS**. Для iMessage використовуйте [BlueBubbles](/uk/channels/bluebubbles) (рекомендовано) — сервер BlueBubbles працює на будь-якому Mac, а Gateway може працювати на Linux або деінде. Якщо вам потрібні інші інструменти лише для macOS, запускайте Gateway на Mac або під’єднайте macOS node.

    Документація: [BlueBubbles](/uk/channels/bluebubbles), [Nodes](/uk/nodes), [Mac remote mode](/uk/platforms/mac/remote).

  </Accordion>

  <Accordion title="Чи потрібен Mac mini для підтримки iMessage?">
    Вам потрібен **якийсь пристрій macOS**, на якому виконано вхід у Messages. Це **не обов’язково** має бути Mac mini —
    підійде будь-який Mac. **Використовуйте [BlueBubbles](/uk/channels/bluebubbles)** (рекомендовано) для iMessage — сервер BlueBubbles працює на macOS, тоді як Gateway може працювати на Linux або деінде.

    Поширені варіанти налаштування:

    - Запустіть Gateway на Linux/VPS, а сервер BlueBubbles — на будь-якому Mac, на якому виконано вхід у Messages.
    - Запустіть усе на Mac, якщо хочете найпростішу конфігурацію на одній машині.

    Документація: [BlueBubbles](/uk/channels/bluebubbles), [Nodes](/uk/nodes),
    [Mac remote mode](/uk/platforms/mac/remote).

  </Accordion>

  <Accordion title="Якщо я куплю Mac mini для запуску OpenClaw, чи можу я підключити його до MacBook Pro?">
    Так. **Mac mini може запускати Gateway**, а ваш MacBook Pro може підключатися як
    **node** (супутній пристрій). Nodes не запускають Gateway — вони надають додаткові
    можливості, як-от screen/camera/canvas і `system.run` на цьому пристрої.

    Поширений сценарій:

    - Gateway на Mac mini (завжди ввімкнений).
    - MacBook Pro запускає macOS app або хост node і під’єднується до Gateway.
    - Щоб побачити його, використовуйте `openclaw nodes status` / `openclaw nodes list`.

    Документація: [Nodes](/uk/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="Чи можна використовувати Bun?">
    Bun **не рекомендується**. Ми бачимо помилки runtime, особливо з WhatsApp і Telegram.
    Для стабільних gateway використовуйте **Node**.

    Якщо ви все ж хочете поекспериментувати з Bun, робіть це на неproduction gateway
    без WhatsApp/Telegram.

  </Accordion>

  <Accordion title="Telegram: що вказувати в allowFrom?">
    `channels.telegram.allowFrom` — це **Telegram user ID людини-відправника** (числовий). Це не ім’я користувача бота.

    Onboarding приймає введення `@username` і перетворює його на числовий ID, але авторизація OpenClaw використовує лише числові ID.

    Безпечніше (без стороннього бота):

    - Напишіть своєму боту в DM, потім виконайте `openclaw logs --follow` і прочитайте `from.id`.

    Офіційний Bot API:

    - Напишіть своєму боту в DM, потім викличте `https://api.telegram.org/bot<bot_token>/getUpdates` і прочитайте `message.from.id`.

    Сторонні варіанти (менш приватні):

    - Напишіть у DM `@userinfobot` або `@getidsbot`.

    Див. [/channels/telegram](/uk/channels/telegram#access-control-and-activation).

  </Accordion>

  <Accordion title="Чи можуть кілька людей використовувати один номер WhatsApp із різними інстансами OpenClaw?">
    Так, через **маршрутизацію multi-agent**. Прив’яжіть **DM** WhatsApp кожного відправника (peer `kind: "direct"`, E.164 відправника, наприклад `+15551234567`) до різного `agentId`, щоб кожна людина мала власний workspace і session store. Відповіді все одно надсилатимуться з **того самого облікового запису WhatsApp**, а керування доступом до DM (`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`) є глобальним для кожного облікового запису WhatsApp. Див. [Маршрутизація Multi-Agent](/uk/concepts/multi-agent) і [WhatsApp](/uk/channels/whatsapp).
  </Accordion>

  <Accordion title='Чи можу я запустити agent "швидкий чат" і agent "Opus для кодування"?'>
    Так. Використовуйте маршрутизацію multi-agent: призначте кожному agent власну model за замовчуванням, а потім прив’яжіть вхідні маршрути (обліковий запис провайдера або конкретні peers) до кожного agent. Приклад config є в [Маршрутизація Multi-Agent](/uk/concepts/multi-agent). Див. також [Models](/uk/concepts/models) і [Конфігурація](/uk/gateway/configuration).
  </Accordion>

  <Accordion title="Чи працює Homebrew на Linux?">
    Так. Homebrew підтримує Linux (Linuxbrew). Швидке налаштування:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    Якщо ви запускаєте OpenClaw через systemd, переконайтеся, що PATH сервісу містить `/home/linuxbrew/.linuxbrew/bin` (або ваш префікс brew), щоб інструменти, встановлені через `brew`, визначалися в оболонках без входу.
    Останні збірки також додають попереду поширені каталоги user bin у Linux systemd services (наприклад, `~/.local/bin`, `~/.npm-global/bin`, `~/.local/share/pnpm`, `~/.bun/bin`) і враховують `PNPM_HOME`, `NPM_CONFIG_PREFIX`, `BUN_INSTALL`, `VOLTA_HOME`, `ASDF_DATA_DIR`, `NVM_DIR` і `FNM_DIR`, якщо їх задано.

  </Accordion>

  <Accordion title="Різниця між hackable git install і npm install">
    - **Hackable (git) install:** повний checkout вихідного коду, можна редагувати, найкраще для contributors.
      Ви локально запускаєте збірки й можете вносити зміни в код/документацію.
    - **npm install:** глобальне встановлення CLI, без репозиторію, найкраще для сценарію "просто запустити".
      Оновлення надходять із npm dist-tags.

    Документація: [Початок роботи](/uk/start/getting-started), [Оновлення](/uk/install/updating).

  </Accordion>

  <Accordion title="Чи можу я пізніше перемикатися між npm і git install?">
    Так. Установіть інший варіант, а потім запустіть Doctor, щоб сервіс gateway вказував на нову точку входу.
    Це **не видаляє ваші дані** — змінюється лише встановлений код OpenClaw. Ваш state
    (`~/.openclaw`) і workspace (`~/.openclaw/workspace`) залишаються недоторканими.

    З npm на git:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    openclaw doctor
    openclaw gateway restart
    ```

    З git на npm:

    ```bash
    npm install -g openclaw@latest
    openclaw doctor
    openclaw gateway restart
    ```

    Doctor виявляє невідповідність точки входу сервісу gateway і пропонує переписати config сервісу відповідно до поточного встановлення (використовуйте `--repair` в автоматизації).

    Поради щодо резервного копіювання: див. [Стратегія резервного копіювання](#де-що-зберігається-на-диску).

  </Accordion>

  <Accordion title="Чи варто запускати Gateway на ноутбуці чи на VPS?">
    Коротка відповідь: **якщо вам потрібна надійність 24/7, використовуйте VPS**. Якщо вам потрібен
    найменший тертя і вас влаштовують сон/перезапуски, запускайте локально.

    **Ноутбук (локальний Gateway)**

    - **Переваги:** без витрат на сервер, прямий доступ до локальних файлів, видиме вікно браузера.
    - **Недоліки:** сон/обриви мережі = роз’єднання, оновлення/перезавантаження ОС переривають роботу, машина має залишатися активною.

    **VPS / хмара**

    - **Переваги:** завжди ввімкнений, стабільна мережа, немає проблем через сон ноутбука, легше підтримувати безперервну роботу.
    - **Недоліки:** часто працює без GUI (використовуйте знімки екрана), доступ лише до віддалених файлів, для оновлень потрібен SSH.

    **Примітка щодо OpenClaw:** WhatsApp/Telegram/Slack/Mattermost/Discord чудово працюють із VPS. Єдиний реальний компроміс — **headless browser** проти видимого вікна. Див. [Browser](/uk/tools/browser).

    **Рекомендований варіант за замовчуванням:** VPS, якщо у вас раніше були відключення gateway. Локальний запуск чудово підходить, коли ви активно користуєтеся Mac і хочете мати доступ до локальних файлів або автоматизації UI з видимим браузером.

  </Accordion>

  <Accordion title="Наскільки важливо запускати OpenClaw на виділеній машині?">
    Це не обов’язково, але **рекомендується для надійності та ізоляції**.

    - **Виділений хост (VPS/Mac mini/Pi):** завжди ввімкнений, менше переривань через сон/перезавантаження, чистіші дозволи, легше підтримувати безперервну роботу.
    - **Спільний ноутбук/настільний ПК:** цілком нормально для тестування й активного використання, але очікуйте пауз, коли машина засинає або оновлюється.

    Якщо ви хочете отримати найкраще з обох світів, тримайте Gateway на виділеному хості, а свій ноутбук під’єднайте як **node** для локальних інструментів screen/camera/exec. Див. [Nodes](/uk/nodes).
    Рекомендації з безпеки див. у [Security](/uk/gateway/security).

  </Accordion>

  <Accordion title="Які мінімальні вимоги до VPS і яка ОС рекомендується?">
    OpenClaw легкий. Для базового Gateway + одного chat channel:

    - **Абсолютний мінімум:** 1 vCPU, 1GB RAM, ~500MB диска.
    - **Рекомендовано:** 1–2 vCPU, 2GB RAM або більше із запасом (логи, медіа, кілька channels). Інструменти Node та автоматизація браузера можуть вимагати багато ресурсів.

    ОС: використовуйте **Ubuntu LTS** (або будь-який сучасний Debian/Ubuntu). Шлях встановлення для Linux найкраще протестовано саме там.

    Документація: [Linux](/uk/platforms/linux), [VPS hosting](/uk/vps).

  </Accordion>

  <Accordion title="Чи можна запускати OpenClaw у VM і які вимоги?">
    Так. Ставтеся до VM так само, як до VPS: вона має бути завжди ввімкнена, доступна та мати достатньо
    RAM для Gateway і всіх channels, які ви вмикаєте.

    Базові рекомендації:

    - **Абсолютний мінімум:** 1 vCPU, 1GB RAM.
    - **Рекомендовано:** 2GB RAM або більше, якщо ви використовуєте кілька channels, автоматизацію браузера чи медіаінструменти.
    - **ОС:** Ubuntu LTS або інший сучасний Debian/Ubuntu.

    Якщо ви працюєте у Windows, **WSL2 — найпростіше налаштування у стилі VM** і має найкращу
    сумісність з інструментами. Див. [Windows](/uk/platforms/windows), [VPS hosting](/uk/vps).
    Якщо ви запускаєте macOS у VM, див. [macOS VM](/uk/install/macos-vm).

  </Accordion>
</AccordionGroup>

## Що таке OpenClaw?

<AccordionGroup>
  <Accordion title="Що таке OpenClaw, в одному абзаці?">
    OpenClaw — це персональний AI-помічник, який ви запускаєте на власних пристроях. Він відповідає в месенджерах, якими ви вже користуєтеся (WhatsApp, Telegram, Slack, Mattermost, Discord, Google Chat, Signal, iMessage, WebChat, а також bundled channel plugins, як-от QQ Bot) і також може працювати з голосом + live Canvas на підтримуваних платформах. **Gateway** — це постійно активна control plane; помічник і є продуктом.
  </Accordion>

  <Accordion title="Ціннісна пропозиція">
    OpenClaw — це не "просто обгортка для Claude". Це **локально-орієнтована control plane**, яка дає змогу запускати
    потужного помічника на **вашому власному обладнанні**, доступного з чат-застосунків, якими ви вже користуєтеся, з
    sessions зі станом, memory та інструментами — без передачі контролю над вашими процесами
    розміщеному SaaS.

    Основні переваги:

    - **Ваші пристрої, ваші дані:** запускайте Gateway де завгодно (Mac, Linux, VPS) і зберігайте
      workspace + історію session локально.
    - **Реальні channels, а не веб-пісочниця:** WhatsApp/Telegram/Slack/Discord/Signal/iMessage тощо,
      а також мобільний голос і Canvas на підтримуваних платформах.
    - **Незалежність від model:** використовуйте Anthropic, OpenAI, MiniMax, OpenRouter тощо, з маршрутизацією
      і резервним перемиканням на рівні agent.
    - **Лише локальний варіант:** запускайте локальні models, щоб **усі дані могли залишатися на вашому пристрої**, якщо ви цього хочете.
    - **Маршрутизація multi-agent:** окремі agents для channel, облікового запису чи завдання, кожен зі своїм
      workspace і параметрами за замовчуванням.
    - **Відкритий код і можливість змінювати:** перевіряйте, розширюйте та розміщуйте самостійно без прив’язки до постачальника.

    Документація: [Gateway](/uk/gateway), [Channels](/uk/channels), [Multi-agent](/uk/concepts/multi-agent),
    [Memory](/uk/concepts/memory).

  </Accordion>

  <Accordion title="Я щойно все налаштував — що мені зробити спочатку?">
    Хороші перші проєкти:

    - Створити вебсайт (WordPress, Shopify або простий статичний сайт).
    - Прототипувати мобільний застосунок (структура, екрани, план API).
    - Упорядкувати файли та папки (очищення, іменування, тегування).
    - Підключити Gmail і автоматизувати зведення або подальші дії.

    Він може виконувати великі завдання, але найкраще працює, коли ви ділите їх на фази та
    використовуєте sub agents для паралельної роботи.

  </Accordion>

  <Accordion title="Які п’ять основних повсякденних сценаріїв використання OpenClaw?">
    Повсякденна користь зазвичай виглядає так:

    - **Персональні зведення:** підсумки пошти, календаря та новин, які вас цікавлять.
    - **Дослідження та чернетки:** швидкий пошук інформації, підсумки та перші чернетки листів або документів.
    - **Нагадування та подальші дії:** поштовхи та чеклісти на основі Cron або Heartbeat.
    - **Автоматизація браузера:** заповнення форм, збір даних і повторення веб-завдань.
    - **Координація між пристроями:** надішліть завдання з телефона, дайте Gateway виконати його на сервері й отримайте результат назад у чаті.

  </Accordion>

  <Accordion title="Чи може OpenClaw допомогти з генерацією лідів, аутричем, рекламою та блогами для SaaS?">
    Так — для **дослідження, кваліфікації та підготовки чернеток**. Він може сканувати сайти, створювати короткі списки,
    підсумовувати інформацію про потенційних клієнтів і писати чернетки аутричу або рекламних текстів.

    Для **аутричу чи запуску реклами** залишайте людину в циклі. Уникайте спаму, дотримуйтеся місцевих законів і
    правил платформи та перевіряйте все перед надсиланням. Найбезпечніший підхід — нехай
    OpenClaw готує чернетку, а ви її затверджуєте.

    Документація: [Security](/uk/gateway/security).

  </Accordion>

  <Accordion title="Які переваги порівняно з Claude Code для веброзробки?">
    OpenClaw — це **персональний помічник** і шар координації, а не заміна IDE. Використовуйте
    Claude Code або Codex для найшвидшого прямого циклу кодування всередині репозиторію. Використовуйте OpenClaw, коли вам
    потрібні довготривала memory, доступ із різних пристроїв та оркестрація інструментів.

    Переваги:

    - **Постійна memory + workspace** між sessions
    - **Доступ із різних платформ** (WhatsApp, Telegram, TUI, WebChat)
    - **Оркестрація інструментів** (browser, files, scheduling, hooks)
    - **Завжди ввімкнений Gateway** (працює на VPS, взаємодія звідусіль)
    - **Nodes** для локальних browser/screen/camera/exec

    Вітрина: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills і автоматизація

<AccordionGroup>
  <Accordion title="Як налаштовувати skills, не забруднюючи репозиторій?">
    Використовуйте керовані override замість редагування копії в репозиторії. Розміщуйте свої зміни в `~/.openclaw/skills/<name>/SKILL.md` (або додайте папку через `skills.load.extraDirs` у `~/.openclaw/openclaw.json`). Пріоритет такий: `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs`, тож керовані override все одно мають вищий пріоритет за bundled skills без змін у git. Якщо вам потрібно, щоб skill було встановлено глобально, але видно лише деяким agents, зберігайте спільну копію в `~/.openclaw/skills` і керуйте видимістю через `agents.defaults.skills` та `agents.list[].skills`. Лише зміни, варті upstream, мають жити в репозиторії та надсилатися як PR.
  </Accordion>

  <Accordion title="Чи можу я завантажувати skills з користувацької папки?">
    Так. Додавайте додаткові каталоги через `skills.load.extraDirs` у `~/.openclaw/openclaw.json` (найнижчий пріоритет). Пріоритет за замовчуванням: `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs`. `clawhub` за замовчуванням встановлює в `./skills`, що OpenClaw трактує як `<workspace>/skills` під час наступної session. Якщо skill має бути видимий лише певним agents, поєднайте це з `agents.defaults.skills` або `agents.list[].skills`.
  </Accordion>

  <Accordion title="Як використовувати різні models для різних завдань?">
    На сьогодні підтримуються такі шаблони:

    - **Cron jobs**: ізольовані завдання можуть задавати override `model` для кожного завдання.
    - **Sub-agents**: спрямовуйте завдання до окремих agents з різними models за замовчуванням.
    - **Перемикання на вимогу**: використовуйте `/model`, щоб у будь-який момент змінити model поточної session.

    Див. [Cron jobs](/uk/automation/cron-jobs), [Маршрутизація Multi-Agent](/uk/concepts/multi-agent) і [Slash-команди](/uk/tools/slash-commands).

  </Accordion>

  <Accordion title="Бот зависає під час важкої роботи. Як це винести окремо?">
    Використовуйте **sub-agents** для довгих або паралельних завдань. Sub-agents працюють у власній session,
    повертають підсумок і не дають вашому основному чату зависати.

    Попросіть свого бота "spawn a sub-agent for this task" або використайте `/subagents`.
    Використовуйте `/status` у чаті, щоб бачити, що Gateway робить просто зараз (і чи він зайнятий).

    Порада щодо токенів: і довгі завдання, і sub-agents споживають токени. Якщо вартість важлива, задайте
    дешевшу model для sub-agents через `agents.defaults.subagents.model`.

    Документація: [Sub-agents](/uk/tools/subagents), [Фонові завдання](/uk/automation/tasks).

  </Accordion>

  <Accordion title="Як працюють прив’язані до thread session subagent у Discord?">
    Використовуйте прив’язки thread. Ви можете прив’язати Discord thread до subagent або цілі session, щоб подальші повідомлення в цьому thread залишалися в межах цієї прив’язаної session.

    Базовий процес:

    - Створіть через `sessions_spawn` з `thread: true` (і, за бажанням, `mode: "session"` для постійшого продовження).
    - Або прив’яжіть вручну через `/focus <target>`.
    - Використовуйте `/agents`, щоб переглянути стан прив’язки.
    - Використовуйте `/session idle <duration|off>` і `/session max-age <duration|off>`, щоб керувати автоматичним скасуванням фокуса.
    - Використовуйте `/unfocus`, щоб від’єднати thread.

    Потрібна config:

    - Глобальні параметри за замовчуванням: `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`.
    - Override для Discord: `channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`.
    - Автоматична прив’язка під час створення: задайте `channels.discord.threadBindings.spawnSubagentSessions: true`.

    Документація: [Sub-agents](/uk/tools/subagents), [Discord](/uk/channels/discord), [Довідник із конфігурації](/uk/gateway/configuration-reference), [Slash-команди](/uk/tools/slash-commands).

  </Accordion>

  <Accordion title="Subagent завершив роботу, але оновлення про завершення надійшло не туди або взагалі не було опубліковане. Що перевірити?">
    Спочатку перевірте визначений маршрут запитувача:

    - Доставка subagent у режимі completion віддає перевагу будь-якому прив’язаному thread або маршруту conversation, якщо такий існує.
    - Якщо джерело completion містить лише channel, OpenClaw використовує запасний маршрут із збереженого маршруту сесії запитувача (`lastChannel` / `lastTo` / `lastAccountId`), щоб пряма доставка все ще могла спрацювати.
    - Якщо немає ні прив’язаного маршруту, ні придатного збереженого маршруту, пряма доставка може завершитися невдачею, і результат замість негайної публікації в чаті перейде до доставки через queued session.
    - Некоректні або застарілі цілі все одно можуть примусово спричинити запасний перехід до queue або остаточну невдачу доставки.
    - Якщо остання видима відповідь assistant у дочірньому процесі — це точний тихий токен `NO_REPLY` / `no_reply` або точно `ANNOUNCE_SKIP`, OpenClaw навмисно приглушує оголошення замість публікації застарілого попереднього прогресу.
    - Якщо дочірній процес завершився за тайм-аутом після одних лише викликів інструментів, оголошення може згорнути це в короткий підсумок часткового прогресу замість відтворення сирого виводу інструментів.

    Налагодження:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    Документація: [Sub-agents](/uk/tools/subagents), [Фонові завдання](/uk/automation/tasks), [Session Tools](/uk/concepts/session-tool).

  </Accordion>

  <Accordion title="Cron або нагадування не спрацьовують. Що перевірити?">
    Cron виконується всередині процесу Gateway. Якщо Gateway не працює безперервно,
    заплановані завдання не запускатимуться.

    Чекліст:

    - Переконайтеся, що Cron увімкнено (`cron.enabled`) і `OPENCLAW_SKIP_CRON` не задано.
    - Перевірте, що Gateway працює 24/7 (без сну/перезапусків).
    - Перевірте налаштування часового поясу для завдання (`--tz` порівняно з часовим поясом хоста).

    Налагодження:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    Документація: [Cron jobs](/uk/automation/cron-jobs), [Автоматизація та завдання](/uk/automation).

  </Accordion>

  <Accordion title="Cron спрацював, але нічого не було надіслано в channel. Чому?">
    Спочатку перевірте режим доставки:

    - `--no-deliver` / `delivery.mode: "none"` означає, що зовнішнє повідомлення не очікується.
    - Відсутня або некоректна ціль оголошення (`channel` / `to`) означає, що runner пропустив вихідну доставку.
    - Збої auth channel (`unauthorized`, `Forbidden`) означають, що runner спробував доставити, але облікові дані це заблокували.
    - Тихий ізольований результат (`NO_REPLY` / `no_reply` only) вважається навмисно недоставлюваним, тож runner також приглушує запасну queued delivery.

    Для ізольованих Cron jobs фінальною доставкою керує runner. Від agent очікується
    повернення текстового підсумку для надсилання runner.
    `--no-deliver` зберігає цей результат внутрішнім; він не дозволяє agent натомість надсилати напряму через
    message tool.

    Налагодження:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Документація: [Cron jobs](/uk/automation/cron-jobs), [Фонові завдання](/uk/automation/tasks).

  </Accordion>

  <Accordion title="Чому ізольований запуск Cron перемкнув models або один раз повторився?">
    Зазвичай це шлях live-перемикання model, а не дубльоване планування.

    Ізольований Cron може зберегти передачу runtime model і повторити запуск, коли активний
    процес викидає `LiveSessionModelSwitchError`. Повторна спроба зберігає перемкнені
    provider/model, а якщо перемикання також включало новий override профілю auth, Cron
    теж зберігає його перед повтором.

    Пов’язані правила вибору:

    - Спочатку має пріоритет override model Gmail hook, якщо застосовно.
    - Потім `model` для конкретного завдання.
    - Потім будь-який збережений override model cron-session.
    - Потім звичайний вибір agent/default model.

    Цикл повторних спроб обмежений. Після початкової спроби плюс 2 повтори через перемикання
    Cron перериває виконання замість нескінченного циклу.

    Налагодження:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Документація: [Cron jobs](/uk/automation/cron-jobs), [cron CLI](/cli/cron).

  </Accordion>

  <Accordion title="Як установити Skills на Linux?">
    Використовуйте нативні команди `openclaw skills` або розміщуйте skills у своєму workspace. UI Skills для macOS недоступний на Linux.
    Переглядати skills можна на [https://clawhub.ai](https://clawhub.ai).

    ```bash
    openclaw skills search "calendar"
    openclaw skills search --limit 20
    openclaw skills install <skill-slug>
    openclaw skills install <skill-slug> --version <version>
    openclaw skills install <skill-slug> --force
    openclaw skills update --all
    openclaw skills list --eligible
    openclaw skills check
    ```

    Нативний `openclaw skills install` записує в каталог `skills/`
    активного workspace. Встановлюйте окремий CLI `clawhub`, лише якщо хочете публікувати або
    синхронізувати власні skills. Для спільних установлень між agents розміщуйте skill у
    `~/.openclaw/skills` і використовуйте `agents.defaults.skills` або
    `agents.list[].skills`, якщо хочете обмежити, які agents можуть його бачити.

  </Accordion>

  <Accordion title="Чи може OpenClaw запускати завдання за розкладом або безперервно у фоновому режимі?">
    Так. Використовуйте планувальник Gateway:

    - **Cron jobs** для запланованих або повторюваних завдань (зберігаються після перезапусків).
    - **Heartbeat** для періодичних перевірок "main session".
    - **Ізольовані jobs** для автономних agents, які публікують підсумки або доставляють їх у чати.

    Документація: [Cron jobs](/uk/automation/cron-jobs), [Автоматизація та завдання](/uk/automation),
    [Heartbeat](/uk/gateway/heartbeat).

  </Accordion>

  <Accordion title="Чи можу я запускати навички лише для Apple macOS з Linux?">
    Не напряму. Навички macOS обмежуються через `metadata.openclaw.os` плюс необхідні бінарники, а навички з’являються в системному prompt лише тоді, коли вони придатні на **хості Gateway**. На Linux навички лише для `darwin` (як-от `apple-notes`, `apple-reminders`, `things-mac`) не завантажаться, якщо ви не перевизначите це обмеження.

    У вас є три підтримувані варіанти:

    **Варіант A — запустити Gateway на Mac (найпростіше).**
    Запустіть Gateway там, де існують бінарники macOS, а потім підключайтеся з Linux у [віддаленому режимі](#gateway-порти-вже-запущені-та-віддалений-режим) або через Tailscale. Навички завантажаться звичайним чином, тому що хост Gateway — це macOS.

    **Варіант B — використати macOS node (без SSH).**
    Запустіть Gateway на Linux, під’єднайте macOS node (menubar app) і встановіть **Node Run Commands** у значення "Always Ask" або "Always Allow" на Mac. OpenClaw може вважати навички лише для macOS придатними, коли потрібні бінарники існують на node. Agent виконує ці навички через інструмент `nodes`. Якщо ви виберете "Always Ask", підтвердження "Always Allow" у prompt додасть цю команду до allowlist.

    **Варіант C — проксувати бінарники macOS через SSH (розширено).**
    Залиште Gateway на Linux, але налаштуйте так, щоб потрібні CLI-бінарники визначалися як SSH-обгортки, які виконуються на Mac. Потім перевизначте skill, щоб дозволити Linux і зберегти його придатність.

    1. Створіть SSH-обгортку для бінарника (приклад: `memo` для Apple Notes):

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. Додайте обгортку в `PATH` на хості Linux (наприклад, `~/bin/memo`).
    3. Перевизначте metadata skill (workspace або `~/.openclaw/skills`), щоб дозволити Linux:

       ```markdown
       ---
       name: apple-notes
       description: Керування Apple Notes через CLI memo на macOS.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. Почніть нову session, щоб знімок skills оновився.

  </Accordion>

  <Accordion title="Чи є у вас інтеграція з Notion або HeyGen?">
    Наразі вбудованої немає.

    Варіанти:

    - **Користувацький skill / Plugin:** найкраще для надійного доступу до API (і Notion, і HeyGen мають API).
    - **Автоматизація браузера:** працює без коду, але повільніше й менш надійно.

    Якщо ви хочете зберігати контекст окремо для кожного клієнта (робочі процеси agency), простий шаблон такий:

    - Одна сторінка Notion на кожного клієнта (контекст + вподобання + активна робота).
    - Попросіть agent отримувати цю сторінку на початку session.

    Якщо вам потрібна нативна інтеграція, створіть запит на нову функцію або зберіть skill,
    орієнтований на ці API.

    Установлення skills:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    Нативні встановлення потрапляють у каталог `skills/` активного workspace. Для спільних skills між agents розміщуйте їх у `~/.openclaw/skills/<name>/SKILL.md`. Якщо спільне встановлення мають бачити лише деякі agents, налаштуйте `agents.defaults.skills` або `agents.list[].skills`. Деякі skills очікують наявності бінарників, установлених через Homebrew; на Linux це означає Linuxbrew (див. запис FAQ про Homebrew на Linux вище). Див. [Skills](/uk/tools/skills), [Конфігурація Skills](/uk/tools/skills-config) і [ClawHub](/uk/tools/clawhub).

  </Accordion>

  <Accordion title="Як використовувати наявний увійшовший Chrome з OpenClaw?">
    Використовуйте вбудований профіль браузера `user`, який під’єднується через Chrome DevTools MCP:

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    Якщо вам потрібна власна назва, створіть явний профіль MCP:

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    Цей шлях локальний для хоста. Якщо Gateway працює деінде, або запустіть хост node на машині з браузером, або використовуйте віддалений CDP.

    Поточні обмеження для `existing-session` / `user`:

    - дії прив’язані до `ref`, а не до CSS-селекторів
    - завантаження файлів потребує `ref` / `inputRef` і наразі підтримує лише один файл за раз
    - `responsebody`, експорт PDF, перехоплення завантажень і пакетні дії все ще потребують керованого браузера або сирого профілю CDP

  </Accordion>
</AccordionGroup>

## Ізоляція та memory

<AccordionGroup>
  <Accordion title="Чи є окрема документація про ізоляцію?">
    Так. Див. [Ізоляція](/uk/gateway/sandboxing). Для налаштування, специфічного для Docker (повний gateway у Docker або образи sandbox), див. [Docker](/uk/install/docker).
  </Accordion>

  <Accordion title="Docker здається обмеженим — як увімкнути повні можливості?">
    Образ за замовчуванням орієнтований насамперед на безпеку та працює від імені користувача `node`, тому не
    містить системних пакетів, Homebrew чи bundled браузерів. Для повнішого налаштування:

    - Зберігайте `/home/node` через `OPENCLAW_HOME_VOLUME`, щоб кеші не зникали.
    - Вбудуйте системні залежності в образ через `OPENCLAW_DOCKER_APT_PACKAGES`.
    - Установіть браузери Playwright через bundled CLI:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - Задайте `PLAYWRIGHT_BROWSERS_PATH` і переконайтеся, що цей шлях зберігається.

    Документація: [Docker](/uk/install/docker), [Browser](/uk/tools/browser).

  </Accordion>

  <Accordion title="Чи можу я зберегти DM приватними, але зробити групи публічними/ізольованими з одним agent?">
    Так — якщо ваш приватний трафік — це **DM**, а публічний трафік — **groups**.

    Використовуйте `agents.defaults.sandbox.mode: "non-main"`, щоб sessions груп/channel (ключі не-main) працювали в Docker, тоді як main DM session залишалася на хості. Потім обмежте, які інструменти доступні в ізольованих sessions, через `tools.sandbox.tools`.

    Покрокове налаштування + приклад config: [Groups: особисті DM + публічні групи](/uk/channels/groups#pattern-personal-dms-public-groups-single-agent)

    Довідка щодо ключової config: [Конфігурація Gateway](/uk/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="Як прив’язати папку хоста до sandbox?">
    Установіть `agents.defaults.sandbox.docker.binds` у `["host:path:mode"]` (наприклад, `"/home/user/src:/src:ro"`). Глобальні прив’язки й прив’язки для окремого agent об’єднуються; прив’язки окремого agent ігноруються, коли `scope: "shared"`. Використовуйте `:ro` для всього чутливого й пам’ятайте, що прив’язки обходять межі файлової системи sandbox.

    OpenClaw перевіряє джерела bind як за нормалізованим шляхом, так і за canonical path, визначеним через найглибший наявний предок. Це означає, що виходи через symlink-батьківський каталог усе одно надійно блокуються, навіть коли останній сегмент шляху ще не існує, а перевірки allowed-root також застосовуються після розв’язання symlink.

    Приклади та примітки з безпеки див. у [Ізоляція](/uk/gateway/sandboxing#custom-bind-mounts) і [Sandbox vs Tool Policy vs Elevated](/uk/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check).

  </Accordion>

  <Accordion title="Як працює memory?">
    Memory OpenClaw — це просто Markdown-файли в workspace agent:

    - Щоденні нотатки в `memory/YYYY-MM-DD.md`
    - Добірні довгострокові нотатки в `MEMORY.md` (лише main/private sessions)

    OpenClaw також виконує **тихий flush memory перед Compaction**, щоб нагадати моделі
    записати стійкі нотатки перед автоматичним Compaction. Це запускається лише тоді, коли workspace
    доступний для запису (sandbox у режимі лише читання це пропускають). Див. [Memory](/uk/concepts/memory).

  </Accordion>

  <Accordion title="Memory постійно щось забуває. Як зробити, щоб це зберігалося?">
    Попросіть бота **записати факт у memory**. Довгострокові нотатки мають бути в `MEMORY.md`,
    короткостроковий контекст — у `memory/YYYY-MM-DD.md`.

    Це все ще область, яку ми покращуємо. Допомагає нагадувати моделі зберігати memory;
    вона знатиме, що робити. Якщо вона все одно забуває, перевірте, що Gateway використовує той самий
    workspace під час кожного запуску.

    Документація: [Memory](/uk/concepts/memory), [Робочий простір agent](/uk/concepts/agent-workspace).

  </Accordion>

  <Accordion title="Чи зберігається memory назавжди? Які є обмеження?">
    Файли memory живуть на диску й зберігаються, доки ви їх не видалите. Обмеженням є ваше
    сховище, а не модель. **Контекст session** усе ще обмежений вікном контексту
    моделі, тому довгі розмови можуть проходити через Compaction або обрізання. Саме тому
    існує пошук у memory — він повертає в контекст лише релевантні частини.

    Документація: [Memory](/uk/concepts/memory), [Контекст](/uk/concepts/context).

  </Accordion>

  <Accordion title="Чи потрібен для семантичного пошуку в memory API-ключ OpenAI?">
    Лише якщо ви використовуєте **OpenAI embeddings**. OAuth Codex покриває chat/completions і
    **не** надає доступу до embeddings, тому **вхід через Codex (OAuth або
    вхід через Codex CLI)** не допоможе для семантичного пошуку в memory. Для embeddings OpenAI
    усе одно потрібен справжній API-ключ (`OPENAI_API_KEY` або `models.providers.openai.apiKey`).

    Якщо ви явно не задаєте provider, OpenClaw автоматично вибирає provider, коли
    може визначити API-ключ (auth profiles, `models.providers.*.apiKey` або env vars).
    Він віддає перевагу OpenAI, якщо визначено ключ OpenAI, інакше Gemini, якщо ключ Gemini
    визначено, потім Voyage, потім Mistral. Якщо віддалений ключ недоступний, пошук у memory
    залишається вимкненим, доки ви його не налаштуєте. Якщо у вас налаштовано й наявний
    шлях до локальної моделі, OpenClaw
    віддає перевагу `local`. Ollama підтримується, якщо ви явно задаєте
    `memorySearch.provider = "ollama"`.

    Якщо ви хочете залишитися локально, задайте `memorySearch.provider = "local"` (і за бажанням
    `memorySearch.fallback = "none"`). Якщо вам потрібні embeddings Gemini, задайте
    `memorySearch.provider = "gemini"` і надайте `GEMINI_API_KEY` (або
    `memorySearch.remote.apiKey`). Ми підтримуємо embedding-моделі **OpenAI, Gemini, Voyage, Mistral, Ollama або local** —
    деталі налаштування див. у [Memory](/uk/concepts/memory).

  </Accordion>
</AccordionGroup>

## Де що зберігається на диску

<AccordionGroup>
  <Accordion title="Чи всі дані, які використовуються з OpenClaw, зберігаються локально?">
    Ні — **стан OpenClaw локальний**, але **зовнішні сервіси все одно бачать те, що ви їм надсилаєте**.

    - **Локально за замовчуванням:** sessions, файли memory, config і workspace живуть на хості Gateway
      (`~/.openclaw` + каталог вашого workspace).
    - **Віддалено за необхідністю:** повідомлення, які ви надсилаєте провайдерам моделей (Anthropic/OpenAI тощо), передаються
      до їхніх API, а chat-платформи (WhatsApp/Telegram/Slack тощо) зберігають дані повідомлень на
      своїх серверах.
    - **Ви керуєте слідом:** використання локальних моделей залишає prompt на вашій машині, але трафік
      channel все одно проходить через сервери відповідного channel.

    Пов’язане: [Робочий простір agent](/uk/concepts/agent-workspace), [Memory](/uk/concepts/memory).

  </Accordion>

  <Accordion title="Де OpenClaw зберігає свої дані?">
    Усе зберігається в `$OPENCLAW_STATE_DIR` (типово: `~/.openclaw`):

    | Path                                                            | Призначення                                                        |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | Основна config (JSON5)                                             |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | Застарілий імпорт OAuth (копіюється в auth profiles під час першого використання) |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | Auth profiles (OAuth, API-ключі та необов’язкові `keyRef`/`tokenRef`) |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | Необов’язковий file-backed payload секретів для провайдерів `file` SecretRef |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | Застарілий файл сумісності (статичні записи `api_key` очищуються)  |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | Стан провайдера (наприклад, `whatsapp/<accountId>/creds.json`)     |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | Стан для кожного agent (agentDir + sessions)                       |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | Історія розмов і стан (для кожного agent)                          |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | Метадані session (для кожного agent)                               |

    Застарілий шлях для single-agent: `~/.openclaw/agent/*` (мігрується через `openclaw doctor`).

    Ваш **workspace** (`AGENTS.md`, файли memory, skills тощо) зберігається окремо й налаштовується через `agents.defaults.workspace` (типово: `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title="Де мають зберігатися AGENTS.md / SOUL.md / USER.md / MEMORY.md?">
    Ці файли зберігаються в **workspace agent**, а не в `~/.openclaw`.

    - **Workspace (для кожного agent):** `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
      `MEMORY.md` (або застарілий запасний варіант `memory.md`, якщо `MEMORY.md` відсутній),
      `memory/YYYY-MM-DD.md`, необов’язковий `HEARTBEAT.md`.
    - **State dir (`~/.openclaw`)**: config, стан channel/provider, auth profiles, sessions, логи,
      і спільні skills (`~/.openclaw/skills`).

    Типовий workspace — `~/.openclaw/workspace`, налаштовується через:

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    Якщо бот "забуває" після перезапуску, переконайтеся, що Gateway використовує той самий
    workspace під час кожного запуску (і пам’ятайте: віддалений режим використовує **workspace хоста gateway**,
    а не вашого локального ноутбука).

    Порада: якщо ви хочете зберегти поведінку або вподобання надовго, попросіть бота **записати це в
    AGENTS.md або MEMORY.md**, а не покладатися на історію чату.

    Див. [Робочий простір agent](/uk/concepts/agent-workspace) і [Memory](/uk/concepts/memory).

  </Accordion>

  <Accordion title="Рекомендована стратегія резервного копіювання">
    Помістіть свій **workspace agent** у **приватний** git-репозиторій і зберігайте резервну копію десь
    у приватному місці (наприклад, GitHub private). Це збереже memory + файли AGENTS/SOUL/USER
    й дозволить пізніше відновити "розум" помічника.

    **Не** робіть commit нічого з `~/.openclaw` (облікові дані, sessions, токени або зашифровані payload секретів).
    Якщо вам потрібне повне відновлення, окремо зробіть резервну копію і workspace, і state directory
    (див. питання про міграцію вище).

    Документація: [Робочий простір agent](/uk/concepts/agent-workspace).

  </Accordion>

  <Accordion title="Як повністю видалити OpenClaw?">
    Див. окремий посібник: [Видалення](/uk/install/uninstall).
  </Accordion>

  <Accordion title="Чи можуть agents працювати поза workspace?">
    Так. Workspace — це **типовий cwd** і прив’язка для memory, а не жорсткий sandbox.
    Відносні шляхи розв’язуються всередині workspace, але абсолютні шляхи можуть звертатися до інших
    розташувань хоста, якщо sandbox не увімкнено. Якщо вам потрібна ізоляція, використовуйте
    [`agents.defaults.sandbox`](/uk/gateway/sandboxing) або налаштування sandbox для окремого agent. Якщо ви
    хочете, щоб репозиторій був типовим робочим каталогом, укажіть `workspace`
    цього agent на корінь репозиторію. Репозиторій OpenClaw — це лише вихідний код; тримайте
    workspace окремо, якщо тільки ви навмисно не хочете, щоб agent працював усередині нього.

    Приклад (репозиторій як типовий cwd):

    ```json5
    {
      agents: {
        defaults: {
          workspace: "~/Projects/my-repo",
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Віддалений режим: де зберігається session store?">
    Стан session належить **хосту gateway**. Якщо ви працюєте у віддаленому режимі, потрібне вам сховище session знаходиться на віддаленій машині, а не на вашому локальному ноутбуці. Див. [Керування session](/uk/concepts/session).
  </Accordion>
</AccordionGroup>

## Основи config

<AccordionGroup>
  <Accordion title="Який формат config? Де він знаходиться?">
    OpenClaw читає необов’язкову config **JSON5** з `$OPENCLAW_CONFIG_PATH` (типово: `~/.openclaw/openclaw.json`):

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    Якщо файл відсутній, використовуються відносно безпечні значення за замовчуванням (зокрема типовий workspace `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title='Я встановив gateway.bind: "lan" (або "tailnet"), і тепер нічого не слухає / UI каже unauthorized'>
    Прив’язки не до loopback **потребують коректного шляху auth gateway**. На практиці це означає:

    - auth через shared secret: токен або пароль
    - `gateway.auth.mode: "trusted-proxy"` за правильно налаштованим identity-aware reverse proxy не на loopback

    ```json5
    {
      gateway: {
        bind: "lan",
        auth: {
          mode: "token",
          token: "replace-me",
        },
      },
    }
    ```

    Примітки:

    - `gateway.remote.token` / `.password` **самі по собі** не вмикають локальну auth gateway.
    - Локальні шляхи виклику можуть використовувати `gateway.remote.*` як запасний варіант лише тоді, коли `gateway.auth.*` не задано.
    - Для auth через пароль задайте `gateway.auth.mode: "password"` плюс `gateway.auth.password` (або `OPENCLAW_GATEWAY_PASSWORD`).
    - Якщо `gateway.auth.token` / `gateway.auth.password` явно налаштовано через SecretRef і його не вдається розв’язати, розв’язання надійно завершується помилкою (без прихованого запасного варіанта через remote).
    - Налаштування Control UI через shared secret проходять автентифікацію через `connect.params.auth.token` або `connect.params.auth.password` (зберігаються в налаштуваннях app/UI). Режими з ідентичністю, як-от Tailscale Serve або `trusted-proxy`, натомість використовують заголовки запиту. Не розміщуйте shared secrets в URL.
    - З `gateway.auth.mode: "trusted-proxy"` reverse proxy loopback на тому самому хості **все одно** не задовольняють auth trusted-proxy. Trusted proxy має бути налаштованим джерелом не на loopback.

  </Accordion>

  <Accordion title="Чому тепер мені потрібен токен на localhost?">
    OpenClaw примусово вимагає auth gateway за замовчуванням, зокрема й на loopback. У звичайному типовому сценарії це означає auth через токен: якщо явний шлях auth не налаштовано, під час запуску gateway вибирається режим token і токен генерується автоматично, зберігаючись у `gateway.auth.token`, тож **локальні WS-клієнти мають проходити автентифікацію**. Це блокує інші локальні процеси від виклику Gateway.

    Якщо вам потрібен інший шлях auth, ви можете явно вибрати режим password (або, для identity-aware reverse proxy не на loopback, `trusted-proxy`). Якщо ви **справді** хочете відкритий loopback, явно задайте `gateway.auth.mode: "none"` у config. Doctor може згенерувати токен у будь-який момент: `openclaw doctor --generate-gateway-token`.

  </Accordion>

  <Accordion title="Чи потрібно перезапускати після зміни config?">
    Gateway відстежує config і підтримує hot-reload:

    - `gateway.reload.mode: "hybrid"` (типово): безпечно застосовує зміни на гарячу, а для критичних виконує перезапуск
    - також підтримуються `hot`, `restart`, `off`

  </Accordion>

  <Accordion title="Як вимкнути кумедні слогани в CLI?">
    Задайте `cli.banner.taglineMode` у config:

    ```json5
    {
      cli: {
        banner: {
          taglineMode: "off", // random | default | off
        },
      },
    }
    ```

    - `off`: приховує текст слогана, але залишає рядок із назвою banner/версією.
    - `default`: щоразу використовує `All your chats, one OpenClaw.`.
    - `random`: чергування кумедних/сезонних слоганів (типова поведінка).
    - Якщо ви не хочете banner взагалі, задайте env `OPENCLAW_HIDE_BANNER=1`.

  </Accordion>

  <Accordion title="Як увімкнути web search (і web fetch)?">
    `web_fetch` працює без API-ключа. `web_search` залежить від вибраного
    provider:

    - Провайдери на основі API, як-от Brave, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Perplexity і Tavily, вимагають звичайного налаштування API-ключа.
    - Ollama Web Search не потребує ключа, але використовує ваш налаштований хост Ollama і вимагає `ollama signin`.
    - DuckDuckGo не потребує ключа, але це неофіційна інтеграція на основі HTML.
    - SearXNG не потребує ключа/може бути self-hosted; налаштуйте `SEARXNG_BASE_URL` або `plugins.entries.searxng.config.webSearch.baseUrl`.

    **Рекомендовано:** виконайте `openclaw configure --section web` і виберіть provider.
    Альтернативи через середовище:

    - Brave: `BRAVE_API_KEY`
    - Exa: `EXA_API_KEY`
    - Firecrawl: `FIRECRAWL_API_KEY`
    - Gemini: `GEMINI_API_KEY`
    - Grok: `XAI_API_KEY`
    - Kimi: `KIMI_API_KEY` або `MOONSHOT_API_KEY`
    - MiniMax Search: `MINIMAX_CODE_PLAN_KEY`, `MINIMAX_CODING_API_KEY` або `MINIMAX_API_KEY`
    - Perplexity: `PERPLEXITY_API_KEY` або `OPENROUTER_API_KEY`
    - SearXNG: `SEARXNG_BASE_URL`
    - Tavily: `TAVILY_API_KEY`

    ```json5
    {
      plugins: {
        entries: {
          brave: {
            config: {
              webSearch: {
                apiKey: "BRAVE_API_KEY_HERE",
              },
            },
          },
        },
        },
        tools: {
          web: {
            search: {
              enabled: true,
              provider: "brave",
              maxResults: 5,
            },
            fetch: {
              enabled: true,
              provider: "firecrawl", // необов’язково; пропустіть для auto-detect
            },
          },
        },
    }
    ```

    Конфігурація web-search, специфічна для provider, тепер розміщується в `plugins.entries.<plugin>.config.webSearch.*`.
    Застарілі шляхи provider `tools.web.search.*` усе ще тимчасово завантажуються для сумісності, але їх не слід використовувати в нових config.
    Запасна config web-fetch Firecrawl розміщується в `plugins.entries.firecrawl.config.webFetch.*`.

    Примітки:

    - Якщо ви використовуєте allowlist, додайте `web_search`/`web_fetch`/`x_search` або `group:web`.
    - `web_fetch` увімкнено за замовчуванням (якщо його явно не вимкнено).
    - Якщо `tools.web.fetch.provider` пропущено, OpenClaw автоматично визначає першого готового запасного provider fetch зі доступних облікових даних. Наразі bundled provider — це Firecrawl.
    - Демони читають env vars з `~/.openclaw/.env` (або із середовища сервісу).

    Документація: [Web tools](/uk/tools/web).

  </Accordion>

  <Accordion title="config.apply стер мою config. Як відновитися і як цього уникнути?">
    `config.apply` замінює **всю config цілком**. Якщо ви надсилаєте частковий об’єкт, усе
    інше видаляється.

    Відновлення:

    - Відновіть із резервної копії (git або скопійований `~/.openclaw/openclaw.json`).
    - Якщо резервної копії немає, повторно запустіть `openclaw doctor` і знову налаштуйте channels/models.
    - Якщо це було неочікувано, створіть bug report і додайте свою останню відому config або будь-яку резервну копію.
    - Локальний coding agent часто може відновити робочу config із логів або історії.

    Як уникнути:

    - Використовуйте `openclaw config set` для невеликих змін.
    - Використовуйте `openclaw configure` для інтерактивного редагування.
    - Спочатку використовуйте `config.schema.lookup`, коли ви не впевнені в точному шляху чи формі поля; він повертає вузол неглибокої schema плюс підсумки безпосередніх дочірніх елементів для покрокового заглиблення.
    - Використовуйте `config.patch` для часткових редагувань через RPC; залишайте `config.apply` лише для повної заміни config.
    - Якщо ви використовуєте інструмент `gateway` лише для owner з запуску agent, він усе одно відхилятиме записи в `tools.exec.ask` / `tools.exec.security` (зокрема застарілі псевдоніми `tools.bash.*`, які нормалізуються до тих самих захищених шляхів exec).

    Документація: [Config](/cli/config), [Configure](/cli/configure), [Doctor](/uk/gateway/doctor).

  </Accordion>

  <Accordion title="Як запустити центральний Gateway зі спеціалізованими workers на різних пристроях?">
    Типовий шаблон — **один Gateway** (наприклад, Raspberry Pi) плюс **nodes** і **agents**:

    - **Gateway (центральний):** керує channels (Signal/WhatsApp), маршрутизацією і sessions.
    - **Nodes (пристрої):** Mac/iOS/Android підключаються як периферія і надають локальні інструменти (`system.run`, `canvas`, `camera`).
    - **Agents (workers):** окремі "мізки"/workspace для спеціальних ролей (наприклад, "Hetzner ops", "Особисті дані").
    - **Sub-agents:** запускають фонову роботу з main agent, коли вам потрібен паралелізм.
    - **TUI:** підключається до Gateway і перемикає agents/sessions.

    Документація: [Nodes](/uk/nodes), [Віддалений доступ](/uk/gateway/remote), [Маршрутизація Multi-Agent](/uk/concepts/multi-agent), [Sub-agents](/uk/tools/subagents), [TUI](/web/tui).

  </Accordion>

  <Accordion title="Чи може браузер OpenClaw працювати в headless-режимі?">
    Так. Це параметр config:

    ```json5
    {
      browser: { headless: true },
      agents: {
        defaults: {
          sandbox: { browser: { headless: true } },
        },
      },
    }
    ```

    Типове значення — `false` (із видимим вікном). Headless-режим з більшою ймовірністю викликає anti-bot перевірки на деяких сайтах. Див. [Browser](/uk/tools/browser).

    Headless використовує **той самий рушій Chromium** і працює для більшості сценаріїв автоматизації (форми, кліки, scraping, входи). Основні відмінності:

    - Немає видимого вікна браузера (використовуйте знімки екрана, якщо потрібна візуалізація).
    - Деякі сайти суворіше ставляться до автоматизації в headless-режимі (CAPTCHA, anti-bot).
      Наприклад, X/Twitter часто блокує headless sessions.

  </Accordion>

  <Accordion title="Як використовувати Brave для керування браузером?">
    Установіть `browser.executablePath` на ваш бінарник Brave (або будь-який браузер на базі Chromium) і перезапустіть Gateway.
    Повні приклади config див. у [Browser](/uk/tools/browser#use-brave-or-another-chromium-based-browser).
  </Accordion>
</AccordionGroup>

## Віддалені gateway і nodes

<AccordionGroup>
  <Accordion title="Як команди проходять між Telegram, gateway і nodes?">
    Повідомлення Telegram обробляє **gateway**. Gateway запускає agent і
    лише потім викликає nodes через **Gateway WebSocket**, коли потрібен інструмент node:

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    Nodes не бачать вхідний трафік provider; вони отримують лише виклики node RPC.

  </Accordion>

  <Accordion title="Як мій agent може отримати доступ до мого комп’ютера, якщо Gateway розміщено віддалено?">
    Коротка відповідь: **під’єднайте свій комп’ютер як node**. Gateway працює деінде, але може
    викликати інструменти `node.*` (екран, камера, система) на вашій локальній машині через Gateway WebSocket.

    Типове налаштування:

    1. Запустіть Gateway на завжди ввімкненому хості (VPS/домашній сервер).
    2. Підключіть хост Gateway і ваш комп’ютер до однієї tailnet.
    3. Переконайтеся, що WS Gateway доступний (прив’язка tailnet або SSH tunnel).
    4. Відкрийте локально macOS app і підключіться в режимі **Remote over SSH** (або напряму через tailnet),
       щоб він міг зареєструватися як node.
    5. Схваліть node на Gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Окремий TCP bridge не потрібен; nodes підключаються через Gateway WebSocket.

    Нагадування щодо безпеки: під’єднання node macOS дозволяє `system.run` на цій машині. Підключайте
    лише пристрої, яким довіряєте, і перегляньте [Security](/uk/gateway/security).

    Документація: [Nodes](/uk/nodes), [Протокол Gateway](/uk/gateway/protocol), [macOS remote mode](/uk/platforms/mac/remote), [Security](/uk/gateway/security).

  </Accordion>

  <Accordion title="Tailscale підключено, але я не отримую відповідей. Що тепер?">
    Перевірте основи:

    - Gateway працює: `openclaw gateway status`
    - Стан Gateway: `openclaw status`
    - Стан channel: `openclaw channels status`

    Потім перевірте auth і маршрутизацію:

    - Якщо ви використовуєте Tailscale Serve, переконайтеся, що `gateway.auth.allowTailscale` налаштовано правильно.
    - Якщо ви підключаєтеся через SSH tunnel, переконайтеся, що локальний tunnel працює і вказує на правильний порт.
    - Переконайтеся, що ваші allowlist (DM або group) містять ваш обліковий запис.

    Документація: [Tailscale](/uk/gateway/tailscale), [Віддалений доступ](/uk/gateway/remote), [Channels](/uk/channels).

  </Accordion>

  <Accordion title="Чи можуть два інстанси OpenClaw спілкуватися між собою (локальний + VPS)?">
    Так. Вбудованого мосту "bot-to-bot" немає, але це можна налаштувати кількома
    надійними способами:

    **Найпростіше:** використовуйте звичайний chat channel, до якого обидва боти мають доступ (Telegram/Slack/WhatsApp).
    Нехай Bot A надсилає повідомлення Bot B, а потім Bot B відповідає як зазвичай.

    **CLI bridge (універсальний):** запустіть скрипт, який викликає інший Gateway через
    `openclaw agent --message ... --deliver`, націлюючись на чат, який слухає інший бот.
    Якщо один бот розміщено на віддаленому VPS, спрямуйте свій CLI на цей віддалений Gateway
    через SSH/Tailscale (див. [Віддалений доступ](/uk/gateway/remote)).

    Приклад шаблону (запускати з машини, яка може дістатися цільового Gateway):

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    Порада: додайте захист, щоб два боти не зациклювалися безкінечно (лише згадки, allowlist для channel
    або правило "не відповідати на повідомлення ботів").

    Документація: [Віддалений доступ](/uk/gateway/remote), [Agent CLI](/cli/agent), [Agent send](/uk/tools/agent-send).

  </Accordion>

  <Accordion title="Чи потрібні окремі VPS для кількох agents?">
    Ні. Один Gateway може розміщувати кількох agents, кожен із власним workspace, models за замовчуванням
    та маршрутизацією. Це типовий варіант і він набагато дешевший і простіший, ніж запускати
    окремий VPS для кожного agent.

    Використовуйте окремі VPS лише тоді, коли вам потрібна жорстка ізоляція (межі безпеки) або дуже
    різні config, якими ви не хочете ділитися. В інших випадках тримайте один Gateway і
    використовуйте кількох agents або sub-agents.

  </Accordion>

  <Accordion title="Чи є перевага у використанні node на моєму особистому ноутбуці замість SSH із VPS?">
    Так — nodes є основним способом доступу до вашого ноутбука з віддаленого Gateway і
    відкривають більше, ніж просто доступ до оболонки. Gateway працює на macOS/Linux (Windows через WSL2) і є
    легким (невеликий VPS або пристрій рівня Raspberry Pi цілком підходить; 4 GB RAM більш ніж достатньо), тому типовий
    сценарій — це завжди ввімкнений хост плюс ваш ноутбук як node.

    - **Не потрібен вхідний SSH.** Nodes самі підключаються до Gateway WebSocket і використовують pair-підключення пристрою.
    - **Безпечніший контроль виконання.** `system.run` на цьому ноутбуці захищено allowlist/затвердженнями node.
    - **Більше інструментів пристрою.** Nodes надають `canvas`, `camera` і `screen` на додачу до `system.run`.
    - **Локальна автоматизація браузера.** Тримайте Gateway на VPS, але запускайте Chrome локально через хост node на ноутбуці або підключайтеся до локального Chrome на хості через Chrome MCP.

    SSH підходить для разового доступу до оболонки, але nodes простіші для постійних робочих процесів agent і
    автоматизації пристрою.

    Документація: [Nodes](/uk/nodes), [Nodes CLI](/cli/nodes), [Browser](/uk/tools/browser).

  </Accordion>

  <Accordion title="Чи запускають nodes сервіс gateway?">
    Ні. На одному хості має працювати лише **один gateway**, якщо тільки ви навмисно не запускаєте ізольовані профілі (див. [Кілька gateway](/uk/gateway/multiple-gateways)). Nodes — це периферійні елементи, які підключаються
    до gateway (nodes iOS/Android або режим macOS "node mode" у menubar app). Для headless
    хостів node і керування через CLI див. [Node host CLI](/cli/node).

    Для змін `gateway`, `discovery` і `canvasHost` потрібен повний перезапуск.

  </Accordion>

  <Accordion title="Чи є API / RPC-спосіб застосувати config?">
    Так.

    - `config.schema.lookup`: перевірити одне піддерево config із його неглибоким вузлом schema, відповідною UI-підказкою та підсумками безпосередніх дочірніх елементів перед записом
    - `config.get`: отримати поточний snapshot + hash
    - `config.patch`: безпечне часткове оновлення (рекомендовано для більшості редагувань через RPC); виконує hot-reload, коли можливо, і перезапуск, коли потрібно
    - `config.apply`: перевірити й замінити всю config; виконує hot-reload, коли можливо, і перезапуск, коли потрібно
    - Інструмент runtime `gateway`, доступний лише owner, усе ще відмовляється переписувати `tools.exec.ask` / `tools.exec.security`; застарілі псевдоніми `tools.bash.*` нормалізуються до тих самих захищених шляхів exec

  </Accordion>

  <Accordion title="Мінімальна розумна config для першого встановлення">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    Це задає ваш workspace і обмежує, хто може запускати бота.

  </Accordion>

  <Accordion title="Як налаштувати Tailscale на VPS і підключитися з Mac?">
    Мінімальні кроки:

    1. **Установіть і виконайте вхід на VPS**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **Установіть і виконайте вхід на Mac**
       - Використайте застосунок Tailscale і увійдіть у ту саму tailnet.
    3. **Увімкніть MagicDNS (рекомендовано)**
       - В адміністративній консолі Tailscale увімкніть MagicDNS, щоб VPS мав стабільне ім’я.
    4. **Використовуйте ім’я хоста tailnet**
       - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

    Якщо ви хочете використовувати Control UI без SSH, застосуйте Tailscale Serve на VPS:

    ```bash
    openclaw gateway --tailscale serve
    ```

    Це залишає gateway прив’язаним до loopback і відкриває HTTPS через Tailscale. Див. [Tailscale](/uk/gateway/tailscale).

  </Accordion>

  <Accordion title="Як підключити Mac node до віддаленого Gateway (Tailscale Serve)?">
    Serve відкриває **Gateway Control UI + WS**. Nodes підключаються через ту саму кінцеву точку Gateway WS.

    Рекомендоване налаштування:

    1. **Переконайтеся, що VPS і Mac перебувають в одній tailnet**.
    2. **Використовуйте macOS app у режимі Remote** (ціль SSH може бути hostname tailnet).
       Застосунок тунелює порт Gateway і підключається як node.
    3. **Схваліть node** на gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Документація: [Протокол Gateway](/uk/gateway/protocol), [Discovery](/uk/gateway/discovery), [macOS remote mode](/uk/platforms/mac/remote).

  </Accordion>

  <Accordion title="Чи варто встановлювати на другий ноутбук чи просто додати node?">
    Якщо вам потрібні лише **локальні інструменти** (screen/camera/exec) на другому ноутбуці, додайте його як
    **node**. Це зберігає один Gateway і дозволяє уникнути дублювання config. Локальні інструменти node
    наразі доступні лише на macOS, але ми плануємо розширити їх на інші ОС.

    Другий Gateway встановлюйте лише тоді, коли вам потрібна **жорстка ізоляція** або два повністю окремі боти.

    Документація: [Nodes](/uk/nodes), [Nodes CLI](/cli/nodes), [Кілька gateway](/uk/gateway/multiple-gateways).

  </Accordion>
</AccordionGroup>

## Env vars і завантаження .env

<AccordionGroup>
  <Accordion title="Як OpenClaw завантажує змінні середовища?">
    OpenClaw читає env vars із батьківського процесу (shell, launchd/systemd, CI тощо) і додатково завантажує:

    - `.env` з поточного робочого каталогу
    - глобальний запасний `.env` з `~/.openclaw/.env` (тобто `$OPENCLAW_STATE_DIR/.env`)

    Жоден файл `.env` не перевизначає наявні env vars.

    Ви також можете визначати вбудовані env vars у config (застосовуються лише якщо вони відсутні в env процесу):

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    Повний порядок пріоритету та джерела див. у [/environment](/uk/help/environment).

  </Accordion>

  <Accordion title="Я запустив Gateway через сервіс, і мої env vars зникли. Що тепер?">
    Два поширені способи виправлення:

    1. Помістіть відсутні ключі в `~/.openclaw/.env`, щоб вони підхоплювалися, навіть коли сервіс не успадковує env вашої shell.
    2. Увімкніть імпорт shell (необов’язкова зручність):

    ```json5
    {
      env: {
        shellEnv: {
          enabled: true,
          timeoutMs: 15000,
        },
      },
    }
    ```

    Це запускає вашу login shell і імпортує лише відсутні очікувані ключі (ніколи не перевизначає). Еквіваленти env vars:
    `OPENCLAW_LOAD_SHELL_ENV=1`, `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`.

  </Accordion>

  <Accordion title='Я задав COPILOT_GITHUB_TOKEN, але models status показує "Shell env: off." Чому?'>
    `openclaw models status` повідомляє, чи увімкнено **імпорт env із shell**. "Shell env: off"
    **не** означає, що ваших env vars немає — це лише означає, що OpenClaw не завантажуватиме
    вашу login shell автоматично.

    Якщо Gateway працює як сервіс (launchd/systemd), він не успадковує середовище
    вашої shell. Виправити це можна одним із таких способів:

    1. Помістіть токен у `~/.openclaw/.env`:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. Або увімкніть імпорт shell (`env.shellEnv.enabled: true`).
    3. Або додайте його до блоку `env` у config (застосовується лише якщо відсутній).

    Потім перезапустіть gateway і перевірте знову:

    ```bash
    openclaw models status
    ```

    Токени Copilot читаються з `COPILOT_GITHUB_TOKEN` (також `GH_TOKEN` / `GITHUB_TOKEN`).
    Див. [/concepts/model-providers](/uk/concepts/model-providers) і [/environment](/uk/help/environment).

  </Accordion>
</AccordionGroup>

## Sessions і кілька чатів

<AccordionGroup>
  <Accordion title="Як почати нову розмову?">
    Надішліть `/new` або `/reset` окремим повідомленням. Див. [Керування session](/uk/concepts/session).
  </Accordion>

  <Accordion title="Чи скидаються sessions автоматично, якщо я ніколи не надсилаю /new?">
    Sessions можуть завершуватися після `session.idleMinutes`, але за замовчуванням це **вимкнено** (типове значення **0**).
    Установіть додатне значення, щоб увімкнути завершення через бездіяльність. Коли це ввімкнено, **наступне**
    повідомлення після періоду бездіяльності починає новий ідентифікатор session для цього chat key.
    Це не видаляє transcript — лише починає нову session.

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="Чи є спосіб створити команду інстансів OpenClaw (один CEO і багато agents)?">
    Так, через **маршрутизацію multi-agent** і **sub-agents**. Ви можете створити одного координуючого
    agent і кілька worker-agents із власними workspace і models.

    Водночас це краще сприймати як **цікавий експеримент**. Це витрачає багато токенів і часто
    менш ефективно, ніж використання одного бота з окремими sessions. Типова модель, яку ми
    уявляємо, — це один бот, з яким ви спілкуєтеся, з різними sessions для паралельної роботи. Цей
    бот також може запускати sub-agents за потреби.

    Документація: [Маршрутизація multi-agent](/uk/concepts/multi-agent), [Sub-agents](/uk/tools/subagents), [Agents CLI](/cli/agents).

  </Accordion>

  <Accordion title="Чому контекст було обрізано посеред завдання? Як цьому запобігти?">
    Контекст session обмежено вікном моделі. Довгі чати, великі виводи інструментів або багато
    файлів можуть спричинити Compaction або обрізання.

    Що допомагає:

    - Попросіть бота підсумувати поточний стан і записати його у файл.
    - Використовуйте `/compact` перед довгими завданнями, а `/new` — під час зміни теми.
    - Зберігайте важливий контекст у workspace і просіть бота перечитувати його.
    - Використовуйте sub-agents для довгої або паралельної роботи, щоб main chat залишався меншим.
    - Виберіть model із більшим вікном контексту, якщо це трапляється часто.

  </Accordion>

  <Accordion title="Як повністю скинути OpenClaw, але залишити його встановленим?">
    Використовуйте команду скидання:

    ```bash
    openclaw reset
    ```

    Повне неінтерактивне скидання:

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    Потім знову запустіть налаштування:

    ```bash
    openclaw onboard --install-daemon
    ```

    Примітки:

    - Onboarding також пропонує **Reset**, якщо виявляє наявну config. Див. [Onboarding (CLI)](/uk/start/wizard).
    - Якщо ви використовували профілі (`--profile` / `OPENCLAW_PROFILE`), скиньте кожен state dir (типово це `~/.openclaw-<profile>`).
    - Скидання для dev: `openclaw gateway --dev --reset` (лише для dev; очищає config dev + облікові дані + sessions + workspace).

  </Accordion>

  <Accordion title='Я отримую помилки "context too large" — як скинути або виконати compact?'>
    Використайте один із цих варіантів:

    - **Compact** (зберігає розмову, але підсумовує старіші ходи):

      ```
      /compact
      ```

      або `/compact <instructions>`, щоб керувати підсумком.

    - **Скидання** (новий ідентифікатор session для того самого chat key):

      ```
      /new
      /reset
      ```

    Якщо це повторюється:

    - Увімкніть або налаштуйте **session pruning** (`agents.defaults.contextPruning`), щоб обрізати старий вивід інструментів.
    - Використовуйте model із більшим вікном контексту.

    Документація: [Compaction](/uk/concepts/compaction), [Session pruning](/uk/concepts/session-pruning), [Керування session](/uk/concepts/session).

  </Accordion>

  <Accordion title='Чому я бачу "LLM request rejected: messages.content.tool_use.input field required"?'>
    Це помилка перевірки provider: модель згенерувала блок `tool_use` без обов’язкового
    `input`. Зазвичай це означає, що історія session застаріла або пошкоджена (часто після довгих thread
    або зміни інструмента/schema).

    Виправлення: почніть нову session командою `/new` (окремим повідомленням).

  </Accordion>

  <Accordion title="Чому я отримую heartbeat-повідомлення кожні 30 хвилин?">
    Heartbeat запускається кожні **30m** за замовчуванням (**1h** при використанні auth через OAuth). Налаштуйте або вимкніть їх:

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // або "0m", щоб вимкнути
          },
        },
      },
    }
    ```

    Якщо `HEARTBEAT.md` існує, але фактично порожній (лише порожні рядки й markdown-заголовки
    на кшталт `# Heading`), OpenClaw пропускає запуск heartbeat, щоб заощадити API-виклики.
    Якщо файл відсутній, heartbeat усе одно запускається, і модель вирішує, що робити.

    Override для окремого agent використовують `agents.list[].heartbeat`. Документація: [Heartbeat](/uk/gateway/heartbeat).

  </Accordion>

  <Accordion title='Чи потрібно додавати "обліковий запис бота" до групи WhatsApp?'>
    Ні. OpenClaw працює від **вашого власного облікового запису**, тому якщо ви є в групі, OpenClaw може її бачити.
    За замовчуванням відповіді в групах заблоковані, доки ви не дозволите відправників (`groupPolicy: "allowlist"`).

    Якщо ви хочете, щоб відповідати в групах могли запускати лише **ви**:

    ```json5
    {
      channels: {
        whatsapp: {
          groupPolicy: "allowlist",
          groupAllowFrom: ["+15551234567"],
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Як отримати JID групи WhatsApp?">
    Варіант 1 (найшвидший): перегляньте хвіст логів і надішліть тестове повідомлення в групу:

    ```bash
    openclaw logs --follow --json
    ```

    Знайдіть `chatId` (або `from`), що закінчується на `@g.us`, наприклад:
    `1234567890-1234567890@g.us`.

    Варіант 2 (якщо вже налаштовано/додано в allowlist): перелічіть групи з config:

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    Документація: [WhatsApp](/uk/channels/whatsapp), [Directory](/cli/directory), [Logs](/cli/logs).

  </Accordion>

  <Accordion title="Чому OpenClaw не відповідає в групі?">
    Дві поширені причини:

    - Увімкнено обмеження за згадкою (типово). Ви маєте @згадати бота (або відповідати `mentionPatterns`).
    - Ви налаштували `channels.whatsapp.groups` без `"*"`, і цю групу не додано до allowlist.

    Див. [Groups](/uk/channels/groups) і [Group messages](/uk/channels/group-messages).

  </Accordion>

  <Accordion title="Чи ділять groups/threads контекст із DM?">
    Прямі чати за замовчуванням згортаються до main session. Groups/channels мають власні ключі session, а topics Telegram / threads Discord — це окремі sessions. Див. [Groups](/uk/channels/groups) і [Group messages](/uk/channels/group-messages).
  </Accordion>

  <Accordion title="Скільки workspace і agents я можу створити?">
    Жорстких обмежень немає. Десятки (навіть сотні) — це нормально, але звертайте увагу на:

    - **Зростання диска:** sessions + transcripts живуть у `~/.openclaw/agents/<agentId>/sessions/`.
    - **Витрати токенів:** більше agents означає більше одночасного використання моделей.
    - **Операційні накладні витрати:** auth profiles, workspace та маршрутизація channel для кожного agent.

    Поради:

    - Тримайте один **активний** workspace на agent (`agents.defaults.workspace`).
    - Очищуйте старі sessions (видаляйте JSONL або записи сховища), якщо диск розростається.
    - Використовуйте `openclaw doctor`, щоб виявляти зайві workspace і невідповідності профілів.

  </Accordion>

  <Accordion title="Чи можу я запускати кілька ботів або чатів одночасно (Slack), і як це краще налаштувати?">
    Так. Використовуйте **Маршрутизацію Multi-Agent**, щоб запускати кілька ізольованих agents і спрямовувати вхідні повідомлення за
    channel/account/peer. Slack підтримується як channel і може бути прив’язаний до конкретних agents.

    Доступ до браузера потужний, але не означає "може зробити все, що людина" — anti-bot, CAPTCHA і MFA
    усе ще можуть блокувати автоматизацію. Для найнадійнішого керування браузером використовуйте локальний Chrome MCP на хості,
    або використовуйте CDP на машині, яка фактично запускає браузер.

    Найкраща практика налаштування:

    - Постійно ввімкнений хост Gateway (VPS/Mac mini).
    - Один agent на роль (bindings).
    - Channels Slack, прив’язані до цих agents.
    - Локальний браузер через Chrome MCP або node за потреби.

    Документація: [Маршрутизація Multi-Agent](/uk/concepts/multi-agent), [Slack](/uk/channels/slack),
    [Browser](/uk/tools/browser), [Nodes](/uk/nodes).

  </Accordion>
</AccordionGroup>

## Models: типові значення, вибір, псевдоніми, перемикання

<AccordionGroup>
  <Accordion title='Що таке "model за замовчуванням"?'>
    Модель за замовчуванням в OpenClaw — це те, що ви задаєте як:

    ```
    agents.defaults.model.primary
    ```

    На models посилаються як `provider/model` (приклад: `openai/gpt-5.4`). Якщо ви пропускаєте provider, OpenClaw спочатку намагається знайти псевдонім, потім — унікальний збіг точно цього model id серед налаштованих providers, і лише після цього використовує налаштований provider за замовчуванням як застарілий шлях сумісності. Якщо цей provider більше не надає налаштовану model за замовчуванням, OpenClaw переключається на перші налаштовані provider/model замість того, щоб показувати застаріле типове значення видаленого provider. Вам усе одно слід **явно** задавати `provider/model`.

  </Accordion>

  <Accordion title="Яку model ви рекомендуєте?">
    **Рекомендоване типове значення:** використовуйте найсильнішу модель останнього покоління, доступну у вашому стеку provider.
    **Для agents з увімкненими інструментами або agents з недовіреним входом:** ставте силу model вище за вартість.
    **Для звичайного/низькоризикового чату:** використовуйте дешевші резервні models і маршрутизуйте за роллю agent.

    Для MiniMax є окрема документація: [MiniMax](/uk/providers/minimax) і
    [Локальні моделі](/uk/gateway/local-models).

    Практичне правило: використовуйте **найкращу model, яку можете собі дозволити** для важливих завдань, і дешевшу
    model для повсякденного чату або підсумків. Ви можете маршрутизувати models за agent і використовувати sub-agents для
    паралелізації довгих завдань (кожен sub-agent споживає токени). Див. [Models](/uk/concepts/models) і
    [Sub-agents](/uk/tools/subagents).

    Серйозне попередження: слабші/надмірно квантизовані models більш вразливі до prompt
    injection і небезпечної поведінки. Див. [Security](/uk/gateway/security).

    Більше контексту: [Models](/uk/concepts/models).

  </Accordion>

  <Accordion title="Як перемикати models без стирання config?">
    Використовуйте **команди model** або редагуйте лише поля **model**. Уникайте повної заміни config.

    Безпечні варіанти:

    - `/model` у чаті (швидко, для поточної session)
    - `openclaw models set ...` (оновлює лише config model)
    - `openclaw configure --section model` (інтерактивно)
    - редагуйте `agents.defaults.model` у `~/.openclaw/openclaw.json`

    Уникайте `config.apply` із частковим об’єктом, якщо ви не збираєтеся замінити всю config.
    Для редагувань через RPC спочатку перевіряйте через `config.schema.lookup` і надавайте перевагу `config.patch`. Дані lookup дають нормалізований шлях, документацію/обмеження неглибокої schema та підсумки безпосередніх дочірніх елементів
    для часткових оновлень.
    Якщо ви таки перезаписали config, відновіть її з резервної копії або повторно запустіть `openclaw doctor` для виправлення.

    Документація: [Models](/uk/concepts/models), [Configure](/cli/configure), [Config](/cli/config), [Doctor](/uk/gateway/doctor).

  </Accordion>

  <Accordion title="Чи можу я використовувати self-hosted models (llama.cpp, vLLM, Ollama)?">
    Так. Ollama — найпростіший шлях до локальних models.

    Найшвидше налаштування:

    1. Установіть Ollama з `https://ollama.com/download`
    2. Завантажте локальну model, наприклад `ollama pull gemma4`
    3. Якщо вам потрібні також хмарні models, виконайте `ollama signin`
    4. Запустіть `openclaw onboard` і виберіть `Ollama`
    5. Виберіть `Local` або `Cloud + Local`

    Примітки:

    - `Cloud + Local` надає вам хмарні models плюс локальні models Ollama
    - хмарні models, як-от `kimi-k2.5:cloud`, не потребують локального завантаження
    - для ручного перемикання використовуйте `openclaw models list` і `openclaw models set ollama/<model>`

    Примітка щодо безпеки: менші або сильно квантизовані models більш вразливі до prompt
    injection. Ми наполегливо рекомендуємо **великі models** для будь-якого бота, який може використовувати інструменти.
    Якщо ви все ж хочете маленькі models, увімкніть sandboxing і суворі allowlist інструментів.

    Документація: [Ollama](/uk/providers/ollama), [Локальні моделі](/uk/gateway/local-models),
    [Провайдери моделей](/uk/concepts/model-providers), [Security](/uk/gateway/security),
    [Ізоляція](/uk/gateway/sandboxing).

  </Accordion>

  <Accordion title="Які models використовують OpenClaw, Flawd і Krill?">
    - У цих розгортаннях можуть бути різні налаштування, і вони можуть змінюватися з часом; фіксованої рекомендації щодо provider немає.
    - Перевіряйте поточне налаштування runtime на кожному gateway через `openclaw models status`.
    - Для agents із чутливими до безпеки/увімкненими інструментами використовуйте найсильнішу модель останнього покоління з доступних.
  </Accordion>

  <Accordion title="Як перемикати models на льоту (без перезапуску)?">
    Використовуйте команду `/model` як окреме повідомлення:

    ```
    /model sonnet
    /model opus
    /model gpt
    /model gpt-mini
    /model gemini
    /model gemini-flash
    /model gemini-flash-lite
    ```

    Це вбудовані псевдоніми. Користувацькі псевдоніми можна додавати через `agents.defaults.models`.

    Ви можете переглянути доступні models через `/model`, `/model list` або `/model status`.

    `/model` (і `/model list`) показує компактний нумерований вибір. Вибирайте за номером:

    ```
    /model 3
    ```

    Ви також можете примусово вибрати конкретний auth profile для provider (для session):

    ```
    /model opus@anthropic:default
    /model opus@anthropic:work
    ```

    Порада: `/model status` показує, який agent активний, який файл `auth-profiles.json` використовується і який auth profile буде спробовано наступним.
    Він також показує налаштовану кінцеву точку provider (`baseUrl`) і режим API (`api`), коли це доступно.

    **Як зняти фіксацію profile, який я задав через @profile?**

    Повторно запустіть `/model` **без** суфікса `@profile`:

    ```
    /model anthropic/claude-opus-4-6
    ```

    Якщо ви хочете повернутися до типового значення, виберіть його через `/model` (або надішліть `/model <default provider/model>`).
    Використовуйте `/model status`, щоб підтвердити, який auth profile активний.

  </Accordion>

  <Accordion title="Чи можу я використовувати GPT 5.2 для щоденних завдань, а Codex 5.3 для кодування?">
    Так. Установіть одну як типову й перемикайтеся за потреби:

    - **Швидке перемикання (для session):** `/model gpt-5.4` для щоденних завдань, `/model openai-codex/gpt-5.4` для кодування з OAuth Codex.
    - **Типове значення + перемикання:** задайте `agents.defaults.model.primary` як `openai/gpt-5.4`, а потім перемикайтеся на `openai-codex/gpt-5.4` під час кодування (або навпаки).
    - **Sub-agents:** спрямовуйте завдання кодування до sub-agents з іншою model за замовчуванням.

    Див. [Models](/uk/concepts/models) і [Slash-команди](/uk/tools/slash-commands).

  </Accordion>

  <Accordion title="Як налаштувати fast mode для GPT 5.4?">
    Використовуйте або перемикач для session, або типове значення в config:

    - **Для session:** надішліть `/fast on`, поки session використовує `openai/gpt-5.4` або `openai-codex/gpt-5.4`.
    - **Типове значення для model:** задайте `agents.defaults.models["openai/gpt-5.4"].params.fastMode` як `true`.
    - **Також для OAuth Codex:** якщо ви також використовуєте `openai-codex/gpt-5.4`, задайте там той самий прапорець.

    Приклад:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
            "openai-codex/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
          },
        },
      },
    }
    ```

    Для OpenAI fast mode відповідає `service_tier = "priority"` у підтримуваних нативних запитах Responses. Session `/fast` має вищий пріоритет за типові значення config.

    Див. [Thinking and fast mode](/uk/tools/thinking) і [OpenAI fast mode](/uk/providers/openai#openai-fast-mode).

  </Accordion>

  <Accordion title='Чому я бачу "Model ... is not allowed", а потім немає відповіді?'>
    Якщо задано `agents.defaults.models`, це стає **allowlist** для `/model` і будь-яких
    override session. Вибір model, якої немає в цьому списку, повертає:

    ```
    Model "provider/model" is not allowed. Use /model to list available models.
    ```

    Ця помилка повертається **замість** звичайної відповіді. Виправлення: додайте model до
    `agents.defaults.models`, приберіть allowlist або виберіть model через `/model list`.

  </Accordion>

  <Accordion title='Чому я бачу "Unknown model: minimax/MiniMax-M2.7"?'>
    Це означає, що **provider не налаштовано** (не знайдено config provider MiniMax або auth
    profile), тому model не вдається визначити.

    Чекліст для виправлення:

    1. Оновіться до актуального релізу OpenClaw (або працюйте з вихідного коду `main`), а потім перезапустіть gateway.
    2. Переконайтеся, що MiniMax налаштовано (майстром або через JSON), або що auth MiniMax
       існує в env/auth profiles, щоб відповідний provider можна було додати
       (`MINIMAX_API_KEY` для `minimax`, `MINIMAX_OAUTH_TOKEN` або збережений OAuth MiniMax
       для `minimax-portal`).
    3. Використовуйте точний id model (з урахуванням регістру) для вашого шляху auth:
       `minimax/MiniMax-M2.7` або `minimax/MiniMax-M2.7-highspeed` для налаштування через API-ключ,
       або `minimax-portal/MiniMax-M2.7` /
       `minimax-portal/MiniMax-M2.7-highspeed` для налаштування через OAuth.
    4. Виконайте:

       ```bash
       openclaw models list
       ```

       і виберіть зі списку (або `/model list` у чаті).

    Див. [MiniMax](/uk/providers/minimax) і [Models](/uk/concepts/models).

  </Accordion>

  <Accordion title="Чи можу я використовувати MiniMax як типову model, а OpenAI для складних завдань?">
    Так. Використовуйте **MiniMax як типову** і перемикайте models **для session** за потреби.
    Резервні варіанти призначені для **помилок**, а не для "складних завдань", тому використовуйте `/model` або окремого agent.

    **Варіант A: перемикання для session**

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-...", OPENAI_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "minimax/MiniMax-M2.7" },
          models: {
            "minimax/MiniMax-M2.7": { alias: "minimax" },
            "openai/gpt-5.4": { alias: "gpt" },
          },
        },
      },
    }
    ```

    Потім:

    ```
    /model gpt
    ```

    **Варіант B: окремі agents**

    - Типова model для Agent A: MiniMax
    - Типова model для Agent B: OpenAI
    - Маршрутизуйте за agent або використовуйте `/agent` для перемикання

    Документація: [Models](/uk/concepts/models), [Маршрутизація Multi-Agent](/uk/concepts/multi-agent), [MiniMax](/uk/providers/minimax), [OpenAI](/uk/providers/openai).

  </Accordion>

  <Accordion title="Чи є opus / sonnet / gpt вбудованими скороченнями?">
    Так. OpenClaw постачається з кількома типовими скороченнями (застосовуються лише тоді, коли model існує в `agents.defaults.models`):

    - `opus` → `anthropic/claude-opus-4-6`
    - `sonnet` → `anthropic/claude-sonnet-4-6`
    - `gpt` → `openai/gpt-5.4`
    - `gpt-mini` → `openai/gpt-5.4-mini`
    - `gpt-nano` → `openai/gpt-5.4-nano`
    - `gemini` → `google/gemini-3.1-pro-preview`
    - `gemini-flash` → `google/gemini-3-flash-preview`
    - `gemini-flash-lite` → `google/gemini-3.1-flash-lite-preview`

    Якщо ви задаєте власний псевдонім із такою самою назвою, перемагає ваше значення.

  </Accordion>

  <Accordion title="Як визначати/перевизначати скорочення model (псевдоніми)?">
    Псевдоніми беруться з `agents.defaults.models.<modelId>.alias`. Приклад:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "anthropic/claude-opus-4-6" },
          models: {
            "anthropic/claude-opus-4-6": { alias: "opus" },
            "anthropic/claude-sonnet-4-6": { alias: "sonnet" },
            "anthropic/claude-haiku-4-5": { alias: "haiku" },
          },
        },
      },
    }
    ```

    Тоді `/model sonnet` (або `/<alias>`, коли це підтримується) розв’язується в цей ID model.

  </Accordion>

  <Accordion title="Як додати models від інших providers, наприклад OpenRouter або Z.AI?">
    OpenRouter (оплата за токени; багато models):

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "openrouter/anthropic/claude-sonnet-4-6" },
          models: { "openrouter/anthropic/claude-sonnet-4-6": {} },
        },
      },
      env: { OPENROUTER_API_KEY: "sk-or-..." },
    }
    ```

    Z.AI (models GLM):

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "zai/glm-5" },
          models: { "zai/glm-5": {} },
        },
      },
      env: { ZAI_API_KEY: "..." },
    }
    ```

    Якщо ви посилаєтеся на provider/model, але потрібний ключ provider відсутній, ви отримаєте помилку auth під час виконання (наприклад, `No API key found for provider "zai"`).

    **Після додавання нового agent не знайдено API-ключ для provider**

    Зазвичай це означає, що **новий agent** має порожнє сховище auth. Auth є прив’язаною до agent і
    зберігається тут:

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

    Варіанти виправлення:

    - Виконайте `openclaw agents add <id>` і налаштуйте auth у майстрі.
    - Або скопіюйте `auth-profiles.json` з `agentDir` головного agent до `agentDir` нового agent.

    **Не** використовуйте спільний `agentDir` для кількох agents; це спричиняє конфлікти auth/session.

  </Accordion>
</AccordionGroup>

## Резервне перемикання model і "All models failed"

<AccordionGroup>
  <Accordion title="Як працює резервне перемикання?">
    Резервне перемикання відбувається у два етапи:

    1. **Ротація auth profile** у межах того самого provider.
    2. **Резервний перехід model** до наступної model у `agents.defaults.model.fallbacks`.

    До невдалих profiles застосовуються cooldown (експоненційне збільшення затримки), тож OpenClaw може продовжувати відповідати, навіть коли provider обмежений rate limit або тимчасово не працює.

    Кошик rate limit включає не лише звичайні відповіді `429`. OpenClaw
    також вважає повідомлення на кшталт `Too many concurrent requests`,
    `ThrottlingException`, `concurrency limit reached`,
    `workers_ai ... quota limit exceeded`, `resource exhausted` і періодичні
    обмеження вікна використання (`weekly/monthly limit reached`) такими, що
    варті резервного перемикання через rate limit.

    Деякі відповіді, схожі на billing, не є `402`, а деякі HTTP-відповіді `402`
    також залишаються в цьому тимчасовому кошику. Якщо provider повертає
    явний billing-текст на `401` або `403`, OpenClaw усе ще може тримати це
    в категорії billing, але текстові зіставлення, специфічні для provider, залишаються в межах
    provider, якому вони належать (наприклад, OpenRouter `Key limit exceeded`). Якщо повідомлення `402`
    натомість схоже на повторюване вікно використання або
    ліміт витрат organization/workspace (`daily limit reached, resets tomorrow`,
    `organization spending limit exceeded`), OpenClaw трактує це як
    `rate_limit`, а не як довге відключення через billing.

    Помилки переповнення контексту відрізняються: сигнатури на кшталт
    `request_too_large`, `input exceeds the maximum number of tokens`,
    `input token count exceeds the maximum number of input tokens`,
    `input is too long for the model` або `ollama error: context length
    exceeded` залишаються на шляху Compaction/повторної спроби замість переходу
    до резервної model.

    Загальний текст помилок сервера навмисно вужчий, ніж "усе, де є
    unknown/error". OpenClaw вважає гідними резервного перемикання такі
    залежні від provider тимчасові форми, як-от bare Anthropic `An unknown error occurred`, bare OpenRouter
    `Provider returned error`, помилки причини зупинки на кшталт `Unhandled stop reason:
    error`, JSON-пейлоади `api_error` із текстом тимчасових серверних помилок
    (`internal server error`, `unknown error, 520`, `upstream error`, `backend
    error`) і помилки перевантаження provider на кшталт `ModelNotReadyException` — якщо контекст provider
    збігається.
    Загальний внутрішній запасний текст на кшталт `LLM request failed with an unknown
    error.` залишається консервативним і сам по собі не запускає резервне перемикання model.

  </Accordion>

  <Accordion title='Що означає "No credentials found for profile anthropic:default"?'>
    Це означає, що система спробувала використати ID auth profile `anthropic:default`, але не змогла знайти для нього облікові дані в очікуваному сховищі auth.

    **Чекліст для виправлення:**

    - **Перевірте, де зберігаються auth profiles** (нові та застарілі шляхи)
      - Поточний шлях: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
      - Застарілий шлях: `~/.openclaw/agent/*` (мігрується через `openclaw doctor`)
    - **Переконайтеся, що Gateway завантажує вашу env var**
      - Якщо ви задали `ANTHROPIC_API_KEY` у shell, але запускаєте Gateway через systemd/launchd, він може не успадкувати його. Помістіть її в `~/.openclaw/.env` або увімкніть `env.shellEnv`.
    - **Переконайтеся, що редагуєте правильного agent**
      - У multi-agent налаштуваннях може бути кілька файлів `auth-profiles.json`.
    - **Базова перевірка стану model/auth**
      - Використовуйте `openclaw models status`, щоб побачити налаштовані models і чи пройшли providers автентифікацію.

    **Чекліст для виправлення "No credentials found for profile anthropic"**

    Це означає, що виконання прив’язане до auth profile Anthropic, але Gateway
    не може знайти його у своєму сховищі auth.

    - **Використовуйте Claude CLI**
      - Виконайте `openclaw models auth login --provider anthropic --method cli --set-default` на хості gateway.
    - **Якщо ви хочете використовувати натомість API-ключ**
      - Помістіть `ANTHROPIC_API_KEY` у `~/.openclaw/.env` на **хості gateway**.
      - Очистьте будь-який зафіксований порядок, що примусово вимагає відсутній profile:

        ```bash
        openclaw models auth order clear --provider anthropic
        ```

    - **Переконайтеся, що запускаєте команди на хості gateway**
      - У віддаленому режимі auth profiles живуть на машині gateway, а не на вашому ноутбуці.

  </Accordion>

  <Accordion title="Чому він також спробував Google Gemini і завершився невдачею?">
    Якщо ваша config model містить Google Gemini як резервний варіант (або ви перемкнулися на скорочення Gemini), OpenClaw спробує її під час резервного перемикання model. Якщо ви не налаштували облікові дані Google, побачите `No API key found for provider "google"`.

    Виправлення: або надайте auth Google, або приберіть/уникайте models Google у `agents.defaults.model.fallbacks` / псевдонімах, щоб резервне перемикання не спрямовувалося туди.

    **LLM request rejected: thinking signature required (Google Antigravity)**

    Причина: історія session містить **блоки thinking без signatures** (часто через
    перерваний/частковий потік). Google Antigravity вимагає signatures для блоків thinking.

    Виправлення: тепер OpenClaw видаляє блоки thinking без signatures для Claude Google Antigravity. Якщо це все ще з’являється, почніть **нову session** або задайте `/thinking off` для цього agent.

  </Accordion>
</AccordionGroup>

## Auth profiles: що це таке і як ними керувати

Пов’язане: [/concepts/oauth](/uk/concepts/oauth) (OAuth-потоки, зберігання токенів, шаблони для кількох облікових записів)

<AccordionGroup>
  <Accordion title="Що таке auth profile?">
    Auth profile — це іменований запис облікових даних (OAuth або API-ключ), прив’язаний до provider. Profiles зберігаються тут:

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

  </Accordion>

  <Accordion title="Які типові ID profile?">
    OpenClaw використовує ID з префіксом provider, наприклад:

    - `anthropic:default` (поширений варіант, коли немає email-ідентичності)
    - `anthropic:<email>` для OAuth-ідентичностей
    - користувацькі ID на ваш вибір (наприклад, `anthropic:work`)

  </Accordion>

  <Accordion title="Чи можу я керувати тим, який auth profile буде спробовано першим?">
    Так. Config підтримує необов’язкові metadata для profiles і порядок для кожного provider (`auth.order.<provider>`). Це **не** зберігає секрети; воно зіставляє ID із provider/mode і задає порядок ротації.

    OpenClaw може тимчасово пропустити profile, якщо вона перебуває в короткому **cooldown** (rate limits/timeouts/auth failures) або в довшому стані **disabled** (billing/недостатньо кредитів). Щоб перевірити це, виконайте `openclaw models status --json` і перевірте `auth.unusableProfiles`. Налаштування: `auth.cooldowns.billingBackoffHours*`.

    Cooldown через rate limit можуть бути прив’язані до model. Profile, яка перебуває в cooldown
    для однієї model, усе ще може бути придатною для спорідненої model у межах того самого provider,
    тоді як billing/disabled-вікна все ще блокують увесь profile.

    Ви також можете задати **override порядку для agent** (зберігається в `auth-state.json` цього agent) через CLI:

    ```bash
    # За замовчуванням використовує налаштований default agent (пропустіть --agent)
    openclaw models auth order get --provider anthropic

    # Зафіксувати ротацію на одному profile (пробувати лише цей)
    openclaw models auth order set --provider anthropic anthropic:default

    # Або задати явний порядок (резервний перехід у межах provider)
    openclaw models auth order set --provider anthropic anthropic:work anthropic:default

    # Очистити override (повернутися до config auth.order / round-robin)
    openclaw models auth order clear --provider anthropic
    ```

    Щоб націлитися на конкретного agent:

    ```bash
    openclaw models auth order set --provider anthropic --agent main anthropic:default
    ```

    Щоб перевірити, що саме буде спробовано на практиці, використовуйте:

    ```bash
    openclaw models status --probe
    ```

    Якщо збережений profile пропущено з явного порядку, probe повідомляє
    `excluded_by_auth_order` для цього profile замість того, щоб тихо його пробувати.

  </Accordion>

  <Accordion title="OAuth чи API-ключ — у чому різниця?">
    OpenClaw підтримує обидва варіанти:

    - **OAuth** часто використовує доступ за підпискою (де це застосовно).
    - **API-ключі** використовують білінг pay-per-token.

    Майстер явно підтримує Anthropic Claude CLI, OpenAI Codex OAuth і API-ключі.

  </Accordion>
</AccordionGroup>

## Gateway: порти, "already running" і віддалений режим

<AccordionGroup>
  <Accordion title="Який порт використовує Gateway?">
    `gateway.port` керує єдиним мультиплексованим портом для WebSocket + HTTP (Control UI, hooks тощо).

    Пріоритет:

    ```
    --port > OPENCLAW_GATEWAY_PORT > gateway.port > default 18789
    ```

  </Accordion>

  <Accordion title='Чому `openclaw gateway status` показує "Runtime: running", але "RPC probe: failed"?'>
    Тому що "running" — це погляд **supervisor** (launchd/systemd/schtasks). RPC probe — це коли CLI фактично підключається до gateway WebSocket і викликає `status`.

    Використовуйте `openclaw gateway status` і довіряйте цим рядкам:

    - `Probe target:` (URL, який probe фактично використав)
    - `Listening:` (що насправді прив’язано до порту)
    - `Last gateway error:` (типова першопричина, коли процес живий, але порт не слухає)

  </Accordion>

  <Accordion title='Чому `openclaw gateway status` показує різні значення для "Config (cli)" і "Config (service)"?'>
    Ви редагуєте один файл config, а сервіс працює з іншим (часто через невідповідність `--profile` / `OPENCLAW_STATE_DIR`).

    Виправлення:

    ```bash
    openclaw gateway install --force
    ```

    Запустіть це з тим самим `--profile` / середовищем, яке сервіс має використовувати.

  </Accordion>

  <Accordion title='Що означає "another gateway instance is already listening"?'>
    OpenClaw забезпечує блокування runtime, одразу прив’язуючи слухач WebSocket під час запуску (типово `ws://127.0.0.1:18789`). Якщо прив’язка завершується помилкою `EADDRINUSE`, викидається `GatewayLockError`, що означає: інший інстанс уже слухає.

    Виправлення: зупиніть інший інстанс, звільніть порт або запустіть з `openclaw gateway --port <port>`.

  </Accordion>

  <Accordion title="Як запустити OpenClaw у віддаленому режимі (клієнт підключається до Gateway деінде)?">
    Установіть `gateway.mode: "remote"` і вкажіть URL віддаленого WebSocket, за потреби з віддаленими обліковими даними shared secret:

    ```json5
    {
      gateway: {
        mode: "remote",
        remote: {
          url: "ws://gateway.tailnet:18789",
          token: "your-token",
          password: "your-password",
        },
      },
    }
    ```

    Примітки:

    - `openclaw gateway` запускається лише тоді, коли `gateway.mode` має значення `local` (або якщо ви передаєте прапорець перевизначення).
    - macOS app відстежує файл config і в реальному часі перемикає режими, коли ці значення змінюються.
    - `gateway.remote.token` / `.password` — це лише клієнтські віддалені облікові дані; вони самі по собі не вмикають локальну auth gateway.

  </Accordion>

  <Accordion title='Control UI показує "unauthorized" (або постійно перепідключається). Що тепер?'>
    Ваш шлях auth gateway і метод auth UI не збігаються.

    Факти (з коду):

    - Control UI зберігає токен у `sessionStorage` для поточної session вкладки браузера та вибраного URL gateway, тож оновлення в тій самій вкладці продовжують працювати без відновлення довготривалого зберігання токена в localStorage.
    - За `AUTH_TOKEN_MISMATCH` довірені клієнти можуть виконати одну обмежену повторну спробу з кешованим токеном пристрою, коли gateway повертає підказки для повтору (`canRetryWithDeviceToken=true`, `recommendedNextStep=retry_with_device_token`).
    - Ця повторна спроба з кешованим токеном тепер повторно використовує кешовані схвалені scopes, збережені разом із токеном пристрою. Явні виклики `deviceToken` / явні `scopes` усе ще зберігають свій запитаний набір scope замість успадкування кешованих scopes.
    - Поза цим шляхом повтору пріоритет auth під час підключення такий: спочатку явний shared token/password, потім явний `deviceToken`, потім збережений токен пристрою, потім bootstrap token.
    - Перевірки scope bootstrap token мають префікси ролей. Вбудований allowlist bootstrap operator задовольняє лише запити operator; node або інші ролі не-operator усе ще потребують scopes із префіксом власної ролі.

    Виправлення:

    - Найшвидше: `openclaw dashboard` (виводить + копіює URL dashboard, намагається відкрити; у headless показує підказку щодо SSH).
    - Якщо у вас ще немає токена: `openclaw doctor --generate-gateway-token`.
    - Якщо віддалено, спочатку налаштуйте tunnel: `ssh -N -L 18789:127.0.0.1:18789 user@host`, а потім відкрийте `http://127.0.0.1:18789/`.
    - Режим shared-secret: задайте `gateway.auth.token` / `OPENCLAW_GATEWAY_TOKEN` або `gateway.auth.password` / `OPENCLAW_GATEWAY_PASSWORD`, а потім вставте відповідний secret у налаштуваннях Control UI.
    - Режим Tailscale Serve: переконайтеся, що `gateway.auth.allowTailscale` увімкнено і ви відкриваєте URL Serve, а не сирий URL loopback/tailnet, який оминає заголовки ідентичності Tailscale.
    - Режим trusted-proxy: переконайтеся, що ви заходите через налаштований identity-aware proxy не на loopback, а не через loopback proxy на тому самому хості чи сирий URL gateway.
    - Якщо невідповідність зберігається після однієї повторної спроби, перевипустіть/пересхваліть токен підключеного пристрою:
      - `openclaw devices list`
      - `openclaw devices rotate --device <id> --role operator`
    - Якщо цей виклик rotate каже, що в ньому відмовлено, перевірте дві речі:
      - sessions paired-device можуть перевипускати лише **власний** пристрій, якщо в них також немає `operator.admin`
      - явні значення `--scope` не можуть перевищувати поточні операторські scopes викликача
    - Досі застрягли? Виконайте `openclaw status --all` і дотримуйтеся [Усунення проблем](/uk/gateway/troubleshooting). Подробиці auth див. у [Dashboard](/web/dashboard).

  </Accordion>

  <Accordion title="Я встановив gateway.bind tailnet, але він не може прив’язатися і нічого не слухає">
    Прив’язка `tailnet` вибирає IP-адресу Tailscale з мережевих інтерфейсів (100.64.0.0/10). Якщо машина не підключена до Tailscale (або інтерфейс вимкнений), прив’язуватися немає до чого.

    Виправлення:

    - Запустіть Tailscale на цьому хості (щоб він мав адресу 100.x), або
    - Перемкніться на `gateway.bind: "loopback"` / `"lan"`.

    Примітка: `tailnet` задається явно. `auto` віддає перевагу loopback; використовуйте `gateway.bind: "tailnet"`, коли хочете прив’язку лише до tailnet.

  </Accordion>

  <Accordion title="Чи можу я запускати кілька Gateway на одному хості?">
    Зазвичай ні — один Gateway може обслуговувати кілька messaging channels і agents. Використовуйте кілька Gateway лише тоді, коли вам потрібна надлишковість (наприклад, резервний бот) або жорстка ізоляція.

    Так, але потрібно ізолювати:

    - `OPENCLAW_CONFIG_PATH` (config для кожного інстансу)
    - `OPENCLAW_STATE_DIR` (state для кожного інстансу)
    - `agents.defaults.workspace` (ізоляція workspace)
    - `gateway.port` (унікальні порти)

    Швидке налаштування (рекомендовано):

    - Використовуйте `openclaw --profile <name> ...` для кожного інстансу (автоматично створює `~/.openclaw-<name>`).
    - Установіть унікальний `gateway.port` у config кожного профілю (або передайте `--port` для ручних запусків).
    - Установіть сервіс для кожного профілю: `openclaw --profile <name> gateway install`.

    Profiles також додають суфікси до назв сервісів (`ai.openclaw.<profile>`; застарілі `com.openclaw.*`, `openclaw-gateway-<profile>.service`, `OpenClaw Gateway (<profile>)`).
    Повний посібник: [Кілька gateway](/uk/gateway/multiple-gateways).

  </Accordion>

  <Accordion title='Що означає "invalid handshake" / code 1008?'>
    Gateway — це **сервер WebSocket**, і він очікує, що найпершим повідомленням
    буде frame `connect`. Якщо він отримує щось інше, то закриває з’єднання
    з **code 1008** (порушення політики).

    Поширені причини:

    - Ви відкрили **HTTP** URL у браузері (`http://...`) замість клієнта WS.
    - Ви використали неправильний порт або шлях.
    - Proxy або tunnel прибрав auth headers або надіслав запит, який не є запитом Gateway.

    Швидкі виправлення:

    1. Використовуйте URL WS: `ws://<host>:18789` (або `wss://...`, якщо HTTPS).
    2. Не відкривайте порт WS у звичайній вкладці браузера.
    3. Якщо auth увімкнено, додайте token/password у frame `connect`.

    Якщо ви використовуєте CLI або TUI, URL має виглядати так:

    ```
    openclaw tui --url ws://<host>:18789 --token <token>
    ```

    Подробиці протоколу: [Протокол Gateway](/uk/gateway/protocol).

  </Accordion>
</AccordionGroup>

## Logging і налагодження

<AccordionGroup>
  <Accordion title="Де знаходяться логи?">
    Файлові логи (структуровані):

    ```
    /tmp/openclaw/openclaw-YYYY-MM-DD.log
    ```

    Ви можете задати стабільний шлях через `logging.file`. Рівень file log визначається через `logging.level`. Докладність консолі контролюється через `--verbose` і `logging.consoleLevel`.

    Найшвидший перегляд хвоста логів:

    ```bash
    openclaw logs --follow
    ```

    Логи сервісу/supervisor (коли gateway працює через launchd/systemd):

    - macOS: `$OPENCLAW_STATE_DIR/logs/gateway.log` і `gateway.err.log` (типово: `~/.openclaw/logs/...`; profiles використовують `~/.openclaw-<profile>/logs/...`)
    - Linux: `journalctl --user -u openclaw-gateway[-<profile>].service -n 200 --no-pager`
    - Windows: `schtasks /Query /TN "OpenClaw Gateway (<profile>)" /V /FO LIST`

    Докладніше див. у [Усунення проблем](/uk/gateway/troubleshooting).

  </Accordion>

  <Accordion title="Як запускати/зупиняти/перезапускати сервіс Gateway?">
    Використовуйте допоміжні команди gateway:

    ```bash
    openclaw gateway status
    openclaw gateway restart
    ```

    Якщо ви запускаєте gateway вручну, `openclaw gateway --force` може повернути порт. Див. [Gateway](/uk/gateway).

  </Accordion>

  <Accordion title="Я закрив термінал у Windows — як перезапустити OpenClaw?">
    Існує **два режими встановлення у Windows**:

    **1) WSL2 (рекомендовано):** Gateway працює всередині Linux.

    Відкрийте PowerShell, увійдіть у WSL, а потім перезапустіть:

    ```powershell
    wsl
    openclaw gateway status
    openclaw gateway restart
    ```

    Якщо ви ніколи не встановлювали сервіс, запустіть його на передньому плані:

    ```bash
    openclaw gateway run
    ```

    **2) Нативний Windows (не рекомендується):** Gateway працює безпосередньо у Windows.

    Відкрийте PowerShell і виконайте:

    ```powershell
    openclaw gateway status
    openclaw gateway restart
    ```

    Якщо ви запускаєте його вручну (без сервісу), використовуйте:

    ```powershell
    openclaw gateway run
    ```

    Документація: [Windows (WSL2)](/uk/platforms/windows), [Інструкція з роботи сервісу Gateway](/uk/gateway).

  </Accordion>

  <Accordion title="Gateway працює, але відповіді ніколи не надходять. Що перевірити?">
    Почніть зі швидкої перевірки стану:

    ```bash
    openclaw status
    openclaw models status
    openclaw channels status
    openclaw logs --follow
    ```

    Поширені причини:

    - Auth model не завантажено на **хості gateway** (перевірте `models status`).
    - Pairing/allowlist channel блокує відповіді (перевірте config channel + логи).
    - WebChat/Dashboard відкрито без правильного токена.

    Якщо ви працюєте віддалено, переконайтеся, що tunnel/Tailscale-з’єднання активне і що
    Gateway WebSocket доступний.

    Документація: [Channels](/uk/channels), [Усунення проблем](/uk/gateway/troubleshooting), [Віддалений доступ](/uk/gateway/remote).

  </Accordion>

  <Accordion title='"Disconnected from gateway: no reason" — що тепер?'>
    Зазвичай це означає, що UI втратив з’єднання WebSocket. Перевірте:

    1. Чи працює Gateway? `openclaw gateway status`
    2. Чи Gateway у доброму стані? `openclaw status`
    3. Чи UI має правильний токен? `openclaw dashboard`
    4. Якщо віддалено, чи tunnel/Tailscale-з’єднання активне?

    Потім перегляньте хвіст логів:

    ```bash
    openclaw logs --follow
    ```

    Документація: [Dashboard](/web/dashboard), [Віддалений доступ](/uk/gateway/remote), [Усунення проблем](/uk/gateway/troubleshooting).

  </Accordion>

  <Accordion title="Не вдається виконати Telegram setMyCommands. Що перевірити?">
    Почніть із логів і стану channel:

    ```bash
    openclaw channels status
    openclaw channels logs --channel telegram
    ```

    Далі зіставте помилку:

    - `BOT_COMMANDS_TOO_MUCH`: меню Telegram містить забагато записів. OpenClaw уже обрізає список до ліміту Telegram і повторює спробу з меншою кількістю команд, але деякі елементи меню все одно потрібно прибрати. Зменште кількість plugin/skill/custom-команд або вимкніть `channels.telegram.commands.native`, якщо меню вам не потрібне.
    - `TypeError: fetch failed`, `Network request for 'setMyCommands' failed!` або подібні мережеві помилки: якщо ви працюєте на VPS або за proxy, переконайтеся, що вихідний HTTPS дозволено й DNS працює для `api.telegram.org`.

    Якщо Gateway віддалений, переконайтеся, що дивитеся логи саме на хості Gateway.

    Документація: [Telegram](/uk/channels/telegram), [Усунення проблем із channels](/uk/channels/troubleshooting).

  </Accordion>

  <Accordion title="TUI не показує вивід. Що перевірити?">
    Спочатку переконайтеся, що Gateway доступний і agent може працювати:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    У TUI використовуйте `/status`, щоб побачити поточний стан. Якщо ви очікуєте відповіді в chat
    channel, переконайтеся, що доставку ввімкнено (`/deliver on`).

    Документація: [TUI](/web/tui), [Slash-команди](/uk/tools/slash-commands).

  </Accordion>

  <Accordion title="Як повністю зупинити, а потім запустити Gateway?">
    Якщо ви встановили сервіс:

    ```bash
    openclaw gateway stop
    openclaw gateway start
    ```

    Це зупиняє/запускає **сервіс під керуванням supervisor** (launchd на macOS, systemd на Linux).
    Використовуйте це, коли Gateway працює у фоновому режимі як демон.

    Якщо ви запускаєте у foreground, зупиніть через Ctrl-C, а потім:

    ```bash
    openclaw gateway run
    ```

    Документація: [Інструкція з роботи сервісу Gateway](/uk/gateway).

  </Accordion>

  <Accordion title="ELI5: openclaw gateway restart vs openclaw gateway">
    - `openclaw gateway restart`: перезапускає **фоновий сервіс** (launchd/systemd).
    - `openclaw gateway`: запускає gateway **у foreground** для цієї сесії термінала.

    Якщо ви встановили сервіс, використовуйте команди gateway. Використовуйте `openclaw gateway`, коли
    вам потрібен одноразовий запуск у foreground.

  </Accordion>

  <Accordion title="Найшвидший спосіб отримати більше деталей, коли щось ламається">
    Запустіть Gateway з `--verbose`, щоб отримати більше деталей у консолі. Потім перевірте файл логу щодо auth channel, маршрутизації model і помилок RPC.
  </Accordion>
</AccordionGroup>

## Медіа та вкладення

<AccordionGroup>
  <Accordion title="Мій skill згенерував зображення/PDF, але нічого не було надіслано">
    Вихідні вкладення від agent мають містити рядок `MEDIA:<path-or-url>` (в окремому рядку). Див. [Налаштування помічника OpenClaw](/uk/start/openclaw) і [Agent send](/uk/tools/agent-send).

    Надсилання через CLI:

    ```bash
    openclaw message send --target +15555550123 --message "Here you go" --media /path/to/file.png
    ```

    Також перевірте:

    - Цільовий channel підтримує вихідні медіа і не заблокований allowlist.
    - Файл відповідає обмеженням розміру provider (зображення змінюються до максимуму 2048px).
    - `tools.fs.workspaceOnly=true` обмежує надсилання локальних шляхів workspace, temp/media-store і файлами, перевіреними sandbox.
    - `tools.fs.workspaceOnly=false` дозволяє `MEDIA:` надсилати локальні файли хоста, які agent уже може читати, але лише для медіа плюс безпечних типів документів (зображення, аудіо, відео, PDF та документи Office). Звичайний текст і файли, схожі на секрети, усе одно блокуються.

    Див. [Зображення](/uk/nodes/images).

  </Accordion>
</AccordionGroup>

## Безпека та контроль доступу

<AccordionGroup>
  <Accordion title="Чи безпечно відкривати OpenClaw для вхідних DM?">
    Ставтеся до вхідних DM як до недовіреного вводу. Значення за замовчуванням спроєктовані для зменшення ризику:

    - Типова поведінка на channels, що підтримують DM, — це **pairing**:
      - Невідомі відправники отримують код pairing; бот не обробляє їхнє повідомлення.
      - Схвалення: `openclaw pairing approve --channel <channel> [--account <id>] <code>`
      - Кількість очікуваних запитів обмежено **3 на channel**; перевіряйте `openclaw pairing list --channel <channel> [--account <id>]`, якщо код не надійшов.
    - Публічне відкриття DM потребує явного opt-in (`dmPolicy: "open"` і allowlist `"*"`).

    Запустіть `openclaw doctor`, щоб виявити ризиковані політики DM.

  </Accordion>

  <Accordion title="Чи prompt injection є проблемою лише для публічних ботів?">
    Ні. Prompt injection стосується **недовіреного вмісту**, а не лише того, хто може надсилати DM боту.
    Якщо ваш помічник читає зовнішній вміст (web search/fetch, сторінки браузера, email,
    docs, вкладення, вставлені логи), цей вміст може містити інструкції, які намагаються
    перехопити модель. Це може трапитися, навіть якщо **ви — єдиний відправник**.

    Найбільший ризик виникає, коли ввімкнені інструменти: модель можна змусити
    ексфільтрувати контекст або викликати інструменти від вашого імені. Зменшуйте зону ураження так:

    - використовуйте "reader" agent у режимі лише читання або без інструментів для підсумовування недовіреного вмісту
    - тримайте `web_search` / `web_fetch` / `browser` вимкненими для agents з увімкненими інструментами
    - також вважайте недовіреним декодований текст файлів/документів: OpenResponses
      `input_file` і витягнення з медіавкладень обгортають витягнутий текст
      явними маркерами меж зовнішнього вмісту замість передачі сирого тексту файлу
    - використовуйте sandboxing і суворі allowlist інструментів

    Подробиці: [Security](/uk/gateway/security).

  </Accordion>

  <Accordion title="Чи повинен мій бот мати власний email, обліковий запис GitHub або номер телефону?">
    Так, для більшості сценаріїв. Ізоляція бота за допомогою окремих облікових записів і номерів телефону
    зменшує зону ураження, якщо щось піде не так. Це також полегшує ротацію
    облікових даних або відкликання доступу без впливу на ваші особисті облікові записи.

    Починайте з малого. Надавайте доступ лише до тих інструментів і облікових записів, які вам справді потрібні, і розширюйте
    його пізніше за потреби.

    Документація: [Security](/uk/gateway/security), [Pairing](/uk/channels/pairing).

  </Accordion>

  <Accordion title="Чи можу я надати йому автономність над моїми текстовими повідомленнями і чи це безпечно?">
    Ми **не** рекомендуємо повну автономність щодо ваших особистих повідомлень. Найбезпечніший шаблон:

    - Тримайте DM у режимі **pairing** або в жорсткому allowlist.
    - Використовуйте **окремий номер або обліковий запис**, якщо хочете, щоб він надсилав повідомлення від вашого імені.
    - Нехай він створює чернетку, а ви **схвалюйте перед надсиланням**.

    Якщо хочете поекспериментувати, робіть це на окремому обліковому записі й тримайте його ізольованим. Див.
    [Security](/uk/gateway/security).

  </Accordion>

  <Accordion title="Чи можу я використовувати дешевші models для завдань персонального помічника?">
    Так, **якщо** agent працює лише в чаті, а вхідні дані довірені. Менші рівні
    більш схильні до перехоплення інструкцій, тому уникайте їх для agents з увімкненими інструментами
    або під час читання недовіреного вмісту. Якщо вам усе ж потрібна менша model, жорстко обмежте
    інструменти й запускайте всередині sandbox. Див. [Security](/uk/gateway/security).
  </Accordion>

  <Accordion title="Я виконав /start у Telegram, але не отримав код pairing">
    Коди pairing надсилаються **лише** коли невідомий відправник пише боту і
    ввімкнено `dmPolicy: "pairing"`. Сам по собі `/start` не генерує код.

    Перевірте запити, що очікують:

    ```bash
    openclaw pairing list telegram
    ```

    Якщо вам потрібен негайний доступ, додайте свій sender id до allowlist або встановіть `dmPolicy: "open"`
    для цього облікового запису.

  </Accordion>

  <Accordion title="WhatsApp: чи буде він писати моїм контактам? Як працює pairing?">
    Ні. Типова політика DM у WhatsApp — **pairing**. Невідомі відправники отримують лише код pairing, а їхнє повідомлення **не обробляється**. OpenClaw відповідає лише в ті чати, з яких отримує повідомлення, або на явні надсилання, які ініціюєте ви.

    Схвалення pairing:

    ```bash
    openclaw pairing approve whatsapp <code>
    ```

    Перегляд запитів, що очікують:

    ```bash
    openclaw pairing list whatsapp
    ```

    Запит номера телефону в майстрі: він використовується для налаштування вашого **allowlist/owner**, щоб ваші власні DM були дозволені. Він не використовується для автоматичного надсилання. Якщо ви запускаєте на своєму особистому номері WhatsApp, використовуйте цей номер і ввімкніть `channels.whatsapp.selfChatMode`.

  </Accordion>
</AccordionGroup>

## Команди чату, переривання завдань і "воно не зупиняється"

<AccordionGroup>
  <Accordion title="Як зробити так, щоб внутрішні системні повідомлення не показувалися в чаті?">
    Більшість внутрішніх повідомлень або повідомлень інструментів з’являються лише тоді, коли для цієї session увімкнено **verbose**, **trace** або **reasoning**.

    Виправлення в чаті, де ви це бачите:

    ```
    /verbose off
    /trace off
    /reasoning off
    ```

    Якщо все одно занадто шумно, перевірте налаштування session у Control UI і встановіть verbose
    у значення **inherit**. Також переконайтеся, що ви не використовуєте профіль бота, у якому `verboseDefault` задано
    як `on` у config.

    Документація: [Thinking and verbose](/uk/tools/thinking), [Security](/uk/gateway/security#reasoning-verbose-output-in-groups).

  </Accordion>

  <Accordion title="Як зупинити/скасувати поточне завдання?">
    Надішліть будь-що з цього **як окреме повідомлення** (без slash):

    ```
    stop
    stop action
    stop current action
    stop run
    stop current run
    stop agent
    stop the agent
    stop openclaw
    openclaw stop
    stop don't do anything
    stop do not do anything
    stop doing anything
    please stop
    stop please
    abort
    esc
    wait
    exit
    interrupt
    ```

    Це тригери переривання (не slash-команди).

    Для фонових процесів (з інструмента exec) ви можете попросити agent виконати:

    ```
    process action:kill sessionId:XXX
    ```

    Огляд slash-команд: див. [Slash-команди](/uk/tools/slash-commands).

    Більшість команд мають надсилатися як **окреме** повідомлення, що починається з `/`, але деякі скорочення (наприклад, `/status`) також працюють inline для відправників з allowlist.

  </Accordion>

  <Accordion title='Як надіслати повідомлення в Discord із Telegram? ("Cross-context messaging denied")'>
    OpenClaw блокує **крос-провайдерний** обмін повідомленнями за замовчуванням. Якщо виклик інструмента прив’язано
    до Telegram, він не надішле в Discord, доки ви явно цього не дозволите.

    Увімкніть крос-провайдерний обмін повідомленнями для agent:

    ```json5
    {
      tools: {
        message: {
          crossContext: {
            allowAcrossProviders: true,
            marker: { enabled: true, prefix: "[from {channel}] " },
          },
        },
      },
    }
    ```

    Після редагування config перезапустіть gateway.

  </Accordion>

  <Accordion title='Чому здається, що бот "ігнорує" швидку серію повідомлень?'>
    Режим queue визначає, як нові повідомлення взаємодіють із поточним виконанням. Використовуйте `/queue`, щоб змінювати режими:

    - `steer` - нові повідомлення перенаправляють поточне завдання
    - `followup` - повідомлення виконуються по одному
    - `collect` - пакетування повідомлень і одна відповідь (типово)
    - `steer-backlog` - спочатку перенаправити, потім обробити беклог
    - `interrupt` - перервати поточне виконання і почати заново

    Ви можете додавати параметри, як-от `debounce:2s cap:25 drop:summarize`, для режимів followup.

  </Accordion>
</AccordionGroup>

## Різне

<AccordionGroup>
  <Accordion title='Яка model є типовою для Anthropic з API-ключем?'>
    В OpenClaw облікові дані й вибір model — це окремі речі. Установлення `ANTHROPIC_API_KEY` (або збереження API-ключа Anthropic в auth profiles) вмикає автентифікацію, але фактична model за замовчуванням — це те, що ви налаштовуєте в `agents.defaults.model.primary` (наприклад, `anthropic/claude-sonnet-4-6` або `anthropic/claude-opus-4-6`). Якщо ви бачите `No credentials found for profile "anthropic:default"`, це означає, що Gateway не зміг знайти облікові дані Anthropic в очікуваному `auth-profiles.json` для agent, який виконується.
  </Accordion>
</AccordionGroup>

---

Усе ще застрягли? Запитайте в [Discord](https://discord.com/invite/clawd) або відкрийте [обговорення GitHub](https://github.com/openclaw/openclaw/discussions).
