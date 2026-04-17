---
read_when:
    - Chcesz używać generowania wideo Runway w OpenClaw
    - Potrzebujesz konfiguracji klucza API/env Runway
    - Chcesz ustawić Runway jako domyślnego dostawcę wideo
summary: Konfiguracja generowania wideo Runway w OpenClaw
title: Runway
x-i18n:
    generated_at: "2026-04-12T23:33:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: fb9a2d26687920544222b0769f314743af245629fd45b7f456c0161a47476176
    source_path: providers/runway.md
    workflow: 15
---

# Runway

OpenClaw zawiera bundlowanego dostawcę `runway` do hostowanej generacji wideo.

| Właściwość   | Wartość                                                           |
| ------------ | ----------------------------------------------------------------- |
| Id dostawcy  | `runway`                                                          |
| Uwierzytelnianie | `RUNWAYML_API_SECRET` (kanoniczne) lub `RUNWAY_API_KEY`      |
| API          | Oparta na zadaniach generacja wideo Runway (odpytywanie `GET /v1/tasks/{id}`) |

## Pierwsze kroki

<Steps>
  <Step title="Ustaw klucz API">
    ```bash
    openclaw onboard --auth-choice runway-api-key
    ```
  </Step>
  <Step title="Ustaw Runway jako domyślnego dostawcę wideo">
    ```bash
    openclaw config set agents.defaults.videoGenerationModel.primary "runway/gen4.5"
    ```
  </Step>
  <Step title="Wygeneruj wideo">
    Poproś agenta o wygenerowanie wideo. Runway zostanie użyty automatycznie.
  </Step>
</Steps>

## Obsługiwane tryby

| Tryb           | Model              | Wejście referencyjne      |
| -------------- | ------------------ | ------------------------- |
| Tekst na wideo | `gen4.5` (domyślny) | Brak                     |
| Obraz na wideo | `gen4.5`           | 1 lokalny lub zdalny obraz |
| Wideo na wideo | `gen4_aleph`       | 1 lokalne lub zdalne wideo |

<Note>
Lokalne odwołania do obrazów i wideo są obsługiwane przez URI danych. Uruchomienia tylko tekstowe
obecnie udostępniają proporcje `16:9` i `9:16`.
</Note>

<Warning>
Wideo na wideo obecnie wymaga konkretnie `runway/gen4_aleph`.
</Warning>

## Konfiguracja

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "runway/gen4.5",
      },
    },
  },
}
```

## Uwagi zaawansowane

<AccordionGroup>
  <Accordion title="Aliasy zmiennych środowiskowych">
    OpenClaw rozpoznaje zarówno `RUNWAYML_API_SECRET` (kanoniczne), jak i `RUNWAY_API_KEY`.
    Dowolna z tych zmiennych uwierzytelni dostawcę Runway.
  </Accordion>

  <Accordion title="Odpytywanie zadań">
    Runway używa API opartego na zadaniach. Po wysłaniu żądania generowania OpenClaw
    odpytuje `GET /v1/tasks/{id}`, aż wideo będzie gotowe. Żadna dodatkowa
    konfiguracja zachowania odpytywania nie jest potrzebna.
  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Generowanie wideo" href="/pl/tools/video-generation" icon="video">
    Współdzielone parametry narzędzia, wybór dostawcy i zachowanie asynchroniczne.
  </Card>
  <Card title="Dokumentacja konfiguracji" href="/pl/gateway/configuration-reference#agent-defaults" icon="gear">
    Ustawienia domyślne agenta, w tym model generowania wideo.
  </Card>
</CardGroup>
