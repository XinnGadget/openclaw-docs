---
read_when:
    - Chcesz używać hostowanych przez Bedrock Mantle modeli OSS z OpenClaw
    - Potrzebujesz endpointu Mantle zgodnego z OpenAI dla GPT-OSS, Qwen, Kimi lub GLM
summary: Używaj modeli Amazon Bedrock Mantle (zgodnych z OpenAI) z OpenClaw
title: Amazon Bedrock Mantle
x-i18n:
    generated_at: "2026-04-06T03:10:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4e5b33ede4067fb7de02a046f3e375cbd2af4bf68e7751c8dd687447f1a78c86
    source_path: providers/bedrock-mantle.md
    workflow: 15
---

# Amazon Bedrock Mantle

OpenClaw zawiera wbudowanego providera **Amazon Bedrock Mantle**, który łączy się z
endpointem Mantle zgodnym z OpenAI. Mantle hostuje modele open source i
zewnętrzne (GPT-OSS, Qwen, Kimi, GLM i podobne) przez standardową
powierzchnię `/v1/chat/completions` opartą na infrastrukturze Bedrock.

## Co obsługuje OpenClaw

- Provider: `amazon-bedrock-mantle`
- API: `openai-completions` (zgodne z OpenAI)
- Auth: jawny `AWS_BEARER_TOKEN_BEDROCK` lub generowanie bearer tokena z łańcucha poświadczeń IAM
- Region: `AWS_REGION` lub `AWS_DEFAULT_REGION` (domyślnie: `us-east-1`)

## Automatyczne wykrywanie modeli

Gdy ustawiono `AWS_BEARER_TOKEN_BEDROCK`, OpenClaw używa go bezpośrednio. W przeciwnym razie
OpenClaw próbuje wygenerować bearer token Mantle z domyślnego
łańcucha poświadczeń AWS, w tym współdzielonych profili credentials/config, SSO, web
identity oraz ról instancji lub zadań. Następnie wykrywa dostępne modele Mantle
przez odpytywanie endpointu `/v1/models` dla danego regionu. Wyniki wykrywania są
przechowywane w cache przez 1 godzinę, a bearery tokeny pochodzące z IAM są odświeżane co godzinę.

Obsługiwane regiony: `us-east-1`, `us-east-2`, `us-west-2`, `ap-northeast-1`,
`ap-south-1`, `ap-southeast-3`, `eu-central-1`, `eu-west-1`, `eu-west-2`,
`eu-south-1`, `eu-north-1`, `sa-east-1`.

## Onboarding

1. Wybierz jedną ścieżkę auth na **hoście gatewaya**:

Jawny bearer token:

```bash
export AWS_BEARER_TOKEN_BEDROCK="..."
# Opcjonalnie (domyślnie `us-east-1`):
export AWS_REGION="us-west-2"
```

Poświadczenia IAM:

```bash
# Działa tutaj dowolne źródło auth zgodne z AWS SDK, na przykład:
export AWS_PROFILE="default"
export AWS_REGION="us-west-2"
```

2. Zweryfikuj, że modele zostały wykryte:

```bash
openclaw models list
```

Wykryte modele pojawią się pod providerem `amazon-bedrock-mantle`. Nie jest
wymagana dodatkowa konfiguracja, chyba że chcesz nadpisać wartości domyślne.

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

## Uwagi

- OpenClaw może wygenerować bearer token Mantle za Ciebie z poświadczeń IAM
  zgodnych z AWS SDK, gdy `AWS_BEARER_TOKEN_BEDROCK` nie jest ustawiony.
- Bearer token to ten sam `AWS_BEARER_TOKEN_BEDROCK`, którego używa standardowy
  provider [Amazon Bedrock](/pl/providers/bedrock).
- Obsługa reasoning jest wywnioskowana z identyfikatorów modeli zawierających wzorce takie jak
  `thinking`, `reasoner` lub `gpt-oss-120b`.
- Jeśli endpoint Mantle jest niedostępny lub nie zwraca modeli, provider jest
  pomijany bezgłośnie.
