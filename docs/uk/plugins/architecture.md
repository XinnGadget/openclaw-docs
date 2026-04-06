---
read_when:
    - Створення або налагодження нативних плагінів OpenClaw
    - Розуміння моделі можливостей плагінів або меж володіння
    - Робота над конвеєром завантаження плагінів або реєстром
    - Реалізація хуків runtime для провайдерів або плагінів каналів
sidebarTitle: Internals
summary: 'Внутрішня будова плагінів: модель можливостей, межі володіння, контракти, конвеєр завантаження та допоміжні засоби runtime'
title: Внутрішня будова плагінів
x-i18n:
    generated_at: "2026-04-06T12:35:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 44f8354fffab48f31dacc6b1c0e57ef35710d3312d8f79c0d56ae7e2a4530e8f
    source_path: plugins/architecture.md
    workflow: 15
---

# Внутрішня будова плагінів

<Info>
  Це **довідник із поглибленої архітектури**. Практичні посібники див. тут:
  - [Встановлення та використання плагінів](/uk/tools/plugin) — посібник для користувача
  - [Початок роботи](/uk/plugins/building-plugins) — перший посібник зі створення плагіна
  - [Плагіни каналів](/uk/plugins/sdk-channel-plugins) — створення каналу обміну повідомленнями
  - [Плагіни провайдерів](/uk/plugins/sdk-provider-plugins) — створення провайдера моделей
  - [Огляд SDK](/uk/plugins/sdk-overview) — карта імпортів і API реєстрації
</Info>

На цій сторінці описано внутрішню архітектуру системи плагінів OpenClaw.

## Публічна модель можливостей

Можливості — це публічна модель **нативних плагінів** усередині OpenClaw. Кожен
нативний плагін OpenClaw реєструється для одного або кількох типів можливостей:

| Можливість            | Метод реєстрації                                | Приклади плагінів                    |
| --------------------- | ----------------------------------------------- | ------------------------------------ |
| Текстовий висновок    | `api.registerProvider(...)`                     | `openai`, `anthropic`                |
| Мовлення              | `api.registerSpeechProvider(...)`               | `elevenlabs`, `microsoft`            |
| Транскрипція в реальному часі | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                             |
| Голос у реальному часі | `api.registerRealtimeVoiceProvider(...)`       | `openai`                             |
| Розуміння медіа       | `api.registerMediaUnderstandingProvider(...)`   | `openai`, `google`                   |
| Генерація зображень   | `api.registerImageGenerationProvider(...)`      | `openai`, `google`, `fal`, `minimax` |
| Генерація музики      | `api.registerMusicGenerationProvider(...)`      | `google`, `minimax`                  |
| Генерація відео       | `api.registerVideoGenerationProvider(...)`      | `qwen`                               |
| Веб-отримання         | `api.registerWebFetchProvider(...)`             | `firecrawl`                          |
| Веб-пошук             | `api.registerWebSearchProvider(...)`            | `google`                             |
| Канал / обмін повідомленнями | `api.registerChannel(...)`               | `msteams`, `matrix`                  |

Плагін, який реєструє нуль можливостей, але надає hooks, tools або
services, є **застарілим hook-only** плагіном. Такий шаблон усе ще повністю підтримується.

### Позиція щодо зовнішньої сумісності

Модель можливостей уже реалізована в core і використовується в bundled/native plugins
сьогодні, але сумісність зовнішніх плагінів усе ще потребує вищої планки, ніж
«це експортується, отже це заморожено».

Поточні рекомендації:

- **наявні зовнішні плагіни:** зберігайте працездатність інтеграцій на основі hooks; розглядайте
  це як базовий рівень сумісності
- **нові bundled/native plugins:** надавайте перевагу явній реєстрації можливостей замість
  vendor-specific доступу напряму або нових hook-only дизайнів
- **зовнішні плагіни, що переходять на реєстрацію можливостей:** дозволено, але розглядайте
  допоміжні поверхні, специфічні для можливостей, як такі, що розвиваються, якщо в документації контракт не позначено як стабільний

Практичне правило:

- API реєстрації можливостей — це цільовий напрямок
- legacy hooks лишаються найбезпечнішим шляхом без поломок для зовнішніх плагінів під час
  переходу
- не всі експортовані helper subpaths однакові; надавайте перевагу вузькому документованому
  контракту, а не випадковим допоміжним експортам

### Форми плагінів

OpenClaw класифікує кожен завантажений плагін за формою на основі його фактичної
поведінки під час реєстрації (а не лише статичних метаданих):

- **plain-capability** -- реєструє рівно один тип можливості (наприклад,
  плагін лише провайдера, як-от `mistral`)
- **hybrid-capability** -- реєструє кілька типів можливостей (наприклад,
  `openai` володіє текстовим висновком, мовленням, розумінням медіа та
  генерацією зображень)
- **hook-only** -- реєструє лише hooks (типізовані або custom), без можливостей,
  tools, commands або services
- **non-capability** -- реєструє tools, commands, services або routes, але не можливості

