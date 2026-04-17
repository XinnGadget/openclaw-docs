---
read_when:
    - Chcesz używać hostowanych modeli OSS Bedrock Mantle z OpenClaw
    - Potrzebujesz zgodnego z OpenAI endpointu Mantle dla GPT-OSS, Qwen, Kimi lub GLM
summary: Używaj modeli Amazon Bedrock Mantle (zgodnych z OpenAI) z OpenClaw
title: Amazon Bedrock Mantle
x-i18n:
    generated_at: "2026-04-12T23:29:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: 27e602b6f6a3ae92427de135cb9df6356e0daaea6b6fe54723a7542dd0d5d21e
    source_path: providers/bedrock-mantle.md
    workflow: 15
---

# Amazon Bedrock Mantle

OpenClaw zawiera dołączonego dostawcę **Amazon Bedrock Mantle**, który łączy się z
kompatybilnym z OpenAI endpointem Mantle. Mantle hostuje modele open source i
zewnętrzne (GPT-OSS, Qwen, Kimi, GLM i podobne) przez standardową
powierzchnię ` /v1/chat/completions` opartą na infrastrukturze Bedrock.

| Właściwość    | Wartość                                                                            |
| ------------- | ---------------------------------------------------------------------------------- |
| Identyfikator dostawcy | `amazon-bedrock-mantle`                                                  |
| API           | `openai-completions` (zgodne z OpenAI)                                             |
| Uwierzytelnianie | Jawny `AWS_BEARER_TOKEN_BEDROCK` lub generowanie bearer tokenu z łańcucha poświadczeń IAM |
| Domyślny region | `us-east-1` (nadpisz przez `AWS_REGION` lub `AWS_DEFAULT_REGION`)               |

## Pierwsze kroki

Wybierz preferowaną metodę uwierzytelniania i wykonaj kroki konfiguracji.

<Tabs>
  <Tab title="Jawny bearer token">
    **Najlepsze dla:** środowisk, w których masz już bearer token Mantle.

    <Steps>
      <Step title="Ustaw bearer token na hoście Gateway">
        ```bash
        export AWS_BEARER_TOKEN_BEDROCK="..."
        ```

        Opcjonalnie ustaw region (domyślnie `us-east-1`):

        ```bash
        export AWS_REGION="us-west-2"
        ```
      </Step>
      <Step title="Sprawdź, czy modele są wykrywane">
        ```bash
        openclaw models list
        ```

        Wykryte modele pojawiają się pod dostawcą `amazon-bedrock-mantle`. Nie jest
        wymagana dodatkowa konfiguracja, chyba że chcesz nadpisać ustawienia domyślne.
      </Step>
    </Steps>

  </Tab>

  <Tab title="Poświadczenia IAM">
    **Najlepsze dla:** używania poświadczeń zgodnych z AWS SDK (współdzielona konfiguracja, SSO, tożsamość webowa, role instancji lub zadań).

    <Steps>
      <Step title="Skonfiguruj poświadczenia AWS na hoście Gateway">
        Działa dowolne źródło uwierzytelniania zgodne z AWS SDK:

        ```bash
        export AWS_PROFILE="default"
        export AWS_REGION="us-west-2"
        ```
      </Step>
      <Step title="Sprawdź, czy modele są wykrywane">
        ```bash
        openclaw models list
        ```

        OpenClaw automatycznie generuje bearer token Mantle z łańcucha poświadczeń.
      </Step>
    </Steps>

    <Tip>
    Gdy `AWS_BEARER_TOKEN_BEDROCK` nie jest ustawione, OpenClaw sam generuje bearer token z domyślnego łańcucha poświadczeń AWS, w tym współdzielonych profili poświadczeń/konfiguracji, SSO, tożsamości webowej oraz ról instancji lub zadań.
    </Tip>

  </Tab>
</Tabs>

## Automatyczne wykrywanie modeli

Gdy `AWS_BEARER_TOKEN_BEDROCK` jest ustawione, OpenClaw używa go bezpośrednio. W przeciwnym razie
OpenClaw próbuje wygenerować bearer token Mantle z domyślnego
łańcucha poświadczeń AWS. Następnie wykrywa dostępne modele Mantle, wysyłając zapytanie do
endpointu `/v1/models` dla danego regionu.

| Zachowanie       | Szczegóły                  |
| ---------------- | -------------------------- |
| Pamięć podręczna wykrywania | Wyniki buforowane przez 1 godzinę |
| Odświeżanie tokenu IAM | Co godzinę             |

<Note>
Bearer token to ten sam `AWS_BEARER_TOKEN_BEDROCK`, którego używa standardowy dostawca [Amazon Bedrock](/pl/providers/bedrock).
</Note>

### Obsługiwane regiony

`us-east-1`, `us-east-2`, `us-west-2`, `ap-northeast-1`,
`ap-south-1`, `ap-southeast-3`, `eu-central-1`, `eu-west-1`, `eu-west-2`,
`eu-south-1`, `eu-north-1`, `sa-east-1`.

## Konfiguracja ręczna

Jeśli wolisz jawną konfigurację zamiast automatycznego wykrywania:

```json5
{
  models: {
    providers: {
      "amazon-bedrock-mantle": {
        baseUrl: "https://bedrock-mantle.us-east-1.api.aws/v1",
        api: "openai-completions",
        auth: "api-key",
        apiKey: "env:AWS_BEARER_TOKEN_BEDROCK",
        models: [
          {
            id: "gpt-oss-120b",
            name: "GPT-OSS 120B",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 32000,
            maxTokens: 4096,
          },
        ],
      },
    },
  },
}
```

## Uwagi zaawansowane

<AccordionGroup>
  <Accordion title="Obsługa rozumowania">
    Obsługa rozumowania jest wywnioskowana z identyfikatorów modeli zawierających wzorce takie jak
    `thinking`, `reasoner` lub `gpt-oss-120b`. OpenClaw automatycznie ustawia `reasoning: true`
    dla pasujących modeli podczas wykrywania.
  </Accordion>

  <Accordion title="Niedostępność endpointu">
    Jeśli endpoint Mantle jest niedostępny lub nie zwraca modeli, dostawca jest
    po cichu pomijany. OpenClaw nie zgłasza błędu; inni skonfigurowani dostawcy
    nadal działają normalnie.
  </Accordion>

  <Accordion title="Relacja z dostawcą Amazon Bedrock">
    Bedrock Mantle to oddzielny dostawca względem standardowego
    dostawcy [Amazon Bedrock](/pl/providers/bedrock). Mantle używa
    kompatybilnej z OpenAI powierzchni `/v1`, podczas gdy standardowy dostawca Bedrock używa
    natywnego API Bedrock.

    Obaj dostawcy współdzielą te same poświadczenia `AWS_BEARER_TOKEN_BEDROCK`, gdy
    są dostępne.

  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Amazon Bedrock" href="/pl/providers/bedrock" icon="cloud">
    Natywny dostawca Bedrock dla Anthropic Claude, Titan i innych modeli.
  </Card>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, odwołań do modeli i zachowania failover.
  </Card>
  <Card title="OAuth i uwierzytelnianie" href="/pl/gateway/authentication" icon="key">
    Szczegóły uwierzytelniania i zasady ponownego użycia poświadczeń.
  </Card>
  <Card title="Rozwiązywanie problemów" href="/pl/help/troubleshooting" icon="wrench">
    Typowe problemy i sposoby ich rozwiązania.
  </Card>
</CardGroup>
