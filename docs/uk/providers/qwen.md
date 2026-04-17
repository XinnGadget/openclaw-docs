---
read_when:
    - Ви хочете використовувати Qwen з OpenClaw
    - Раніше ви використовували Qwen OAuth
summary: Використовуйте Qwen Cloud через вбудований провайдер qwen OpenClaw
title: Qwen
x-i18n:
    generated_at: "2026-04-12T11:08:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5247f851ef891645df6572d748ea15deeea47cd1d75858bc0d044a2930065106
    source_path: providers/qwen.md
    workflow: 15
---

# Qwen

<Warning>

**Qwen OAuth було видалено.** Безкоштовна OAuth-інтеграція
(`qwen-portal`), яка використовувала ендпоїнти `portal.qwen.ai`, більше недоступна.
Див. [Issue #49557](https://github.com/openclaw/openclaw/issues/49557) для
контексту.

</Warning>

OpenClaw тепер розглядає Qwen як вбудованого провайдера першого класу з канонічним id
`qwen`. Вбудований провайдер орієнтується на ендпоїнти Qwen Cloud / Alibaba DashScope та
Coding Plan і зберігає роботу застарілих id `modelstudio` як псевдоніма сумісності.

- Провайдер: `qwen`
- Бажана змінна середовища: `QWEN_API_KEY`
- Також приймаються для сумісності: `MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY`
- Стиль API: сумісний з OpenAI

<Tip>
Якщо ви хочете використовувати `qwen3.6-plus`, віддайте перевагу ендпоїнту **Standard (оплата за використання)**.
Підтримка Coding Plan може відставати від публічного каталогу.
</Tip>

## Початок роботи

Виберіть тип плану та виконайте кроки налаштування.

<Tabs>
  <Tab title="Coding Plan (підписка)">
    **Найкраще для:** доступу за підпискою через Qwen Coding Plan.

    <Steps>
      <Step title="Отримайте свій API-ключ">
        Створіть або скопіюйте API-ключ із [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys).
      </Step>
      <Step title="Запустіть онбординг">
        Для ендпоїнта **Global**:

        ```bash
        openclaw onboard --auth-choice qwen-api-key
        ```

        Для ендпоїнта **China**:

        ```bash
        openclaw onboard --auth-choice qwen-api-key-cn
        ```
      </Step>
      <Step title="Установіть модель за замовчуванням">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "qwen/qwen3.5-plus" },
            },
          },
        }
        ```
      </Step>
      <Step title="Перевірте, що модель доступна">
        ```bash
        openclaw models list --provider qwen
        ```
      </Step>
    </Steps>

    <Note>
    Застарілі id `modelstudio-*` для auth-choice і посилання на моделі `modelstudio/...` усе ще
    працюють як псевдоніми сумісності, але нові сценарії налаштування мають використовувати канонічні
    id auth-choice `qwen-*` і посилання на моделі `qwen/...`.
    </Note>

  </Tab>

  <Tab title="Standard (оплата за використання)">
    **Найкраще для:** доступу з оплатою за використання через ендпоїнт Standard Model Studio, включно з моделями на кшталт `qwen3.6-plus`, які можуть бути недоступні в Coding Plan.

    <Steps>
      <Step title="Отримайте свій API-ключ">
        Створіть або скопіюйте API-ключ із [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys).
      </Step>
      <Step title="Запустіть онбординг">
        Для ендпоїнта **Global**:

        ```bash
        openclaw onboard --auth-choice qwen-standard-api-key
        ```

        Для ендпоїнта **China**:

        ```bash
        openclaw onboard --auth-choice qwen-standard-api-key-cn
        ```
      </Step>
      <Step title="Установіть модель за замовчуванням">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "qwen/qwen3.5-plus" },
            },
          },
        }
        ```
      </Step>
      <Step title="Перевірте, що модель доступна">
        ```bash
        openclaw models list --provider qwen
        ```
      </Step>
    </Steps>

    <Note>
    Застарілі id `modelstudio-*` для auth-choice і посилання на моделі `modelstudio/...` усе ще
    працюють як псевдоніми сумісності, але нові сценарії налаштування мають використовувати канонічні
    id auth-choice `qwen-*` і посилання на моделі `qwen/...`.
    </Note>

  </Tab>
</Tabs>

## Типи планів та ендпоїнти

