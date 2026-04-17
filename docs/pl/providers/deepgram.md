---
read_when:
    - Chcesz używać Deepgram speech-to-text do załączników audio
    - Potrzebujesz szybkiego przykładu konfiguracji Deepgram
summary: Transkrypcja Deepgram dla przychodzących notatek głosowych
title: Deepgram
x-i18n:
    generated_at: "2026-04-12T23:30:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: 091523d6669e3d258f07c035ec756bd587299b6c7025520659232b1b2c1e21a5
    source_path: providers/deepgram.md
    workflow: 15
---

# Deepgram (Transkrypcja audio)

Deepgram to API speech-to-text. W OpenClaw jest używane do **transkrypcji przychodzącego audio/notatek głosowych** przez `tools.media.audio`.

Po włączeniu OpenClaw przesyła plik audio do Deepgram i wstrzykuje transkrypcję
do pipeline odpowiedzi (`{{Transcript}}` + blok `[Audio]`). To **nie jest streaming**;
używany jest endpoint transkrypcji nagrań wstępnie zarejestrowanych.

| Szczegół      | Wartość                                                    |
| ------------- | ---------------------------------------------------------- |
| Strona        | [deepgram.com](https://deepgram.com)                       |
| Dokumentacja  | [developers.deepgram.com](https://developers.deepgram.com) |
| Uwierzytelnianie | `DEEPGRAM_API_KEY`                                      |
| Model domyślny | `nova-3`                                                  |

## Pierwsze kroki

<Steps>
  <Step title="Ustaw klucz API">
    Dodaj klucz API Deepgram do środowiska:

    ```
    DEEPGRAM_API_KEY=dg_...
    ```

  </Step>
  <Step title="Włącz dostawcę audio">
    ```json5
    {
      tools: {
        media: {
          audio: {
            enabled: true,
            models: [{ provider: "deepgram", model: "nova-3" }],
          },
        },
      },
    }
    ```
  </Step>
  <Step title="Wyślij notatkę głosową">
    Wyślij wiadomość audio przez dowolny podłączony kanał. OpenClaw transkrybuje ją
    przez Deepgram i wstrzykuje transkrypcję do pipeline odpowiedzi.
  </Step>
</Steps>

## Opcje konfiguracji

| Opcja            | Ścieżka                                                      | Opis                                      |
| ---------------- | ------------------------------------------------------------ | ----------------------------------------- |
| `model`          | `tools.media.audio.models[].model`                           | ID modelu Deepgram (domyślnie: `nova-3`)  |
| `language`       | `tools.media.audio.models[].language`                        | Wskazówka języka (opcjonalnie)            |
| `detect_language` | `tools.media.audio.providerOptions.deepgram.detect_language` | Włącza wykrywanie języka (opcjonalnie)    |
| `punctuate`      | `tools.media.audio.providerOptions.deepgram.punctuate`       | Włącza interpunkcję (opcjonalnie)         |
| `smart_format`   | `tools.media.audio.providerOptions.deepgram.smart_format`    | Włącza inteligentne formatowanie (opcjonalnie) |

<Tabs>
  <Tab title="Ze wskazówką języka">
    ```json5
    {
      tools: {
        media: {
          audio: {
            enabled: true,
            models: [{ provider: "deepgram", model: "nova-3", language: "en" }],
          },
        },
      },
    }
    ```
  </Tab>
  <Tab title="Z opcjami Deepgram">
    ```json5
    {
      tools: {
        media: {
          audio: {
            enabled: true,
            providerOptions: {
              deepgram: {
                detect_language: true,
                punctuate: true,
                smart_format: true,
              },
            },
            models: [{ provider: "deepgram", model: "nova-3" }],
          },
        },
      },
    }
    ```
  </Tab>
</Tabs>

## Uwagi

<AccordionGroup>
  <Accordion title="Uwierzytelnianie">
    Uwierzytelnianie przebiega według standardowej kolejności dostawców. `DEEPGRAM_API_KEY` to
    najprostsza ścieżka.
  </Accordion>
  <Accordion title="Proxy i niestandardowe endpointy">
    Nadpisz endpointy lub nagłówki za pomocą `tools.media.audio.baseUrl` i
    `tools.media.audio.headers`, gdy używasz proxy.
  </Accordion>
  <Accordion title="Zachowanie wyjścia">
    Wyjście podlega tym samym zasadom audio co u innych dostawców (limity rozmiaru, timeouty,
    wstrzykiwanie transkrypcji).
  </Accordion>
</AccordionGroup>

<Note>
Transkrypcja Deepgram działa **tylko dla nagrań wstępnie zarejestrowanych** (nie dla streamingu w czasie rzeczywistym). OpenClaw
przesyła cały plik audio i czeka na pełną transkrypcję, zanim wstrzyknie
ją do rozmowy.
</Note>

## Powiązane

<CardGroup cols={2}>
  <Card title="Narzędzia mediów" href="/tools/media" icon="photo-film">
    Przegląd pipeline przetwarzania audio, obrazów i wideo.
  </Card>
  <Card title="Konfiguracja" href="/pl/gateway/configuration" icon="gear">
    Pełna referencja konfiguracji, w tym ustawienia narzędzi mediów.
  </Card>
  <Card title="Rozwiązywanie problemów" href="/pl/help/troubleshooting" icon="wrench">
    Typowe problemy i kroki debugowania.
  </Card>
  <Card title="FAQ" href="/pl/help/faq" icon="circle-question">
    Najczęściej zadawane pytania dotyczące konfiguracji OpenClaw.
  </Card>
</CardGroup>
