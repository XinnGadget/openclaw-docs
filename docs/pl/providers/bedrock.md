---
read_when:
    - Chcesz używać modeli Amazon Bedrock z OpenClaw
    - Potrzebujesz konfiguracji poświadczeń/regionu AWS do wywołań modeli
summary: Używaj modeli Amazon Bedrock (Converse API) z OpenClaw
title: Amazon Bedrock
x-i18n:
    generated_at: "2026-04-06T03:11:26Z"
    model: gpt-5.4
    provider: openai
    source_hash: 70bb29fe9199084b1179ced60935b5908318f5b80ced490bf44a45e0467c4929
    source_path: providers/bedrock.md
    workflow: 15
---

# Amazon Bedrock

OpenClaw może używać modeli **Amazon Bedrock** przez provider strumieniowy **Bedrock Converse**
z pi‑ai. Uwierzytelnianie Bedrock używa **domyślnego łańcucha poświadczeń AWS SDK**,
a nie klucza API.

## Co obsługuje pi-ai

- Provider: `amazon-bedrock`
- API: `bedrock-converse-stream`
- Auth: poświadczenia AWS (zmienne środowiskowe, współdzielona konfiguracja lub rola instancji)
- Region: `AWS_REGION` lub `AWS_DEFAULT_REGION` (domyślnie: `us-east-1`)

## Automatyczne wykrywanie modeli

OpenClaw może automatycznie wykrywać modele Bedrock, które obsługują **streaming**
i **wyjście tekstowe**. Wykrywanie używa `bedrock:ListFoundationModels` oraz
`bedrock:ListInferenceProfiles`, a wyniki są przechowywane w cache (domyślnie: 1 godzina).

Jak włączany jest niejawny provider:

- Jeśli `plugins.entries.amazon-bedrock.config.discovery.enabled` ma wartość `true`,
  OpenClaw spróbuje wykrywania nawet wtedy, gdy nie ma żadnego znacznika środowiskowego AWS.
- Jeśli `plugins.entries.amazon-bedrock.config.discovery.enabled` nie jest ustawione,
  OpenClaw automatycznie dodaje
  niejawnego providera Bedrock tylko wtedy, gdy widzi jeden z tych znaczników auth AWS:
  `AWS_BEARER_TOKEN_BEDROCK`, `AWS_ACCESS_KEY_ID` +
  `AWS_SECRET_ACCESS_KEY` lub `AWS_PROFILE`.
- Rzeczywista ścieżka auth Bedrock w runtime nadal używa domyślnego łańcucha AWS SDK, więc
  współdzielona konfiguracja, SSO oraz auth roli instancji IMDS mogą działać nawet wtedy, gdy wykrywanie
  wymagało ustawienia `enabled: true`, aby się włączyć.

Opcje konfiguracji znajdują się pod `plugins.entries.amazon-bedrock.config.discovery`:

```json5
{
  plugins: {
    entries: {
      "amazon-bedrock": {
        config: {
          discovery: {
            enabled: true,
            region: "us-east-1",
            providerFilter: ["anthropic", "amazon"],
            refreshInterval: 3600,
            defaultContextWindow: 32000,
            defaultMaxTokens: 4096,
          },
        },
      },
    },
  },
}
```

Uwagi:

- `enabled` domyślnie działa w trybie auto. W trybie auto OpenClaw włącza
  niejawnego providera Bedrock tylko wtedy, gdy widzi obsługiwany znacznik środowiskowy AWS.
- `region` domyślnie używa `AWS_REGION` lub `AWS_DEFAULT_REGION`, a następnie `us-east-1`.
- `providerFilter` dopasowuje nazwy providerów Bedrock (na przykład `anthropic`).
- `refreshInterval` podaje się w sekundach; ustaw `0`, aby wyłączyć cache.
- `defaultContextWindow` (domyślnie: `32000`) i `defaultMaxTokens` (domyślnie: `4096`)
  są używane dla wykrytych modeli (nadpisz je, jeśli znasz limity swojego modelu).
- Dla jawnych wpisów `models.providers["amazon-bedrock"]` OpenClaw nadal może
  wcześnie rozwiązać auth znaczników środowiskowych Bedrock z takich znaczników AWS jak
  `AWS_BEARER_TOKEN_BEDROCK`, bez wymuszania pełnego ładowania auth w runtime. Rzeczywista
  ścieżka auth dla wywołań modeli nadal używa domyślnego łańcucha AWS SDK.

## Onboarding

1. Upewnij się, że poświadczenia AWS są dostępne na **hoście gatewaya**:

