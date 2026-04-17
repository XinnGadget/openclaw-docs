---
read_when:
    - Chcesz używać Chutes z OpenClaw
    - Potrzebujesz ścieżki konfiguracji OAuth lub klucza API
    - Chcesz poznać model domyślny, aliasy lub zachowanie wykrywania modeli
summary: Konfiguracja Chutes (OAuth lub klucz API, wykrywanie modeli, aliasy)
title: Chutes
x-i18n:
    generated_at: "2026-04-12T23:29:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: 07c52b1d1d2792412e6daabc92df5310434b3520116d9e0fd2ad26bfa5297e1c
    source_path: providers/chutes.md
    workflow: 15
---

# Chutes

[Chutes](https://chutes.ai) udostępnia katalogi modeli open source przez API
zgodne z OpenAI. OpenClaw obsługuje zarówno OAuth w przeglądarce, jak i
bezpośrednie uwierzytelnianie kluczem API dla dołączonego dostawcy `chutes`.

| Właściwość | Wartość                    |
| ---------- | -------------------------- |
| Dostawca   | `chutes`                   |
| API        | zgodne z OpenAI            |
| Bazowy URL | `https://llm.chutes.ai/v1` |
| Uwierzytelnianie | OAuth lub klucz API (zobacz poniżej) |

## Pierwsze kroki

<Tabs>
  <Tab title="OAuth">
    <Steps>
      <Step title="Uruchom przepływ onboarding OAuth">
        ```bash
        openclaw onboard --auth-choice chutes
        ```
        OpenClaw uruchamia lokalnie przepływ w przeglądarce albo pokazuje URL + przepływ
        wklejenia przekierowania na hostach zdalnych lub bezgłowych. Tokeny OAuth są automatycznie
        odświeżane przez profile uwierzytelniania OpenClaw.
      </Step>
      <Step title="Zweryfikuj model domyślny">
        Po onboardingu model domyślny jest ustawiany na
        `chutes/zai-org/GLM-4.7-TEE`, a dołączony katalog Chutes zostaje
        zarejestrowany.
      </Step>
    </Steps>
  </Tab>
  <Tab title="Klucz API">
    <Steps>
      <Step title="Pobierz klucz API">
        Utwórz klucz na
        [chutes.ai/settings/api-keys](https://chutes.ai/settings/api-keys).
      </Step>
      <Step title="Uruchom przepływ onboarding klucza API">
        ```bash
        openclaw onboard --auth-choice chutes-api-key
        ```
      </Step>
      <Step title="Zweryfikuj model domyślny">
        Po onboardingu model domyślny jest ustawiany na
        `chutes/zai-org/GLM-4.7-TEE`, a dołączony katalog Chutes zostaje
        zarejestrowany.
      </Step>
    </Steps>
  </Tab>
</Tabs>

<Note>
Obie ścieżki uwierzytelniania rejestrują dołączony katalog Chutes i ustawiają model domyślny na
`chutes/zai-org/GLM-4.7-TEE`. Zmienne środowiskowe runtime: `CHUTES_API_KEY`,
`CHUTES_OAUTH_TOKEN`.
</Note>

## Zachowanie wykrywania

Gdy uwierzytelnianie Chutes jest dostępne, OpenClaw odpytuje katalog Chutes przy użyciu
tych poświadczeń i korzysta z wykrytych modeli. Jeśli wykrywanie się nie powiedzie, OpenClaw
przechodzi do dołączonego statycznego katalogu zapasowego, dzięki czemu onboarding i uruchamianie
nadal działają.

## Domyślne aliasy

OpenClaw rejestruje trzy wygodne aliasy dla dołączonego katalogu Chutes:

| Alias           | Model docelowy                                        |
| --------------- | ----------------------------------------------------- |
| `chutes-fast`   | `chutes/zai-org/GLM-4.7-FP8`                          |
| `chutes-pro`    | `chutes/deepseek-ai/DeepSeek-V3.2-TEE`                |
| `chutes-vision` | `chutes/chutesai/Mistral-Small-3.2-24B-Instruct-2506` |

## Wbudowany katalog startowy

Dołączony katalog zapasowy obejmuje bieżące referencje Chutes:

| Ref modelu                                            |
| ----------------------------------------------------- |
| `chutes/zai-org/GLM-4.7-TEE`                          |
| `chutes/zai-org/GLM-5-TEE`                            |
| `chutes/deepseek-ai/DeepSeek-V3.2-TEE`                |
| `chutes/deepseek-ai/DeepSeek-R1-0528-TEE`             |
| `chutes/moonshotai/Kimi-K2.5-TEE`                     |
| `chutes/chutesai/Mistral-Small-3.2-24B-Instruct-2506` |
| `chutes/Qwen/Qwen3-Coder-Next-TEE`                    |
| `chutes/openai/gpt-oss-120b-TEE`                      |

## Przykład konfiguracji

```json5
{
  agents: {
    defaults: {
      model: { primary: "chutes/zai-org/GLM-4.7-TEE" },
      models: {
        "chutes/zai-org/GLM-4.7-TEE": { alias: "Chutes GLM 4.7" },
        "chutes/deepseek-ai/DeepSeek-V3.2-TEE": { alias: "Chutes DeepSeek V3.2" },
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Nadpisania OAuth">
    Możesz dostosować przepływ OAuth za pomocą opcjonalnych zmiennych środowiskowych:

    | Zmienna | Cel |
    | -------- | ------- |
    | `CHUTES_CLIENT_ID` | Niestandardowy identyfikator klienta OAuth |
    | `CHUTES_CLIENT_SECRET` | Niestandardowy sekret klienta OAuth |
    | `CHUTES_OAUTH_REDIRECT_URI` | Niestandardowy URI przekierowania |
    | `CHUTES_OAUTH_SCOPES` | Niestandardowe zakresy OAuth |

    Zobacz [dokumentację OAuth Chutes](https://chutes.ai/docs/sign-in-with-chutes/overview),
    aby poznać wymagania dotyczące aplikacji przekierowującej i uzyskać pomoc.

  </Accordion>

  <Accordion title="Uwagi">
    - Wykrywanie przy użyciu klucza API i OAuth używa tego samego identyfikatora dostawcy `chutes`.
    - Modele Chutes są rejestrowane jako `chutes/<model-id>`.
    - Jeśli wykrywanie nie powiedzie się przy uruchamianiu, dołączony statyczny katalog jest używany automatycznie.
  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Dostawcy modeli" href="/pl/concepts/model-providers" icon="layers">
    Reguły dostawców, referencje modeli i zachowanie failover.
  </Card>
  <Card title="Dokumentacja konfiguracji" href="/pl/gateway/configuration-reference" icon="gear">
    Pełny schemat konfiguracji, w tym ustawienia dostawców.
  </Card>
  <Card title="Chutes" href="https://chutes.ai" icon="arrow-up-right-from-square">
    Panel Chutes i dokumentacja API.
  </Card>
  <Card title="Klucze API Chutes" href="https://chutes.ai/settings/api-keys" icon="key">
    Tworzenie i zarządzanie kluczami API Chutes.
  </Card>
</CardGroup>