| План                       | Регіон | Auth choice                | Ендпоїнт                                         |
| -------------------------- | ------ | -------------------------- | ------------------------------------------------ |
| Standard (оплата за використання)   | China  | `qwen-standard-api-key-cn` | `dashscope.aliyuncs.com/compatible-mode/v1`      |
| Standard (оплата за використання)   | Global | `qwen-standard-api-key`    | `dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Coding Plan (підписка) | China  | `qwen-api-key-cn`          | `coding.dashscope.aliyuncs.com/v1`               |
| Coding Plan (підписка) | Global | `qwen-api-key`             | `coding-intl.dashscope.aliyuncs.com/v1`          |

Провайдер автоматично вибирає ендпоїнт на основі вашого auth choice. Канонічні
варіанти використовують сімейство `qwen-*`; `modelstudio-*` лишається лише для сумісності.
Ви можете перевизначити це за допомогою власного `baseUrl` у конфігурації.

<Tip>
**Керування ключами:** [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys) |
**Документація:** [docs.qwencloud.com](https://docs.qwencloud.com/developer-guides/getting-started/introduction)
</Tip>

## Вбудований каталог

Наразі OpenClaw постачається з таким вбудованим каталогом Qwen. Налаштований каталог
враховує ендпоїнт: конфігурації Coding Plan не включають моделі, які, як відомо, працюють
лише на ендпоїнті Standard.

| Посилання на модель         | Вхідні дані | Контекст  | Примітки                                           |
| --------------------------- | ----------- | --------- | -------------------------------------------------- |
| `qwen/qwen3.5-plus`         | text, image | 1,000,000 | Модель за замовчуванням                            |
| `qwen/qwen3.6-plus`         | text, image | 1,000,000 | Віддавайте перевагу ендпоїнтам Standard, коли вам потрібна ця модель |
| `qwen/qwen3-max-2026-01-23` | text        | 262,144   | Лінійка Qwen Max                                   |
| `qwen/qwen3-coder-next`     | text        | 262,144   | Кодування                                          |
| `qwen/qwen3-coder-plus`     | text        | 1,000,000 | Кодування                                          |
| `qwen/MiniMax-M2.5`         | text        | 1,000,000 | Reasoning увімкнено                               |
| `qwen/glm-5`                | text        | 202,752   | GLM                                                |
| `qwen/glm-4.7`              | text        | 202,752   | GLM                                                |
| `qwen/kimi-k2.5`            | text, image | 262,144   | Moonshot AI через Alibaba                          |

<Note>
Доступність усе ще може відрізнятися залежно від ендпоїнта та тарифного плану, навіть якщо модель
присутня у вбудованому каталозі.
</Note>

## Мультимодальні доповнення

Розширення `qwen` також надає мультимодальні можливості на ендпоїнтах **Standard**
DashScope (не на ендпоїнтах Coding Plan):

- **Розуміння відео** через `qwen-vl-max-latest`
- **Генерація відео Wan** через `wan2.6-t2v` (за замовчуванням), `wan2.6-i2v`, `wan2.6-r2v`, `wan2.6-r2v-flash`, `wan2.7-r2v`

Щоб використовувати Qwen як провайдера відео за замовчуванням:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "qwen/wan2.6-t2v" },
    },
  },
}
```

<Note>
Див. [Генерація відео](/uk/tools/video-generation) для спільних параметрів інструмента, вибору провайдера та поведінки failover.
</Note>

## Додатково