Використайте `openclaw plugins inspect <id>`, щоб побачити форму плагіна та
розподіл його можливостей. Докладніше див. у [довідці CLI](/cli/plugins#inspect).

### Legacy hooks

Хук `before_agent_start` лишається підтримуваним як шлях сумісності для
hook-only плагінів. Реальні legacy-плагіни все ще від нього залежать.

Напрямок:

- зберігати його працездатність
- документувати його як застарілий
- для перевизначення моделі/провайдера надавати перевагу `before_model_resolve`
- для мутації prompt надавати перевагу `before_prompt_build`
- видаляти лише після зниження реального використання і після того, як покриття fixture підтвердить безпечність міграції

### Сигнали сумісності

Коли ви запускаєте `openclaw doctor` або `openclaw plugins inspect <id>`, ви можете побачити
одну з таких позначок:

| Сигнал                     | Значення                                                     |
| -------------------------- | ------------------------------------------------------------ |
| **config valid**           | Конфігурація коректно парситься, а плагіни успішно резолвляться |
| **compatibility advisory** | Плагін використовує підтримуваний, але старіший шаблон (наприклад, `hook-only`) |
| **legacy warning**         | Плагін використовує `before_agent_start`, який є застарілим  |
| **hard error**             | Конфігурація некоректна або плагін не вдалося завантажити    |

Ні `hook-only`, ні `before_agent_start` не зламають ваш плагін сьогодні --
`hook-only` є рекомендаційним сигналом, а `before_agent_start` лише спричиняє попередження. Ці
сигнали також з’являються в `openclaw status --all` і `openclaw plugins doctor`.

## Огляд архітектури

Система плагінів OpenClaw має чотири шари:

1. **Маніфест + виявлення**
   OpenClaw знаходить кандидатів у плагіни за налаштованими шляхами, коренями workspace,
   глобальними коренями розширень і bundled extensions. Під час виявлення спочатку читаються нативні
   маніфести `openclaw.plugin.json` та підтримувані bundle manifests.
2. **Увімкнення + валідація**
   Core вирішує, чи виявлений плагін увімкнений, вимкнений, заблокований або
   вибраний для ексклюзивного слота, наприклад memory.
3. **Завантаження runtime**
   Нативні плагіни OpenClaw завантажуються в поточний процес через jiti і реєструють
   можливості в центральному реєстрі. Сумісні bundles нормалізуються в
   записи реєстру без імпорту коду runtime.
4. **Споживання поверхонь**
   Решта OpenClaw читає реєстр, щоб надавати tools, channels, налаштування provider,
   hooks, HTTP routes, CLI commands і services.

Зокрема для CLI плагінів виявлення кореневих команд поділено на дві фази:

- метадані часу парсингу надходять із `registerCli(..., { descriptors: [...] })`
- реальний модуль CLI плагіна може лишатися lazy і реєструватися під час першого виклику

Це дозволяє зберігати код CLI, що належить плагіну, всередині плагіна, водночас даючи OpenClaw
змогу резервувати імена кореневих команд до парсингу.

Важлива межа дизайну:

- виявлення + валідація конфігурації мають працювати на основі **метаданих маніфесту/схеми**
  без виконання коду плагіна
- нативна поведінка runtime походить із шляху модуля плагіна `register(api)`

Цей поділ дає OpenClaw змогу валідувати конфігурацію, пояснювати відсутні/вимкнені плагіни та
будувати підказки UI/схем до повної активації runtime.

### Плагіни каналів і спільний tool повідомлень

Плагінам каналів не потрібно реєструвати окремий tool для send/edit/react для
звичайних дій чату. OpenClaw зберігає один спільний `message` tool у core, а
плагіни каналів володіють специфічним для каналу виявленням і виконанням за ним.

Поточна межа така:

- core володіє спільним хостом `message` tool, підключенням prompt, обліком сесій/гілок
  і диспетчеризацією виконання
- плагіни каналів володіють scoped виявленням дій, виявленням можливостей і будь-якими
  фрагментами схем, специфічними для каналу
- плагіни каналів володіють граматикою розмови сесії, специфічною для провайдера, зокрема
  тим, як id розмов кодують id гілок або успадковуються від батьківських розмов
- плагіни каналів виконують фінальну дію через свій action adapter

Для плагінів каналів поверхня SDK —
`ChannelMessageActionAdapter.describeMessageTool(...)`. Цей уніфікований виклик виявлення
дозволяє плагіну повертати видимі дії, можливості й внески до схеми
разом, щоб ці частини не розходилися.

Core передає scope runtime у цей крок виявлення. Важливі поля:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- довірений вхідний `requesterSenderId`

Це важливо для context-sensitive плагінів. Канал може приховувати або показувати
message actions залежно від активного облікового запису, поточної кімнати/гілки/повідомлення або
довіреної особи запитувача без жорстко закладених гілок, специфічних для каналу, у
core `message` tool.

Саме тому зміни маршрутизації embedded-runner усе ще є роботою плагіна: runner
відповідає за пересилання поточної ідентичності чату/сесії в межу
виявлення плагіна, щоб спільний `message` tool показував правильну поверхню,
якою володіє канал, для поточного ходу.

Для допоміжних засобів виконання, що належать каналу, bundled plugins мають тримати runtime
виконання у своїх власних модулях розширень. Core більше не володіє runtime
message-action для Discord, Slack, Telegram або WhatsApp у `src/agents/tools`.
Ми не публікуємо окремі subpaths `plugin-sdk/*-action-runtime`, і bundled
plugins мають імпортувати власний локальний код runtime напряму зі своїх
модулів розширень.

Та сама межа застосовується до іменованих поверхонь SDK провайдерів загалом:
core не повинен імпортувати зручні barrel-файли, специфічні для каналів Slack, Discord, Signal,
WhatsApp чи подібних розширень. Якщо core потрібна певна поведінка, або використайте
власний barrel bundled plugin `api.ts` / `runtime-api.ts`, або підніміть цю потребу
до вузької загальної можливості у спільному SDK.

Зокрема для опитувань є два шляхи виконання:

- `outbound.sendPoll` — спільна базова лінія для каналів, що відповідають спільній
  моделі опитувань
- `actions.handleAction("poll")` — бажаний шлях для семантики опитувань, специфічної для каналу,
  або додаткових параметрів опитування

Core тепер відкладає спільний розбір опитувань до того, як диспетчеризація опитування плагіна відхилить
дію, тому обробники опитувань, що належать плагіну, можуть приймати поля опитувань, специфічні для каналу,
і generic parser опитувань не блокуватиме їх раніше.

Повну послідовність запуску див. у розділі [Конвеєр завантаження](#load-pipeline).

## Модель володіння можливостями

OpenClaw розглядає нативний плагін як межу володіння для **компанії** або
**функції**, а не як набір розрізнених інтеграцій.

Це означає:

- плагін компанії зазвичай має володіти всіма поверхнями OpenClaw, що належать цій компанії
- плагін функції зазвичай має володіти всією поверхнею функції, яку він додає
- канали мають споживати спільні можливості core, а не довільно перевпроваджувати
  поведінку провайдерів

Приклади:

- bundled plugin `openai` володіє поведінкою провайдера моделей OpenAI і поведінкою OpenAI
  для speech + realtime-voice + media-understanding + image-generation
- bundled plugin `elevenlabs` володіє поведінкою мовлення ElevenLabs
- bundled plugin `microsoft` володіє поведінкою мовлення Microsoft
- bundled plugin `google` володіє поведінкою провайдера моделей Google плюс поведінкою Google
  для media-understanding + image-generation + web-search
- bundled plugin `firecrawl` володіє поведінкою web-fetch Firecrawl
- bundled plugins `minimax`, `mistral`, `moonshot` і `zai` володіють своїми
  backend-ами media-understanding
- bundled plugin `qwen` володіє поведінкою текстового провайдера Qwen плюс
  media-understanding і video-generation
- плагін `voice-call` — це плагін функції: він володіє транспортом дзвінків, tools,
  CLI, routes і мостом Twilio media-stream, але споживає спільні можливості speech
  плюс realtime-transcription і realtime-voice замість прямого імпорту vendor plugins

Бажаний кінцевий стан:

- OpenAI живе в одному плагіні, навіть якщо охоплює текстові моделі, мовлення, зображення та
  майбутнє відео
- інший вендор може зробити те саме для своєї власної поверхні
- каналам не важливо, який плагін вендора володіє провайдером; вони споживають
  спільний контракт можливості, який надає core

Ось ключова відмінність:

- **plugin** = межа володіння
- **capability** = контракт core, який кілька плагінів можуть реалізовувати або споживати

Тож якщо OpenClaw додає нову предметну область, як-от відео, перше питання не
«який провайдер має жорстко закодувати обробку відео?» Перше питання — «яким є
контракт основної можливості відео?» Щойно цей контракт існує, vendor plugins
можуть реєструватися для нього, а channel/feature plugins можуть його споживати.

Якщо можливість ще не існує, правильний крок зазвичай такий:

1. визначити відсутню можливість у core
2. відкрити її через API/runtime плагіна у типізований спосіб
3. підключити канали/функції до цієї можливості
4. дозволити vendor plugins реєструвати реалізації

Так володіння лишається явним і водночас уникається поведінка core, яка залежить від
одного вендора або одноразового шляху коду, специфічного для плагіна.

### Шарування можливостей

Користуйтеся цією ментальною моделлю, коли вирішуєте, де має бути код:

- **шар можливостей core**: спільна оркестрація, політика, fallback, правила
  злиття конфігурації, семантика доставки та типізовані контракти
- **шар vendor plugin**: API, auth, каталоги моделей, синтез мовлення,
  генерація зображень, майбутні backend-и відео, ендпоїнти використання
- **шар channel/feature plugin**: інтеграція Slack/Discord/voice-call тощо,
  яка споживає можливості core і показує їх на своїй поверхні

Наприклад, TTS має таку форму:

- core володіє політикою TTS під час відповіді, порядком fallback, prefs і доставкою в канал
- `openai`, `elevenlabs` і `microsoft` володіють реалізаціями синтезу
- `voice-call` споживає helper runtime TTS для телефонії

Такому ж шаблону слід надавати перевагу і для майбутніх можливостей.

### Приклад плагіна компанії з кількома можливостями

Плагін компанії має виглядати цілісно ззовні. Якщо OpenClaw має спільні
контракти для моделей, мовлення, транскрипції в реальному часі, голосу в реальному часі, розуміння медіа,
генерації зображень, генерації відео, web fetch і web search,
вендор може володіти всіма своїми поверхнями в одному місці:

```ts
import type { OpenClawPluginDefinition } from "openclaw/plugin-sdk/plugin-entry";
import {
  describeImageWithModel,
  transcribeOpenAiCompatibleAudio,
} from "openclaw/plugin-sdk/media-understanding";

const plugin: OpenClawPluginDefinition = {
  id: "exampleai",
  name: "ExampleAI",
  register(api) {
    api.registerProvider({
      id: "exampleai",
      // auth/model catalog/runtime hooks
    });

    api.registerSpeechProvider({
      id: "exampleai",
      // vendor speech config — implement the SpeechProviderPlugin interface directly
    });

    api.registerMediaUnderstandingProvider({
      id: "exampleai",
      capabilities: ["image", "audio", "video"],
      async describeImage(req) {
        return describeImageWithModel({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
      async transcribeAudio(req) {
        return transcribeOpenAiCompatibleAudio({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
    });

    api.registerWebSearchProvider(
      createPluginBackedWebSearchProvider({
        id: "exampleai-search",
        // credential + fetch logic
      }),
    );
  },
};

export default plugin;
```

Важливі не точні назви helpers. Важлива форма:

- один плагін володіє поверхнею вендора
- core усе ще володіє контрактами можливостей
- канали та плагіни функцій споживають helpers `api.runtime.*`, а не код вендора
- contract tests можуть перевіряти, що плагін зареєстрував можливості, якими
  він заявляє, що володіє

### Приклад можливості: розуміння відео

OpenClaw уже розглядає розуміння зображень/аудіо/відео як одну спільну
можливість. Та сама модель володіння застосовується і тут:

1. core визначає контракт media-understanding
2. vendor plugins реєструють `describeImage`, `transcribeAudio` і
   `describeVideo`, де це доречно
3. канали та плагіни функцій споживають спільну поведінку core замість
   прямого підключення до коду вендора

Це не дозволяє закласти припущення одного провайдера щодо відео в core. Плагін володіє
поверхнею вендора; core володіє контрактом можливості та поведінкою fallback.

Генерація відео вже використовує таку саму послідовність: core володіє типізованим
контрактом можливості та helper runtime, а vendor plugins реєструють
реалізації `api.registerVideoGenerationProvider(...)` для нього.

Потрібен конкретний чекліст розгортання? Див.
[Capability Cookbook](/uk/plugins/architecture).

## Контракти та примусове дотримання

Поверхня API плагінів навмисно типізована і централізована в
`OpenClawPluginApi`. Цей контракт визначає підтримувані точки реєстрації та
helpers runtime, на які може покладатися плагін.

Чому це важливо:

- автори плагінів отримують один стабільний внутрішній стандарт
- core може відхилити дубльоване володіння, наприклад коли два плагіни реєструють один і той самий
  id провайдера
- під час запуску можна показати діагностику для некоректної реєстрації, придатну до дії
- contract tests можуть примусово контролювати володіння bundled-plugin і запобігати тихому дрейфу

Є два шари примусового контролю:

1. **контроль під час реєстрації в runtime**
   Реєстр плагінів валідує реєстрації під час завантаження плагінів. Приклади:
   дублікати id провайдерів, дублікати id speech-провайдерів і некоректні
   реєстрації породжують діагностику плагіна замість невизначеної поведінки.
2. **contract tests**
   Bundled plugins фіксуються в contract registries під час тестових запусків, щоб
   OpenClaw міг явно перевіряти володіння. Сьогодні це використовується для model
   providers, speech providers, web search providers і володіння реєстрацією bundled.

Практичний ефект полягає в тому, що OpenClaw наперед знає, який плагін володіє якою
поверхнею. Це дозволяє core і каналам безшовно поєднуватися, оскільки володіння
заявлене, типізоване й тестоване, а не неявне.

### Що має входити в контракт

Хороші контракти плагінів:

- типізовані
- невеликі
- специфічні до можливості
- належать core
- багаторазово використовуються кількома плагінами
- можуть споживатися каналами/функціями без знання про вендора

Погані контракти плагінів:

- політика, специфічна для вендора, прихована в core
- одноразові обхідні шляхи для плагінів, що обходять реєстр
- код каналу, що напряму звертається до реалізації вендора
- довільні runtime-об’єкти, які не входять до `OpenClawPluginApi` або
  `api.runtime`

Якщо сумніваєтеся, підніміть рівень абстракції: спочатку визначте можливість, а потім
дозвольте плагінам у неї підключатися.

## Модель виконання

Нативні плагіни OpenClaw працюють **у поточному процесі** разом із Gateway. Вони не
ізольовані. Завантажений нативний плагін має ту саму межу довіри на рівні процесу, що й
код core.

Наслідки:

- нативний плагін може реєструвати tools, network handlers, hooks і services
- помилка нативного плагіна може призвести до збою gateway або його дестабілізації
- зловмисний нативний плагін еквівалентний довільному виконанню коду всередині
  процесу OpenClaw

Сумісні bundles безпечніші за замовчуванням, тому що OpenClaw наразі розглядає їх
як пакети метаданих/контенту. У поточних випусках це переважно означає bundled
skills.

Використовуйте allowlists і явні шляхи встановлення/завантаження для небандлених плагінів. Розглядайте
workspace plugins як код часу розробки, а не як виробничі значення за замовчуванням.

Для назв пакетів bundled workspace тримайте id плагіна прив’язаним до npm-імені:
`@openclaw/<id>` за замовчуванням або затверджений типізований суфікс, як-от
`-provider`, `-plugin`, `-speech`, `-sandbox` або `-media-understanding`, коли
пакет навмисно надає вужчу роль плагіна.

Важлива примітка щодо довіри:

- `plugins.allow` довіряє **id плагінів**, а не походженню джерела.
- Workspace plugin з тим самим id, що й bundled plugin, навмисно затіняє
  bundled-копію, коли такий workspace plugin увімкнено/внесено до allowlist.
- Це нормально й корисно для локальної розробки, тестування патчів і hotfixes.

## Межа експорту

OpenClaw експортує можливості, а не зручні для реалізації допоміжні засоби.

Зберігайте публічною реєстрацію можливостей. Скорочуйте helper-експорти, що не є контрактом:

- helper subpaths, специфічні для bundled-plugin
- runtime plumbing subpaths, не призначені як публічний API
- зручні helpers, специфічні для вендора
- helpers налаштування/onboarding, які є деталями реалізації

Деякі helper subpaths bundled-plugin усе ще присутні у згенерованій карті експорту SDK
заради сумісності та підтримки bundled-plugin. Поточні приклади:
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` і кілька швів `plugin-sdk/matrix*`. Розглядайте їх як
зарезервовані детальні експорти реалізації, а не як рекомендований шаблон SDK для
нових сторонніх плагінів.

## Конвеєр завантаження

Під час запуску OpenClaw приблизно робить таке:

1. виявляє корені плагінів-кандидатів
2. читає native або compatible bundle manifests і метадані пакетів
3. відхиляє небезпечних кандидатів
4. нормалізує конфігурацію плагінів (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. вирішує, чи вмикати кожного кандидата
6. завантажує увімкнені native modules через jiti
7. викликає native hooks `register(api)` (або `activate(api)` — legacy alias) і збирає реєстрації до реєстру плагінів
8. відкриває реєстр для surfaces команд/runtime

<Note>
`activate` — це legacy alias для `register` — loader резолвить те, що присутнє (`def.register ?? def.activate`), і викликає його в тій самій точці. Усі bundled plugins використовують `register`; для нових плагінів надавайте перевагу `register`.
</Note>

Перевірки безпеки відбуваються **до** виконання runtime. Кандидати блокуються,
якщо entry виходить за межі кореня плагіна, шлях доступний на запис усім, або
володіння шляхом виглядає підозріло для небандлених плагінів.

### Поведінка «спочатку маніфест»

Маніфест — це джерело істини control-plane. OpenClaw використовує його, щоб:

- ідентифікувати плагін
- виявляти оголошені channels/skills/config schema або можливості bundle
- валідувати `plugins.entries.<id>.config`
- доповнювати labels/placeholders у Control UI
- показувати метадані встановлення/каталогу

Для нативних плагінів модуль runtime — це частина data-plane. Він реєструє
фактичну поведінку, як-от hooks, tools, commands або потоки provider.

### Що кешує loader

OpenClaw зберігає короткочасні кеші в поточному процесі для:

- результатів виявлення
- даних реєстру маніфестів
- реєстрів завантажених плагінів

Ці кеші зменшують навантаження від ривкового запуску та повторних команд. Їх безпечно
сприймати як короткоживучі кеші продуктивності, а не як збереження стану.

Примітка щодо продуктивності:

- Встановіть `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` або
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1`, щоб вимкнути ці кеші.
- Налаштовуйте вікна кешу через `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` і
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS`.

## Модель реєстру

Завантажені плагіни не змінюють напряму довільні глобальні об’єкти core. Вони
реєструються в центральному реєстрі плагінів.

Реєстр відстежує:

- записи плагінів (ідентичність, джерело, походження, статус, діагностика)
- tools
- legacy hooks і типізовані hooks
- channels
- providers
- обробники Gateway RPC
- HTTP routes
- реєстратори CLI
- фонові services
- commands, що належать плагінам

Потім функції core читають із цього реєстру замість прямого звернення до модулів плагінів.
Це зберігає односторонність завантаження:

- модуль плагіна -> реєстрація в реєстрі
- runtime core -> споживання реєстру

Це розділення важливе для підтримуваності. Воно означає, що більшості поверхонь core
потрібна лише одна точка інтеграції: «прочитати реєстр», а не «додати спецобробку для кожного модуля плагіна».

## Колбеки прив’язки розмови

Плагіни, що прив’язують розмову, можуть реагувати, коли схвалення вирішено.

Використовуйте `api.onConversationBindingResolved(...)`, щоб отримати callback після того, як
запит на прив’язку схвалено або відхилено:

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // A binding now exists for this plugin + conversation.
        console.log(event.binding?.conversationId);
        return;
      }

      // The request was denied; clear any local pending state.
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

Поля payload callback:

- `status`: `"approved"` або `"denied"`
- `decision`: `"allow-once"`, `"allow-always"` або `"deny"`
- `binding`: резолвлена прив’язка для схвалених запитів
- `request`: підсумок початкового запиту, підказка від’єднання, id відправника та
  метадані розмови

Цей callback призначений лише для сповіщення. Він не змінює того, кому дозволено прив’язувати
розмову, і виконується після завершення обробки схвалення в core.

## Хуки runtime провайдера

Плагіни провайдерів тепер мають два шари:

- метадані маніфесту: `providerAuthEnvVars` для дешевого пошуку env-auth до
  завантаження runtime, плюс `providerAuthChoices` для дешевих labels onboarding/auth-choice
  і метаданих прапорців CLI до завантаження runtime
- hooks часу конфігурації: `catalog` / legacy `discovery` плюс `applyConfigDefaults`
- hooks runtime: `normalizeModelId`, `normalizeTransport`,
  `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `resolveExternalOAuthProfiles`,
  `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`, `normalizeResolvedModel`,
  `contributeResolvedModelCompat`, `capabilities`,
  `normalizeToolSchemas`, `inspectToolSchemas`,
  `resolveReasoningOutputMode`, `prepareExtraParams`, `createStreamFn`,
  `wrapStreamFn`, `resolveTransportTurnState`,
  `resolveWebSocketSessionPolicy`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`, `matchesContextOverflowError`,
  `classifyFailoverReason`, `isCacheTtlEligible`,
  `buildMissingAuthMessage`, `suppressBuiltInModel`, `augmentModelCatalog`,
  `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `isModernModelRef`, `prepareRuntimeAuth`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `createEmbeddingProvider`,
  `buildReplayPolicy`,
  `sanitizeReplayHistory`, `validateReplayTurns`, `onModelSelected`

OpenClaw як і раніше володіє загальним циклом агента, failover, обробкою transcript і
політикою tools. Ці hooks — поверхня розширення для поведінки, специфічної для провайдера, без
потреби в цілком custom inference transport.

Використовуйте маніфест `providerAuthEnvVars`, коли провайдер має облікові дані на основі env,
які generic auth/status/model-picker шляхи мають бачити без завантаження runtime плагіна.
Використовуйте маніфест `providerAuthChoices`, коли поверхні onboarding/auth-choice CLI
мають знати id вибору провайдера, labels груп і просте підключення auth
через один прапорець без завантаження runtime провайдера. Зберігайте runtime провайдера
`envVars` для підказок оператору, наприклад labels onboarding або vars для
налаштування OAuth client-id/client-secret.

### Порядок і використання hooks

Для плагінів моделей/провайдерів OpenClaw викликає hooks приблизно в такому порядку.
Стовпець «Коли використовувати» — це короткий довідник для прийняття рішень.

| #   | Hook                              | Що він робить                                                                                   | Коли використовувати                                                                                                                        |
| --- | --------------------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | Публікує конфігурацію провайдера в `models.providers` під час генерації `models.json`          | Провайдер володіє каталогом або значеннями base URL за замовчуванням                                                                        |
| 2   | `applyConfigDefaults`             | Застосовує глобальні значення конфігурації за замовчуванням, що належать провайдеру, під час матеріалізації конфігурації | Значення за замовчуванням залежать від режиму auth, env або семантики сімейства моделей провайдера                                        |
| --  | _(built-in model lookup)_         | OpenClaw спочатку пробує звичайний шлях реєстру/каталогу                                       | _(це не hook плагіна)_                                                                                                                      |
| 3   | `normalizeModelId`                | Нормалізує legacy або preview псевдоніми model-id до пошуку                                    | Провайдер володіє очищенням псевдонімів до канонічного резолву моделі                                                                       |
| 4   | `normalizeTransport`              | Нормалізує `api` / `baseUrl` сімейства провайдера перед загальним складанням моделі            | Провайдер володіє очищенням transport для custom provider ids у тому самому сімействі transport                                            |
| 5   | `normalizeConfig`                 | Нормалізує `models.providers.<id>` до runtime/provider resolution                              | Провайдеру потрібне очищення конфігурації, яке має жити разом із плагіном; bundled Google-family helpers також страхують підтримувані записи конфігурації Google |
| 6   | `applyNativeStreamingUsageCompat` | Застосовує compat-переписування native streaming-usage до провайдерів конфігурації             | Провайдеру потрібні виправлення метаданих native streaming usage, що залежать від ендпоїнта                                                |
| 7   | `resolveConfigApiKey`             | Резолвить auth env-marker для провайдерів конфігурації до завантаження runtime auth            | Провайдер має власний резолвер API-key через env-marker; `amazon-bedrock` також має тут вбудований резолвер AWS env-marker                |
| 8   | `resolveSyntheticAuth`            | Показує локальну/self-hosted або auth на основі config без збереження відкритого тексту        | Провайдер може працювати із synthetic/local credential marker                                                                               |
| 9   | `resolveExternalOAuthProfiles`    | Накладає external OAuth profiles; типове `persistence` — `runtime-only` для облікових даних, що належать CLI/app | Провайдер повторно використовує external OAuth credentials без збереження скопійованих refresh tokens                                      |
| 10  | `shouldDeferSyntheticProfileAuth` | Понижує пріоритет збережених synthetic placeholder profiles порівняно з auth на основі env/config | Провайдер зберігає synthetic placeholder profiles, які не мають вигравати за пріоритетом                                                   |
| 11  | `resolveDynamicModel`             | Синхронний fallback для model ids, що належать провайдеру, але ще відсутні в локальному реєстрі | Провайдер приймає довільні model ids вищого рівня                                                                                           |
| 12  | `prepareDynamicModel`             | Асинхронний прогрів, після чого `resolveDynamicModel` запускається знову                        | Провайдеру потрібні мережеві метадані до резолву невідомих ids                                                                              |
| 13  | `normalizeResolvedModel`          | Фінальне переписування перед тим, як embedded runner використає резолвлену модель               | Провайдеру потрібні переписування transport, але він усе ще використовує transport core                                                     |
| 14  | `contributeResolvedModelCompat`   | Додає compat flags для моделей вендора за іншим сумісним transport                             | Провайдер розпізнає власні моделі на proxy transports без перехоплення самого провайдера                                                   |
| 15  | `capabilities`                    | Метадані transcript/tooling, що належать провайдеру й використовуються спільною логікою core   | Провайдеру потрібні особливості transcript/provider-family                                                                                  |
| 16  | `normalizeToolSchemas`            | Нормалізує схеми tools до того, як embedded runner їх побачить                                  | Провайдеру потрібне очищення схем для сімейства transport                                                                                   |
| 17  | `inspectToolSchemas`              | Показує діагностику схем, що належить провайдеру, після нормалізації                            | Провайдер хоче попередження про keywords без навчання core правилам, специфічним для провайдера                                            |
| 18  | `resolveReasoningOutputMode`      | Вибирає native або tagged контракт reasoning-output                                             | Провайдеру потрібен tagged reasoning/final output замість native полів                                                                      |
| 19  | `prepareExtraParams`              | Нормалізація параметрів запиту перед загальними обгортками параметрів потоку                    | Провайдеру потрібні параметри запиту за замовчуванням або очищення параметрів для конкретного провайдера                                   |
| 20  | `createStreamFn`                  | Повністю замінює звичайний шлях потоку custom transport                                         | Провайдеру потрібен custom wire protocol, а не просто обгортка                                                                              |
| 21  | `wrapStreamFn`                    | Обгортка потоку після застосування загальних обгорток                                           | Провайдеру потрібні обгортки сумісності headers/body/model без custom transport                                                             |
| 22  | `resolveTransportTurnState`       | Прикріплює native headers або метадані transport на кожен хід                                   | Провайдер хоче, щоб generic transports надсилали ідентичність ходу, нативну для провайдера                                                 |
| 23  | `resolveWebSocketSessionPolicy`   | Прикріплює native WebSocket headers або політику паузи сесії                                    | Провайдер хоче, щоб generic WS transports налаштовували headers сесії або політику fallback                                                |
| 24  | `formatApiKey`                    | Форматер auth-profile: збережений profile стає runtime-рядком `apiKey`                          | Провайдер зберігає додаткові auth metadata і потребує custom shape runtime token                                                            |
| 25  | `refreshOAuth`                    | Перевизначення OAuth refresh для custom refresh endpoints або політики помилки refresh          | Провайдер не відповідає спільним refreshers `pi-ai`                                                                                         |
| 26  | `buildAuthDoctorHint`             | Підказка виправлення, що додається при помилці OAuth refresh                                    | Провайдеру потрібні власні вказівки з виправлення auth після помилки refresh                                                                |
| 27  | `matchesContextOverflowError`     | Матчер переповнення context-window, що належить провайдеру                                      | Провайдер має сирі помилки переповнення, які generic heuristics пропустять                                                                  |
| 28  | `classifyFailoverReason`          | Класифікація причини failover, що належить провайдеру                                           | Провайдер може зіставляти сирі помилки API/transport із rate-limit/overload тощо                                                           |
| 29  | `isCacheTtlEligible`              | Політика prompt-cache для proxy/backhaul провайдерів                                            | Провайдеру потрібне керування TTL кешу, специфічне для proxy                                                                                |
| 30  | `buildMissingAuthMessage`         | Заміна generic повідомлення про відновлення при відсутності auth                                | Провайдеру потрібна власна підказка відновлення auth                                                                                        |
| 31  | `suppressBuiltInModel`            | Приховування застарілих upstream моделей плюс необов’язкова користувацька підказка про помилку  | Провайдеру потрібно приховувати застарілі рядки upstream або замінювати їх підказкою вендора                                               |
| 32  | `augmentModelCatalog`             | Synthetic/final рядки каталогу додаються після виявлення                                        | Провайдеру потрібні synthetic рядки прямої сумісності в `models list` і вибірниках                                                         |
| 33  | `isBinaryThinking`                | Перемикач reasoning увімк./вимк. для провайдерів із binary-thinking                             | Провайдер підтримує лише двійкове вмикання/вимикання thinking                                                                               |
| 34  | `supportsXHighThinking`           | Підтримка reasoning `xhigh` для вибраних моделей                                                | Провайдер хоче `xhigh` лише для підмножини моделей                                                                                          |
| 35  | `resolveDefaultThinkingLevel`     | Рівень `/think` за замовчуванням для конкретного сімейства моделей                              | Провайдер володіє політикою `/think` за замовчуванням для сімейства моделей                                                                 |
| 36  | `isModernModelRef`                | Матчер modern-model для live profile filters і відбору smoke                                    | Провайдер володіє зіставленням preferred-model для live/smoke                                                                               |
| 37  | `prepareRuntimeAuth`              | Обмінює налаштовані облікові дані на фактичний runtime token/key безпосередньо перед inference  | Провайдеру потрібен обмін token або короткоживучі облікові дані запиту                                                                      |
| 38  | `resolveUsageAuth`                | Резолвить облікові дані usage/billing для `/usage` і пов’язаних поверхонь status                | Провайдеру потрібен custom розбір usage/quota token або інші облікові дані usage                                                           |
| 39  | `fetchUsageSnapshot`              | Отримує й нормалізує snapshots usage/quota, специфічні для провайдера, після резолву auth       | Провайдеру потрібен власний ендпоїнт usage або parser payload                                                                               |
| 40  | `createEmbeddingProvider`         | Створює adapter embedding, що належить провайдеру, для memory/search                            | Поведінка embedding для memory має належати плагіну провайдера                                                                              |
| 41  | `buildReplayPolicy`               | Повертає політику replay, яка контролює обробку transcript для провайдера                       | Провайдеру потрібна custom політика transcript (наприклад, видалення thinking-block)                                                       |
| 42  | `sanitizeReplayHistory`           | Переписує історію replay після загального очищення transcript                                    | Провайдеру потрібні переписування replay, специфічні для провайдера, понад спільні helpers компактування                                   |
| 43  | `validateReplayTurns`             | Фінальна валідація або переформування ходів replay перед embedded runner                         | Transport провайдера потребує суворішої валідації ходів після загального очищення                                                           |
| 44  | `onModelSelected`                 | Виконує побічні ефекти після вибору моделі, що належать провайдеру                              | Провайдеру потрібна телеметрія або стан, що належить провайдеру, коли модель стає активною                                                 |

`normalizeModelId`, `normalizeTransport` і `normalizeConfig` спочатку перевіряють
відповідний plugin провайдера, а потім переходять до інших hook-capable provider plugins,
доки хтось справді не змінить id моделі або transport/config. Це дозволяє
shim-ам alias/compat провайдерів працювати без потреби для викликача знати, який
bundled plugin володіє переписуванням. Якщо жоден hook провайдера не переписує підтримуваний
запис конфігурації Google-family, bundled normalizer конфігурації Google усе одно застосує
це очищення сумісності.

Якщо провайдеру потрібен повністю custom wire protocol або custom request executor,
це інший клас розширення. Ці hooks призначені для поведінки провайдера,
яка все ще працює на звичайному inference loop OpenClaw.

### Приклад провайдера

```ts
api.registerProvider({
  id: "example-proxy",
  label: "Example Proxy",
  auth: [],
  catalog: {
    order: "simple",
    run: async (ctx) => {
      const apiKey = ctx.resolveProviderApiKey("example-proxy").apiKey;
      if (!apiKey) {
        return null;
      }
      return {
        provider: {
          baseUrl: "https://proxy.example.com/v1",
          apiKey,
          api: "openai-completions",
          models: [{ id: "auto", name: "Auto" }],
        },
      };
    },
  },
  resolveDynamicModel: (ctx) => ({
    id: ctx.modelId,
    name: ctx.modelId,
    provider: "example-proxy",
    api: "openai-completions",
    baseUrl: "https://proxy.example.com/v1",
    reasoning: false,
    input: ["text"],
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: 128000,
    maxTokens: 8192,
  }),
  prepareRuntimeAuth: async (ctx) => {
    const exchanged = await exchangeToken(ctx.apiKey);
    return {
      apiKey: exchanged.token,
      baseUrl: exchanged.baseUrl,
      expiresAt: exchanged.expiresAt,
    };
  },
  resolveUsageAuth: async (ctx) => {
    const auth = await ctx.resolveOAuthToken();
    return auth ? { token: auth.token } : null;
  },
  fetchUsageSnapshot: async (ctx) => {
    return await fetchExampleProxyUsage(ctx.token, ctx.timeoutMs, ctx.fetchFn);
  },
});
```

### Вбудовані приклади

- Anthropic використовує `resolveDynamicModel`, `capabilities`, `buildAuthDoctorHint`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `isCacheTtlEligible`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  і `wrapStreamFn`, оскільки володіє прямою сумісністю Claude 4.6,
  підказками сімейства провайдера, інструкціями з виправлення auth, інтеграцією
  ендпоїнта usage, придатністю prompt-cache, значеннями конфігурації за замовчуванням, що враховують auth,
  політикою thinking Claude за замовчуванням/адаптивною, а також stream shaping, специфічним для Anthropic,
  для beta headers, `/fast` / `serviceTier` і `context1m`.
- Специфічні для Claude stream helpers Anthropic поки що залишаються у власному
  публічному шві bundled plugin `api.ts` / `contract-api.ts`. Ця поверхня пакета
  експортує `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` і низькорівневі
  builders обгорток Anthropic замість розширення generic SDK навколо правил beta-header
  одного провайдера.
- OpenAI використовує `resolveDynamicModel`, `normalizeResolvedModel` і
  `capabilities`, а також `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking` і `isModernModelRef`,
  оскільки володіє прямою сумісністю GPT-5.4, прямою нормалізацією OpenAI
  `openai-completions` -> `openai-responses`, підказками auth з урахуванням Codex,
  приховуванням Spark, synthetic рядками списку OpenAI і політикою GPT-5 thinking /
  live-model; сімейство stream `openai-responses-defaults` володіє
  спільними native OpenAI Responses wrappers для attribution headers,
  `/fast`/`serviceTier`, текстової багатослівності, native Codex web search,
  формування payload reasoning-compat і керування context Responses.
- OpenRouter використовує `catalog`, а також `resolveDynamicModel` і
  `prepareDynamicModel`, тому що провайдер є pass-through і може відкривати нові
  model ids до оновлення статичного каталогу OpenClaw; він також використовує
  `capabilities`, `wrapStreamFn` і `isCacheTtlEligible`, щоб тримати
  request headers, routing metadata, patches reasoning і політику prompt-cache,
  специфічні для провайдера, поза core. Його політика replay походить із сімейства
  `passthrough-gemini`, а сімейство stream `openrouter-thinking`
  володіє proxy-ін’єкцією reasoning і пропусками unsupported-model / `auto`.
- GitHub Copilot використовує `catalog`, `auth`, `resolveDynamicModel` і
  `capabilities`, а також `prepareRuntimeAuth` і `fetchUsageSnapshot`,
  оскільки йому потрібні device login, що належить провайдеру, поведінка fallback моделей,
  особливості transcript Claude, обмін GitHub token -> Copilot token
  і endpoint usage, що належить провайдеру.
- OpenAI Codex використовує `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth` і `augmentModelCatalog`, а також
  `prepareExtraParams`, `resolveUsageAuth` і `fetchUsageSnapshot`, тому що він
  усе ще працює на transports core OpenAI, але володіє своєю нормалізацією
  transport/base URL, політикою fallback OAuth refresh, вибором transport за замовчуванням,
  synthetic рядками каталогу Codex і інтеграцією ендпоїнта usage ChatGPT; він
  використовує те саме сімейство stream `openai-responses-defaults`, що й прямий OpenAI.
- Google AI Studio і Gemini CLI OAuth використовують `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn` і `isModernModelRef`, тому що
  сімейство replay `google-gemini` володіє fallback сумісності Gemini 3.1,
  native валідацією replay Gemini, очищенням bootstrap replay,
  режимом tagged reasoning-output і зіставленням modern-model, а
  сімейство stream `google-thinking` володіє нормалізацією payload thinking Gemini;
  Gemini CLI OAuth також використовує `formatApiKey`, `resolveUsageAuth` і
  `fetchUsageSnapshot` для форматування token, розбору token і підключення
  endpoint quota.
- Anthropic Vertex використовує `buildReplayPolicy` через
  сімейство replay `anthropic-by-model`, щоб очищення replay, специфічне для Claude, залишалося
  обмеженим id Claude, а не кожним transport `anthropic-messages`.
- Amazon Bedrock використовує `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason` і `resolveDefaultThinkingLevel`, оскільки володіє
  класифікацією помилок throttle/not-ready/context-overflow, специфічною для Bedrock,
  для трафіку Anthropic-on-Bedrock; його політика replay все ще використовує той самий
  захист лише для Claude `anthropic-by-model`.
- OpenRouter, Kilocode, Opencode і Opencode Go використовують `buildReplayPolicy`
  через сімейство replay `passthrough-gemini`, тому що вони проксіюють моделі Gemini
  через transports, сумісні з OpenAI, і потребують очищення thought-signature Gemini
  без native валідації replay Gemini або переписувань bootstrap.
- MiniMax використовує `buildReplayPolicy` через
  сімейство replay `hybrid-anthropic-openai`, тому що один провайдер володіє семантикою як
  повідомлень Anthropic, так і OpenAI-compatible; він зберігає видалення thinking-block
  лише для Claude на стороні Anthropic, водночас перевизначаючи режим reasoning
  output назад на native, а сімейство stream `minimax-fast-mode` володіє
  переписуваннями моделей fast-mode на спільному stream path.
- Moonshot використовує `catalog` плюс `wrapStreamFn`, тому що все ще використовує
  спільний transport OpenAI, але потребує нормалізації payload thinking, що належить провайдеру; сімейство
  stream `moonshot-thinking` зіставляє config плюс стан `/think` на його
  native binary thinking payload.
- Kilocode використовує `catalog`, `capabilities`, `wrapStreamFn` і
  `isCacheTtlEligible`, тому що йому потрібні request headers, специфічні для провайдера,
  нормалізація payload reasoning, підказки transcript Gemini і керування
  TTL кешу Anthropic; сімейство stream `kilocode-thinking` зберігає ін’єкцію Kilo thinking
  на шляху спільного proxy stream, водночас пропускаючи `kilo/auto` та
  інші proxy model ids, які не підтримують явний payload reasoning.
- Z.AI використовує `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth` і `fetchUsageSnapshot`, тому що володіє fallback GLM-5,
  значеннями `tool_stream` за замовчуванням, UX binary thinking, зіставленням modern-model
  і як auth usage, так і отриманням quota; сімейство stream `tool-stream-default-on`
  тримає wrapper `tool_stream` з увімкненням за замовчуванням поза написаним вручну glue для кожного провайдера.
- xAI використовує `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel` і `isModernModelRef`,
  оскільки володіє нормалізацією native xAI Responses transport, переписуванням
  псевдонімів fast-mode Grok, типовим `tool_stream`, очищенням strict-tool /
  payload reasoning, fallback повторним використанням auth для tools, що належать плагіну,
  резолвом прямих сумісних моделей Grok і patches compat, що належать провайдеру, як-от профіль схем tools xAI,
  непідтримувані keywords схем, native `web_search` і декодування HTML-entity
  аргументів виклику tool.
- Mistral, OpenCode Zen і OpenCode Go використовують лише `capabilities`,
  щоб винести особливості transcript/tooling за межі core.
- Bundled providers лише з каталогом, як-от `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway` і `volcengine`, використовують
  лише `catalog`.
- Qwen використовує `catalog` для свого текстового провайдера, а також спільні реєстрації
  media-understanding і video-generation для своїх мультимодальних поверхонь.
- MiniMax і Xiaomi використовують `catalog` плюс hooks usage, тому що їхня поведінка `/usage`
  належить плагіну, хоча inference усе ще працює через спільні transports.

## Helpers runtime

Плагіни можуть отримувати доступ до вибраних helpers core через `api.runtime`. Для TTS:

```ts
const clip = await api.runtime.tts.textToSpeech({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const result = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

Примітки:

- `textToSpeech` повертає звичайний payload виводу TTS core для поверхонь файлів/голосових нотаток.
- Використовує конфігурацію core `messages.tts` і вибір провайдера.
- Повертає PCM audio buffer + sample rate. Плагіни мають виконувати ресемплінг/кодування для провайдерів.
- `listVoices` необов’язковий для кожного провайдера. Використовуйте його для voice pickers або setup flows, що належать вендору.
- Списки голосів можуть містити багатші метадані, як-от locale, gender і personality tags для picker-ів, що враховують провайдера.
- OpenAI і ElevenLabs сьогодні підтримують телефонію. Microsoft — ні.

Плагіни також можуть реєструвати speech providers через `api.registerSpeechProvider(...)`.

```ts
api.registerSpeechProvider({
  id: "acme-speech",
  label: "Acme Speech",
  isConfigured: ({ config }) => Boolean(config.messages?.tts),
  synthesize: async (req) => {
    return {
      audioBuffer: Buffer.from([]),
      outputFormat: "mp3",
      fileExtension: ".mp3",
      voiceCompatible: false,
    };
  },
});
```

Примітки:

- Зберігайте політику TTS, fallback і доставку відповіді в core.
- Використовуйте speech providers для поведінки синтезу, що належить вендору.
- Legacy-ввід Microsoft `edge` нормалізується до id провайдера `microsoft`.
- Бажана модель володіння орієнтована на компанію: один vendor plugin може володіти
  text, speech, image і майбутніми media providers, щойно OpenClaw додасть ці
  контракти можливостей.

Для розуміння зображень/аудіо/відео плагіни реєструють один типізований
провайдер media-understanding замість generic key/value bag:

```ts
api.registerMediaUnderstandingProvider({
  id: "google",
  capabilities: ["image", "audio", "video"],
  describeImage: async (req) => ({ text: "..." }),
  transcribeAudio: async (req) => ({ text: "..." }),
  describeVideo: async (req) => ({ text: "..." }),
});
```

Примітки:

- Зберігайте оркестрацію, fallback, config і підключення каналів у core.
- Зберігайте поведінку вендора в плагіні провайдера.
- Адитивне розширення має лишатися типізованим: нові необов’язкові методи, нові необов’язкові
  поля результату, нові необов’язкові можливості.
- Генерація відео вже дотримується того самого шаблону:
  - core володіє контрактом можливості та helper runtime
  - vendor plugins реєструють `api.registerVideoGenerationProvider(...)`
  - feature/channel plugins споживають `api.runtime.videoGeneration.*`

Для helpers runtime media-understanding плагіни можуть викликати:

```ts
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});
```

Для аудіотранскрипції плагіни можуть використовувати або runtime media-understanding,
або старий псевдонім STT:

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // Optional when MIME cannot be inferred reliably:
  mime: "audio/ogg",
});
```

