---
read_when:
    - Ви хочете зрозуміти, які інструменти надає OpenClaw
    - Вам потрібно налаштувати, дозволити або заборонити інструменти
    - 'Ви вирішуєте, що обрати: вбудовані інструменти, Skills чи plugins'
summary: 'Огляд інструментів і plugins OpenClaw: що може агент і як його розширювати'
title: Інструменти і Plugins
x-i18n:
    generated_at: "2026-04-06T00:53:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: c09e6ba0bba59be93eec676f119ab81b51f08536744f5d91f340734a4ce531c5
    source_path: tools/index.md
    workflow: 15
---

# Інструменти і Plugins

Усе, що агент робить окрім генерування тексту, відбувається через **інструменти**.
Інструменти — це спосіб, яким агент читає файли, виконує команди, переглядає вебсторінки, надсилає
повідомлення та взаємодіє з пристроями.

## Інструменти, Skills і plugins

OpenClaw має три шари, які працюють разом:

<Steps>
  <Step title="Інструменти — це те, що викликає агент">
    Інструмент — це типізована функція, яку агент може викликати (наприклад, `exec`, `browser`,
    `web_search`, `message`). OpenClaw постачається з набором **вбудованих інструментів**, а
    plugins можуть реєструвати додаткові.

    Агент бачить інструменти як структуровані визначення функцій, надіслані до API моделі.

  </Step>

  <Step title="Skills навчають агента, коли і як діяти">
    Skill — це markdown-файл (`SKILL.md`), який вбудовується в системний prompt.
    Skills надають агенту контекст, обмеження та покрокові вказівки для
    ефективного використання інструментів. Skills зберігаються у вашому workspace, у спільних теках
    або постачаються всередині plugins.

    [Довідник Skills](/uk/tools/skills) | [Створення Skills](/uk/tools/creating-skills)

  </Step>

  <Step title="Plugins пакують усе разом">
    Plugin — це пакет, який може реєструвати будь-яку комбінацію можливостей:
    канали, провайдери моделей, інструменти, Skills, мовлення, транскрипцію в реальному часі,
    голос у реальному часі, розуміння медіа, генерацію зображень, генерацію відео,
    отримання вебсторінок, вебпошук тощо. Деякі plugins є **core** (постачаються з
    OpenClaw), інші — **external** (опубліковані спільнотою в npm).

    [Встановлення і налаштування plugins](/uk/tools/plugin) | [Створіть власний](/uk/plugins/building-plugins)

  </Step>
</Steps>

## Вбудовані інструменти

Ці інструменти постачаються з OpenClaw і доступні без встановлення будь-яких plugins:

| Інструмент                                  | Що він робить                                                         | Сторінка                                    |
| ------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------- |
| `exec` / `process`                          | Виконує shell-команди, керує фоновими процесами                       | [Exec](/uk/tools/exec)                         |
| `code_execution`                            | Виконує ізольований віддалений аналіз Python                          | [Code Execution](/uk/tools/code-execution)     |
| `browser`                                   | Керує браузером Chromium (перехід, клік, знімок екрана)               | [Browser](/uk/tools/browser)                   |
| `web_search` / `x_search` / `web_fetch`     | Шукає у вебі, шукає дописи в X, отримує вміст сторінок                | [Web](/uk/tools/web)                           |
| `read` / `write` / `edit`                   | Ввід/вивід файлів у workspace                                         |                                             |
| `apply_patch`                               | Патчі файлів із кількома фрагментами                                  | [Apply Patch](/uk/tools/apply-patch)           |
| `message`                                   | Надсилає повідомлення в усі канали                                    | [Agent Send](/uk/tools/agent-send)             |
| `canvas`                                    | Керує node Canvas (present, eval, snapshot)                           |                                             |
| `nodes`                                     | Виявляє та вибирає спарені пристрої                                   |                                             |
| `cron` / `gateway`                          | Керує запланованими завданнями; перевіряє, патчить, перезапускає або оновлює gateway |                                             |
| `image` / `image_generate`                  | Аналізує або генерує зображення                                       | [Image Generation](/uk/tools/image-generation) |
| `music_generate`                            | Генерує музичні треки                                                 | [Music Generation](/uk/tools/music-generation) |
| `video_generate`                            | Генерує відео                                                         | [Video Generation](/uk/tools/video-generation) |
| `tts`                                       | Одноразове перетворення тексту на мовлення                            | [TTS](/uk/tools/tts)                           |
| `sessions_*` / `subagents` / `agents_list`  | Керування сесіями, статус і оркестрація субагентів                    | [Sub-agents](/uk/tools/subagents)              |
| `session_status`                            | Полегшене читання у стилі `/status` і перевизначення моделі для сесії | [Session Tools](/uk/concepts/session-tool)     |

Для роботи із зображеннями використовуйте `image` для аналізу, а `image_generate` — для генерації або редагування. Якщо ви націлюєтеся на `openai/*`, `google/*`, `fal/*` або іншого нестандартного провайдера зображень, спочатку налаштуйте автентифікацію/API-ключ цього провайдера.

Для роботи з музикою використовуйте `music_generate`. Якщо ви націлюєтеся на `google/*`, `minimax/*` або іншого нестандартного музичного провайдера, спочатку налаштуйте автентифікацію/API-ключ цього провайдера.

