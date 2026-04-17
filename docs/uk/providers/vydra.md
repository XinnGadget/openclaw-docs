---
read_when:
    - Ви хочете генерацію медіа Vydra в OpenClaw
    - Вам потрібні вказівки щодо налаштування API-ключа Vydra
summary: Використовуйте зображення, відео та мовлення Vydra в OpenClaw
title: Vydra
x-i18n:
    generated_at: "2026-04-12T10:19:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: ab623d14b656ce0b68d648a6393fcee3bb880077d6583e0d5c1012e91757f20e
    source_path: providers/vydra.md
    workflow: 15
---

# Vydra

Вбудований Plugin Vydra додає:

- Генерацію зображень через `vydra/grok-imagine`
- Генерацію відео через `vydra/veo3` і `vydra/kling`
- Синтез мовлення через TTS-маршрут Vydra на базі ElevenLabs

OpenClaw використовує той самий `VYDRA_API_KEY` для всіх трьох можливостей.

<Warning>
Використовуйте `https://www.vydra.ai/api/v1` як базову URL-адресу.

Базовий хост Vydra (`https://vydra.ai/api/v1`) наразі перенаправляє на `www`. Деякі HTTP-клієнти скидають `Authorization` під час такого міжхостового перенаправлення, через що дійсний API-ключ перетворюється на оманливу помилку автентифікації. Щоб уникнути цього, вбудований Plugin безпосередньо використовує базову URL-адресу `www`.
</Warning>

## Налаштування

<Steps>
  <Step title="Запустіть інтерактивне початкове налаштування">
    ```bash
    openclaw onboard --auth-choice vydra-api-key
    ```

    Або встановіть змінну середовища напряму:

    ```bash
    export VYDRA_API_KEY="vydra_live_..."
    ```

  </Step>
  <Step title="Виберіть можливість за замовчуванням">
    Виберіть одну або кілька наведених нижче можливостей (зображення, відео або мовлення) і застосуйте відповідну конфігурацію.
  </Step>
</Steps>

## Можливості

<AccordionGroup>
  <Accordion title="Генерація зображень">
    Типова модель зображень:

    - `vydra/grok-imagine`

    Зробіть її типовим постачальником зображень:

    ```json5
    {
      agents: {
        defaults: {
          imageGenerationModel: {
            primary: "vydra/grok-imagine",
          },
        },
      },
    }
    ```

    Поточна вбудована підтримка охоплює лише text-to-image. Розміщені в Vydra маршрути редагування очікують віддалені URL-адреси зображень, а OpenClaw поки що не додає у вбудованому Plugin Vydra-специфічний міст для завантаження.

    <Note>
    Див. [Генерація зображень](/uk/tools/image-generation), щоб дізнатися про спільні параметри інструмента, вибір постачальника та поведінку резервного перемикання.
    </Note>

  </Accordion>

  <Accordion title="Генерація відео">
    Зареєстровані моделі відео:

    - `vydra/veo3` для text-to-video
    - `vydra/kling` для image-to-video

    Зробіть Vydra типовим постачальником відео:

    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "vydra/veo3",
          },
        },
      },
    }
    ```

    Примітки:

    - `vydra/veo3` у вбудованому варіанті підтримується лише як text-to-video.
    - `vydra/kling` наразі вимагає посилання на віддалену URL-адресу зображення. Завантаження локальних файлів відхиляються одразу.
    - Поточний HTTP-маршрут `kling` у Vydra поводиться непослідовно щодо того, чи вимагає він `image_url` або `video_url`; вбудований постачальник зіставляє ту саму віддалену URL-адресу зображення з обома полями.
    - Вбудований Plugin дотримується консервативного підходу і не передає недокументовані параметри стилю, як-от співвідношення сторін, роздільна здатність, водяний знак або згенероване аудіо.

    <Note>
    Див. [Генерація відео](/uk/tools/video-generation), щоб дізнатися про спільні параметри інструмента, вибір постачальника та поведінку резервного перемикання.
    </Note>

  </Accordion>

  <Accordion title="Live-тести відео">
    Спеціальне live-покриття для постачальника:

    ```bash
    OPENCLAW_LIVE_TEST=1 \
    OPENCLAW_LIVE_VYDRA_VIDEO=1 \
    pnpm test:live -- extensions/vydra/vydra.live.test.ts
    ```

    Вбудований live-файл Vydra тепер охоплює:

    - `vydra/veo3` text-to-video
    - `vydra/kling` image-to-video з використанням віддаленої URL-адреси зображення

    За потреби перевизначте віддалений фікстур зображення:

    ```bash
    export OPENCLAW_LIVE_VYDRA_KLING_IMAGE_URL="https://example.com/reference.png"
    ```

  </Accordion>

  <Accordion title="Синтез мовлення">
    Задайте Vydra як постачальника мовлення:

    ```json5
    {
      messages: {
        tts: {
          provider: "vydra",
          providers: {
            vydra: {
              apiKey: "${VYDRA_API_KEY}",
              voiceId: "21m00Tcm4TlvDq8ikWAM",
            },
          },
        },
      },
    }
    ```

    Типові значення:

    - Модель: `elevenlabs/tts`
    - ID голосу: `21m00Tcm4TlvDq8ikWAM`

    Вбудований Plugin наразі надає один перевірений типовий голос і повертає аудіофайли MP3.

  </Accordion>
</AccordionGroup>

## Пов’язане

<CardGroup cols={2}>
  <Card title="Каталог постачальників" href="/uk/providers/index" icon="list">
    Перегляньте всіх доступних постачальників.
  </Card>
  <Card title="Генерація зображень" href="/uk/tools/image-generation" icon="image">
    Спільні параметри інструмента зображень і вибір постачальника.
  </Card>
  <Card title="Генерація відео" href="/uk/tools/video-generation" icon="video">
    Спільні параметри інструмента відео і вибір постачальника.
  </Card>
  <Card title="Довідник із конфігурації" href="/uk/gateway/configuration-reference#agent-defaults" icon="gear">
    Типові значення агентів і конфігурація моделей.
  </Card>
</CardGroup>
