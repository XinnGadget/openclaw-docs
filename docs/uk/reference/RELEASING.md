---
read_when:
    - Шукаю визначення публічних каналів випусків
    - Шукаю іменування версій та частоту випусків
summary: Публічні канали випусків, іменування версій та частота випусків
title: Політика випусків
x-i18n:
    generated_at: "2026-04-13T13:00:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 402c7f8c38323f735df79611ae3272ffc3816dfd39dd73048b9cab2715fdc334
    source_path: reference/RELEASING.md
    workflow: 15
---

# Політика випусків

OpenClaw має три публічні канали випусків:

- stable: позначені тегами випуски, які за замовчуванням публікуються в npm `beta`, або в npm `latest`, якщо це явно запитано
- beta: prerelease-теги, які публікуються в npm `beta`
- dev: рухома вершина `main`

## Іменування версій

- Версія stable-випуску: `YYYY.M.D`
  - Git-тег: `vYYYY.M.D`
- Версія stable-коригувального випуску: `YYYY.M.D-N`
  - Git-тег: `vYYYY.M.D-N`
- Версія beta-prerelease: `YYYY.M.D-beta.N`
  - Git-тег: `vYYYY.M.D-beta.N`
- Не додавайте провідні нулі до місяця або дня
- `latest` означає поточний просунутий stable-випуск npm
- `beta` означає поточну ціль встановлення beta
- Stable і stable-коригувальні випуски за замовчуванням публікуються в npm `beta`; оператори випусків можуть явно націлити їх на `latest` або просунути перевірену beta-збірку пізніше
- Кожен випуск OpenClaw постачається разом як npm-пакет і програма для macOS

## Частота випусків

- Випуски спочатку проходять через beta
- Stable іде лише після перевірки останньої beta
- Детальна процедура випуску, схвалення, облікові дані та нотатки щодо відновлення доступні
  лише для maintainers

## Передрелізна перевірка

- Запустіть `pnpm build && pnpm ui:build` перед `pnpm release:check`, щоб очікувані
  артефакти випуску `dist/*` і бандл Control UI існували для кроку
  перевірки pack
- Запускайте `pnpm release:check` перед кожним позначеним тегом випуском
- Перевірки випуску тепер виконуються в окремому ручному workflow:
  `OpenClaw Release Checks`
- Цей поділ навмисний: він зберігає реальний шлях npm-випуску коротким,
  детермінованим і зосередженим на артефактах, тоді як повільніші live-перевірки йдуть
  у власному каналі, щоб не затримувати і не блокувати публікацію
- Перевірки випуску мають запускатися з workflow ref `main`, щоб логіка
  workflow і секрети залишалися канонічними
- Цей workflow приймає або наявний тег випуску, або поточний повний
  40-символьний commit SHA `main`
- У режимі commit-SHA він приймає лише поточний HEAD `origin/main`; використовуйте
  тег випуску для старіших commit випуску
- Передрелізна перевірка лише для валідації `OpenClaw NPM Release` також приймає поточний
  повний 40-символьний commit SHA `main` без вимоги наявності запушеного тегу
- Шлях із SHA є лише валідаційним і не може бути просунутий до реальної публікації
- У режимі SHA workflow синтезує `v<package.json version>` лише для перевірки
  метаданих пакета; реальна публікація все одно потребує реального тегу випуску
- Обидва workflow зберігають реальний шлях публікації та просування на GitHub-hosted
  runners, тоді як шлях валідації без змін стану може використовувати більші
  Blacksmith Linux runners