Примітки:

- `api.runtime.mediaUnderstanding.*` — це бажана спільна поверхня для
  розуміння зображень/аудіо/відео.
- Використовує конфігурацію аудіо core media-understanding (`tools.media.audio`) і порядок fallback провайдерів.
- Повертає `{ text: undefined }`, коли не було отримано результату транскрипції (наприклад, для пропущеного/непідтримуваного вводу).
- `api.runtime.stt.transcribeAudioFile(...)` лишається alias сумісності.

Плагіни також можуть запускати фонові підзапуски subagent через `api.runtime.subagent`:

```ts
const result = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai",
  model: "gpt-4.1-mini",
  deliver: false,
});
```

Примітки:

- `provider` і `model` — це необов’язкові перевизначення для конкретного запуску, а не постійні зміни сесії.
- OpenClaw враховує ці поля перевизначення лише для довірених викликачів.
- Для fallback-запусків, що належать плагіну, оператори мають явно дозволити це через `plugins.entries.<id>.subagent.allowModelOverride: true`.
- Використовуйте `plugins.entries.<id>.subagent.allowedModels`, щоб обмежити довірені плагіни конкретними канонічними цілями `provider/model`, або `"*"` для явного дозволу будь-якої цілі.
- Запуски subagent від недовірених плагінів усе ще працюють, але запити на перевизначення відхиляються замість тихого fallback.

