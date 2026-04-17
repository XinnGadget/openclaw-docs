---
read_when:
    - Chcesz używać generowania multimediów Vydra w OpenClaw
    - Potrzebujesz wskazówek dotyczących konfiguracji klucza API Vydra
summary: Używaj obrazów, wideo i mowy Vydra w OpenClaw
title: Vydra
x-i18n:
    generated_at: "2026-04-12T23:33:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: ab623d14b656ce0b68d648a6393fcee3bb880077d6583e0d5c1012e91757f20e
    source_path: providers/vydra.md
    workflow: 15
---

# Vydra

Bundlowany Plugin Vydra dodaje:

- Generowanie obrazów przez `vydra/grok-imagine`
- Generowanie wideo przez `vydra/veo3` i `vydra/kling`
- Syntezę mowy przez trasę TTS Vydra opartą na ElevenLabs

OpenClaw używa tego samego `VYDRA_API_KEY` dla wszystkich trzech możliwości.

<Warning>
Używaj `https://www.vydra.ai/api/v1` jako bazowego URL-a.

Główny host Vydra (`https://vydra.ai/api/v1`) obecnie przekierowuje do `www`. Niektóre klienty HTTP usuwają `Authorization` przy takim przekierowaniu między hostami, co zamienia prawidłowy klucz API w mylący błąd uwierzytelniania. Bundlowany Plugin używa bezpośrednio bazowego URL-a `www`, aby tego uniknąć.
</Warning>

## Konfiguracja

<Steps>
  <Step title="Uruchom interaktywny onboarding">
    ```bash
    openclaw onboard --auth-choice vydra-api-key
    ```

    Lub ustaw bezpośrednio zmienną env:

    ```bash
    export VYDRA_API_KEY="vydra_live_..."
    ```

  </Step>
  <Step title="Wybierz domyślną możliwość">
    Wybierz jedną lub więcej z poniższych możliwości (obraz, wideo lub mowa) i zastosuj pasującą konfigurację.
  </Step>
</Steps>

## Możliwości

<AccordionGroup>
  <Accordion title="Generowanie obrazów">
    Domyślny model obrazu:

    - `vydra/grok-imagine`

    Ustaw go jako domyślnego dostawcę obrazów:

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

    Obecne wsparcie bundlowane obejmuje tylko tekst na obraz. Hostowane trasy edycji Vydra oczekują zdalnych URL-i obrazów, a OpenClaw nie dodaje jeszcze mostu wysyłania specyficznego dla Vydra w bundlowanym Pluginie.

    <Note>
    Zobacz [Generowanie obrazów](/pl/tools/image-generation), aby poznać współdzielone parametry narzędzia, wybór dostawcy i zachowanie failover.
    </Note>

  </Accordion>

  <Accordion title="Generowanie wideo">
    Zarejestrowane modele wideo:

    - `vydra/veo3` dla tekstu na wideo
    - `vydra/kling` dla obrazu na wideo

    Ustaw Vydra jako domyślnego dostawcę wideo:

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

    Uwagi:

    - `vydra/veo3` jest bundlowany wyłącznie jako tekst na wideo.
    - `vydra/kling` obecnie wymaga odwołania do zdalnego URL-a obrazu. Wysyłanie lokalnych plików jest odrzucane z góry.
    - Obecna trasa HTTP `kling` w Vydra bywa niespójna w kwestii tego, czy wymaga `image_url`, czy `video_url`; bundlowany dostawca mapuje ten sam zdalny URL obrazu do obu pól.
    - Bundlowany Plugin pozostaje zachowawczy i nie przekazuje nieudokumentowanych ustawień stylu, takich jak proporcje, rozdzielczość, znak wodny czy wygenerowane audio.

    <Note>
    Zobacz [Generowanie wideo](/pl/tools/video-generation), aby poznać współdzielone parametry narzędzia, wybór dostawcy i zachowanie failover.
    </Note>

  </Accordion>

  <Accordion title="Testy live wideo">
    Pokrycie live specyficzne dla dostawcy:

    ```bash
    OPENCLAW_LIVE_TEST=1 \
    OPENCLAW_LIVE_VYDRA_VIDEO=1 \
    pnpm test:live -- extensions/vydra/vydra.live.test.ts
    ```

    Bundlowany plik live Vydra obejmuje teraz:

    - `vydra/veo3` tekst na wideo
    - `vydra/kling` obraz na wideo z użyciem zdalnego URL-a obrazu

    W razie potrzeby nadpisz fixture zdalnego obrazu:

    ```bash
    export OPENCLAW_LIVE_VYDRA_KLING_IMAGE_URL="https://example.com/reference.png"
    ```

  </Accordion>

  <Accordion title="Synteza mowy">
    Ustaw Vydra jako dostawcę mowy:

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

    Ustawienia domyślne:

    - Model: `elevenlabs/tts`
    - Id głosu: `21m00Tcm4TlvDq8ikWAM`

    Bundlowany Plugin obecnie udostępnia jeden sprawdzony domyślny głos i zwraca pliki audio MP3.

  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Katalog dostawców" href="/pl/providers/index" icon="list">
    Przeglądaj wszystkich dostępnych dostawców.
  </Card>
  <Card title="Generowanie obrazów" href="/pl/tools/image-generation" icon="image">
    Współdzielone parametry narzędzia obrazów i wybór dostawcy.
  </Card>
  <Card title="Generowanie wideo" href="/pl/tools/video-generation" icon="video">
    Współdzielone parametry narzędzia wideo i wybór dostawcy.
  </Card>
  <Card title="Dokumentacja konfiguracji" href="/pl/gateway/configuration-reference#agent-defaults" icon="gear">
    Ustawienia domyślne agenta i konfiguracja modelu.
  </Card>
</CardGroup>
