---
read_when:
    - Шукаю визначення публічних каналів релізів
    - Шукаю назви версій і частоту випусків
summary: Публічні канали релізів, назви версій і частота випусків
title: Політика випусків
x-i18n:
    generated_at: "2026-04-14T21:23:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: 88724307269ab783a9fbf8a0540fea198d8a3add68457f4e64d5707114fa518c
    source_path: reference/RELEASING.md
    workflow: 15
---

# Політика випусків

OpenClaw має три публічні гілки випусків:

- stable: теговані випуски, які за замовчуванням публікуються в npm `beta`, або в npm `latest`, якщо це явно запитано
- beta: prerelease-теги, які публікуються в npm `beta`
- dev: рухома голова `main`

## Назви версій

- Версія стабільного випуску: `YYYY.M.D`
  - Git-тег: `vYYYY.M.D`
- Версія стабільного виправлювального випуску: `YYYY.M.D-N`
  - Git-тег: `vYYYY.M.D-N`
- Версія бета-prerelease: `YYYY.M.D-beta.N`
  - Git-тег: `vYYYY.M.D-beta.N`
- Не додавайте нулі на початку місяця або дня
- `latest` означає поточний підвищений стабільний випуск npm
- `beta` означає поточну ціль встановлення бета-версії
- Стабільні та стабільні виправлювальні випуски за замовчуванням публікуються в npm `beta`; оператори випусків можуть явно націлити `latest` або пізніше підвищити перевірену бета-збірку
- Кожен випуск OpenClaw одночасно постачає npm-пакет і застосунок macOS

## Частота випусків

- Випуски спочатку проходять через beta
- Stable виходить лише після перевірки останньої beta
- Детальна процедура випуску, затвердження, облікові дані та примітки щодо відновлення
  доступні лише для супроводжувачів

## Передрелізна перевірка

- Запустіть `pnpm build && pnpm ui:build` перед `pnpm release:check`, щоб очікувані
  артефакти випуску `dist/*` і збірка Control UI були наявні для кроку
  перевірки pack
- Запускайте `pnpm release:check` перед кожним тегованим випуском
- Перевірки випуску тепер виконуються в окремому ручному workflow:
  `OpenClaw Release Checks`
- Кросплатформова перевірка встановлення, оновлення та виконання під час роботи dispatch-иться з
  приватного caller workflow
  `openclaw/releases-private/.github/workflows/openclaw-cross-os-release-checks.yml`,
  який викликає повторно використовуваний публічний workflow
  `.github/workflows/openclaw-cross-os-release-checks-reusable.yml`
- Цей поділ навмисний: зберігайте реальний шлях npm-випуску коротким,
  детермінованим і зосередженим на артефактах, тоді як повільніші live-перевірки залишаються у
  власній гілці, щоб не затримувати і не блокувати публікацію
- Перевірки випуску мають dispatch-итися з workflow ref `main`, щоб логіка
  workflow і секрети залишалися канонічними
- Цей workflow приймає або наявний тег випуску, або поточний повний
  40-символьний SHA коміту `main`
- У режимі commit-SHA він приймає лише поточний HEAD `origin/main`; використовуйте
  тег випуску для старіших комітів випуску
- Передрелізна перевірка лише для валідації `OpenClaw NPM Release` також приймає поточний
  повний 40-символьний SHA коміту `main` без вимоги наявності запушеного тега
- Цей шлях із SHA призначений лише для валідації й не може бути підвищений до реальної публікації
- У режимі SHA workflow синтезує `v<package.json version>` лише для
  перевірки метаданих пакета; реальна публікація все одно вимагає справжнього тега випуску
- Обидва workflow зберігають реальний шлях публікації та підвищення на GitHub-hosted
  runners, тоді як немутуючий шлях валідації може використовувати більші
  Blacksmith Linux runners
