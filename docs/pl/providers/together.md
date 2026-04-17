---
read_when:
    - Chcesz używać Together AI z OpenClaw
    - Potrzebujesz zmiennej środowiskowej z kluczem API albo opcji uwierzytelniania w CLI
summary: Konfiguracja Together AI (uwierzytelnianie + wybór modelu)
title: Together AI
x-i18n:
    generated_at: "2026-04-12T23:33:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: 33531a1646443ac2e46ee1fbfbb60ec71093611b022618106e8e5435641680ac
    source_path: providers/together.md
    workflow: 15
---

# Together AI

[Together AI](https://together.ai) zapewnia dostęp do czołowych modeli
open-source, w tym Llama, DeepSeek, Kimi i innych, przez ujednolicone API.

| Właściwość | Wartość                      |
| ---------- | ---------------------------- |
| Dostawca   | `together`                   |
| Uwierzytelnianie | `TOGETHER_API_KEY`     |
| API        | Zgodne z OpenAI              |
| Bazowy URL | `https://api.together.xyz/v1` |

## Pierwsze kroki

<Steps>
  <Step title="Pobierz klucz API">
    Utwórz klucz API na
    [api.together.ai/settings/api-keys](https://api.together.ai/settings/api-keys).
  </Step>
  <Step title="Uruchom onboarding">
    ```bash
    openclaw onboard --auth-choice together-api-key
    ```
  </Step>
  <Step title="Ustaw model domyślny">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "together/moonshotai/Kimi-K2.5" },
        },
      },
    }
    ```
  </Step>
</Steps>

### Przykład nieinteraktywny

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice together-api-key \
  --together-api-key "$TOGETHER_API_KEY"
```

<Note>
Preset onboardingu ustawia `together/moonshotai/Kimi-K2.5` jako model
domyślny.
</Note>

## Wbudowany katalog

OpenClaw zawiera ten dołączony katalog Together:

| Odwołanie modelu                                           | Nazwa                                  | Wejście     | Kontekst   | Uwagi                            |
| ---------------------------------------------------------- | -------------------------------------- | ----------- | ---------- | -------------------------------- |
| `together/moonshotai/Kimi-K2.5`                            | Kimi K2.5                              | text, image | 262,144    | Model domyślny; reasoning włączone |
| `together/zai-org/GLM-4.7`                                 | GLM 4.7 Fp8                            | text        | 202,752    | Model tekstowy ogólnego przeznaczenia |
| `together/meta-llama/Llama-3.3-70B-Instruct-Turbo`         | Llama 3.3 70B Instruct Turbo           | text        | 131,072    | Szybki model instrukcyjny        |
| `together/meta-llama/Llama-4-Scout-17B-16E-Instruct`       | Llama 4 Scout 17B 16E Instruct         | text, image | 10,000,000 | Multimodalny                     |
| `together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | Llama 4 Maverick 17B 128E Instruct FP8 | text, image | 20,000,000 | Multimodalny                     |
| `together/deepseek-ai/DeepSeek-V3.1`                       | DeepSeek V3.1                          | text        | 131,072    | Ogólny model tekstowy            |
| `together/deepseek-ai/DeepSeek-R1`                         | DeepSeek R1                            | text        | 131,072    | Model reasoning                  |
| `together/moonshotai/Kimi-K2-Instruct-0905`                | Kimi K2-Instruct 0905                  | text        | 262,144    | Dodatkowy model tekstowy Kimi    |

## Generowanie wideo

Dołączony Plugin `together` rejestruje również generowanie wideo przez
współdzielone narzędzie `video_generate`.

| Właściwość          | Wartość                              |
| ------------------- | ------------------------------------ |
| Domyślny model wideo| `together/Wan-AI/Wan2.2-T2V-A14B`    |
| Tryby               | tekst na wideo, referencja pojedynczego obrazu |
| Obsługiwane parametry | `aspectRatio`, `resolution`        |

Aby używać Together jako domyślnego dostawcy wideo:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "together/Wan-AI/Wan2.2-T2V-A14B",
      },
    },
  },
}
```

<Tip>
Zobacz [Generowanie wideo](/pl/tools/video-generation), aby poznać wspólne parametry narzędzia,
wybór dostawcy i zachowanie failover.
</Tip>

<AccordionGroup>
  <Accordion title="Uwaga o środowisku">
    Jeśli Gateway działa jako demon (launchd/systemd), upewnij się, że
    `TOGETHER_API_KEY` jest dostępne dla tego procesu (na przykład w
    `~/.openclaw/.env` albo przez `env.shellEnv`).

    <Warning>
    Klucze ustawione tylko w Twojej interaktywnej powłoce nie są widoczne dla
    procesów gateway zarządzanych przez demona. Użyj `~/.openclaw/.env` albo konfiguracji `env.shellEnv`, aby
    zapewnić trwałą dostępność.
    </Warning>

  </Accordion>

  <Accordion title="Rozwiązywanie problemów">
    - Sprawdź, czy Twój klucz działa: `openclaw models list --provider together`
    - Jeśli modele się nie pojawiają, potwierdź, że klucz API jest ustawiony we właściwym
      środowisku dla procesu Gateway.
    - Odwołania do modeli mają postać `together/<model-id>`.
  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Dostawcy modeli" href="/pl/concepts/model-providers" icon="layers">
    Zasady dostawców, odwołania do modeli i zachowanie failover.
  </Card>
  <Card title="Generowanie wideo" href="/pl/tools/video-generation" icon="video">
    Wspólne parametry narzędzia generowania wideo i wybór dostawcy.
  </Card>
  <Card title="Referencja konfiguracji" href="/pl/gateway/configuration-reference" icon="gear">
    Pełny schemat konfiguracji, w tym ustawienia dostawców.
  </Card>
  <Card title="Together AI" href="https://together.ai" icon="arrow-up-right-from-square">
    Dashboard Together AI, dokumentacja API i cennik.
  </Card>
</CardGroup>