Для web search плагіни можуть споживати спільний helper runtime замість
звернення до підключення agent tool:

```ts
const providers = api.runtime.webSearch.listProviders({
  config: api.config,
});

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: {
    query: "OpenClaw plugin runtime helpers",
    count: 5,
  },
});
```

Плагіни також можуть реєструвати web-search providers через
`api.registerWebSearchProvider(...)`.

Примітки:

- Зберігайте вибір провайдера, резолв облікових даних і спільну семантику запитів у core.
- Використовуйте web-search providers для транспортів пошуку, специфічних для вендора.
- `api.runtime.webSearch.*` — це бажана спільна поверхня для feature/channel plugins, яким потрібна поведінка пошуку без залежності від обгортки agent tool.

### `api.runtime.imageGeneration`

```ts
const result = await api.runtime.imageGeneration.generate({
  config: api.config,
  args: { prompt: "A friendly lobster mascot", size: "1024x1024" },
});

const providers = api.runtime.imageGeneration.listProviders({
  config: api.config,
});
```

- `generate(...)`: згенерувати зображення за допомогою налаштованого ланцюжка провайдерів генерації зображень.
- `listProviders(...)`: перелічити доступних провайдерів генерації зображень і їхні можливості.

## HTTP routes Gateway

Плагіни можуть відкривати HTTP endpoints через `api.registerHttpRoute(...)`.