- Цей workflow запускає
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  з використанням секретів workflow `OPENAI_API_KEY` і `ANTHROPIC_API_KEY`
- Передрелізна перевірка npm-випуску більше не очікує на окрему гілку перевірок випуску
- Перед затвердженням запустіть `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  (або відповідний тег beta/correction)
- Після публікації в npm запустіть
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  (або відповідну версію beta/correction), щоб перевірити опублікований шлях
  встановлення з реєстру в новому тимчасовому префіксі
- Автоматизація випусків для супроводжувачів тепер використовує схему preflight-then-promote:
  - реальна публікація в npm має пройти успішний npm `preflight_run_id`
  - стабільні npm-випуски за замовчуванням націлюються на `beta`
  - стабільна npm-публікація може явно націлювати `latest` через вхід workflow
  - мутація npm dist-tag на основі токена тепер розміщена в
    `openclaw/releases-private/.github/workflows/openclaw-npm-dist-tags.yml`
    з міркувань безпеки, оскільки `npm dist-tag add` усе ще потребує `NPM_TOKEN`, тоді як
    публічний репозиторій зберігає OIDC-only публікацію
  - публічний `macOS Release` призначений лише для валідації
  - реальна приватна публікація mac має пройти успішні приватні mac
    `preflight_run_id` і `validate_run_id`
  - реальні шляхи публікації підвищують уже підготовлені артефакти замість повторної
    їх збірки
- Для стабільних виправлювальних випусків на кшталт `YYYY.M.D-N` post-publish verifier
  також перевіряє той самий шлях оновлення в тимчасовому префіксі з `YYYY.M.D` до `YYYY.M.D-N`,
  щоб виправлення випуску не могли непомітно залишити старіші глобальні встановлення на
  базовому стабільному payload
- Передрелізна перевірка npm-випуску завершується fail closed, якщо tarball не містить і
  `dist/control-ui/index.html`, і непорожній payload `dist/control-ui/assets/`,
  щоб ми знову не випустили порожню інформаційну панель браузера
- `pnpm test:install:smoke` також забезпечує бюджет `unpackedSize` npm pack для
  tarball-кандидата на оновлення, щоб installer e2e виявляв випадкове роздуття пакета
  до шляху публікації випуску
- Якщо робота над випуском зачіпала планування CI, маніфести часу виконання розширень або
  матриці тестів розширень, згенеруйте заново та перегляньте виходи матриці workflow
  `checks-node-extensions`, якими володіє planner, з `.github/workflows/ci.yml`
  перед затвердженням, щоб примітки до випуску не описували застарілу структуру CI
- Готовність стабільного випуску macOS також включає поверхні оновлювача:
  - GitHub-випуск має в підсумку містити запаковані `.zip`, `.dmg` і `.dSYM.zip`
  - `appcast.xml` у `main` після публікації має вказувати на новий стабільний zip
  - запакований застосунок має зберігати не-debug bundle id, непорожній Sparkle feed
    URL і `CFBundleVersion` на рівні або вище канонічного мінімального build floor Sparkle
    для цієї версії випуску

## Входи workflow NPM

`OpenClaw NPM Release` приймає такі вхідні параметри, керовані оператором:

- `tag`: обов’язковий тег випуску, наприклад `v2026.4.2`, `v2026.4.2-1` або
  `v2026.4.2-beta.1`; коли `preflight_only=true`, це також може бути поточний
  повний 40-символьний SHA коміту `main` для передрелізної перевірки лише для валідації
- `preflight_only`: `true` для лише валідації/збірки/пакування, `false` для
  реального шляху публікації
- `preflight_run_id`: обов’язковий на реальному шляху публікації, щоб workflow повторно використав
  підготовлений tarball з успішного запуску передрелізної перевірки
- `npm_dist_tag`: цільовий тег npm для шляху публікації; за замовчуванням `beta`

`OpenClaw Release Checks` приймає такі вхідні параметри, керовані оператором:

- `ref`: наявний тег випуску або поточний повний 40-символьний commit
  SHA `main` для валідації

Правила:

- Stable і correction-теги можуть публікуватися або в `beta`, або в `latest`
- Beta prerelease-теги можуть публікуватися лише в `beta`
- Повний commit SHA дозволений лише коли `preflight_only=true`
- Режим commit-SHA для перевірок випуску також вимагає поточний HEAD `origin/main`
- Реальний шлях публікації має використовувати той самий `npm_dist_tag`, що використовувався під час передрелізної перевірки;
  workflow перевіряє ці метадані перед продовженням публікації

## Послідовність стабільного npm-випуску

Під час створення стабільного npm-випуску:

1. Запустіть `OpenClaw NPM Release` з `preflight_only=true`
   - До появи тега ви можете використовувати поточний повний SHA коміту `main` для
     dry run передрелізного workflow лише для валідації
2. Оберіть `npm_dist_tag=beta` для звичайного beta-first потоку або `latest` лише
   коли ви свідомо хочете прямої стабільної публікації
3. Окремо запустіть `OpenClaw Release Checks` з тим самим тегом або
   повним поточним SHA `main`, якщо вам потрібне live-покриття prompt cache
   - Це навмисно винесено окремо, щоб live-покриття залишалося доступним без
     повторного зв’язування довгих або нестабільних перевірок із workflow публікації
4. Збережіть успішний `preflight_run_id`
5. Знову запустіть `OpenClaw NPM Release` з `preflight_only=false`, тим самим
   `tag`, тим самим `npm_dist_tag` і збереженим `preflight_run_id`
6. Якщо випуск потрапив у `beta`, використайте приватний workflow
   `openclaw/releases-private/.github/workflows/openclaw-npm-dist-tags.yml`,
   щоб підвищити цю стабільну версію з `beta` до `latest`
7. Якщо випуск було навмисно опубліковано безпосередньо в `latest`, і `beta`
   має одразу перейти на ту саму стабільну збірку, використайте той самий приватний
   workflow, щоб спрямувати обидва dist-tags на стабільну версію, або дозвольте його
   запланованій самовідновлюваній синхронізації перемістити `beta` пізніше

Мутація dist-tag розміщена в приватному репозиторії з міркувань безпеки, оскільки вона все ще
потребує `NPM_TOKEN`, тоді як публічний репозиторій зберігає OIDC-only публікацію.

Це зберігає як шлях прямої публікації, так і шлях beta-first підвищення
задокументованими та видимими для оператора.

## Публічні посилання

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`.github/workflows/openclaw-release-checks.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-release-checks.yml)
- [`.github/workflows/openclaw-cross-os-release-checks-reusable.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-cross-os-release-checks-reusable.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

Супроводжувачі використовують приватну документацію щодо випусків у
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
як фактичний runbook.
