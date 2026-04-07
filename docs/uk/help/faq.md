---
read_when:
    - Відповідь на поширені запитання щодо налаштування, встановлення, онбордингу або підтримки під час виконання
    - Тріаж проблем, про які повідомляють користувачі, перед глибшим налагодженням
summary: Часті запитання про налаштування, конфігурацію та використання OpenClaw
title: ЧаПи
x-i18n:
    generated_at: "2026-04-07T19:00:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: 001b4605966b45b08108606f76ae937ec348c2179b04cf6fb34fef94833705e6
    source_path: help/faq.md
    workflow: 15
---

# ЧаПи

Швидкі відповіді та глибше усунення несправностей для реальних сценаріїв (локальна розробка, VPS, мультиагентність, OAuth/API-ключі, перемикання моделей при збоях). Для діагностики під час виконання див. [Усунення несправностей](/uk/gateway/troubleshooting). Повний довідник конфігурації див. у [Конфігурація](/uk/gateway/configuration).

## Перші 60 секунд, якщо щось зламалося

1. **Швидкий статус (перша перевірка)**

   ```bash
   openclaw status
   ```

   Швидкий локальний підсумок: ОС + оновлення, доступність gateway/сервісу, агенти/сесії, конфігурація провайдера + проблеми під час виконання (коли gateway доступний).

2. **Звіт, який можна вставити та поширити**

   ```bash
   openclaw status --all
   ```

   Діагностика лише для читання з хвостом журналу (токени замасковані).

3. **Стан демона + порту**

   ```bash
   openclaw gateway status
   ```

   Показує стан supervisor під час виконання проти доступності RPC, цільовий URL для probe та яку конфігурацію сервіс, імовірно, використав.

4. **Глибокі probe-перевірки**

   ```bash
   openclaw status --deep
   ```

   Виконує живу probe-перевірку стану gateway, включно з probe-перевірками каналів, коли це підтримується
   (потрібен доступний gateway). Див. [Стан](/uk/gateway/health).

5. **Переглянути хвіст останнього журналу**

   ```bash
   openclaw logs --follow
   ```

   Якщо RPC недоступний, використайте запасний варіант:

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   Файлові журнали відокремлені від журналів сервісу; див. [Журналювання](/uk/logging) та [Усунення несправностей](/uk/gateway/troubleshooting).

6. **Запустити doctor (виправлення)**

   ```bash
   openclaw doctor
   ```

   Виправляє/мігрує конфігурацію/стан + запускає перевірки справності. Див. [Doctor](/uk/gateway/doctor).

7. **Знімок gateway**

   ```bash
   openclaw health --json
   openclaw health --verbose   # показує цільовий URL + шлях до конфігурації при помилках
   ```

   Запитує в запущеного gateway повний знімок стану (лише WS). Див. [Стан](/uk/gateway/health).

## Швидкий старт і початкове налаштування