```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
# Opcjonalnie:
export AWS_SESSION_TOKEN="..."
export AWS_PROFILE="your-profile"
# Opcjonalnie (klucz API/token bearer Bedrock):
export AWS_BEARER_TOKEN_BEDROCK="..."
```

2. Dodaj providera Bedrock i model do swojej konfiguracji (bez wymaganego `apiKey`):

```json5
{
  models: {
    providers: {
      "amazon-bedrock": {
        baseUrl: "https://bedrock-runtime.us-east-1.amazonaws.com",
        api: "bedrock-converse-stream",
        auth: "aws-sdk",
        models: [
          {
            id: "us.anthropic.claude-opus-4-6-v1:0",
            name: "Claude Opus 4.6 (Bedrock)",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "amazon-bedrock/us.anthropic.claude-opus-4-6-v1:0" },
    },
  },
}
```

## Role instancji EC2

Gdy OpenClaw działa na instancji EC2 z dołączoną rolą IAM, AWS SDK
może używać usługi metadanych instancji (IMDS) do uwierzytelniania. W przypadku wykrywania modeli Bedrock
OpenClaw automatycznie włącza niejawnego providera tylko na podstawie znaczników środowiskowych AWS,
chyba że jawnie ustawisz
`plugins.entries.amazon-bedrock.config.discovery.enabled: true`.

Zalecana konfiguracja dla hostów opartych na IMDS:

- Ustaw `plugins.entries.amazon-bedrock.config.discovery.enabled` na `true`.
- Ustaw `plugins.entries.amazon-bedrock.config.discovery.region` (lub wyeksportuj `AWS_REGION`).
- **Nie** potrzebujesz fałszywego klucza API.
- `AWS_PROFILE=default` potrzebujesz tylko wtedy, gdy chcesz mieć znacznik środowiskowy
  dla trybu auto lub powierzchni statusu.

```bash
# Zalecane: jawne włączenie wykrywania + region
openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1

# Opcjonalnie: dodaj znacznik środowiskowy, jeśli chcesz używać trybu auto bez jawnego włączenia
export AWS_PROFILE=default
export AWS_REGION=us-east-1
```

**Wymagane uprawnienia IAM** dla roli instancji EC2:

- `bedrock:InvokeModel`
- `bedrock:InvokeModelWithResponseStream`
- `bedrock:ListFoundationModels` (dla automatycznego wykrywania)
- `bedrock:ListInferenceProfiles` (dla wykrywania profili inferencyjnych)

Lub dołącz zarządzaną politykę `AmazonBedrockFullAccess`.

## Szybka konfiguracja (ścieżka AWS)

```bash
# 1. Utwórz rolę IAM i profil instancji
aws iam create-role --role-name EC2-Bedrock-Access \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

aws iam attach-role-policy --role-name EC2-Bedrock-Access \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

aws iam create-instance-profile --instance-profile-name EC2-Bedrock-Access
aws iam add-role-to-instance-profile \
  --instance-profile-name EC2-Bedrock-Access \
  --role-name EC2-Bedrock-Access

# 2. Dołącz do swojej instancji EC2
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxx \
  --iam-instance-profile Name=EC2-Bedrock-Access

# 3. Na instancji EC2 jawnie włącz wykrywanie
openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1

# 4. Opcjonalnie: dodaj znacznik środowiskowy, jeśli chcesz używać trybu auto bez jawnego włączenia
echo 'export AWS_PROFILE=default' >> ~/.bashrc
echo 'export AWS_REGION=us-east-1' >> ~/.bashrc
source ~/.bashrc

# 5. Zweryfikuj, że modele zostały wykryte
openclaw models list
```

## Profile inferencyjne

OpenClaw wykrywa **regionalne i globalne profile inferencyjne** obok
modeli foundation. Gdy profil mapuje się na znany model foundation,
profil dziedziczy możliwości tego modelu (okno kontekstu, maksymalna liczba tokenów,
reasoning, vision), a poprawny region żądania Bedrock jest wstrzykiwany
automatycznie. Oznacza to, że międzyregionalne profile Claude działają bez ręcznego
nadpisywania providera.

Identyfikatory profili inferencyjnych wyglądają jak `us.anthropic.claude-opus-4-6-v1:0` (regionalny)
lub `anthropic.claude-opus-4-6-v1:0` (globalny). Jeśli model bazowy jest już
obecny w wynikach wykrywania, profil dziedziczy pełny zestaw jego możliwości;
w przeciwnym razie stosowane są bezpieczne wartości domyślne.