- Цей workflow запускає
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  з використанням обох workflow secrets: `OPENAI_API_KEY` і `ANTHROPIC_API_KEY`
- Передрелізна перевірка npm-випуску більше не очікує на окремий канал перевірок випуску
- Перед схваленням запустіть `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  (або відповідний тег beta/коригувального випуску)
- Після npm publish запустіть
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  (або відповідну beta/коригувальну версію), щоб перевірити шлях встановлення
  опублікованого реєстру в новому тимчасовому prefix
- Автоматизація випусків для maintainers тепер використовує модель preflight-then-promote:
  - реальний npm publish має пройти успішний npm `preflight_run_id`
  - stable npm-випуски за замовчуванням спрямовуються в `beta`
  - stable npm publish може явно націлюватися на `latest` через вхід workflow
  - stable npm-просування з `beta` до `latest` усе ще доступне як явний ручний режим у довіреному workflow `OpenClaw NPM Release`
  - прямі stable-публікації також можуть запускати явний режим синхронізації dist-tag, який
    вказує і `latest`, і `beta` на вже опубліковану stable-версію
  - ці режими dist-tag усе ще потребують дійсного `NPM_TOKEN` у середовищі `npm-release`, оскільки керування npm `dist-tag` є окремим від trusted publishing
  - публічний `macOS Release` є лише валідаційним
  - реальна приватна mac-публікація має пройти успішні приватні mac
    `preflight_run_id` і `validate_run_id`
  - реальні шляхи публікації просувають підготовлені артефакти замість повторного
    їх збирання
- Для stable-коригувальних випусків на кшталт `YYYY.M.D-N`, post-publish verifier
  також перевіряє той самий шлях оновлення в temp-prefix з `YYYY.M.D` до `YYYY.M.D-N`,
  щоб коригування випуску не могли непомітно залишити старіші глобальні встановлення
  на базовому stable-навантаженні
- Передрелізна перевірка npm-випуску завершується fail closed, якщо tarball не містить і
  `dist/control-ui/index.html`, і непорожнє навантаження `dist/control-ui/assets/`,
  щоб ми знову не випустили порожню панель браузера
- Якщо робота над випуском зачіпала планування CI, маніфести часу виконання extensions або
  матриці тестів extensions, перед схваленням заново згенеруйте й перегляньте
  виходи матриці workflow `checks-node-extensions`, якими володіє planner, із `.github/workflows/ci.yml`,
  щоб примітки до випуску не описували застарілу схему CI
- Готовність stable-випуску macOS також включає поверхні оновлювача:
  - GitHub release має зрештою містити запаковані `.zip`, `.dmg` і `.dSYM.zip`
  - `appcast.xml` у `main` після публікації має вказувати на новий stable zip
  - запакована програма має зберігати non-debug bundle id, непорожній Sparkle feed
    URL і `CFBundleVersion` на рівні або вище за канонічну нижню межу збірки Sparkle
    для цієї версії випуску

## Вхідні параметри workflow NPM

`OpenClaw NPM Release` приймає такі керовані оператором вхідні параметри:

- `tag`: обов’язковий тег випуску, наприклад `v2026.4.2`, `v2026.4.2-1` або
  `v2026.4.2-beta.1`; коли `preflight_only=true`, це також може бути поточний
  повний 40-символьний commit SHA `main` для передрелізної перевірки лише для валідації
- `preflight_only`: `true` для лише валідації/збирання/пакування, `false` для
  шляху реальної публікації
- `preflight_run_id`: обов’язковий на шляху реальної публікації, щоб workflow повторно використав
  підготовлений tarball з успішного передрелізного запуску
- `npm_dist_tag`: цільовий тег npm для шляху публікації; за замовчуванням `beta`
- `promote_beta_to_latest`: `true`, щоб пропустити публікацію і перемістити вже опубліковану
  stable-збірку `beta` на `latest`
- `sync_stable_dist_tags`: `true`, щоб пропустити публікацію і спрямувати і `latest`, і
  `beta` на вже опубліковану stable-версію

`OpenClaw Release Checks` приймає такі керовані оператором вхідні параметри:

- `ref`: наявний тег випуску або поточний повний 40-символьний commit
  SHA для перевірки

Правила:

- Stable і correction-теги можуть публікуватися або в `beta`, або в `latest`
- Beta prerelease-теги можуть публікуватися лише в `beta`
- Повний вхід commit SHA дозволено лише коли `preflight_only=true`
- Режим commit-SHA для перевірок випуску також вимагає поточного HEAD `origin/main`
- Реальний шлях публікації має використовувати той самий `npm_dist_tag`, що й під час передрелізної перевірки;
  workflow перевіряє ці метадані перед продовженням публікації
- Режим просування має використовувати stable або correction-тег, `preflight_only=false`,
  порожній `preflight_run_id` і `npm_dist_tag=beta`
- Режим синхронізації dist-tag має використовувати stable або correction-тег,
  `preflight_only=false`, порожній `preflight_run_id`, `npm_dist_tag=latest`
  і `promote_beta_to_latest=false`
- Режими просування та синхронізації dist-tag також потребують дійсного `NPM_TOKEN` у
  середовищі `npm-release`, оскільки `npm dist-tag add` усе ще потребує звичайної npm
  автентифікації

## Послідовність stable npm-випуску

Під час створення stable npm-випуску:

1. Запустіть `OpenClaw NPM Release` з `preflight_only=true`
   - Поки тег ще не існує, ви можете використовувати поточний повний commit SHA `main` для
     лише валідаційного dry run workflow передрелізної перевірки
2. Виберіть `npm_dist_tag=beta` для звичайного beta-first потоку або `latest` лише
   коли ви свідомо хочете прямої stable-публікації
3. Запустіть `OpenClaw Release Checks` окремо з тим самим тегом або
   повним поточним commit SHA `main`, якщо вам потрібне live-покриття prompt cache
   - Це навмисно окремо, щоб live-покриття залишалося доступним без
     повторного зв’язування довгих або нестабільних перевірок з workflow публікації
4. Збережіть успішний `preflight_run_id`
5. Запустіть `OpenClaw NPM Release` знову з `preflight_only=false`, тим самим
   `tag`, тим самим `npm_dist_tag` і збереженим `preflight_run_id`
6. Якщо випуск потрапив у `beta`, пізніше запустіть `OpenClaw NPM Release` з
   тим самим stable `tag`, `promote_beta_to_latest=true`, `preflight_only=false`,
   порожнім `preflight_run_id` і `npm_dist_tag=beta`, коли ви захочете перемістити цю
   опубліковану збірку на `latest`
7. Якщо випуск було свідомо опубліковано безпосередньо в `latest` і `beta`
   має вказувати на ту саму stable-збірку, запустіть `OpenClaw NPM Release` з тим самим
   stable `tag`, `sync_stable_dist_tags=true`, `promote_beta_to_latest=false`,
   `preflight_only=false`, порожнім `preflight_run_id` і `npm_dist_tag=latest`

Режими просування та синхронізації dist-tag усе ще потребують схвалення середовища `npm-release`
і дійсного `NPM_TOKEN` у цьому середовищі.

Це зберігає і шлях прямої публікації, і beta-first шлях просування
задокументованими та видимими для операторів.

## Публічні посилання

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`.github/workflows/openclaw-release-checks.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-release-checks.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

Maintainers використовують приватну документацію з випусків у
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
для фактичного runbook.