```ts
api.registerHttpRoute({
  path: "/acme/webhook",
  auth: "plugin",
  match: "exact",
  handler: async (_req, res) => {
    res.statusCode = 200;
    res.end("ok");
    return true;
  },
});
```

Поля route:

- `path`: шлях route у межах HTTP-сервера gateway.
- `auth`: обов’язково. Використовуйте `"gateway"` для звичайної auth gateway або `"plugin"` для auth/webhook verification, якими керує плагін.
- `match`: необов’язково. `"exact"` (типово) або `"prefix"`.
- `replaceExisting`: необов’язково. Дозволяє тому самому плагіну замінити власну наявну реєстрацію route.
- `handler`: повертайте `true`, коли route обробив запит.

Примітки:

- `api.registerHttpHandler(...)` видалено, і він спричинить помилку завантаження плагіна. Використовуйте `api.registerHttpRoute(...)`.
- Routes плагіна мають явно оголошувати `auth`.
- Конфлікти точного `path + match` відхиляються, якщо не вказано `replaceExisting: true`, і один плагін не може замінити route іншого плагіна.
- Перекривні routes з різними рівнями `auth` відхиляються. Ланцюжки fallthrough `exact`/`prefix` мають бути лише в межах одного рівня auth.
- Routes `auth: "plugin"` **не** отримують автоматично runtime scopes оператора. Вони призначені для webhook/signature verification, якими керує плагін, а не для привілейованих викликів helpers Gateway.
- Routes `auth: "gateway"` працюють у межах runtime scope запиту Gateway, але цей scope навмисно консервативний:
  - bearer auth на спільному секреті (`gateway.auth.mode = "token"` / `"password"`) утримує runtime scopes route плагіна на рівні `operator.write`, навіть якщо викликач надсилає `x-openclaw-scopes`
  - довірені HTTP-режими з ідентичністю (наприклад, `trusted-proxy` або `gateway.auth.mode = "none"` на приватному ingress) враховують `x-openclaw-scopes` лише коли заголовок явно присутній
  - якщо `x-openclaw-scopes` відсутній у таких запитах plugin-route з ідентичністю, runtime scope повертається до `operator.write`