<AccordionGroup>
  <Accordion title="Я застряг, найшвидший спосіб вибратися">
    Використайте локального AI-агента, який може **бачити вашу машину**. Це набагато ефективніше, ніж питати
    в Discord, тому що більшість випадків «я застряг» — це **проблеми локальної конфігурації або середовища**,
    які віддалені помічники не можуть перевірити.

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    Ці інструменти можуть читати репозиторій, запускати команди, перевіряти журнали та допомагати виправляти
    налаштування на рівні машини (PATH, сервіси, дозволи, файли auth). Надайте їм **повну checkout-копію вихідного коду** через
    hackable (git) встановлення:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Це встановлює OpenClaw **із git checkout**, тож агент може читати код + документацію та
    міркувати про точну версію, яку ви запускаєте. Ви завжди можете повернутися на stable пізніше,
    повторно запустивши інсталятор без `--install-method git`.

    Порада: попросіть агента **спланувати та контролювати** виправлення (крок за кроком), а потім виконати лише
    потрібні команди. Це робить зміни меншими та простішими для аудиту.

    Якщо ви виявили справжній баг або виправлення, будь ласка, створіть GitHub issue або надішліть PR:
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    Почніть із цих команд (діліться виводом, коли просите про допомогу):

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    Що вони роблять:

    - `openclaw status`: швидкий знімок стану gateway/агента + базової конфігурації.
    - `openclaw models status`: перевіряє auth провайдерів + доступність моделей.
    - `openclaw doctor`: перевіряє та виправляє поширені проблеми конфігурації/стану.

    Інші корисні перевірки CLI: `openclaw status --all`, `openclaw logs --follow`,
    `openclaw gateway status`, `openclaw health --verbose`.

    Швидкий цикл налагодження: [Перші 60 секунд, якщо щось зламалося](#перші-60-секунд-якщо-щось-зламалося).
    Документація зі встановлення: [Встановлення](/uk/install), [Прапорці інсталятора](/uk/install/installer), [Оновлення](/uk/install/updating).

  </Accordion>

  <Accordion title="Heartbeat постійно пропускається. Що означають причини пропуску?">
    Поширені причини пропуску heartbeat:

    - `quiet-hours`: поза налаштованим вікном active-hours
    - `empty-heartbeat-file`: `HEARTBEAT.md` існує, але містить лише порожній каркас/заголовки
    - `no-tasks-due`: активний режим задач `HEARTBEAT.md`, але жоден інтервал задачі ще не настав
    - `alerts-disabled`: усю видимість heartbeat вимкнено (`showOk`, `showAlerts` і `useIndicator` вимкнені)

    У режимі задач часові позначки виконання зсуваються лише після завершення
    реального запуску heartbeat. Пропущені запуски не позначають задачі як виконані.

    Документація: [Heartbeat](/uk/gateway/heartbeat), [Автоматизація й задачі](/uk/automation).

  </Accordion>

  <Accordion title="Рекомендований спосіб встановити й налаштувати OpenClaw">
    Репозиторій рекомендує запуск із сирців і використання онбордингу:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    Майстер також може автоматично зібрати UI-ресурси. Після онбордингу ви зазвичай запускаєте Gateway на порту **18789**.

    Із сирців (для учасників/розробників):

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

  <Accordion title="Як відкрити dashboard після онбордингу?">
    Майстер відкриває ваш браузер із чистим URL dashboard (без токенів) одразу після онбордингу, а також виводить посилання у підсумку. Тримайте цю вкладку відкритою; якщо вона не запустилася, скопіюйте/вставте надрукований URL на тій самій машині.
  </Accordion>

  <Accordion title="Як автентифікувати dashboard на localhost і віддалено?">
    **Localhost (та сама машина):**

    - Відкрийте `http://127.0.0.1:18789/`.
    - Якщо запитується auth через shared secret, вставте налаштований token або password у налаштуваннях Control UI.
    - Джерело token: `gateway.auth.token` (або `OPENCLAW_GATEWAY_TOKEN`).
    - Джерело password: `gateway.auth.password` (або `OPENCLAW_GATEWAY_PASSWORD`).
    - Якщо shared secret ще не налаштовано, згенеруйте token за допомогою `openclaw doctor --generate-gateway-token`.

    **Не на localhost:**

    - **Tailscale Serve** (рекомендовано): залиште bind loopback, запустіть `openclaw gateway --tailscale serve`, відкрийте `https://<magicdns>/`. Якщо `gateway.auth.allowTailscale` дорівнює `true`, заголовки ідентичності задовольняють auth для Control UI/WebSocket (без вставляння shared secret, за умови довіреного gateway host); HTTP API усе одно потребують auth через shared secret, якщо ви свідомо не використовуєте `none` для private-ingress або HTTP auth довіреного proxy.
      Невдалі одночасні спроби Serve auth від того самого клієнта серіалізуються до того, як limiter невдалої auth зафіксує їх, тому друга невдала повторна спроба вже може показати `retry later`.
    - **Tailnet bind**: запустіть `openclaw gateway --bind tailnet --token "<token>"` (або налаштуйте auth через password), відкрийте `http://<tailscale-ip>:18789/`, потім вставте відповідний shared secret у налаштування dashboard.
    - **Identity-aware reverse proxy**: залиште Gateway за trusted proxy без loopback, налаштуйте `gateway.auth.mode: "trusted-proxy"`, потім відкрийте URL proxy.
    - **SSH tunnel**: `ssh -N -L 18789:127.0.0.1:18789 user@host`, потім відкрийте `http://127.0.0.1:18789/`. Auth через shared secret усе ще діє поверх тунелю; вставте налаштований token або password, якщо буде запит.

    Див. [Dashboard](/web/dashboard) і [Web surfaces](/web) щодо режимів bind і деталей auth.

  </Accordion>

  <Accordion title="Чому є дві конфігурації схвалення exec для chat approvals?">
    Вони керують різними шарами:

    - `approvals.exec`: пересилає запити на схвалення в chat-призначення
    - `channels.<channel>.execApprovals`: робить цей канал нативним клієнтом схвалення для exec approvals

    Політика exec на host усе ще є справжнім бар’єром схвалення. Конфігурація chat лише керує тим, де
    з’являються запити на схвалення і як люди можуть на них відповідати.

    У більшості сценаріїв вам **не** потрібні обидві:

    - Якщо chat уже підтримує команди й відповіді, `/approve` у тому ж chat працює через спільний шлях.
    - Якщо підтримуваний нативний канал може безпечно визначати approver-ів, OpenClaw тепер автоматично вмикає DM-first нативні approvals, коли `channels.<channel>.execApprovals.enabled` не встановлено або дорівнює `"auto"`.
    - Коли доступні нативні картки/кнопки схвалення, цей нативний UI є основним шляхом; агент має включати ручну команду `/approve`, лише якщо результат інструмента каже, що chat approvals недоступні або ручне схвалення — єдиний шлях.
    - Використовуйте `approvals.exec` лише коли запити також треба пересилати в інші chat-и або явні ops-room.
    - Використовуйте `channels.<channel>.execApprovals.target: "channel"` або `"both"` лише коли ви явно хочете, щоб запити на схвалення поверталися в початкову кімнату/тему.
    - Plugin approvals знову окремі: вони за замовчуванням використовують `/approve` у тому ж chat, необов’язкове пересилання `approvals.plugin`, і лише деякі нативні канали додатково зберігають нативну обробку схвалення plugin.

    Коротко: пересилання — для маршрутизації, конфігурація нативного клієнта — для багатшого UX, специфічного для каналу.
    Див. [Exec Approvals](/uk/tools/exec-approvals).

  </Accordion>

  <Accordion title="Яке середовище виконання мені потрібне?">
    Потрібен Node **>= 22**. Рекомендовано `pnpm`. Bun **не рекомендований** для Gateway.
  </Accordion>

  <Accordion title="Чи працює це на Raspberry Pi?">
    Так. Gateway легкий — документація вказує, що для особистого використання достатньо **512MB-1GB RAM**, **1 ядра** і близько **500MB**
    диска, а також зазначає, що **Raspberry Pi 4 може це запускати**.

    Якщо вам потрібен додатковий запас (журнали, медіа, інші сервіси), **рекомендовано 2GB**, але це
    не жорсткий мінімум.

    Порада: невеликий Pi/VPS може хостити Gateway, а ви можете під’єднувати **nodes** на своєму ноутбуці/телефоні для
    локального екрана/камери/canvas або виконання команд. Див. [Nodes](/uk/nodes).

  </Accordion>

  <Accordion title="Є якісь поради для встановлення на Raspberry Pi?">
    Коротко: працює, але очікуйте шорсткі краї.

    - Використовуйте **64-бітну** ОС і тримайте Node >= 22.
    - Віддавайте перевагу **hackable (git) install**, щоб бачити журнали й швидко оновлюватися.
    - Починайте без каналів/Skills, а потім додавайте їх по одному.
    - Якщо натрапите на дивні проблеми з бінарниками, зазвичай це проблема **сумісності ARM**.

    Документація: [Linux](/uk/platforms/linux), [Встановлення](/uk/install).

  </Accordion>

  <Accordion title="Застрягає на wake up my friend / онбординг не вилуплюється. Що робити?">
    Цей екран залежить від доступності Gateway та успішної auth. TUI також автоматично надсилає
    "Wake up, my friend!" під час першого hatch. Якщо ви бачите цей рядок **без відповіді**
    і токени залишаються на 0, агент так і не запустився.

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

    Якщо Gateway віддалений, переконайтеся, що tunnel/Tailscale-з’єднання активне і UI
    спрямований на правильний Gateway. Див. [Віддалений доступ](/uk/gateway/remote).

  </Accordion>

  <Accordion title="Чи можу я перенести своє налаштування на нову машину (Mac mini), не проходячи онбординг заново?">
    Так. Скопіюйте **каталог стану** і **workspace**, а потім один раз запустіть Doctor. Це
    збереже вашого бота «точно таким самим» (memory, історію сесій, auth і стан
    каналів), якщо ви скопіюєте **обидва** місця:

    1. Встановіть OpenClaw на нову машину.
    2. Скопіюйте `$OPENCLAW_STATE_DIR` (типово: `~/.openclaw`) зі старої машини.
    3. Скопіюйте свій workspace (типово: `~/.openclaw/workspace`).
    4. Запустіть `openclaw doctor` і перезапустіть сервіс Gateway.

    Це збереже конфігурацію, профілі auth, облікові дані WhatsApp, сесії та memory. Якщо ви в
    remote mode, пам’ятайте: gateway host володіє сховищем сесій і workspace.

    **Важливо:** якщо ви лише commit/push-ите свій workspace у GitHub, ви створюєте резервну
    копію **memory + bootstrap-файлів**, але **не** історії сесій або auth. Вони живуть
    у `~/.openclaw/` (наприклад `~/.openclaw/agents/<agentId>/sessions/`).

    Пов’язане: [Міграція](/uk/install/migrating), [Де що лежить на диску](#де-що-лежить-на-диску),
    [Workspace агента](/uk/concepts/agent-workspace), [Doctor](/uk/gateway/doctor),
    [Віддалений режим](/uk/gateway/remote).

  </Accordion>

  <Accordion title="Де подивитися, що нового в останній версії?">
    Перегляньте changelog у GitHub:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Найновіші записи — зверху. Якщо верхню секцію позначено як **Unreleased**, наступна датована
    секція — це остання випущена версія. Записи згруповано за **Highlights**, **Changes** і
    **Fixes** (а також документація/інші секції за потреби).

  </Accordion>

  <Accordion title="Не вдається відкрити docs.openclaw.ai (помилка SSL)">
    Деякі підключення Comcast/Xfinity помилково блокують `docs.openclaw.ai` через Xfinity
    Advanced Security. Вимкніть її або додайте `docs.openclaw.ai` до allowlist, а потім повторіть спробу.
    Будь ласка, допоможіть нам розблокувати це, повідомивши тут: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status).

    Якщо ви все ще не можете відкрити сайт, документація дзеркалиться на GitHub:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="Різниця між stable і beta">
    **Stable** і **beta** — це **npm dist-tags**, а не окремі гілки коду:

    - `latest` = stable
    - `beta` = рання збірка для тестування

    Зазвичай stable-реліз спочатку потрапляє в **beta**, а потім окремий крок
    просування переміщує цю ж версію в `latest`. Супровідники також можуть за потреби
    публікувати одразу в `latest`. Саме тому beta і stable після просування можуть
    вказувати на **ту саму версію**.

    Подивитися, що змінилося:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Для однорядкових команд встановлення та різниці між beta і dev див. accordion нижче.

  </Accordion>

  <Accordion title="Як встановити beta-версію і чим beta відрізняється від dev?">
    **Beta** — це npm dist-tag `beta` (може збігатися з `latest` після просування).
    **Dev** — це рухома голова `main` (git); коли публікується, використовує npm dist-tag `dev`.

    Однорядкові команди (macOS/Linux):

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Інсталятор для Windows (PowerShell):
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    Більше деталей: [Канали розробки](/uk/install/development-channels) і [Прапорці інсталятора](/uk/install/installer).

  </Accordion>

  <Accordion title="Як спробувати найсвіжіші біти?">
    Є два варіанти:

    1. **Канал dev (git checkout):**

    ```bash
    openclaw update --channel dev
    ```

    Це перемикає на гілку `main` і оновлює з сирців.

    2. **Hackable install (із сайту інсталятора):**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Це дає вам локальний репозиторій, який можна редагувати, а потім оновлювати через git.

    Якщо віддаєте перевагу чистому ручному clone, використайте:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    Документація: [Оновлення](/cli/update), [Канали розробки](/uk/install/development-channels),
    [Встановлення](/uk/install).

  </Accordion>

  <Accordion title="Скільки зазвичай займає встановлення та онбординг?">
    Приблизно:

    - **Встановлення:** 2-5 хвилин
    - **Онбординг:** 5-15 хвилин залежно від того, скільки каналів/моделей ви налаштовуєте

    Якщо зависає, використайте [Інсталятор завис?](#швидкий-старт-і-початкове-налаштування)
    і швидкий цикл налагодження в [Я застряг](#швидкий-старт-і-початкове-налаштування).

  </Accordion>

  <Accordion title="Інсталятор завис? Як отримати більше зворотного зв’язку?">
    Повторно запустіть інсталятор із **детальним виводом**:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    Встановлення beta з verbose:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    Для hackable (git) install:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    Еквівалент для Windows (PowerShell):

    ```powershell
    # install.ps1 ще не має окремого прапорця -Verbose.
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    Більше варіантів: [Прапорці інсталятора](/uk/install/installer).

  </Accordion>

  <Accordion title="У Windows під час встановлення написано git not found або openclaw not recognized">
    Дві поширені проблеми у Windows:

    **1) помилка npm spawn git / git not found**

    - Встановіть **Git for Windows** і переконайтеся, що `git` є у вашому PATH.
    - Закрийте й знову відкрийте PowerShell, а потім повторно запустіть інсталятор.

    **2) openclaw is not recognized після встановлення**

    - Ваш глобальний npm bin-каталог відсутній у PATH.
    - Перевірте шлях:

      ```powershell
      npm config get prefix
      ```

    - Додайте цей каталог до свого user PATH (суфікс `\bin` у Windows не потрібен; на більшості систем це `%AppData%\npm`).
    - Закрийте й знову відкрийте PowerShell після оновлення PATH.

    Якщо вам потрібне найплавніше налаштування у Windows, використовуйте **WSL2** замість нативного Windows.
    Документація: [Windows](/uk/platforms/windows).

  </Accordion>

  <Accordion title="У Windows вивід exec показує спотворений китайський текст — що робити?">
    Зазвичай це невідповідність code page консолі в нативних оболонках Windows.

    Симптоми:

    - вивід `system.run`/`exec` показує китайську як mojibake
    - та сама команда нормально виглядає в іншому профілі термінала

    Швидкий обхідний шлях у PowerShell:

    ```powershell
    chcp 65001
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    ```

    Потім перезапустіть Gateway і повторіть вашу команду:

    ```powershell
    openclaw gateway restart
    ```

    Якщо ви все ще відтворюєте це в останньому OpenClaw, відстежуйте/повідомляйте тут:

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="Документація не відповіла на моє запитання — як отримати кращу відповідь?">
    Використайте **hackable (git) install**, щоб мати повні сирці та документацію локально, а тоді запитайте
    свого бота (або Claude/Codex) _з цієї папки_, щоб він міг прочитати репозиторій і точно відповісти.

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Більше деталей: [Встановлення](/uk/install) і [Прапорці інсталятора](/uk/install/installer).

  </Accordion>

  <Accordion title="Як встановити OpenClaw на Linux?">
    Коротка відповідь: дотримуйтеся інструкції для Linux, а потім запустіть онбординг.

    - Швидкий шлях для Linux + встановлення сервісу: [Linux](/uk/platforms/linux).
    - Повний покроковий гайд: [Початок роботи](/uk/start/getting-started).
    - Інсталятор + оновлення: [Встановлення й оновлення](/uk/install/updating).

  </Accordion>

  <Accordion title="Як встановити OpenClaw на VPS?">
    Підійде будь-який Linux VPS. Встановіть на сервері, а потім використовуйте SSH/Tailscale для доступу до Gateway.

    Інструкції: [exe.dev](/uk/install/exe-dev), [Hetzner](/uk/install/hetzner), [Fly.io](/uk/install/fly).
    Віддалений доступ: [Віддалений Gateway](/uk/gateway/remote).

  </Accordion>

  <Accordion title="Де інструкції для встановлення в хмарі/VPS?">
    Ми підтримуємо **хаб хостингу** з поширеними провайдерами. Оберіть одного й дотримуйтеся інструкції:

    - [VPS-хостинг](/uk/vps) (усі провайдери в одному місці)
    - [Fly.io](/uk/install/fly)
    - [Hetzner](/uk/install/hetzner)
    - [exe.dev](/uk/install/exe-dev)

    Як це працює в хмарі: **Gateway працює на сервері**, а ви отримуєте до нього доступ
    зі свого ноутбука/телефона через Control UI (або Tailscale/SSH). Ваші state + workspace
    живуть на сервері, тож сприймайте host як джерело істини й робіть його резервні копії.

    Ви можете під’єднувати **nodes** (Mac/iOS/Android/headless) до цього хмарного Gateway, щоб отримати
    локальний екран/камеру/canvas або запускати команди на своєму ноутбуці, залишаючи
    Gateway у хмарі.

    Хаб: [Платформи](/uk/platforms). Віддалений доступ: [Віддалений Gateway](/uk/gateway/remote).
    Nodes: [Nodes](/uk/nodes), [CLI для Nodes](/cli/nodes).

  </Accordion>

  <Accordion title="Чи можу я попросити OpenClaw оновити самого себе?">
    Коротко: **можливо, але не рекомендовано**. Процес оновлення може перезапустити
    Gateway (що розірве активну сесію), може потребувати чистого git checkout і
    може запитувати підтвердження. Безпечніше запускати оновлення з оболонки як оператор.

    Використовуйте CLI:

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    Якщо вам обов’язково треба автоматизувати це через агента:

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    Документація: [Оновлення](/cli/update), [Оновлення](/uk/install/updating).

  </Accordion>

  <Accordion title="Що насправді робить онбординг?">
    `openclaw onboard` — рекомендований шлях налаштування. У **локальному режимі** він проводить вас через:

    - **Налаштування моделі/auth** (OAuth провайдера, API-ключі, Anthropic setup-token, а також локальні варіанти моделей, як-от LM Studio)
    - Розташування **workspace** + bootstrap-файли
    - **Налаштування Gateway** (bind/port/auth/tailscale)
    - **Канали** (WhatsApp, Telegram, Discord, Mattermost, Signal, iMessage, а також bundled channel plugins, як-от QQ Bot)
    - **Встановлення демона** (LaunchAgent у macOS; systemd user unit у Linux/WSL2)
    - **Перевірки справності** та вибір **Skills**

    Також він попереджає, якщо ваша налаштована модель невідома або для неї відсутня auth.

  </Accordion>

  <Accordion title="Чи потрібна мені підписка Claude або OpenAI, щоб це запускати?">
    Ні. Ви можете запускати OpenClaw з **API-ключами** (Anthropic/OpenAI/інші) або з
    **лише локальними моделями**, щоб ваші дані лишалися на вашому пристрої. Підписки (Claude
    Pro/Max або OpenAI Codex) — це необов’язкові способи автентифікації в цих провайдерів.

    Для Anthropic в OpenClaw практичний поділ такий:

    - **Anthropic API key**: звичайна оплата Anthropic API
    - **Claude CLI / auth підписки Claude в OpenClaw**: співробітники Anthropic
      повідомили нам, що таке використання знову дозволено, і OpenClaw розглядає використання `claude -p`
      як санкціоноване для цієї інтеграції, якщо Anthropic не опублікує нову
      політику

    Для довготривалих gateway host-ів Anthropic API keys усе ще є більш
    передбачуваним налаштуванням. OpenAI Codex OAuth явно підтримується для зовнішніх
    інструментів на кшталт OpenClaw.

    OpenClaw також підтримує інші хостингові варіанти на кшталт підписки, зокрема
    **Qwen Cloud Coding Plan**, **MiniMax Coding Plan** і
    **Z.AI / GLM Coding Plan**.

    Документація: [Anthropic](/uk/providers/anthropic), [OpenAI](/uk/providers/openai),
    [Qwen Cloud](/uk/providers/qwen),
    [MiniMax](/uk/providers/minimax), [GLM Models](/uk/providers/glm),
    [Локальні моделі](/uk/gateway/local-models), [Моделі](/uk/concepts/models).

  </Accordion>

  <Accordion title="Чи можу я використовувати підписку Claude Max без API key?">
    Так.

    Співробітники Anthropic повідомили нам, що використання Claude CLI у стилі OpenClaw знову дозволене, тож
    OpenClaw вважає auth через підписку Claude та використання `claude -p` санкціонованими
    для цієї інтеграції, якщо Anthropic не опублікує нову політику. Якщо вам потрібне
    найпередбачуваніше серверне налаштування, використовуйте натомість Anthropic API key.

  </Accordion>

  <Accordion title="Чи підтримуєте ви auth через підписку Claude (Claude Pro або Max)?">
    Так.

    Співробітники Anthropic повідомили нам, що таке використання знову дозволене, тож OpenClaw вважає
    повторне використання Claude CLI та використання `claude -p` санкціонованими для цієї інтеграції,
    якщо Anthropic не опублікує нову політику.

    Anthropic setup-token усе ще доступний як підтримуваний шлях токена OpenClaw, але OpenClaw тепер віддає перевагу повторному використанню Claude CLI та `claude -p`, коли це доступно.
    Для production або багатокористувацьких навантажень auth через Anthropic API key усе ще є
    безпечнішим і передбачуванішим вибором. Якщо вам потрібні інші варіанти hosted auth у стилі підписки
    в OpenClaw, див. [OpenAI](/uk/providers/openai), [Qwen / Model
    Cloud](/uk/providers/qwen), [MiniMax](/uk/providers/minimax) і [GLM
    Models](/uk/providers/glm).

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="Чому я бачу HTTP 429 rate_limit_error від Anthropic?">
Це означає, що вашу **квоту/ліміт швидкості Anthropic** вичерпано для поточного вікна. Якщо ви
використовуєте **Claude CLI**, дочекайтеся скидання вікна або підвищте свій план. Якщо ви
використовуєте **Anthropic API key**, перевірте Anthropic Console
щодо використання/оплати та за потреби підвищте ліміти.

    Якщо повідомлення конкретно таке:
    `Extra usage is required for long context requests`, запит намагається використати
    1M context beta від Anthropic (`context1m: true`). Це працює лише тоді, коли ваші
    облікові дані мають право на billing довгого контексту (billing за API key або
    шлях входу Claude в OpenClaw із увімкненим Extra Usage).

    Порада: налаштуйте **fallback model**, щоб OpenClaw міг продовжувати відповідати, поки для провайдера діє rate limit.
    Див. [Моделі](/cli/models), [OAuth](/uk/concepts/oauth) і
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/uk/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context).

  </Accordion>

  <Accordion title="Чи підтримується AWS Bedrock?">
    Так. OpenClaw має bundled провайдер **Amazon Bedrock (Converse)**. Коли присутні AWS env marker-и, OpenClaw може автоматично виявити каталог потокових/текстових Bedrock і об’єднати його як неявний провайдер `amazon-bedrock`; інакше ви можете явно ввімкнути `plugins.entries.amazon-bedrock.config.discovery.enabled` або додати запис провайдера вручну. Див. [Amazon Bedrock](/uk/providers/bedrock) і [Провайдери моделей](/uk/providers/models). Якщо ви віддаєте перевагу керованому потоку ключів, сумісний з OpenAI proxy перед Bedrock також залишається коректним варіантом.
  </Accordion>

  <Accordion title="Як працює auth Codex?">
    OpenClaw підтримує **OpenAI Code (Codex)** через OAuth (вхід через ChatGPT). Онбординг може запустити потік OAuth і встановить модель за замовчуванням на `openai-codex/gpt-5.4`, коли це доречно. Див. [Провайдери моделей](/uk/concepts/model-providers) і [Онбординг (CLI)](/uk/start/wizard).
  </Accordion>

  <Accordion title="Чому ChatGPT GPT-5.4 не відкриває openai/gpt-5.4 в OpenClaw?">
    OpenClaw розглядає ці два шляхи окремо:

    - `openai-codex/gpt-5.4` = OAuth ChatGPT/Codex
    - `openai/gpt-5.4` = прямий OpenAI Platform API

    В OpenClaw вхід через ChatGPT/Codex прив’язаний до шляху `openai-codex/*`,
    а не до прямого шляху `openai/*`. Якщо ви хочете прямий API-шлях в
    OpenClaw, встановіть `OPENAI_API_KEY` (або еквівалентну конфігурацію провайдера OpenAI).
    Якщо ви хочете вхід через ChatGPT/Codex в OpenClaw, використовуйте `openai-codex/*`.

  </Accordion>

  <Accordion title="Чому ліміти Codex OAuth можуть відрізнятися від ChatGPT web?">
    `openai-codex/*` використовує шлях Codex OAuth, і його доступні квотні вікна
    керуються OpenAI та залежать від плану. На практиці ці ліміти можуть відрізнятися від
    досвіду на сайті/в застосунку ChatGPT, навіть коли обидва пов’язані з тим самим обліковим записом.

    OpenClaw може показувати поточні видимі вікна використання/квот провайдера у
    `openclaw models status`, але він не вигадує і не нормалізує привілеї ChatGPT-web
    у прямий API-доступ. Якщо вам потрібен прямий шлях OpenAI Platform
    billing/limit, використовуйте `openai/*` з API key.

  </Accordion>

  <Accordion title="Чи підтримуєте ви auth через підписку OpenAI (Codex OAuth)?">
    Так. OpenClaw повністю підтримує **OAuth підписки OpenAI Code (Codex)**.
    OpenAI явно дозволяє використання subscription OAuth у зовнішніх інструментах/робочих процесах
    на кшталт OpenClaw. Онбординг може запустити потік OAuth за вас.

    Див. [OAuth](/uk/concepts/oauth), [Провайдери моделей](/uk/concepts/model-providers), і [Онбординг (CLI)](/uk/start/wizard).

  </Accordion>

  <Accordion title="Як налаштувати Gemini CLI OAuth?">
    Gemini CLI використовує **plugin auth flow**, а не client id чи secret у `openclaw.json`.

    Кроки:

    1. Встановіть Gemini CLI локально, щоб `gemini` був у `PATH`
       - Homebrew: `brew install gemini-cli`
       - npm: `npm install -g @google/gemini-cli`
    2. Увімкніть plugin: `openclaw plugins enable google`
    3. Увійдіть: `openclaw models auth login --provider google-gemini-cli --set-default`
    4. Модель за замовчуванням після входу: `google-gemini-cli/gemini-3-flash-preview`
    5. Якщо запити не працюють, установіть `GOOGLE_CLOUD_PROJECT` або `GOOGLE_CLOUD_PROJECT_ID` на gateway host

    Це зберігає токени OAuth у профілях auth на gateway host. Деталі: [Провайдери моделей](/uk/concepts/model-providers).

  </Accordion>

  <Accordion title="Чи підходить локальна модель для невимушених чатів?">
    Зазвичай ні. OpenClaw потребує великого контексту + сильної безпеки; малі карти обрізають і протікають. Якщо вже мусите, запускайте **найбільшу** збірку моделі, яку можете локально (LM Studio), і див. [/gateway/local-models](/uk/gateway/local-models). Менші/квантизовані моделі підвищують ризик prompt injection — див. [Безпека](/uk/gateway/security).
  </Accordion>

  <Accordion title="Як утримувати трафік hosted-моделей у певному регіоні?">
    Обирайте endpoint-и, прив’язані до регіону. OpenRouter надає US-hosted варіанти для MiniMax, Kimi та GLM; оберіть US-hosted варіант, щоб тримати дані в регіоні. Ви все одно можете перелічити Anthropic/OpenAI поруч із ними, використовуючи `models.mode: "merge"`, щоб fallback лишалися доступними, водночас поважаючи обраного вами регіонального провайдера.
  </Accordion>

  <Accordion title="Чи треба мені купувати Mac Mini, щоб це встановити?">
    Ні. OpenClaw працює на macOS або Linux (Windows через WSL2). Mac mini — необов’язковий:
    дехто купує його як завжди ввімкнений host, але невеликий VPS, домашній сервер або коробка рівня Raspberry Pi теж підійдуть.

    Mac потрібен лише для **інструментів, доступних тільки на macOS**. Для iMessage використовуйте [BlueBubbles](/uk/channels/bluebubbles) (рекомендовано) — сервер BlueBubbles працює на будь-якому Mac, а Gateway може працювати на Linux чи деінде. Якщо вам потрібні інші інструменти лише для macOS, запускайте Gateway на Mac або під’єднайте macOS node.

    Документація: [BlueBubbles](/uk/channels/bluebubbles), [Nodes](/uk/nodes), [Віддалений режим Mac](/uk/platforms/mac/remote).

  </Accordion>

  <Accordion title="Чи потрібен мені Mac mini для підтримки iMessage?">
    Вам потрібен **якийсь пристрій macOS**, у якому виконано вхід у Messages. Це **не обов’язково** має бути Mac mini —
    підійде будь-який Mac. **Використовуйте [BlueBubbles](/uk/channels/bluebubbles)** (рекомендовано) для iMessage — сервер BlueBubbles працює на macOS, тоді як Gateway може працювати на Linux або деінде.

    Типові сценарії:

    - Запускайте Gateway на Linux/VPS, а сервер BlueBubbles — на будь-якому Mac із входом у Messages.
    - Запускайте все на Mac, якщо хочете найпростішу конфігурацію на одній машині.

    Документація: [BlueBubbles](/uk/channels/bluebubbles), [Nodes](/uk/nodes),
    [Віддалений режим Mac](/uk/platforms/mac/remote).

  </Accordion>

  <Accordion title="Якщо я куплю Mac mini для запуску OpenClaw, чи зможу я під’єднати його до свого MacBook Pro?">
    Так. **Mac mini може запускати Gateway**, а ваш MacBook Pro може під’єднатися як
    **node** (супутній пристрій). Nodes не запускають Gateway — вони надають додаткові
    можливості, як-от screen/camera/canvas і `system.run` на цьому пристрої.

    Типовий шаблон:

    - Gateway на Mac mini (завжди ввімкнений).
    - MacBook Pro запускає застосунок macOS або host node й під’єднується до Gateway.
    - Використовуйте `openclaw nodes status` / `openclaw nodes list`, щоб це побачити.

    Документація: [Nodes](/uk/nodes), [CLI для Nodes](/cli/nodes).

  </Accordion>

  <Accordion title="Чи можу я використовувати Bun?">
    Bun **не рекомендований**. Ми спостерігаємо баги під час виконання, особливо з WhatsApp і Telegram.
    Для стабільних gateway використовуйте **Node**.

    Якщо ви все ж хочете поекспериментувати з Bun, робіть це на непродукційному gateway
    без WhatsApp/Telegram.

  </Accordion>

  <Accordion title="Telegram: що потрібно вказати в allowFrom?">
    `channels.telegram.allowFrom` — це **Telegram user ID людини-відправника** (числовий). Це не username бота.

    Онбординг приймає ввід `@username` і перетворює його на числовий ID, але авторизація OpenClaw використовує лише числові ID.

    Безпечніше (без стороннього бота):

    - Напишіть у DM своєму боту, а потім виконайте `openclaw logs --follow` і прочитайте `from.id`.

    Офіційний Bot API:

    - Напишіть у DM своєму боту, а потім викличте `https://api.telegram.org/bot<bot_token>/getUpdates` і прочитайте `message.from.id`.

    Сторонній варіант (менше приватності):

    - Напишіть у DM `@userinfobot` або `@getidsbot`.

    Див. [/channels/telegram](/uk/channels/telegram#access-control-and-activation).

  </Accordion>

  <Accordion title="Чи можуть кілька людей використовувати один номер WhatsApp з різними екземплярами OpenClaw?">
    Так, через **маршрутизацію мультиагентності**. Прив’яжіть **DM** WhatsApp кожного відправника (peer `kind: "direct"`, sender E.164 на кшталт `+15551234567`) до різного `agentId`, щоб кожна людина мала власний workspace і сховище сесій. Відповіді все одно надходитимуть з **того самого облікового запису WhatsApp**, а контроль доступу до DM (`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`) є глобальним для всього облікового запису WhatsApp. Див. [Маршрутизація мультиагентності](/uk/concepts/multi-agent) і [WhatsApp](/uk/channels/whatsapp).
  </Accordion>

  <Accordion title='Чи можу я запустити агента "fast chat" і агента "Opus for coding"?'>
    Так. Використовуйте маршрутизацію мультиагентності: надайте кожному агенту власну модель за замовчуванням, а потім прив’яжіть вхідні маршрути (обліковий запис провайдера або конкретні peer-и) до кожного агента. Приклад конфігурації наведено в [Маршрутизація мультиагентності](/uk/concepts/multi-agent). Див. також [Моделі](/uk/concepts/models) і [Конфігурація](/uk/gateway/configuration).
  </Accordion>

  <Accordion title="Чи працює Homebrew на Linux?">
    Так. Homebrew підтримує Linux (Linuxbrew). Швидке налаштування:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    Якщо ви запускаєте OpenClaw через systemd, переконайтеся, що PATH сервісу містить `/home/linuxbrew/.linuxbrew/bin` (або ваш префікс brew), щоб інструменти, встановлені через `brew`, знаходилися в non-login shell.
    Останні збірки також додають поширені user bin-каталоги до Linux systemd services (наприклад `~/.local/bin`, `~/.npm-global/bin`, `~/.local/share/pnpm`, `~/.bun/bin`) і враховують `PNPM_HOME`, `NPM_CONFIG_PREFIX`, `BUN_INSTALL`, `VOLTA_HOME`, `ASDF_DATA_DIR`, `NVM_DIR` та `FNM_DIR`, якщо вони встановлені.

  </Accordion>

  <Accordion title="Різниця між hackable git install і npm install">
    - **Hackable (git) install:** повний checkout сирців, редагований, найкраще для учасників.
      Ви збираєте все локально і можете патчити код/документацію.
    - **npm install:** глобальне встановлення CLI, без репозиторію, найкраще для «просто запустити».
      Оновлення надходять із npm dist-tags.

    Документація: [Початок роботи](/uk/start/getting-started), [Оновлення](/uk/install/updating).

  </Accordion>

  <Accordion title="Чи можу я пізніше перемикатися між npm і git install?">
    Так. Встановіть інший варіант, а потім запустіть Doctor, щоб gateway service вказував на нову entrypoint.
    Це **не видаляє ваші дані** — змінюється лише встановлений код OpenClaw. Ваші state
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

    Doctor виявляє невідповідність entrypoint сервісу gateway і пропонує переписати конфігурацію сервісу так, щоб вона відповідала поточному встановленню (для автоматизації використовуйте `--repair`).

    Поради щодо резервного копіювання: див. [Стратегія резервного копіювання](#де-що-лежить-на-диску).

  </Accordion>

  <Accordion title="Чи слід запускати Gateway на ноутбуці чи на VPS?">
    Коротко: **якщо вам потрібна надійність 24/7, використовуйте VPS**. Якщо вам потрібен
    найменший тертя і вас влаштовують сон/перезапуски, запускайте локально.

    **Ноутбук (локальний Gateway)**

    - **Плюси:** без витрат на сервер, прямий доступ до локальних файлів, видиме вікно браузера.
    - **Мінуси:** сон/обриви мережі = розриви з’єднання, оновлення ОС/перезавантаження переривають роботу, машина має не засинати.

    **VPS / хмара**

    - **Плюси:** завжди ввімкнений, стабільна мережа, без проблем зі сном ноутбука, простіше тримати в роботі.
    - **Мінуси:** часто headless (використовуйте screenshot-и), доступ до файлів лише віддалений, для оновлень потрібен SSH.

    **Примітка, специфічна для OpenClaw:** WhatsApp/Telegram/Slack/Mattermost/Discord чудово працюють із VPS. Єдиний справжній компроміс — **headless browser** проти видимого вікна. Див. [Browser](/uk/tools/browser).

    **Рекомендований варіант за замовчуванням:** VPS, якщо у вас раніше були від’єднання gateway. Локальний запуск чудовий, коли ви активно користуєтеся Mac і хочете локальний доступ до файлів або автоматизацію UI з видимим браузером.

  </Accordion>

  <Accordion title="Наскільки важливо запускати OpenClaw на окремій машині?">
    Не обов’язково, але **рекомендовано для надійності та ізоляції**.

    - **Виділений host (VPS/Mac mini/Pi):** завжди ввімкнений, менше переривань через сон/перезавантаження, чистіші дозволи, легше підтримувати в роботі.
    - **Спільний ноутбук/desktop:** цілком підходить для тестування й активного використання, але очікуйте пауз, коли машина засинає або оновлюється.

    Якщо хочете мати найкраще з обох світів, тримайте Gateway на виділеному host і під’єднуйте свій ноутбук як **node** для локальних screen/camera/exec-інструментів. Див. [Nodes](/uk/nodes).
    Для вказівок з безпеки див. [Безпека](/uk/gateway/security).

  </Accordion>

  <Accordion title="Які мінімальні вимоги до VPS і яка ОС рекомендована?">
    OpenClaw легкий. Для базового Gateway + одного chat-каналу:

    - **Абсолютний мінімум:** 1 vCPU, 1GB RAM, ~500MB диска.
    - **Рекомендовано:** 1-2 vCPU, 2GB RAM або більше для запасу (журнали, медіа, кілька каналів). Інструменти Node і автоматизація браузера можуть бути вимогливими до ресурсів.

    ОС: використовуйте **Ubuntu LTS** (або будь-який сучасний Debian/Ubuntu). Саме цей шлях встановлення для Linux протестовано найкраще.

    Документація: [Linux](/uk/platforms/linux), [VPS-хостинг](/uk/vps).

  </Accordion>

  <Accordion title="Чи можу я запускати OpenClaw у VM і які вимоги?">
    Так. Ставтеся до VM так само, як до VPS: вона має бути завжди ввімкненою, доступною та мати достатньо
    RAM для Gateway і будь-яких каналів, які ви ввімкнете.

    Базові рекомендації:

    - **Абсолютний мінімум:** 1 vCPU, 1GB RAM.
    - **Рекомендовано:** 2GB RAM або більше, якщо ви запускаєте кілька каналів, автоматизацію браузера чи media-інструменти.
    - **ОС:** Ubuntu LTS або інший сучасний Debian/Ubuntu.

    Якщо ви на Windows, **WSL2 — це найпростіше налаштування в стилі VM** і воно має найкращу
    сумісність інструментів. Див. [Windows](/uk/platforms/windows), [VPS-хостинг](/uk/vps).
    Якщо ви запускаєте macOS у VM, див. [macOS VM](/uk/install/macos-vm).

  </Accordion>
</AccordionGroup>

## Що таке OpenClaw?

<AccordionGroup>
  <Accordion title="Що таке OpenClaw, в одному абзаці?">
    OpenClaw — це персональний AI-помічник, якого ви запускаєте на власних пристроях. Він відповідає на поверхнях повідомлень, якими ви вже користуєтеся (WhatsApp, Telegram, Slack, Mattermost, Discord, Google Chat, Signal, iMessage, WebChat, а також bundled channel plugins, як-от QQ Bot) і також може працювати з голосом + live Canvas на підтримуваних платформах. **Gateway** — це завжди ввімкнена control plane; помічник і є продуктом.
  </Accordion>

  <Accordion title="Ціннісна пропозиція">
    OpenClaw — це не «просто обгортка над Claude». Це **локальна control plane**, яка дозволяє вам запускати
    потужного помічника на **вашому власному обладнанні**, доступного через chat-застосунки, якими ви вже користуєтеся, із
    сесіями зі станом, memory та інструментами — без передачі контролю над вашими робочими процесами hosted
    SaaS.

    Основні переваги:

    - **Ваші пристрої, ваші дані:** запускайте Gateway там, де хочете (Mac, Linux, VPS) і тримайте
      workspace + історію сесій локально.
    - **Справжні канали, а не web-пісочниця:** WhatsApp/Telegram/Slack/Discord/Signal/iMessage тощо,
      а також мобільний голос і Canvas на підтримуваних платформах.
    - **Незалежність від моделі:** використовуйте Anthropic, OpenAI, MiniMax, OpenRouter тощо, з маршрутизацією
      по агенту і failover.
    - **Лише локальний варіант:** запускайте локальні моделі, щоб **усі дані могли залишатися на вашому пристрої**, якщо хочете.
    - **Маршрутизація мультиагентності:** окремі агенти для кожного каналу, облікового запису або задачі, кожен із власним
      workspace і значеннями за замовчуванням.
    - **Open source і hackable:** перевіряйте, розширюйте і self-host-те без прив’язки до постачальника.

    Документація: [Gateway](/uk/gateway), [Канали](/uk/channels), [Мультиагентність](/uk/concepts/multi-agent),
    [Memory](/uk/concepts/memory).

  </Accordion>

  <Accordion title="Я щойно це налаштував — що мені робити спочатку?">
    Гарні перші проєкти:

    - Створити сайт (WordPress, Shopify або простий статичний сайт).
    - Прототипувати мобільний застосунок (структура, екрани, план API).
    - Упорядкувати файли й папки (очищення, іменування, теги).
    - Під’єднати Gmail і автоматизувати підсумки або follow up.

    Він може виконувати великі задачі, але найкраще працює, коли ви ділите їх на фази й
    використовуєте sub-agents для паралельної роботи.

  </Accordion>

  <Accordion title="Які п’ять найкращих щоденних сценаріїв використання OpenClaw?">
    Щоденні виграші зазвичай виглядають так:

    - **Персональні брифінги:** підсумки пошти, календаря та новин, які вам важливі.
    - **Дослідження й чернетки:** швидкі дослідження, підсумки та перші чернетки для листів або документів.
    - **Нагадування й follow up:** nudges і чеклисти, керовані cron або heartbeat.
    - **Автоматизація браузера:** заповнення форм, збір даних і повторення web-завдань.
    - **Координація між пристроями:** надішліть задачу з телефона, дозвольте Gateway виконати її на сервері й отримайте результат назад у chat.

  </Accordion>

  <Accordion title="Чи може OpenClaw допомогти з lead gen, outreach, рекламою та блогами для SaaS?">
    Так — для **дослідження, кваліфікації та підготовки чернеток**. Він може сканувати сайти, створювати shortlists,
    підсумовувати потенційних клієнтів і писати чернетки для outreach або реклами.

    Для **outreach або рекламних кампаній** залишайте людину в контурі. Уникайте спаму, дотримуйтеся місцевих законів і
    політик платформ та перевіряйте все перед відправленням. Найбезпечніший підхід — нехай
    OpenClaw створює чернетку, а ви схвалюєте.

    Документація: [Безпека](/uk/gateway/security).

  </Accordion>

  <Accordion title="Які переваги порівняно з Claude Code для web-розробки?">
    OpenClaw — це **персональний помічник** і шар координації, а не заміна IDE. Використовуйте
    Claude Code або Codex для найшвидшого прямого циклу програмування всередині репозиторію. Використовуйте OpenClaw, коли вам
    потрібні стійка memory, міжпристроєвий доступ і оркестрація інструментів.

    Переваги:

    - **Постійна memory + workspace** між сесіями
    - **Доступ із багатьох платформ** (WhatsApp, Telegram, TUI, WebChat)
    - **Оркестрація інструментів** (browser, файли, планування, hooks)
    - **Завжди ввімкнений Gateway** (запускайте на VPS, взаємодійте звідусіль)
    - **Nodes** для локального browser/screen/camera/exec

    Вітрина: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills та автоматизація

<AccordionGroup>
  <Accordion title="Як налаштовувати Skills, не забруднюючи репозиторій?">
    Використовуйте керовані override-и замість редагування копії в репозиторії. Помістіть свої зміни в `~/.openclaw/skills/<name>/SKILL.md` (або додайте папку через `skills.load.extraDirs` у `~/.openclaw/openclaw.json`). Пріоритет такий: `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs`, тож керовані override-и все одно мають перевагу над bundled Skills без змін у git. Якщо вам потрібно встановити skill глобально, але зробити її видимою лише для деяких агентів, тримайте спільну копію в `~/.openclaw/skills` і керуйте видимістю через `agents.defaults.skills` та `agents.list[].skills`. Лише зміни, варті upstream, мають жити в репозиторії та надсилатися як PR.
  </Accordion>

  <Accordion title="Чи можу я завантажувати Skills із власної папки?">
    Так. Додайте додаткові каталоги через `skills.load.extraDirs` у `~/.openclaw/openclaw.json` (найнижчий пріоритет). Типовий пріоритет: `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs`. `clawhub` за замовчуванням встановлює в `./skills`, який OpenClaw розглядає як `<workspace>/skills` у наступній сесії. Якщо skill має бути видимою лише певним агентам, поєднайте це з `agents.defaults.skills` або `agents.list[].skills`.
  </Accordion>

  <Accordion title="Як використовувати різні моделі для різних задач?">
    Наразі підтримуються такі шаблони:

    - **Cron jobs**: ізольовані задачі можуть задавати override `model` для кожної задачі.
    - **Sub-agents**: маршрутизуйте задачі до окремих агентів із різними моделями за замовчуванням.
    - **Перемикання на вимогу**: використовуйте `/model`, щоб будь-коли змінити модель поточної сесії.

    Див. [Cron jobs](/uk/automation/cron-jobs), [Маршрутизація мультиагентності](/uk/concepts/multi-agent) і [Slash commands](/uk/tools/slash-commands).

  </Accordion>

  <Accordion title="Бот зависає під час важкої роботи. Як винести це окремо?">
    Використовуйте **sub-agents** для довгих або паралельних задач. Sub-agents працюють у власній сесії,
    повертають підсумок і зберігають чутливість вашого основного chat.

    Попросіть бота «створити sub-agent для цієї задачі» або використайте `/subagents`.
    Використовуйте `/status` у chat, щоб бачити, що Gateway робить прямо зараз (і чи він зайнятий).

    Порада щодо токенів: і довгі задачі, і sub-agents споживають токени. Якщо вас хвилює вартість, задайте
    дешевшу модель для sub-agents через `agents.defaults.subagents.model`.

    Документація: [Sub-agents](/uk/tools/subagents), [Фонові задачі](/uk/automation/tasks).

  </Accordion>

  <Accordion title="Як працюють прив’язані до thread сесії subagent у Discord?">
    Використовуйте прив’язки thread. Ви можете прив’язати Discord thread до subagent-а або цілі session, щоб подальші повідомлення в цьому thread залишалися на прив’язаній сесії.

    Базовий потік:

    - Створіть через `sessions_spawn` з `thread: true` (і, за бажання, `mode: "session"` для постійних follow-up).
    - Або прив’яжіть вручну через `/focus <target>`.
    - Використовуйте `/agents`, щоб перевірити стан прив’язки.
    - Використовуйте `/session idle <duration|off>` і `/session max-age <duration|off>`, щоб керувати авто-втратою фокусу.
    - Використовуйте `/unfocus`, щоб від’єднати thread.

    Потрібна конфігурація:

    - Глобальні значення за замовчуванням: `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`.
    - Override-и Discord: `channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`.
    - Автоприв’язка під час spawn: встановіть `channels.discord.threadBindings.spawnSubagentSessions: true`.

    Документація: [Sub-agents](/uk/tools/subagents), [Discord](/uk/channels/discord), [Довідник конфігурації](/uk/gateway/configuration-reference), [Slash commands](/uk/tools/slash-commands).

  </Accordion>

  <Accordion title="Subagent завершився, але оновлення про завершення пішло не туди або взагалі не опублікувалося. Що перевірити?">
    Спочатку перевірте розв’язаний маршрут requester-а:

    - Доставка completion-mode subagent віддає перевагу будь-якому прив’язаному thread або маршруту conversation, якщо він існує.
    - Якщо origin завершення містить лише канал, OpenClaw повертається до збереженого маршруту сесії requester-а (`lastChannel` / `lastTo` / `lastAccountId`), щоб пряма доставка все ще могла спрацювати.
    - Якщо немає ні прив’язаного маршруту, ні придатного збереженого маршруту, пряма доставка може не вдатися, і результат повернеться до queued session delivery замість негайної публікації в chat.
    - Недійсні або застарілі цілі все ще можуть примусити fallback до queue або остаточну помилку доставки.
    - Якщо остання видима відповідь assistant у дочірньому процесі — це точний мовчазний токен `NO_REPLY` / `no_reply` або рівно `ANNOUNCE_SKIP`, OpenClaw навмисно пригнічує announce замість публікації застарілого попереднього прогресу.
    - Якщо дочірній процес завершився за timeout після лише викликів інструментів, announce може згорнути це до короткого підсумку часткового прогресу замість відтворення сирого виводу інструментів.

    Налагодження:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    Документація: [Sub-agents](/uk/tools/subagents), [Фонові задачі](/uk/automation/tasks), [Інструмент Session](/uk/concepts/session-tool).

  </Accordion>

  <Accordion title="Cron або нагадування не спрацьовують. Що перевірити?">
    Cron виконується всередині процесу Gateway. Якщо Gateway не працює безперервно,
    заплановані задачі не виконуватимуться.

    Чеклист:

    - Підтвердьте, що cron увімкнено (`cron.enabled`) і `OPENCLAW_SKIP_CRON` не встановлено.
    - Перевірте, що Gateway працює 24/7 (без сну/перезапусків).
    - Перевірте налаштування timezone для задачі (`--tz` проти timezone host).

    Налагодження:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    Документація: [Cron jobs](/uk/automation/cron-jobs), [Автоматизація й задачі](/uk/automation).

  </Accordion>

  <Accordion title="Cron спрацював, але нічого не було надіслано в канал. Чому?">
    Спочатку перевірте режим доставки:

    - `--no-deliver` / `delivery.mode: "none"` означає, що зовнішнє повідомлення не очікується.
    - Відсутня або недійсна announce-ціль (`channel` / `to`) означає, що runner пропустив outbound delivery.
    - Помилки auth каналу (`unauthorized`, `Forbidden`) означають, що runner спробував доставити, але облікові дані це заблокували.
    - Мовчазний ізольований результат (`NO_REPLY` / `no_reply` тільки) вважається навмисно недоставним, тому runner також пригнічує queued fallback delivery.

    Для ізольованих cron job-ів runner володіє фінальною доставкою. Очікується,
    що агент поверне текстовий підсумок, який runner зможе надіслати. `--no-deliver` зберігає
    цей результат внутрішнім; це не дозволяє агенту напряму надсилати через
    message tool.

    Налагодження:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Документація: [Cron jobs](/uk/automation/cron-jobs), [Фонові задачі](/uk/automation/tasks).

  </Accordion>

  <Accordion title="Чому ізольований cron run перемкнув моделі або один раз повторився?">
    Зазвичай це шлях живого перемикання моделі, а не дублювання розкладу.

    Ізольований cron може зберегти runtime handoff моделі й повторити спробу, коли активний
    запуск викидає `LiveSessionModelSwitchError`. Повторна спроба зберігає перемкненого
    провайдера/модель, і якщо перемикання несло новий override профілю auth, cron
    також зберігає його перед повтором.

    Пов’язані правила вибору:

    - Override моделі Gmail hook має найвищий пріоритет, коли це застосовно.
    - Потім `model` для задачі.
    - Потім будь-який збережений override моделі cron-session.
    - Потім звичайний вибір моделі агента/за замовчуванням.

    Цикл повторів обмежений. Після початкової спроби плюс 2 повтори перемикання
    cron переривається замість нескінченного циклу.

    Налагодження:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Документація: [Cron jobs](/uk/automation/cron-jobs), [cron CLI](/cli/cron).

  </Accordion>

  <Accordion title="Як встановити Skills на Linux?">
    Використовуйте нативні команди `openclaw skills` або покладіть Skills у свій workspace. UI Skills для macOS недоступний на Linux.
    Переглянути Skills можна на [https://clawhub.ai](https://clawhub.ai).

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
    синхронізувати власні Skills. Для спільних встановлень між агентами покладіть skill у
    `~/.openclaw/skills` і використовуйте `agents.defaults.skills` або
    `agents.list[].skills`, якщо хочете звузити, які агенти можуть її бачити.

  </Accordion>

  <Accordion title="Чи може OpenClaw запускати задачі за розкладом або безперервно у фоні?">
    Так. Використовуйте scheduler Gateway:

    - **Cron jobs** для запланованих або повторюваних задач (зберігаються між перезапусками).
    - **Heartbeat** для періодичних перевірок «головної сесії».
    - **Ізольовані jobs** для автономних агентів, які публікують підсумки або доставляють повідомлення в chat-и.

    Документація: [Cron jobs](/uk/automation/cron-jobs), [Автоматизація й задачі](/uk/automation),
    [Heartbeat](/uk/gateway/heartbeat).

  </Accordion>

  <Accordion title="Чи можу я запускати Apple Skills лише для macOS із Linux?">
    Не напряму. macOS Skills обмежуються через `metadata.openclaw.os` плюс потрібні бінарники, і Skills з’являються в system prompt, лише якщо вони придатні на **gateway host**. У Linux Skills тільки для `darwin` (як-от `apple-notes`, `apple-reminders`, `things-mac`) не завантажаться, якщо ви не перевизначите gating.

    У вас є три підтримувані шаблони:

    **Варіант A — запускати Gateway на Mac (найпростіше).**
    Запускайте Gateway там, де існують бінарники macOS, а тоді під’єднуйтеся з Linux у [віддаленому режимі](#gateway-порти-вже-запущені-і-віддалений-режим) або через Tailscale. Skills завантажаться нормально, бо gateway host — це macOS.

    **Варіант B — використовувати macOS node (без SSH).**
    Запускайте Gateway на Linux, під’єднайте macOS node (menubar app) і встановіть **Node Run Commands** на "Always Ask" або "Always Allow" на Mac. OpenClaw може вважати Skills лише для macOS придатними, коли потрібні бінарники існують на node. Агент запускає ці Skills через інструмент `nodes`. Якщо ви виберете "Always Ask", схвалення "Always Allow" у prompt додає цю команду до allowlist.

    **Варіант C — проксувати бінарники macOS через SSH (просунуто).**
    Тримайте Gateway на Linux, але зробіть так, щоб потрібні CLI-бінарники резолвилися в SSH-обгортки, які виконуються на Mac. Потім override-те skill, щоб дозволити Linux і вона лишалася придатною.

    1. Створіть SSH-обгортку для бінарника (приклад: `memo` для Apple Notes):

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. Помістіть обгортку в `PATH` на Linux host (наприклад `~/bin/memo`).
    3. Override-те metadata skill, щоб дозволити Linux:

       ```markdown
       ---
       name: apple-notes
       description: Керування Apple Notes через CLI memo на macOS.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. Почніть нову сесію, щоб знімок Skills оновився.

  </Accordion>

  <Accordion title="У вас є інтеграція з Notion або HeyGen?">
    Вбудовано наразі — ні.

    Варіанти:

    - **Власний skill / plugin:** найкраще для надійного API-доступу (і Notion, і HeyGen мають API).
    - **Автоматизація браузера:** працює без коду, але повільніше й крихкіше.

    Якщо ви хочете зберігати контекст по клієнту (робочі процеси агенції), простий шаблон такий:

    - Одна сторінка Notion на клієнта (контекст + вподобання + активна робота).
    - Попросіть агента отримувати цю сторінку на початку сесії.

    Якщо вам потрібна нативна інтеграція, відкрийте feature request або створіть skill,
    орієнтовану на ці API.

    Встановлення Skills:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    Нативні встановлення потрапляють у каталог `skills/` активного workspace. Для спільних Skills між агентами розміщуйте їх у `~/.openclaw/skills/<name>/SKILL.md`. Якщо лише деякі агенти повинні бачити спільне встановлення, налаштуйте `agents.defaults.skills` або `agents.list[].skills`. Деякі Skills очікують бінарники, установлені через Homebrew; на Linux це означає Linuxbrew (див. вище запис ЧаПів про Homebrew на Linux). Див. [Skills](/uk/tools/skills), [Конфігурація Skills](/uk/tools/skills-config) і [ClawHub](/uk/tools/clawhub).

  </Accordion>

  <Accordion title="Як використовувати вже авторизований Chrome з OpenClaw?">
    Використовуйте вбудований профіль браузера `user`, який під’єднується через Chrome DevTools MCP:

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    Якщо вам потрібна власна назва, створіть явний MCP-профіль:

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    Цей шлях локальний для host. Якщо Gateway працює десьінде, або запускайте node host на машині з браузером, або використовуйте віддалений CDP.

    Поточні обмеження `existing-session` / `user`:

    - дії працюють через ref, а не через CSS-selector
    - завантаження файлів потребує `ref` / `inputRef` і наразі підтримує лише один файл за раз
    - `responsebody`, експорт PDF, перехоплення завантажень і пакетні дії все ще потребують керованого browser або сирого CDP-профілю

  </Accordion>
</AccordionGroup>

## Пісочниця та memory

<AccordionGroup>
  <Accordion title="Чи є окремий документ про пісочницю?">
    Так. Див. [Пісочниця](/uk/gateway/sandboxing). Для налаштування, пов’язаного з Docker (повний gateway у Docker або образи пісочниці), див. [Docker](/uk/install/docker).
  </Accordion>

  <Accordion title="Docker здається обмеженим — як увімкнути повні можливості?">
    Стандартний image орієнтований на безпеку й працює від імені користувача `node`, тому він не
    містить system packages, Homebrew чи bundled browser-ів. Для повнішого налаштування:

    - Зберігайте `/home/node` через `OPENCLAW_HOME_VOLUME`, щоб кеші виживали.
    - Вбудовуйте системні залежності в image за допомогою `OPENCLAW_DOCKER_APT_PACKAGES`.
    - Встановлюйте browser-и Playwright через bundled CLI:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - Установіть `PLAYWRIGHT_BROWSERS_PATH` і переконайтеся, що цей шлях зберігається.

    Документація: [Docker](/uk/install/docker), [Browser](/uk/tools/browser).

  </Accordion>

  <Accordion title="Чи можу я тримати DM приватними, але зробити групи публічними/у пісочниці з одним агентом?">
    Так — якщо ваш приватний трафік це **DM**, а публічний трафік — **групи**.

    Використовуйте `agents.defaults.sandbox.mode: "non-main"`, щоб групові/канальні сесії (non-main keys) працювали в Docker, а головна DM-сесія лишалася на host. Потім обмежте, які інструменти доступні в сесіях пісочниці, через `tools.sandbox.tools`.

    Покрокове налаштування + приклад конфігурації: [Групи: персональні DM + публічні групи](/uk/channels/groups#pattern-personal-dms-public-groups-single-agent)

    Довідник ключової конфігурації: [Конфігурація Gateway](/uk/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="Як прив’язати папку host у пісочницю?">
    Установіть `agents.defaults.sandbox.docker.binds` на `["host:path:mode"]` (наприклад, `"/home/user/src:/src:ro"`). Глобальні прив’язки та прив’язки для конкретного агента об’єднуються; прив’язки для агента ігноруються, коли `scope: "shared"`. Використовуйте `:ro` для всього чутливого і пам’ятайте, що прив’язки обходять файлові стіни пісочниці.

    OpenClaw перевіряє джерела bind як за нормалізованим шляхом, так і за канонічним шляхом, розв’язаним через найглибшого існуючого предка. Це означає, що виходи через symlink-parent усе одно закриваються безпечно навіть коли останній сегмент шляху ще не існує, а перевірки allowed-root усе одно застосовуються після розв’язання symlink.

    Див. [Пісочниця](/uk/gateway/sandboxing#custom-bind-mounts) і [Sandbox vs Tool Policy vs Elevated](/uk/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check) для прикладів і приміток з безпеки.

  </Accordion>

  <Accordion title="Як працює memory?">
    Memory OpenClaw — це просто Markdown-файли в workspace агента:

    - Щоденні нотатки в `memory/YYYY-MM-DD.md`
    - Куровані довгострокові нотатки в `MEMORY.md` (лише для main/private session)

    OpenClaw також виконує **мовчазний flush memory перед compaction**, щоб нагадати моделі
    записати стійкі нотатки перед auto-compaction. Це працює лише коли workspace
    доступний для запису (read-only sandboxes пропускають це). Див. [Memory](/uk/concepts/memory).

  </Accordion>

  <Accordion title="Memory постійно все забуває. Як змусити це закріпитися?">
    Попросіть бота **записати факт у memory**. Довгострокові нотатки мають іти в `MEMORY.md`,
    короткостроковий контекст — у `memory/YYYY-MM-DD.md`.

    Це все ще зона, яку ми покращуємо. Допомагає нагадувати моделі зберігати спогади;
    вона знатиме, що робити. Якщо вона продовжує забувати, перевірте, що Gateway використовує той самий
    workspace в кожному запуску.

    Документація: [Memory](/uk/concepts/memory), [Workspace агента](/uk/concepts/agent-workspace).

  </Accordion>

  <Accordion title="Чи зберігається memory назавжди? Які обмеження?">
    Файли memory живуть на диску й зберігаються, доки ви їх не видалите. Обмеженням є ваше
    сховище, а не модель. **Контекст сесії** все одно обмежений вікном контексту моделі,
    тому довгі розмови можуть compact-итися або обрізатися. Саме тому існує пошук по
    memory — він повертає в контекст лише релевантні частини.

    Документація: [Memory](/uk/concepts/memory), [Контекст](/uk/concepts/context).

  </Accordion>

  <Accordion title="Чи потрібен OpenAI API key для семантичного пошуку memory?">
    Лише якщо ви використовуєте **OpenAI embeddings**. Codex OAuth покриває chat/completions і
    **не** дає доступу до embeddings, тож **вхід через Codex (OAuth або
    вхід через Codex CLI)** не допоможе для семантичного пошуку memory. OpenAI embeddings
    усе ще потребують справжній API key (`OPENAI_API_KEY` або `models.providers.openai.apiKey`).

    Якщо ви явно не задаєте провайдера, OpenClaw автоматично вибирає провайдера, коли він
    може розв’язати API key (профілі auth, `models.providers.*.apiKey` або env vars).
    Він віддає перевагу OpenAI, якщо розв’язується ключ OpenAI, інакше Gemini, якщо
    розв’язується ключ Gemini, потім Voyage, потім Mistral. Якщо жодного віддаленого ключа немає,
    пошук memory лишається вимкненим, доки ви його не налаштуєте. Якщо у вас налаштований і наявний
    шлях до локальної моделі, OpenClaw
    віддає перевагу `local`. Ollama підтримується, коли ви явно встановлюєте
    `memorySearch.provider = "ollama"`.

    Якщо ви віддаєте перевагу локальному режиму, встановіть `memorySearch.provider = "local"` (і за бажанням
    `memorySearch.fallback = "none"`). Якщо вам потрібні Gemini embeddings, установіть
    `memorySearch.provider = "gemini"` і надайте `GEMINI_API_KEY` (або
    `memorySearch.remote.apiKey`). Ми підтримуємо embedding-моделі **OpenAI, Gemini, Voyage, Mistral, Ollama або local**
    — подробиці налаштування див. у [Memory](/uk/concepts/memory).

  </Accordion>
</AccordionGroup>

## Де що лежить на диску

<AccordionGroup>
  <Accordion title="Чи всі дані, що використовуються з OpenClaw, зберігаються локально?">
    Ні — **стан OpenClaw локальний**, але **зовнішні сервіси все одно бачать те, що ви їм надсилаєте**.

    - **Локально за замовчуванням:** сесії, файли memory, конфігурація і workspace живуть на gateway host
      (`~/.openclaw` + ваш каталог workspace).
    - **Віддалено за необхідністю:** повідомлення, які ви надсилаєте провайдерам моделей (Anthropic/OpenAI тощо), ідуть до
      їхніх API, а chat-платформи (WhatsApp/Telegram/Slack тощо) зберігають дані повідомлень на
      своїх серверах.
    - **Ви контролюєте слід:** використання локальних моделей зберігає prompt-и на вашій машині, але трафік
      каналів усе одно проходить через сервери каналу.

    Пов’язане: [Workspace агента](/uk/concepts/agent-workspace), [Memory](/uk/concepts/memory).

  </Accordion>

  <Accordion title="Де OpenClaw зберігає свої дані?">
    Усе живе в `$OPENCLAW_STATE_DIR` (типово: `~/.openclaw`):

    | Path                                                            | Призначення                                                         |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | Основна конфігурація (JSON5)                                       |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | Застарілий імпорт OAuth (копіюється в auth profiles під час першого використання) |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | Auth profiles (OAuth, API keys і необов’язкові `keyRef`/`tokenRef`) |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | Необов’язкове резервне сховище секретів у файлі для `file` SecretRef providers |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | Файл застарілої сумісності (статичні записи `api_key` очищаються) |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | Стан провайдера (наприклад `whatsapp/<accountId>/creds.json`)      |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | Стан окремих агентів (agentDir + sessions)                         |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | Історія розмов і стан (для кожного агента)                         |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | Метадані сесій (для кожного агента)                                |

    Застарілий шлях для одного агента: `~/.openclaw/agent/*` (мігрується через `openclaw doctor`).

    Ваш **workspace** (`AGENTS.md`, файли memory, Skills тощо) зберігається окремо й налаштовується через `agents.defaults.workspace` (типово: `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title="Де мають лежати AGENTS.md / SOUL.md / USER.md / MEMORY.md?">
    Ці файли живуть у **workspace агента**, а не в `~/.openclaw`.

    - **Workspace (для кожного агента)**: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
      `MEMORY.md` (або застарілий fallback `memory.md`, коли `MEMORY.md` відсутній),
      `memory/YYYY-MM-DD.md`, необов’язковий `HEARTBEAT.md`.
    - **State dir (`~/.openclaw`)**: конфігурація, стан каналу/провайдера, профілі auth, сесії, журнали,
      і спільні Skills (`~/.openclaw/skills`).

    Workspace за замовчуванням — `~/.openclaw/workspace`, налаштовується через:

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    Якщо бот «забуває» після перезапуску, перевірте, що Gateway використовує той самий
    workspace при кожному запуску (і пам’ятайте: remote mode використовує **workspace gateway host-а**,
    а не вашого локального ноутбука).

    Порада: якщо ви хочете стійку поведінку або вподобання, попросіть бота **записати це в
    AGENTS.md або MEMORY.md**, а не покладатися на історію chat.

    Див. [Workspace агента](/uk/concepts/agent-workspace) і [Memory](/uk/concepts/memory).

  </Accordion>

  <Accordion title="Рекомендована стратегія резервного копіювання">
    Помістіть свій **workspace агента** у **приватний** git-репозиторій і робіть його резервну копію
    десь у приватному місці (наприклад у GitHub private). Це збереже memory + файли AGENTS/SOUL/USER
    та дозволить пізніше відновити «розум» помічника.

    **Не** commit-те нічого з `~/.openclaw` (облікові дані, сесії, токени або зашифровані payload-и секретів).
    Якщо вам потрібне повне відновлення, робіть резервні копії і workspace, і state directory
    окремо (див. питання про міграцію вище).

    Документація: [Workspace агента](/uk/concepts/agent-workspace).

  </Accordion>

  <Accordion title="Як повністю видалити OpenClaw?">
    Див. окремий гайд: [Видалення](/uk/install/uninstall).
  </Accordion>

  <Accordion title="Чи можуть агенти працювати поза workspace?">
    Так. Workspace — це **cwd за замовчуванням** і якір memory, а не жорстка пісочниця.
    Відносні шляхи розв’язуються всередині workspace, але абсолютні шляхи можуть отримати доступ до інших
    місць host-а, якщо пісочниця не ввімкнена. Якщо вам потрібна ізоляція, використовуйте
    [`agents.defaults.sandbox`](/uk/gateway/sandboxing) або налаштування пісочниці для конкретного агента. Якщо ви
    хочете, щоб репозиторій був cwd за замовчуванням, вкажіть `workspace`
    цього агента на корінь репозиторію. Репозиторій OpenClaw — це лише сирці; тримайте
    workspace окремо, якщо тільки ви свідомо не хочете, щоб агент працював усередині нього.

    Приклад (репозиторій як cwd за замовчуванням):

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

  <Accordion title="Віддалений режим: де зберігаються сесії?">
    Станом session володіє **gateway host**. Якщо ви в remote mode, сховище session, яке вас цікавить, знаходиться на віддаленій машині, а не на вашому локальному ноутбуці. Див. [Керування session](/uk/concepts/session).
  </Accordion>
</AccordionGroup>

## Основи конфігурації

<AccordionGroup>
  <Accordion title="Який формат конфігурації? Де вона знаходиться?">
    OpenClaw читає необов’язкову конфігурацію **JSON5** з `$OPENCLAW_CONFIG_PATH` (типово: `~/.openclaw/openclaw.json`):

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    Якщо файл відсутній, використовуються відносно безпечні значення за замовчуванням (зокрема workspace за замовчуванням `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title='Я встановив gateway.bind: "lan" (або "tailnet"), і тепер нічого не слухає / UI каже unauthorized'>
    Bind без loopback **потребують коректного шляху auth gateway**. На практиці це означає:

    - auth через shared secret: token або password
    - `gateway.auth.mode: "trusted-proxy"` за правильно налаштованим identity-aware reverse proxy без loopback

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

    - `gateway.remote.token` / `.password` **самі по собі** не вмикають auth локального gateway.
    - Локальні шляхи виклику можуть використовувати `gateway.remote.*` як fallback лише коли `gateway.auth.*` не встановлено.
    - Для auth через password встановіть натомість `gateway.auth.mode: "password"` разом із `gateway.auth.password` (або `OPENCLAW_GATEWAY_PASSWORD`).
    - Якщо `gateway.auth.token` / `gateway.auth.password` явно налаштовано через SecretRef і його не вдається розв’язати, розв’язання завершується безпечним закриттям (ніякий remote fallback це не маскує).
    - Налаштування Control UI через shared secret автентифікуються через `connect.params.auth.token` або `connect.params.auth.password` (зберігається в налаштуваннях app/UI). Режими з ідентичністю, як-от Tailscale Serve або `trusted-proxy`, натомість використовують request headers. Уникайте розміщення shared secret у URL.
    - З `gateway.auth.mode: "trusted-proxy"` reverse proxy на тому самому host через loopback усе одно **не** задовольняє trusted-proxy auth. Trusted proxy має бути налаштованим джерелом без loopback.

  </Accordion>

  <Accordion title="Чому тепер мені потрібен token на localhost?">
    OpenClaw примусово вимагає gateway auth за замовчуванням, зокрема і на loopback. У звичайному шляху за замовчуванням це означає auth через token: якщо явний шлях auth не налаштовано, під час запуску gateway резолвиться режим token і token генерується автоматично, зберігаючись у `gateway.auth.token`, тож **локальні WS-клієнти повинні автентифікуватися**. Це блокує виклики Gateway іншими локальними процесами.

    Якщо ви віддаєте перевагу іншому шляху auth, можете явно вибрати режим password (або, для identity-aware reverse proxy без loopback, `trusted-proxy`). Якщо ви **справді** хочете відкритий loopback, явно встановіть `gateway.auth.mode: "none"` у конфігурації. Doctor може згенерувати token у будь-який момент: `openclaw doctor --generate-gateway-token`.

  </Accordion>

  <Accordion title="Чи потрібно перезапускати після зміни конфігурації?">
    Gateway відстежує конфігурацію та підтримує hot-reload:

    - `gateway.reload.mode: "hybrid"` (типово): безпечні зміни застосовуються hot, для критичних виконується restart
    - Також підтримуються `hot`, `restart`, `off`

  </Accordion>

  <Accordion title="Як вимкнути кумедні слогани CLI?">
    Установіть `cli.banner.taglineMode` у конфігурації:

    ```json5
    {
      cli: {
        banner: {
          taglineMode: "off", // random | default | off
        },
      },
    }
    ```

    - `off`: приховує текст слогана, але залишає рядок заголовка/версії банера.
    - `default`: щоразу використовує `All your chats, one OpenClaw.`.
    - `random`: ротаційні кумедні/сезонні слогани (типова поведінка).
    - Якщо ви не хочете жодного банера, установіть env `OPENCLAW_HIDE_BANNER=1`.

  </Accordion>

  <Accordion title="Як увімкнути web search (і web fetch)?">
    `web_fetch` працює без API key. `web_search` залежить від вибраного
    провайдера:

    - Провайдери на основі API, такі як Brave, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Perplexity і Tavily, потребують звичайного налаштування API key.
    - Ollama Web Search не потребує ключа, але використовує ваш налаштований Ollama host і вимагає `ollama signin`.
    - DuckDuckGo не потребує ключа, але це неофіційна інтеграція на основі HTML.
    - SearXNG не потребує ключа / self-hosted; налаштуйте `SEARXNG_BASE_URL` або `plugins.entries.searxng.config.webSearch.baseUrl`.

    **Рекомендовано:** запустіть `openclaw configure --section web` і виберіть провайдера.
    Альтернативи через env:

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

    Конфігурація web-search для конкретного провайдера тепер живе під `plugins.entries.<plugin>.config.webSearch.*`.
    Застарілі шляхи провайдера `tools.web.search.*` усе ще тимчасово завантажуються для сумісності, але їх не слід використовувати в нових конфігураціях.
    Конфігурація fallback web-fetch Firecrawl живе під `plugins.entries.firecrawl.config.webFetch.*`.

    Примітки:

    - Якщо ви використовуєте allowlist, додайте `web_search`/`web_fetch`/`x_search` або `group:web`.
    - `web_fetch` увімкнено за замовчуванням (якщо його явно не вимкнено).
    - Якщо `tools.web.fetch.provider` пропущено, OpenClaw автоматично виявляє першого готового fallback-провайдера fetch із доступних облікових даних. Наразі bundled-провайдер — Firecrawl.
    - Демони читають env vars із `~/.openclaw/.env` (або середовища сервісу).

    Документація: [Web-інструменти](/uk/tools/web).

  </Accordion>

  <Accordion title="config.apply стер мою конфігурацію. Як відновити й уникнути цього?">
    `config.apply` замінює **всю конфігурацію**. Якщо ви надсилаєте частковий об’єкт, усе
    інше видаляється.

    Відновлення:

    - Відновіть із резервної копії (git або скопійованого `~/.openclaw/openclaw.json`).
    - Якщо резервної копії немає, повторно запустіть `openclaw doctor` і заново налаштуйте канали/моделі.
    - Якщо це сталося неочікувано, створіть bug report і додайте свою останню відому конфігурацію або будь-яку резервну копію.
    - Локальний coding-agent часто може відновити працездатну конфігурацію з журналів або історії.

    Як уникнути:

    - Використовуйте `openclaw config set` для малих змін.
    - Використовуйте `openclaw configure` для інтерактивного редагування.
    - Спочатку використовуйте `config.schema.lookup`, якщо ви не впевнені в точному шляху або формі поля; воно повертає неглибокий вузол schema плюс підсумки безпосередніх дочірніх елементів для покрокового дослідження.
    - Використовуйте `config.patch` для часткових RPC-редагувань; залишайте `config.apply` лише для повної заміни конфігурації.
    - Якщо ви використовуєте інструмент `gateway`, доступний лише owner, із запуску агента, він усе одно відхиляє записи в `tools.exec.ask` / `tools.exec.security` (зокрема застарілі псевдоніми `tools.bash.*`, які нормалізуються до тих самих захищених шляхів exec).

    Документація: [Config](/cli/config), [Configure](/cli/configure), [Doctor](/uk/gateway/doctor).

  </Accordion>

  <Accordion title="Як запустити центральний Gateway зі спеціалізованими worker-ами на різних пристроях?">
    Поширений шаблон — **один Gateway** (наприклад, Raspberry Pi) плюс **nodes** і **agents**:

    - **Gateway (центральний):** володіє каналами (Signal/WhatsApp), маршрутизацією і сесіями.
    - **Nodes (пристрої):** Macs/iOS/Android під’єднуються як периферія й надають локальні інструменти (`system.run`, `canvas`, `camera`).
    - **Agents (workers):** окремі мізки/workspaces для спеціальних ролей (наприклад, "Hetzner ops", "Personal data").
    - **Sub-agents:** породжують фонову роботу з основного агента, коли вам потрібен паралелізм.
    - **TUI:** під’єднується до Gateway і перемикає агентів/сесії.

    Документація: [Nodes](/uk/nodes), [Віддалений доступ](/uk/gateway/remote), [Маршрутизація мультиагентності](/uk/concepts/multi-agent), [Sub-agents](/uk/tools/subagents), [TUI](/web/tui).

  </Accordion>

  <Accordion title="Чи може browser OpenClaw працювати headless?">
    Так. Це опція конфігурації:

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

    Типове значення — `false` (headful). Headless із більшою ймовірністю викликає anti-bot перевірки на деяких сайтах. Див. [Browser](/uk/tools/browser).

    Headless використовує **той самий рушій Chromium** і працює для більшості автоматизації (форми, кліки, скрапінг, входи). Основні відмінності:

    - Немає видимого вікна браузера (використовуйте screenshot-и, якщо потрібні візуальні дані).
    - Деякі сайти суворіше ставляться до автоматизації в headless-режимі (CAPTCHA, anti-bot).
      Наприклад, X/Twitter часто блокує headless-сесії.

  </Accordion>

  <Accordion title="Як використовувати Brave для керування браузером?">
    Установіть `browser.executablePath` на ваш бінарник Brave (або будь-якого browser-а на основі Chromium) і перезапустіть Gateway.
    Повні приклади конфігурації див. у [Browser](/uk/tools/browser#use-brave-or-another-chromium-based-browser).
  </Accordion>
</AccordionGroup>

## Віддалені gateway та nodes

<AccordionGroup>
  <Accordion title="Як команди поширюються між Telegram, gateway і nodes?">
    Повідомлення Telegram обробляються **gateway**. Gateway запускає агента і
    лише потім викликає nodes через **Gateway WebSocket**, коли потрібен node tool:

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    Nodes не бачать вхідний трафік провайдерів; вони отримують лише node RPC-виклики.

  </Accordion>

  <Accordion title="Як мій агент може отримати доступ до мого комп’ютера, якщо Gateway розміщено віддалено?">
    Коротко: **під’єднайте свій комп’ютер як node**. Gateway працює в іншому місці, але він може
    викликати інструменти `node.*` (screen, camera, system) на вашій локальній машині через Gateway WebSocket.

    Типове налаштування:

    1. Запустіть Gateway на завжди ввімкненому host-і (VPS/домашній сервер).
    2. Додайте gateway host і свій комп’ютер до одного tailnet.
    3. Переконайтеся, що Gateway WS доступний (tailnet bind або SSH tunnel).
    4. Відкрийте локально застосунок macOS і під’єднайтеся в режимі **Remote over SSH** (або напряму через tailnet),
       щоб він міг зареєструватися як node.
    5. Схваліть node на Gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Окремий TCP-міст не потрібен; nodes під’єднуються через Gateway WebSocket.

    Нагадування про безпеку: під’єднання macOS node дозволяє `system.run` на цій машині. Під’єднуйте
    лише ті пристрої, яким довіряєте, і перегляньте [Безпека](/uk/gateway/security).

    Документація: [Nodes](/uk/nodes), [Протокол Gateway](/uk/gateway/protocol), [Віддалений режим macOS](/uk/platforms/mac/remote), [Безпека](/uk/gateway/security).

  </Accordion>

  <Accordion title="Tailscale під’єднано, але я не отримую відповідей. Що тепер?">
    Перевірте базові речі:

    - Gateway працює: `openclaw gateway status`
    - Стан Gateway: `openclaw status`
    - Стан каналу: `openclaw channels status`

    Потім перевірте auth і маршрутизацію:

    - Якщо ви використовуєте Tailscale Serve, переконайтеся, що `gateway.auth.allowTailscale` встановлено правильно.
    - Якщо ви під’єднуєтеся через SSH tunnel, підтвердьте, що локальний tunnel піднятий і вказує на правильний порт.
    - Переконайтеся, що ваші allowlist-и (DM або group) включають ваш обліковий запис.

    Документація: [Tailscale](/uk/gateway/tailscale), [Віддалений доступ](/uk/gateway/remote), [Канали](/uk/channels).

  </Accordion>

  <Accordion title="Чи можуть два екземпляри OpenClaw розмовляти один з одним (локальний + VPS)?">
    Так. Вбудованого мосту «бот-до-бота» немає, але це можна надійно організувати кількома
    способами:

    **Найпростіше:** використовуйте звичайний chat-канал, до якого мають доступ обидва боти (Telegram/Slack/WhatsApp).
    Нехай Бот A надсилає повідомлення Боту B, а потім Бот B відповідає як зазвичай.

    **CLI-міст (загальний):** запустіть script, який викликає інший Gateway через
    `openclaw agent --message ... --deliver`, націлюючись на chat, який слухає
    інший бот. Якщо один бот працює на віддаленому VPS, направте свій CLI на цей віддалений Gateway
    через SSH/Tailscale (див. [Віддалений доступ](/uk/gateway/remote)).

    Приклад шаблону (запускати з машини, яка може досягти цільового Gateway):

    ```bash
    openclaw agent --message "Привіт від локального бота" --deliver --channel telegram --reply-to <chat-id>
    ```

    Порада: додайте запобіжник, щоб два боти не зациклилися безкінечно (відповідь лише на згадку, channel
    allowlist-и або правило «не відповідати на повідомлення ботів»).

    Документація: [Віддалений доступ](/uk/gateway/remote), [CLI агента](/cli/agent), [Надсилання агентом](/uk/tools/agent-send).

  </Accordion>

  <Accordion title="Чи потрібні окремі VPS для кількох агентів?">
    Ні. Один Gateway може хостити кількох агентів, кожен із власним workspace, моделями за замовчуванням,
    і маршрутизацією. Це нормальне налаштування, і воно значно дешевше та простіше, ніж запускати
    один VPS на агента.

    Використовуйте окремі VPS лише тоді, коли вам потрібна жорстка ізоляція (межі безпеки) або дуже
    різні конфігурації, якими ви не хочете ділитися. В іншому разі тримайте один Gateway і
    використовуйте кілька агентів або sub-agents.

  </Accordion>

  <Accordion title="Чи є користь від використання node на моєму особистому ноутбуці замість SSH із VPS?">
    Так — nodes є першокласним способом доступу до вашого ноутбука з віддаленого Gateway, і вони
    відкривають більше, ніж просто доступ до оболонки. Gateway працює на macOS/Linux (Windows через WSL2) і є
    легким (підійде невеликий VPS або коробка рівня Raspberry Pi; 4 GB RAM достатньо), тож поширене
    налаштування — це завжди ввімкнений host плюс ваш ноутбук як node.

    - **Не потрібен вхідний SSH.** Nodes самі під’єднуються до Gateway WebSocket і використовують pairing пристроїв.
    - **Безпечніший контроль виконання.** `system.run` обмежується allowlist-ами/sхваленнями node на цьому ноутбуці.
    - **Більше інструментів пристрою.** Nodes надають `canvas`, `camera` і `screen` на додачу до `system.run`.
    - **Локальна автоматизація браузера.** Тримайте Gateway на VPS, але запускайте Chrome локально через node host на ноутбуці, або під’єднуйтеся до локального Chrome на host через Chrome MCP.

    SSH підходить для епізодичного доступу до оболонки, але nodes простіші для постійних агентських робочих процесів і
    автоматизації пристроїв.

    Документація: [Nodes](/uk/nodes), [CLI для Nodes](/cli/nodes), [Browser](/uk/tools/browser).

  </Accordion>

  <Accordion title="Чи запускають nodes gateway service?">
    Ні. На host має працювати лише **один gateway**, якщо ви навмисно не запускаєте ізольовані профілі (див. [Кілька gateway](/uk/gateway/multiple-gateways)). Nodes — це периферія, яка під’єднується
    до gateway (nodes iOS/Android або macOS "node mode" у menubar app). Для headless node
    host-ів і керування через CLI див. [CLI node host](/cli/node).

    Для змін `gateway`, `discovery` і `canvasHost` потрібен повний restart.

  </Accordion>

  <Accordion title="Чи є API / RPC-спосіб застосувати конфігурацію?">
    Так.

    - `config.schema.lookup`: перевірити одне піддерево конфігурації з його неглибоким вузлом schema, відповідною UI-підказкою та підсумками безпосередніх дочірніх елементів перед записом
    - `config.get`: отримати поточний snapshot + hash
    - `config.patch`: безпечне часткове оновлення (бажано для більшості RPC-редагувань); виконує hot-reload, коли можливо, і restart, коли потрібно
    - `config.apply`: перевіряє + замінює повну конфігурацію; виконує hot-reload, коли можливо, і restart, коли потрібно
    - Інструмент runtime `gateway`, доступний лише owner, усе ще відмовляється переписувати `tools.exec.ask` / `tools.exec.security`; застарілі псевдоніми `tools.bash.*` нормалізуються до тих самих захищених шляхів exec

  </Accordion>

  <Accordion title="Мінімальна притомна конфігурація для першого встановлення">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    Це встановлює ваш workspace і обмежує, хто може запускати бота.

  </Accordion>

  <Accordion title="Як налаштувати Tailscale на VPS і під’єднатися з Mac?">
    Мінімальні кроки:

    1. **Встановіть + увійдіть на VPS**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **Встановіть + увійдіть на своєму Mac**
       - Скористайтеся застосунком Tailscale і увійдіть у той самий tailnet.
    3. **Увімкніть MagicDNS (рекомендовано)**
       - В admin console Tailscale увімкніть MagicDNS, щоб VPS мав стабільну назву.
    4. **Використовуйте hostname tailnet**
       - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

    Якщо ви хочете Control UI без SSH, використовуйте Tailscale Serve на VPS:

    ```bash
    openclaw gateway --tailscale serve
    ```

    Це залишає gateway прив’язаним до loopback і відкриває HTTPS через Tailscale. Див. [Tailscale](/uk/gateway/tailscale).

  </Accordion>

  <Accordion title="Як під’єднати Mac node до віддаленого Gateway (Tailscale Serve)?">
    Serve відкриває **Control UI + WS Gateway**. Nodes під’єднуються через той самий endpoint Gateway WS.

    Рекомендоване налаштування:

    1. **Переконайтеся, що VPS і Mac знаходяться в одному tailnet**.
    2. **Використовуйте застосунок macOS у режимі Remote** (SSH-ціллю може бути hostname tailnet).
       Застосунок протунелює порт Gateway і під’єднається як node.
    3. **Схваліть node** на gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Документація: [Протокол Gateway](/uk/gateway/protocol), [Виявлення](/uk/gateway/discovery), [Віддалений режим macOS](/uk/platforms/mac/remote).

  </Accordion>

  <Accordion title="Чи варто встановлювати на другий ноутбук чи просто додати node?">
    Якщо вам потрібні лише **локальні інструменти** (screen/camera/exec) на другому ноутбуці, додайте його як
    **node**. Це залишає один Gateway і уникає дублювання конфігурації. Локальні node tools
    наразі підтримуються лише на macOS, але ми плануємо розширити це на інші ОС.

    Встановлюйте другий Gateway лише тоді, коли вам потрібна **жорстка ізоляція** або два повністю окремі боти.

    Документація: [Nodes](/uk/nodes), [CLI для Nodes](/cli/nodes), [Кілька gateway](/uk/gateway/multiple-gateways).

  </Accordion>
</AccordionGroup>

## Env vars і завантаження .env

<AccordionGroup>
  <Accordion title="Як OpenClaw завантажує environment variables?">
    OpenClaw читає env vars із батьківського процесу (оболонка, launchd/systemd, CI тощо) і додатково завантажує:

    - `.env` з поточного робочого каталогу
    - глобальний fallback `.env` із `~/.openclaw/.env` (тобто `$OPENCLAW_STATE_DIR/.env`)

    Жоден файл `.env` не перевизначає вже існуючі env vars.

    Ви також можете визначати inline env vars у конфігурації (застосовуються лише якщо їх бракує в process env):

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    Повний порядок пріоритету й джерела див. у [/environment](/uk/help/environment).

  </Accordion>

  <Accordion title="Я запустив Gateway через service, і мої env vars зникли. Що тепер?">
    Два поширені виправлення:

    1. Покладіть відсутні ключі в `~/.openclaw/.env`, щоб вони підхоплювалися, навіть коли service не успадковує env вашої оболонки.
    2. Увімкніть імпорт оболонки (opt-in зручність):

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

  <Accordion title='Я встановив COPILOT_GITHUB_TOKEN, але models status показує "Shell env: off." Чому?'>
    `openclaw models status` повідомляє, чи увімкнено **імпорт env з оболонки**. "Shell env: off"
    **не** означає, що ваших env vars немає — це лише означає, що OpenClaw не завантажуватиме
    вашу login shell автоматично.

    Якщо Gateway працює як service (launchd/systemd), він не успадковує env
    вашої оболонки. Виправлення — зробіть одне з цього:

    1. Покладіть token у `~/.openclaw/.env`:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. Або увімкніть імпорт оболонки (`env.shellEnv.enabled: true`).
    3. Або додайте його в блок `env` конфігурації (застосовується лише якщо бракує).

    Потім перезапустіть gateway і перевірте знову:

    ```bash
    openclaw models status
    ```

    Токени Copilot читаються з `COPILOT_GITHUB_TOKEN` (також `GH_TOKEN` / `GITHUB_TOKEN`).
    Див. [/concepts/model-providers](/uk/concepts/model-providers) і [/environment](/uk/help/environment).

  </Accordion>
</AccordionGroup>

## Сесії та кілька чатів

<AccordionGroup>
  <Accordion title="Як почати нову розмову?">
    Надішліть `/new` або `/reset` як окреме повідомлення. Див. [Керування session](/uk/concepts/session).
  </Accordion>

  <Accordion title="Чи сесії автоматично скидаються, якщо я ніколи не надсилаю /new?">
    Сесії можуть завершуватися після `session.idleMinutes`, але за замовчуванням це **вимкнено** (типове значення **0**).
    Установіть додатне значення, щоб увімкнути завершення через неактивність. Коли це ввімкнено, **наступне**
    повідомлення після періоду неактивності починає новий ID session для цього chat key.
    Це не видаляє transcript-и — лише починає нову session.

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="Чи є спосіб зробити команду з екземплярів OpenClaw (один CEO і багато агентів)?">
    Так, через **маршрутизацію мультиагентності** та **sub-agents**. Ви можете створити одного координатора
    та кількох worker-агентів із власними workspace і моделями.

    Утім, це краще сприймати як **цікавий експеримент**. Він важкий на токени й часто
    менш ефективний, ніж використання одного бота з окремими сесіями. Типова модель, яку ми
    уявляємо, — це один бот, з яким ви розмовляєте, і різні сесії для паралельної роботи. Такий
    бот також може за потреби породжувати sub-agents.

    Документація: [Маршрутизація мультиагентності](/uk/concepts/multi-agent), [Sub-agents](/uk/tools/subagents), [CLI для Agents](/cli/agents).

  </Accordion>

  <Accordion title="Чому контекст обрізався посеред задачі? Як цьому запобігти?">
    Контекст session обмежений вікном моделі. Довгі chat-и, великі виводи інструментів або багато
    файлів можуть спричинити compaction або truncation.

    Що допомагає:

    - Попросіть бота підсумувати поточний стан і записати його у файл.
    - Використовуйте `/compact` перед довгими задачами, а `/new` — при зміні теми.
    - Тримайте важливий контекст у workspace і просіть бота перечитувати його.
    - Використовуйте sub-agents для довгих або паралельних задач, щоб основний chat залишався меншим.
    - Виберіть модель із більшим вікном контексту, якщо це трапляється часто.

  </Accordion>

  <Accordion title="Як повністю скинути OpenClaw, але залишити його встановленим?">
    Використовуйте команду reset:

    ```bash
    openclaw reset
    ```

    Неінтерактивне повне скидання:

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    Потім знову запустіть налаштування:

    ```bash
    openclaw onboard --install-daemon
    ```

    Примітки:

    - Онбординг також пропонує **Reset**, якщо бачить наявну конфігурацію. Див. [Онбординг (CLI)](/uk/start/wizard).
    - Якщо ви використовували профілі (`--profile` / `OPENCLAW_PROFILE`), скидайте кожен state dir (типово це `~/.openclaw-<profile>`).
    - Скидання dev: `openclaw gateway --dev --reset` (лише для dev; стирає dev config + credentials + sessions + workspace).

  </Accordion>

  <Accordion title='Я отримую помилки "context too large" — як скинути або compact-ити?'>
    Використайте один із варіантів:

    - **Compact** (зберігає розмову, але підсумовує старіші ходи):

      ```
      /compact
      ```

      або `/compact <instructions>`, щоб скерувати підсумок.

    - **Reset** (новий ID session для того самого chat key):

      ```
      /new
      /reset
      ```

    Якщо це продовжується:

    - Увімкніть або налаштуйте **обрізання session** (`agents.defaults.contextPruning`), щоб скоротити старий вивід інструментів.
    - Використовуйте модель із більшим вікном контексту.

    Документація: [Compaction](/uk/concepts/compaction), [Обрізання session](/uk/concepts/session-pruning), [Керування session](/uk/concepts/session).

  </Accordion>

  <Accordion title='Чому я бачу "LLM request rejected: messages.content.tool_use.input field required"?'>
    Це помилка перевірки провайдера: модель видала блок `tool_use` без обов’язкового
    `input`. Зазвичай це означає, що історія session застаріла або пошкоджена (часто після довгих thread-ів
    або зміни tool/schema).

    Виправлення: почніть нову session через `/new` (окреме повідомлення).

  </Accordion>

  <Accordion title="Чому я отримую heartbeat-повідомлення кожні 30 хвилин?">
    Heartbeat-и запускаються кожні **30m** за замовчуванням (**1h** при використанні OAuth auth). Налаштуйте або вимкніть їх:

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

    Якщо `HEARTBEAT.md` існує, але фактично порожній (лише порожні рядки та markdown
    заголовки на кшталт `# Heading`), OpenClaw пропускає запуск heartbeat, щоб заощадити API calls.
    Якщо файл відсутній, heartbeat усе одно запускається, і модель сама вирішує, що робити.

    Override-и для агента використовують `agents.list[].heartbeat`. Документація: [Heartbeat](/uk/gateway/heartbeat).

  </Accordion>

  <Accordion title='Чи потрібно мені додавати "bot account" до групи WhatsApp?'>
    Ні. OpenClaw працює від **вашого власного облікового запису**, тож якщо ви є в групі, OpenClaw може її бачити.
    За замовчуванням відповіді в групах блокуються, доки ви не дозволите відправників (`groupPolicy: "allowlist"`).

    Якщо ви хочете, щоб запускати відповіді в групі могли лише **ви**:

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
    Варіант 1 (найшвидше): дивіться хвіст журналів і надішліть тестове повідомлення в групу:

    ```bash
    openclaw logs --follow --json
    ```

    Шукайте `chatId` (або `from`), що закінчується на `@g.us`, наприклад:
    `1234567890-1234567890@g.us`.

    Варіант 2 (якщо вже налаштовано/додано до allowlist): перелічіть групи з конфігурації:

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    Документація: [WhatsApp](/uk/channels/whatsapp), [Directory](/cli/directory), [Журнали](/cli/logs).

  </Accordion>

  <Accordion title="Чому OpenClaw не відповідає в групі?">
    Дві поширені причини:

    - Увімкнено gating за згадками (типово). Ви маєте @згадати бота (або збігтися з `mentionPatterns`).
    - Ви налаштували `channels.whatsapp.groups` без `"*"`, і групу не додано до allowlist.

    Див. [Групи](/uk/channels/groups) і [Групові повідомлення](/uk/channels/group-messages).

  </Accordion>

  <Accordion title="Чи групи/thread-и ділять контекст із DM?">
    Прямі chat-и за замовчуванням згортаються в основну session. Групи/канали мають власні session key, а теми Telegram / thread-и Discord — це окремі session. Див. [Групи](/uk/channels/groups) і [Групові повідомлення](/uk/channels/group-messages).
  </Accordion>

  <Accordion title="Скільки workspace і агентів я можу створити?">
    Жорстких лімітів немає. Десятки (навіть сотні) — нормально, але стежте за:

    - **Зростанням диска:** sessions + transcript-и живуть у `~/.openclaw/agents/<agentId>/sessions/`.
    - **Вартістю токенів:** більше агентів означає більше одночасного використання моделей.
    - **Операційними накладними витратами:** профілі auth для кожного агента, workspace і маршрутизація каналів.

    Поради:

    - Тримайте один **активний** workspace на агента (`agents.defaults.workspace`).
    - Обрізайте старі sessions (видаляйте JSONL або записи сховища), якщо диск росте.
    - Використовуйте `openclaw doctor`, щоб знаходити зайві workspace та невідповідності профілів.

  </Accordion>

  <Accordion title="Чи можу я запускати кілька ботів або чатів одночасно (Slack), і як це краще налаштувати?">
    Так. Використовуйте **Маршрутизацію мультиагентності**, щоб запускати кількох ізольованих агентів і маршрутизувати вхідні повідомлення за
    каналом/обліковим записом/peer. Slack підтримується як канал і може бути прив’язаний до конкретних агентів.

    Доступ до browser потужний, але це не «зробити все, що може людина» — anti-bot, CAPTCHA і MFA
    усе ще можуть блокувати автоматизацію. Для найнадійнішого керування browser використовуйте локальний Chrome MCP на host,
    або використовуйте CDP на машині, де browser реально працює.

    Рекомендоване налаштування:

    - Завжди ввімкнений gateway host (VPS/Mac mini).
    - Один агент на роль (bindings).
    - Slack channel(и), прив’язані до цих агентів.
    - Локальний browser через Chrome MCP або node, коли потрібно.

    Документація: [Маршрутизація мультиагентності](/uk/concepts/multi-agent), [Slack](/uk/channels/slack),
    [Browser](/uk/tools/browser), [Nodes](/uk/nodes).

  </Accordion>
</AccordionGroup>

## Моделі: типові значення, вибір, псевдоніми, перемикання

<AccordionGroup>
  <Accordion title='Що таке "default model"?'>
    default model у OpenClaw — це те, що