Nie jest wymagana dodatkowa konfiguracja. Dopóki wykrywanie jest włączone, a podmiot IAM
ma uprawnienie `bedrock:ListInferenceProfiles`, profile pojawiają się obok
modeli foundation w `openclaw models list`.

## Uwagi

- Bedrock wymaga **włączonego dostępu do modeli** na Twoim koncie/regionie AWS.
- Automatyczne wykrywanie wymaga uprawnień `bedrock:ListFoundationModels` oraz
  `bedrock:ListInferenceProfiles`.
- Jeśli polegasz na trybie auto, ustaw jeden z obsługiwanych znaczników środowiskowych auth AWS na
  hoście gatewaya. Jeśli wolisz auth IMDS/współdzielonej konfiguracji bez znaczników środowiskowych, ustaw
  `plugins.entries.amazon-bedrock.config.discovery.enabled: true`.
- OpenClaw pokazuje źródło poświadczeń w tej kolejności: `AWS_BEARER_TOKEN_BEDROCK`,
  następnie `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`, potem `AWS_PROFILE`, a następnie
  domyślny łańcuch AWS SDK.
- Obsługa reasoning zależy od modelu; sprawdź kartę modelu Bedrock pod kątem
  bieżących możliwości.
- Jeśli wolisz zarządzany przepływ kluczy, możesz także umieścić zgodne z OpenAI
  proxy przed Bedrock i skonfigurować je zamiast tego jako providera OpenAI.

## Guardrails

Możesz stosować [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
do wszystkich wywołań modeli Bedrock, dodając obiekt `guardrail` do
konfiguracji pluginu `amazon-bedrock`. Guardrails pozwalają egzekwować filtrowanie treści,
blokowanie tematów, filtry słów, filtry informacji wrażliwych i kontrole
oparcia kontekstowego.

```json5
{
  plugins: {
    entries: {
      "amazon-bedrock": {
        config: {
          guardrail: {
            guardrailIdentifier: "abc123", // guardrail ID or full ARN
            guardrailVersion: "1", // version number or "DRAFT"
            streamProcessingMode: "sync", // optional: "sync" or "async"
            trace: "enabled", // optional: "enabled", "disabled", or "enabled_full"
          },
        },
      },
    },
  },
}
```

- `guardrailIdentifier` (wymagane) akceptuje identyfikator guardrail (np. `abc123`) lub
  pełny ARN (np. `arn:aws:bedrock:us-east-1:123456789012:guardrail/abc123`).
- `guardrailVersion` (wymagane) określa, której opublikowanej wersji użyć, albo
  `"DRAFT"` dla roboczej wersji.
- `streamProcessingMode` (opcjonalne) kontroluje, czy ocena guardrail działa
  synchronicznie (`"sync"`) czy asynchronicznie (`"async"`) podczas streamingu. Jeśli
  zostanie pominięte, Bedrock użyje swojego domyślnego zachowania.
- `trace` (opcjonalne) włącza ślad guardrail w odpowiedzi API. Ustaw na
  `"enabled"` lub `"enabled_full"` do debugowania; pomiń albo ustaw `"disabled"` w
  środowisku produkcyjnym.

Podmiot IAM używany przez gateway musi mieć uprawnienie `bedrock:ApplyGuardrail`
oprócz standardowych uprawnień wywołań.

## Embeddingi do wyszukiwania pamięci

Bedrock może również służyć jako provider embeddingów dla
[wyszukiwania pamięci](/pl/concepts/memory-search). To ustawia się osobno od
providera inferencji — ustaw `agents.defaults.memorySearch.provider` na `"bedrock"`:

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "bedrock",
        model: "amazon.titan-embed-text-v2:0", // default
      },
    },
  },
}
```

Embeddingi Bedrock używają tego samego łańcucha poświadczeń AWS SDK co inferencja (role
instancji, SSO, klucze dostępu, współdzielona konfiguracja i web identity). Klucz API nie
jest potrzebny. Gdy `provider` ma wartość `"auto"`, Bedrock jest wykrywany automatycznie, jeśli ten
łańcuch poświadczeń zostanie pomyślnie rozwiązany.

Obsługiwane modele embeddingów obejmują Amazon Titan Embed (v1, v2), Amazon Nova
Embed, Cohere Embed (v3, v4) oraz TwelveLabs Marengo. Zobacz
[Dokumentacja konfiguracji pamięci — Bedrock](/pl/reference/memory-config#bedrock-embedding-config),
aby uzyskać pełną listę modeli i opcji wymiarów.