- Практичне правило: не вважайте route плагіна з gateway-auth неявною адміністративною поверхнею. Якщо вашому route потрібна поведінка лише для admin, вимагайте auth-режим із перенесенням ідентичності та документуйте явний контракт заголовка `x-openclaw-scopes`.

## Шляхи імпорту Plugin SDK

Під час створення плагінів використовуйте subpaths SDK замість монолітного імпорту
`openclaw/plugin-sdk`:

- `openclaw/plugin-sdk/plugin-entry` для примітивів реєстрації плагінів.
- `openclaw/plugin-sdk/core` для загального спільного контракту, орієнтованого на плагіни.
- `openclaw/plugin-sdk/config-schema` для експорту кореневої Zod-схеми `openclaw.json`
  (`OpenClawSchema`).
- Стабільні примітиви каналів, як-от `openclaw/plugin-sdk/channel-setup`,
  `openclaw/plugin-sdk/setup-runtime`,
  `openclaw/plugin-sdk/setup-adapter-runtime`,
  `openclaw/plugin-sdk/setup-tools`,
  `openclaw/plugin-sdk/channel-pairing`,
  `openclaw/plugin-sdk/channel-contract`,
  `openclaw/plugin-sdk/channel-feedback`,
  `openclaw/plugin-sdk/channel-inbound`,
  `openclaw/plugin-sdk/channel-lifecycle`,
  `openclaw/plugin-sdk/channel-reply-pipeline`,
  `openclaw/plugin-sdk/command-auth`,
  `openclaw/plugin-sdk/secret-input` і
  `openclaw/plugin-sdk/webhook-ingress` для спільного підключення налаштування/auth/reply/webhook.
  `channel-inbound` — це спільний дім для debounce, mention matching,
  форматування envelope та helpers контексту inbound envelope.
  `channel-setup` — вузький шов setup для необов’язкового встановлення.
  `setup-runtime` — безпечна для runtime поверхня setup, яку використовують `setupEntry` /
  відкладений запуск, включно з адаптерами патчів setup, безпечними для імпорту.
  `setup-adapter-runtime` — шов account-setup adapter, що враховує env.
  `setup-tools` — малий шов допоміжних засобів CLI/archive/docs (`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`).
- Domain subpaths, як-от `openclaw/plugin-sdk/channel-config-helpers`,
  `openclaw/plugin-sdk/allow-from`,
  `openclaw/plugin-sdk/channel-config-schema`,
  `openclaw/plugin-sdk/telegram-command-config`,
  `openclaw/plugin-sdk/channel-policy`,
  `openclaw/plugin-sdk/approval-runtime`,
  `openclaw/plugin-sdk/config-runtime`,
  `openclaw/plugin-sdk/infra-runtime`,
  `openclaw/plugin-sdk/agent-runtime`,
  `openclaw/plugin-sdk/lazy-runtime`,
  `openclaw/plugin-sdk/reply-history`,
  `openclaw/plugin-sdk/routing`,
  `openclaw/plugin-sdk/status-helpers`,
  `openclaw/plugin-sdk/text-runtime`,
  `openclaw/plugin-sdk/runtime-store` і
  `openclaw/plugin-sdk/directory-runtime` для спільних helpers runtime/config.
  `telegram-command-config` — це вузький публічний шов для нормалізації/валідації custom
  команд Telegram і лишається доступним, навіть якщо поверхня контракту bundled
  Telegram тимчасово недоступна.
  `text-runtime` — це спільний шов text/markdown/logging, включно з
  видаленням assistant-visible-text, helpers render/chunking markdown, helpers редагування,
  helpers directive-tag і utilities безпечного тексту.
