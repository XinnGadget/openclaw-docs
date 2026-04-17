---
read_when:
    - Chcesz używać generowania wideo Alibaba Wan w OpenClaw
    - Potrzebujesz konfiguracji klucza API Model Studio lub DashScope do generowania wideo
summary: Generowanie wideo Wan w Alibaba Model Studio w OpenClaw
title: Alibaba Model Studio
x-i18n:
    generated_at: "2026-04-12T23:28:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: a6e97d929952cdba7740f5ab3f6d85c18286b05596a4137bf80bbc8b54f32662
    source_path: providers/alibaba.md
    workflow: 15
---

# Alibaba Model Studio

OpenClaw zawiera dołączonego dostawcę generowania wideo `alibaba` dla modeli Wan w Alibaba Model Studio / DashScope.

- Dostawca: `alibaba`
- Preferowane uwierzytelnianie: `MODELSTUDIO_API_KEY`
- Akceptowane również: `DASHSCOPE_API_KEY`, `QWEN_API_KEY`
- API: asynchroniczne generowanie wideo DashScope / Model Studio

## Pierwsze kroki

<Steps>
  <Step title="Ustaw klucz API">
    ```bash
    openclaw onboard --auth-choice qwen-standard-api-key
    ```
  </Step>
  <Step title="Ustaw domyślny model generowania wideo">
    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "alibaba/wan2.6-t2v",
          },
        },
      },
    }
    ```
  </Step>
  <Step title="Sprawdź, czy dostawca jest dostępny">
    ```bash
    openclaw models list --provider alibaba
    ```
  </Step>
</Steps>

<Note>
Każdy z akceptowanych kluczy uwierzytelniających (`MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY`, `QWEN_API_KEY`) będzie działać. Opcja onboardingu `qwen-standard-api-key` konfiguruje współdzielone poświadczenie DashScope.
</Note>

## Wbudowane modele Wan

Dołączony dostawca `alibaba` obecnie rejestruje:

| Odwołanie modelu          | Tryb                      |
| ------------------------- | ------------------------- |
| `alibaba/wan2.6-t2v`      | Tekst na wideo            |
| `alibaba/wan2.6-i2v`      | Obraz na wideo            |
| `alibaba/wan2.6-r2v`      | Referencja na wideo       |
| `alibaba/wan2.6-r2v-flash`| Referencja na wideo (szybko) |
| `alibaba/wan2.7-r2v`      | Referencja na wideo       |

## Obecne ograniczenia

| Parametr              | Limit                                                     |
| --------------------- | --------------------------------------------------------- |
| Wyjściowe wideo       | Maksymalnie **1** na żądanie                              |
| Obrazy wejściowe      | Maksymalnie **1**                                         |
| Wejściowe wideo       | Maksymalnie **4**                                         |
| Czas trwania          | Maksymalnie **10 sekund**                                 |
| Obsługiwane kontrolki | `size`, `aspectRatio`, `resolution`, `audio`, `watermark` |
| Obraz/wideo referencyjne | Tylko zdalne adresy URL `http(s)`                      |

<Warning>
Tryb obrazu/wideo referencyjnego obecnie wymaga **zdalnych adresów URL `http(s)`**. Lokalne ścieżki plików nie są obsługiwane dla wejść referencyjnych.
</Warning>

## Konfiguracja zaawansowana

<AccordionGroup>
  <Accordion title="Relacja do Qwen">
    Dołączony dostawca `qwen` również używa hostowanych przez Alibaba endpointów DashScope do generowania wideo Wan. Użyj:

    - `qwen/...`, gdy chcesz korzystać z kanonicznej powierzchni dostawcy Qwen
    - `alibaba/...`, gdy chcesz korzystać z bezpośredniej, należącej do dostawcy powierzchni wideo Wan

    Więcej szczegółów znajdziesz w [dokumentacji dostawcy Qwen](/pl/providers/qwen).

  </Accordion>

  <Accordion title="Priorytet kluczy uwierzytelniających">
    OpenClaw sprawdza klucze uwierzytelniające w tej kolejności:

    1. `MODELSTUDIO_API_KEY` (preferowany)
    2. `DASHSCOPE_API_KEY`
    3. `QWEN_API_KEY`

    Każdy z nich uwierzytelni dostawcę `alibaba`.

  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Generowanie wideo" href="/pl/tools/video-generation" icon="video">
    Współdzielone parametry narzędzia wideo i wybór dostawcy.
  </Card>
  <Card title="Qwen" href="/pl/providers/qwen" icon="microchip">
    Konfiguracja dostawcy Qwen i integracja z DashScope.
  </Card>
  <Card title="Referencja konfiguracji" href="/pl/gateway/configuration-reference#agent-defaults" icon="gear">
    Domyślne ustawienia agenta i konfiguracja modeli.
  </Card>
</CardGroup>