<AccordionGroup>
  <Accordion title="Розуміння зображень і відео">
    Вбудований Plugin Qwen реєструє розуміння медіа для зображень і відео
    на ендпоїнтах **Standard** DashScope (не на ендпоїнтах Coding Plan).

    | Властивість      | Значення              |
    | ------------- | --------------------- |
    | Модель         | `qwen-vl-max-latest`  |
    | Підтримуваний вхід | Зображення, відео  |

    Розуміння медіа автоматично визначається з налаштованої автентифікації Qwen —
    додаткова конфігурація не потрібна. Переконайтеся, що ви використовуєте ендпоїнт
    Standard (оплата за використання) для підтримки розуміння медіа.

  </Accordion>

  <Accordion title="Доступність Qwen 3.6 Plus">
    `qwen3.6-plus` доступна на ендпоїнтах Standard (оплата за використання) Model Studio:

    - China: `dashscope.aliyuncs.com/compatible-mode/v1`
    - Global: `dashscope-intl.aliyuncs.com/compatible-mode/v1`

    Якщо ендпоїнти Coding Plan повертають помилку "unsupported model" для
    `qwen3.6-plus`, перейдіть на Standard (оплата за використання) замість пари
    ендпоїнт/ключ Coding Plan.

  </Accordion>

  <Accordion title="План можливостей">
    Розширення `qwen` позиціонується як основний вендорський дім для всієї поверхні Qwen
    Cloud, а не лише для моделей кодування/тексту.

    - **Текстові/chat-моделі:** уже вбудовано
    - **Виклик інструментів, структурований вивід, thinking:** успадковано від OpenAI-сумісного транспорту
    - **Генерація зображень:** заплановано на рівні provider-plugin
    - **Розуміння зображень/відео:** уже вбудовано на ендпоїнті Standard
    - **Мовлення/аудіо:** заплановано на рівні provider-plugin
    - **Ембеддинги пам’яті/reranking:** заплановано через поверхню адаптера ембеддингів
    - **Генерація відео:** уже вбудовано через спільну можливість генерації відео

  </Accordion>

  <Accordion title="Деталі генерації відео">
    Для генерації відео OpenClaw зіставляє налаштований регіон Qwen з відповідним
    хостом DashScope AIGC перед відправленням завдання:

    - Global/Intl: `https://dashscope-intl.aliyuncs.com`
    - China: `https://dashscope.aliyuncs.com`

    Це означає, що звичайний `models.providers.qwen.baseUrl`, який указує на хости
    Qwen Coding Plan або Standard, усе одно зберігає генерацію відео на правильному
    регіональному відеоендпоїнті DashScope.

    Поточні обмеження вбудованої генерації відео Qwen:

    - До **1** вихідного відео на запит
    - До **1** вхідного зображення
    - До **4** вхідних відео
    - Тривалість до **10 секунд**
    - Підтримує `size`, `aspectRatio`, `resolution`, `audio` і `watermark`
    - Режим еталонного зображення/відео наразі вимагає **віддалені URL-адреси http(s)**. Локальні
      шляхи до файлів відхиляються одразу, оскільки відеоендпоїнт DashScope не
      приймає завантажені локальні буфери для цих посилань.

  </Accordion>

  <Accordion title="Сумісність використання потокової передачі">
    Власні ендпоїнти Model Studio оголошують сумісність використання потокової передачі на
    спільному транспорті `openai-completions`. OpenClaw тепер визначає це за можливостями ендпоїнта,
    тому сумісні з DashScope кастомні id провайдерів, що вказують на ті самі нативні хости,
    успадковують таку саму поведінку використання потокової передачі замість того,
    щоб вимагати саме вбудований id провайдера `qwen`.

    Сумісність нативного потокового використання застосовується як до хостів Coding Plan,
    так і до сумісних хостів Standard DashScope:

    - `https://coding.dashscope.aliyuncs.com/v1`
    - `https://coding-intl.dashscope.aliyuncs.com/v1`
    - `https://dashscope.aliyuncs.com/compatible-mode/v1`
    - `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

  </Accordion>

  <Accordion title="Регіони мультимодальних ендпоїнтів">
    Мультимодальні поверхні (розуміння відео та генерація відео Wan) використовують
    ендпоїнти **Standard** DashScope, а не ендпоїнти Coding Plan:

    - Базовий URL Global/Intl Standard: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
    - Базовий URL China Standard: `https://dashscope.aliyuncs.com/compatible-mode/v1`

  </Accordion>

  <Accordion title="Налаштування середовища та демона">
    Якщо Gateway працює як демон (launchd/systemd), переконайтеся, що `QWEN_API_KEY`
    доступний цьому процесу (наприклад, у `~/.openclaw/.env` або через
    `env.shellEnv`).
  </Accordion>
</AccordionGroup>

## Пов’язане

<CardGroup cols={2}>
  <Card title="Вибір моделі" href="/uk/concepts/model-providers" icon="layers">
    Вибір провайдерів, посилань на моделі та поведінки failover.
  </Card>
  <Card title="Генерація відео" href="/uk/tools/video-generation" icon="video">
    Спільні параметри відеоінструмента та вибір провайдера.
  </Card>
  <Card title="Alibaba (ModelStudio)" href="/uk/providers/alibaba" icon="cloud">
    Застарілий провайдер ModelStudio та примітки щодо міграції.
  </Card>
  <Card title="Усунення несправностей" href="/uk/help/troubleshooting" icon="wrench">
    Загальне усунення несправностей і поширені запитання.
  </Card>
</CardGroup>