- Для approval-specific channel seams слід надавати перевагу одному контракту
  `approvalCapability` у плагіні. Тоді core читає auth доставки схвалень, delivery, render і
  native-routing через цю одну можливість замість змішування
  поведінки схвалення з не пов’язаними полями плагіна.
- `openclaw/plugin-sdk/channel-runtime` є застарілим і лишається лише
  як compatibility shim для старіших плагінів. Новий код має імпортувати вужчі
  generic primitives, а код репозиторію не повинен додавати нові імпорти цього shim.
- Внутрішні частини bundled extension лишаються приватними. Зовнішні плагіни мають використовувати лише
  subpaths `openclaw/plugin-sdk/*`. Код/тести core OpenClaw можуть використовувати
  публічні entry points репозиторію під коренем пакета плагіна, як-от `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js`, і вузькоспрямовані файли, як-от
  `login-qr-api.js`. Ніколи не імпортуйте `src/*` пакета плагіна з core або з
  іншого розширення.
- Поділ entry point у репозиторії:
  `<plugin-package-root>/api.js` — це barrel helpers/types,
  `<plugin-package-root>/runtime-api.js` — barrel лише для runtime,
  `<plugin-package-root>/index.js` — entry bundled plugin,
  а `<plugin-package-root>/setup-entry.js` — entry setup plugin.
- Поточні приклади bundled providers:
  - Anthropic використовує `api.js` / `contract-api.js` для Claude stream helpers, таких
    як `wrapAnthropicProviderStream`, helpers beta-header і парсинг `service_tier`.
  - OpenAI використовує `api.js` для builders провайдерів, helpers моделей за замовчуванням і builders realtime provider.
  - OpenRouter використовує `api.js` для builder провайдера, а також helpers onboarding/config,
    тоді як `register.runtime.js` усе ще може реекспортувати generic
    helpers `plugin-sdk/provider-stream` для локального використання в репозиторії.
- Публічні entry points, завантажені через facade, надають перевагу активному snapshot конфігурації runtime,
  якщо він існує, а інакше повертаються до резолвленого файла конфігурації на диску, коли
  OpenClaw ще не надає snapshot runtime.
- Generic shared primitives лишаються бажаним публічним контрактом SDK. Невеликий
  зарезервований набір сумісності branded helper seams bundled channel усе ще
  існує. Розглядайте їх як шви для підтримки/сумісності bundled, а не як нові цілі імпорту для третіх сторін; нові міжканальні контракти все одно мають
  додаватися до generic subpaths `plugin-sdk/*` або локальних barrels плагіна `api.js` /
  `runtime-api.js`.

Примітка щодо сумісності:

- Уникайте кореневого barrel `openclaw/plugin-sdk` у новому коді.
- Насамперед надавайте перевагу вузьким стабільним primitives. Новіші subpaths setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool — це цільовий контракт для нової роботи з
  bundled і зовнішніми плагінами.
  Розбір/зіставлення цілей належить до `openclaw/plugin-sdk/channel-targets`.
  Перевірки message action та helpers id повідомлень реакцій належать до
  `openclaw/plugin-sdk/channel-actions`.
- Helper barrels, специфічні для bundled extension, не є стабільними за замовчуванням. Якщо
  helper потрібен лише bundled extension, тримайте його за локальним
  швом розширення `api.js` або `runtime-api.js` замість просування до
  `openclaw/plugin-sdk/<extension>`.
- Нові шви спільних helpers мають бути generic, а не branded під канал. Спільний розбір
  цілей належить до `openclaw/plugin-sdk/channel-targets`; внутрішні частини, специфічні для каналу,
  лишаються за локальним швом `api.js` або `runtime-api.js` плагіна-власника.
- Subpaths, специфічні для можливостей, як-от `image-generation`,
  `media-understanding` і `speech`, існують, тому що bundled/native plugins використовують
  їх уже сьогодні. Їхня наявність сама по собі не означає, що кожен експортований helper — це
  довгостроковий заморожений зовнішній контракт.

## Схеми message tool

Плагіни мають володіти внесками до схем `describeMessageTool(...)`, специфічними для каналу.
Тримайте поля, специфічні для провайдера, у плагіні, а не в спільному core.

Для спільних portable фрагментів схеми повторно використовуйте generic helpers, експортовані через
`openclaw/plugin-sdk/channel-actions`:

- `createMessageToolButtonsSchema()` для payload у стилі сітки кнопок
- `createMessageToolCardSchema()` для структурованих payload карток

Якщо форма схеми має сенс лише для одного провайдера, визначайте її у власному
вихідному коді цього плагіна, а не просувайте її до спільного SDK.

## Резолв цілей каналу

Плагіни каналів мають володіти семантикою цілей, специфічною для каналу. Зберігайте спільний
outbound host generic і використовуйте поверхню messaging adapter для правил провайдера:

- `messaging.inferTargetChatType({ to })` вирішує, чи слід трактувати нормалізовану ціль
  як `direct`, `group` або `channel` до пошуку в directory.
- `messaging.targetResolver.looksLikeId(raw, normalized)` повідомляє core, чи слід
  одразу перейти до резолву як id, а не шукати в directory.
- `messaging.targetResolver.resolveTarget(...)` — це fallback плагіна, коли
  core потрібен остаточний резолв, що належить провайдеру, після нормалізації або
  після промаху в directory.
- `messaging.resolveOutboundSessionRoute(...)` володіє побудовою маршруту сесії, специфічного для провайдера,
  після того, як ціль резолвлено.

Рекомендований поділ:

- Використовуйте `inferTargetChatType` для категоризації, яка має відбуватися до
  пошуку peers/groups.
- Використовуйте `looksLikeId` для перевірок «вважати це явним/native target id».
- Використовуйте `resolveTarget` для fallback нормалізації, специфічної для провайдера, а не для
  широкого пошуку в directory.
- Тримайте provider-native ids, як-от chat ids, thread ids, JIDs, handles і room
  ids, усередині значень `target` або параметрів, специфічних для провайдера, а не в generic полях SDK.

## Каталоги на основі конфігурації

Плагіни, які виводять записи directory із config, мають тримати цю логіку в
плагіні й повторно використовувати спільні helpers із
`openclaw/plugin-sdk/directory-runtime`.

Використовуйте це, коли каналу потрібні peers/groups на основі config, наприклад:

- DM peers, керовані allowlist
- налаштовані відображення channel/group
- статичні account-scoped fallback-и directory

Спільні helpers у `directory-runtime` обробляють лише generic операції:

- фільтрація запитів
- застосування ліміту
- дедуплікація/helpers нормалізації
- побудова `ChannelDirectoryEntry[]`

Перевірка account та нормалізація id, специфічні для каналу, мають лишатися в реалізації
плагіна.

## Каталоги провайдерів

Плагіни провайдерів можуть визначати каталоги моделей для inference за допомогою
`registerProvider({ catalog: { run(...) { ... } } })`.

`catalog.run(...)` повертає ту саму форму, яку OpenClaw записує в
`models.providers`:

- `{ provider }` для одного запису провайдера
- `{ providers }` для кількох записів провайдера

Використовуйте `catalog`, коли плагін володіє model ids, значеннями base URL за замовчуванням або
метаданими моделей з керуванням через auth, специфічними для провайдера.

`catalog.order` керує тим, коли каталог плагіна зливається відносно
вбудованих неявних провайдерів OpenClaw:

- `simple`: прості провайдери на основі API-key або env
- `profile`: провайдери, які з’являються, коли існують auth profiles
- `paired`: провайдери, які синтезують кілька пов’язаних записів провайдерів
- `late`: останній прохід після інших неявних провайдерів

Пізніші провайдери перемагають при конфлікті ключів, тому плагіни можуть навмисно
перевизначити вбудований запис провайдера з тим самим id провайдера.

Сумісність:

- `discovery` досі працює як legacy alias
- якщо зареєстровано і `catalog`, і `discovery`, OpenClaw використовує `catalog`

## Інспекція каналів у режимі лише читання

Якщо ваш плагін реєструє канал, надавайте перевагу реалізації
`plugin.config.inspectAccount(cfg, accountId)` разом із `resolveAccount(...)`.

Чому:

- `resolveAccount(...)` — це шлях runtime. Він може припускати, що credentials
  повністю матеріалізовані, і швидко завершуватися помилкою, коли обов’язкових секретів бракує.
- Шляхи команд лише для читання, як-от `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve` і потоки doctor/config
  repair, не повинні потребувати матеріалізації credentials runtime лише для
  опису конфігурації.

Рекомендована поведінка `inspectAccount(...)`:

- Повертає лише описовий стан account.
- Зберігає `enabled` і `configured`.
- Включає поля джерела/статусу credentials, коли це доречно, наприклад:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- Вам не потрібно повертати сирі значення token лише для звітування про доступність у режимі лише читання. Повернення `tokenStatus: "available"` (і відповідного поля джерела) достатньо для команд у стилі status.
- Використовуйте `configured_unavailable`, коли credential налаштовано через SecretRef, але
  він недоступний у поточному шляху команди.

Це дозволяє командам лише для читання повідомляти «налаштовано, але недоступно в цьому шляху команди» замість аварійного завершення або хибного звіту про те, що account не налаштовано.

## Пакетні набори

Каталог плагіна може містити `package.json` з `openclaw.extensions`:

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

Кожен entry стає плагіном. Якщо набір містить кілька extensions, id плагіна
стає `name/<fileBase>`.

Якщо ваш плагін імпортує npm dependencies, установіть їх у цьому каталозі, щоб
`node_modules` був доступний (`npm install` / `pnpm install`).

