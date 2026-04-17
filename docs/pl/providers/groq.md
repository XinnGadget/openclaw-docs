---
read_when:
    - Chcesz używać Groq z OpenClaw
    - Potrzebujesz zmiennej env klucza API albo wyboru auth w CLI
summary: Konfiguracja Groq (auth + wybór modelu)
title: Groq
x-i18n:
    generated_at: "2026-04-12T23:31:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: 613289efc36fedd002e1ebf9366e0e7119ea1f9e14a1dae773b90ea57100baee
    source_path: providers/groq.md
    workflow: 15
---

# Groq

[Groq](https://groq.com) zapewnia ultraszybkie wnioskowanie na modelach open source
(Llama, Gemma, Mistral i innych) z użyciem niestandardowego sprzętu LPU. OpenClaw łączy się
z Groq przez jego API zgodne z OpenAI.

| Właściwość | Wartość           |
| ---------- | ----------------- |
| Dostawca   | `groq`            |
| Auth       | `GROQ_API_KEY`    |
| API        | zgodne z OpenAI   |

## Pierwsze kroki

<Steps>
  <Step title="Pobierz klucz API">
    Utwórz klucz API na stronie [console.groq.com/keys](https://console.groq.com/keys).
  </Step>
  <Step title="Ustaw klucz API">
    ```bash
    export GROQ_API_KEY="gsk_..."
    ```
  </Step>
  <Step title="Ustaw model domyślny">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "groq/llama-3.3-70b-versatile" },
        },
      },
    }
    ```
  </Step>
</Steps>

### Przykład pliku konfiguracji

```json5
{
  env: { GROQ_API_KEY: "gsk_..." },
  agents: {
    defaults: {
      model: { primary: "groq/llama-3.3-70b-versatile" },
    },
  },
}
```

## Dostępne modele

Katalog modeli Groq często się zmienia. Uruchom `openclaw models list | grep groq`,
aby zobaczyć aktualnie dostępne modele, albo sprawdź
[console.groq.com/docs/models](https://console.groq.com/docs/models).

| Model                         | Uwagi                              |
| ----------------------------- | ---------------------------------- |
| **Llama 3.3 70B Versatile**   | Ogólnego przeznaczenia, duży kontekst |
| **Llama 3.1 8B Instant**      | Szybki, lekki                      |
| **Gemma 2 9B**                | Kompaktowy, wydajny                |
| **Mixtral 8x7B**              | Architektura MoE, dobre rozumowanie |

<Tip>
Użyj `openclaw models list --provider groq`, aby uzyskać najbardziej aktualną listę
modeli dostępnych na Twoim koncie.
</Tip>

## Transkrypcja audio

Groq zapewnia także szybką transkrypcję audio opartą na Whisper. Gdy jest skonfigurowany jako
dostawca media-understanding, OpenClaw używa modelu Groq `whisper-large-v3-turbo`
do transkrypcji wiadomości głosowych przez wspólną powierzchnię `tools.media.audio`.

```json5
{
  tools: {
    media: {
      audio: {
        models: [{ provider: "groq" }],
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Szczegóły transkrypcji audio">
    | Właściwość | Wartość |
    |----------|-------|
    | Wspólna ścieżka konfiguracji | `tools.media.audio` |
    | Domyślny adres URL bazowy    | `https://api.groq.com/openai/v1` |
    | Model domyślny               | `whisper-large-v3-turbo` |
    | Endpoint API                 | zgodny z OpenAI `/audio/transcriptions` |
  </Accordion>

  <Accordion title="Uwaga dotycząca środowiska">
    Jeśli Gateway działa jako demon (launchd/systemd), upewnij się, że `GROQ_API_KEY` jest
    dostępny dla tego procesu (na przykład w `~/.openclaw/.env` albo przez
    `env.shellEnv`).

    <Warning>
    Klucze ustawione tylko w interaktywnej powłoce nie są widoczne dla procesów
    Gateway zarządzanych przez demona. Aby zapewnić trwałą dostępność, użyj `~/.openclaw/.env` albo konfiguracji `env.shellEnv`.
    </Warning>

  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, odwołań do modeli i zachowania failover.
  </Card>
  <Card title="Informacje o konfiguracji" href="/pl/gateway/configuration-reference" icon="gear">
    Pełny schemat konfiguracji, w tym ustawienia dostawcy i audio.
  </Card>
  <Card title="Konsola Groq" href="https://console.groq.com" icon="arrow-up-right-from-square">
    Panel Groq, dokumentacja API i ceny.
  </Card>
  <Card title="Lista modeli Groq" href="https://console.groq.com/docs/models" icon="list">
    Oficjalny katalog modeli Groq.
  </Card>
</CardGroup>