Для роботи з відео використовуйте `video_generate`. Якщо ви націлюєтеся на `qwen/*` або іншого нестандартного відеопровайдера, спочатку налаштуйте автентифікацію/API-ключ цього провайдера.

Для генерації аудіо на основі workflow використовуйте `music_generate`, коли plugin, наприклад
ComfyUI, реєструє його. Це окремо від `tts`, який відповідає за перетворення тексту на мовлення.

`session_status` — це полегшений інструмент статусу/читання в групі sessions.
Він відповідає на запитання у стилі `/status` про поточну сесію і може
за потреби встановлювати перевизначення моделі для окремої сесії; `model=default` очищає це
перевизначення. Як і `/status`, він може заповнювати відсутні лічильники токенів/кешу та
мітку активної runtime-моделі з найновішого запису використання в транскрипті.

`gateway` — це runtime-інструмент лише для власника, призначений для операцій gateway:

- `config.schema.lookup` для однієї підгілки конфігурації в межах шляху перед редагуванням
- `config.get` для поточного знімка конфігурації + хешу
- `config.patch` для часткових оновлень конфігурації з перезапуском
- `config.apply` лише для повної заміни конфігурації
- `update.run` для явного самооновлення + перезапуску

Для часткових змін віддавайте перевагу `config.schema.lookup`, а потім `config.patch`. Використовуйте
`config.apply` лише тоді, коли ви свідомо замінюєте всю конфігурацію.
Інструмент також відмовляється змінювати `tools.exec.ask` або `tools.exec.security`;
застарілі псевдоніми `tools.bash.*` нормалізуються до тих самих захищених шляхів exec.

### Інструменти, надані plugins

Plugins можуть реєструвати додаткові інструменти. Деякі приклади:

- [Lobster](/uk/tools/lobster) — типізоване workflow-runtime із відновлюваними схваленнями
- [LLM Task](/uk/tools/llm-task) — крок LLM лише з JSON для структурованого виводу
- [Music Generation](/uk/tools/music-generation) — поверхні інструмента `music_generate`, надані plugin
- [Diffs](/uk/tools/diffs) — переглядач і рендерер diff
- [OpenProse](/uk/prose) — оркестрація workflow у стилі markdown-first

## Налаштування інструментів

### Списки дозволів і заборон

Керуйте тим, які інструменти може викликати агент, через `tools.allow` / `tools.deny` у
конфігурації. Заборона завжди має пріоритет над дозволом.

```json5
{
  tools: {
    allow: ["group:fs", "browser", "web_search"],
    deny: ["exec"],
  },
}
```

### Профілі інструментів

`tools.profile` задає базовий список дозволів перед застосуванням `allow`/`deny`.
Перевизначення для окремого агента: `agents.list[].tools.profile`.

| Профіль    | Що він включає                                                                                                                                   |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `full`     | Без обмежень (так само, як якщо не задано)                                                                                                       |
| `coding`   | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `music_generate`, `video_generate` |
| `messaging`| `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                                                        |
| `minimal`  | Лише `session_status`                                                                                                                            |

### Групи інструментів

Використовуйте скорочення `group:*` у списках allow/deny:

| Група              | Інструменти                                                                                                |
| ------------------ | ---------------------------------------------------------------------------------------------------------- |
| `group:runtime`    | exec, process, code_execution (`bash` приймається як псевдонім для `exec`)                                 |
| `group:fs`         | read, write, edit, apply_patch                                                                             |
| `group:sessions`   | sessions_list, sessions_history, sessions_send, sessions_spawn, sessions_yield, subagents, session_status  |
| `group:memory`     | memory_search, memory_get                                                                                  |
| `group:web`        | web_search, x_search, web_fetch                                                                            |
| `group:ui`         | browser, canvas                                                                                            |
| `group:automation` | cron, gateway                                                                                              |
| `group:messaging`  | message                                                                                                    |
| `group:nodes`      | nodes                                                                                                      |
| `group:agents`     | agents_list                                                                                                |
| `group:media`      | image, image_generate, music_generate, video_generate, tts                                                 |
| `group:openclaw`   | Усі вбудовані інструменти OpenClaw (без інструментів plugin)                                               |

`sessions_history` повертає обмежене, відфільтроване з погляду безпеки представлення для пригадування. Воно видаляє
теги thinking, каркас `<relevant-memories>`, XML-корисні навантаження викликів інструментів у звичайному тексті
(включно з `<tool_call>...</tool_call>`,
`<function_call>...</function_call>`, `<tool_calls>...</tool_calls>`,
`<function_calls>...</function_calls>` і усіченими блоками викликів інструментів),
понижений каркас викликів інструментів, витеклі ASCII/повноширинні токени керування моделлю
та некоректний XML викликів інструментів MiniMax із тексту помічника, а потім застосовує
редагування/усічення та, за потреби, заповнювачі для надто великих рядків, замість того щоб діяти
як сирий дамп транскрипту.

### Обмеження для конкретних провайдерів

Використовуйте `tools.byProvider`, щоб обмежувати інструменти для конкретних провайдерів без
зміни глобальних значень за замовчуванням:

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
    },
  },
}
```