Запобіжник безпеки: кожен entry у `openclaw.extensions` має залишатися в межах каталогу плагіна
після резолву symlink. Entries, які виходять за межі каталогу пакета,
відхиляються.

Примітка з безпеки: `openclaw plugins install` встановлює dependencies плагіна за допомогою
`npm install --omit=dev --ignore-scripts` (без lifecycle scripts і без dev dependencies у runtime). Зберігайте дерева залежностей плагінів як «чисті JS/TS» і уникайте пакетів, яким потрібні збірки через `postinstall`.

Необов’язково: `openclaw.setupEntry` може вказувати на полегшений модуль лише для setup.
Коли OpenClaw потребує surfaces setup для вимкненого channel plugin або
коли channel plugin увімкнений, але ще не налаштований, він завантажує `setupEntry`
замість повного entry плагіна. Це робить запуск і setup легшими,
коли ваш основний entry плагіна також підключає tools, hooks або інший код лише для runtime.

Необов’язково: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
може перевести channel plugin на той самий шлях `setupEntry` під час
фази запуску gateway до початку прослуховування, навіть якщо канал уже налаштовано.

Використовуйте це лише коли `setupEntry` повністю покриває поверхню запуску, яка має існувати
до того, як gateway почне прослуховувати. На практиці це означає, що entry setup
має реєструвати кожну можливість каналу, від якої залежить запуск, наприклад:

- саму реєстрацію каналу
- будь-які HTTP routes, які мають бути доступні до початку прослуховування gateway
- будь-які методи gateway, tools або services, які мають існувати в тому самому вікні

Якщо ваш повний entry усе ще володіє будь-якою обов’язковою можливістю запуску, не вмикайте
цей прапорець. Залишайте плагін у типові поведінці і дозвольте OpenClaw завантажити
повний entry під час запуску.

Bundled channels також можуть публікувати helpers surface контракту лише для setup, до яких core
може звертатися до завантаження повного runtime каналу. Поточна поверхня
підвищення setup така:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

Core використовує цю поверхню, коли йому потрібно перевести legacy single-account channel
config у `channels.<id>.accounts.*` без завантаження повного entry плагіна.
Поточний приклад bundled — Matrix: він переносить лише ключі auth/bootstrap у
іменований обліковий запис після підвищення, коли іменовані облікові записи вже існують, і може
зберегти налаштований неканонічний ключ default-account замість того, щоб завжди створювати
`accounts.default`.

Ці адаптери патчів setup тримають виявлення поверхні контракту bundled lazy. Час
імпорту залишається малим; поверхня підвищення завантажується лише при першому використанні
замість повторного входу в запуск bundled channel під час імпорту модуля.

Коли ці поверхні запуску включають gateway RPC methods, тримайте їх під
специфічним для плагіна префіксом. Простори імен core admin (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) залишаються зарезервованими й завжди резолвляться
до `operator.admin`, навіть якщо плагін запитує вужчий scope.

Приклад:

```json
{
  "name": "@scope/my-channel",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

### Метадані каталогу каналів

Плагіни каналів можуть оголошувати метадані setup/discovery через `openclaw.channel` і
підказки встановлення через `openclaw.install`. Це дозволяє ядру каталогу не містити даних.

Приклад:

```json
{
  "name": "@openclaw/nextcloud-talk",
  "openclaw": {
    "extensions": ["./index.ts"],
    "channel": {
      "id": "nextcloud-talk",
      "label": "Nextcloud Talk",
      "selectionLabel": "Nextcloud Talk (self-hosted)",
      "docsPath": "/channels/nextcloud-talk",
      "docsLabel": "nextcloud-talk",
      "blurb": "Self-hosted chat via Nextcloud Talk webhook bots.",
      "order": 65,
      "aliases": ["nc-talk", "nc"]
    },
    "install": {
      "npmSpec": "@openclaw/nextcloud-talk",
      "localPath": "<bundled-plugin-local-path>",
      "defaultChoice": "npm"
    }
  }
}
```

Корисні поля `openclaw.channel` поза мінімальним прикладом:

- `detailLabel`: вторинний label для багатших поверхонь каталогу/status
- `docsLabel`: перевизначає текст посилання на документацію
- `preferOver`: id плагінів/каналів нижчого пріоритету, які цей запис каталогу має випереджати
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: керування копірайтом для поверхонь вибору
- `markdownCapable`: позначає канал як такий, що підтримує markdown, для рішень щодо outbound formatting
- `exposure.configured`: приховує канал із поверхонь списку налаштованих каналів, якщо встановлено `false`
- `exposure.setup`: приховує канал з інтерактивних picker-ів setup/configure, якщо встановлено `false`
- `exposure.docs`: позначає канал як внутрішній/приватний для поверхонь навігації документації
- `showConfigured` / `showInSetup`: legacy aliases усе ще приймаються для сумісності; надавайте перевагу `exposure`
- `quickstartAllowFrom`: додає канал до стандартного потоку quickstart `allowFrom`
- `forceAccountBinding`: вимагає явної прив’язки account, навіть коли існує лише один account
- `preferSessionLookupForAnnounceTarget`: надає перевагу пошуку сесії під час резолву announce targets

OpenClaw також може зливати **зовнішні каталоги каналів** (наприклад, експорт реєстру MPM).
Розмістіть JSON-файл у одному з таких шляхів:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

Або вкажіть `OPENCLAW_PLUGIN_CATALOG_PATHS` (або `OPENCLAW_MPM_CATALOG_PATHS`) на
один або кілька JSON-файлів (розділених комою/крапкою з комою/`PATH`). Кожен файл має
містити `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`. Parser також приймає `"packages"` або `"plugins"` як legacy aliases для ключа `"entries"`.

## Плагіни context engine

Плагіни context engine володіють оркестрацією контексту сесії для ingest, assembly
і compaction. Зареєструйте їх зі свого плагіна через
`api.registerContextEngine(id, factory)`, а потім виберіть активний engine через
`plugins.slots.contextEngine`.

Використовуйте це, коли вашому плагіну потрібно замінити або розширити типовий
конвеєр context, а не просто додати memory search або hooks.

```ts
export default function (api) {
  api.registerContextEngine("lossless-claw", () => ({
    info: { id: "lossless-claw", name: "Lossless Claw", ownsCompaction: true },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages }) {
      return { messages, estimatedTokens: 0 };
    },
    async compact() {
      return { ok: true, compacted: false };
    },
  }));
}
```

Якщо ваш engine **не** володіє алгоритмом compaction, збережіть реалізацію `compact()`
і явно делегуйте її:

```ts
import { delegateCompactionToRuntime } from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("my-memory-engine", () => ({
    info: {
      id: "my-memory-engine",
      name: "My Memory Engine",
      ownsCompaction: false,
    },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages }) {
      return { messages, estimatedTokens: 0 };
    },
    async compact(params) {
      return await delegateCompactionToRuntime(params);
    },
  }));
}
```

## Додавання нової можливості

Коли плагіну потрібна поведінка, яка не вкладається в поточний API, не обходьте
систему плагінів приватним прямим доступом. Додайте відсутню можливість.

Рекомендована послідовність:

1. визначте контракт core
   Вирішіть, якою спільною поведінкою має володіти core: політика, fallback, злиття config,
   життєвий цикл, семантика для каналів і форма helper runtime.
2. додайте типізовані поверхні реєстрації/runtime плагіна
   Розширте `OpenClawPluginApi` та/або `api.runtime` найменшою корисною
   типізованою поверхнею можливості.
3. підключіть споживачів core + каналів/функцій
   Канали та плагіни функцій мають споживати нову можливість через core,
   а не імпортувати реалізацію вендора напряму.
4. зареєструйте реалізації вендорів
   Потім vendor plugins реєструють свої backend-и для цієї можливості.
5. додайте contract coverage
   Додайте тести, щоб із часом володіння та форма реєстрації залишалися явними.

Саме так OpenClaw лишається послідовним, не стаючи жорстко прив’язаним до світогляду
одного провайдера. Див. [Capability Cookbook](/uk/plugins/architecture)
для конкретного чекліста файлів і розгорнутого прикладу.

### Чекліст можливості

Коли ви додаєте нову можливість, реалізація зазвичай має торкатися цих
поверхонь разом:

- типи контракту core у `src/<capability>/types.ts`
- runner/helper runtime core у `src/<capability>/runtime.ts`
- поверхня реєстрації API плагіна в `src/plugins/types.ts`
- підключення реєстру плагінів у `src/plugins/registry.ts`
- відкриття runtime плагіна в `src/plugins/runtime/*`, коли feature/channel
  plugins мають її споживати
- helpers захоплення/тестування в `src/test-utils/plugin-registration.ts`
- перевірки володіння/контрактів у `src/plugins/contracts/registry.ts`
- документація для операторів/плагінів у `docs/`

Якщо якоїсь із цих поверхонь бракує, це зазвичай ознака того, що можливість
ще не повністю інтегрована.

### Шаблон можливості

Мінімальний шаблон:

```ts
// core contract
export type VideoGenerationProviderPlugin = {
  id: string;
  label: string;
  generateVideo: (req: VideoGenerationRequest) => Promise<VideoGenerationResult>;
};

// plugin API
api.registerVideoGenerationProvider({
  id: "openai",
  label: "OpenAI",
  async generateVideo(req) {
    return await generateOpenAiVideo(req);
  },
});

// shared runtime helper for feature/channel plugins
const clip = await api.runtime.videoGeneration.generate({
  prompt: "Show the robot walking through the lab.",
  cfg,
});
```

Шаблон contract test:

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

Це зберігає правило простим:

- core володіє контрактом можливості + оркестрацією
- vendor plugins володіють реалізаціями вендорів
- feature/channel plugins споживають helpers runtime
- contract tests зберігають володіння явним
