---
read_when:
    - Chcesz używać modeli Amazon Bedrock z OpenClaw
    - Potrzebujesz konfiguracji poświadczeń AWS i regionu do wywołań modeli
summary: Używaj modeli Amazon Bedrock (Converse API) z OpenClaw
title: Amazon Bedrock
x-i18n:
    generated_at: "2026-04-12T23:29:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: 88e7e24907ec26af098b648e2eeca32add090a9e381c818693169ab80aeccc47
    source_path: providers/bedrock.md
    workflow: 15
---

# Amazon Bedrock

OpenClaw może używać modeli **Amazon Bedrock** przez dostawcę strumieniowego **Bedrock Converse** z pi-ai. Uwierzytelnianie Bedrock używa **domyślnego łańcucha poświadczeń AWS SDK**, a nie klucza API.

| Właściwość | Wartość                                                      |
| ---------- | ------------------------------------------------------------ |
| Dostawca   | `amazon-bedrock`                                             |
| API        | `bedrock-converse-stream`                                    |
| Uwierzytelnianie | Poświadczenia AWS (zmienne środowiskowe, współdzielona konfiguracja lub rola instancji) |
| Region     | `AWS_REGION` lub `AWS_DEFAULT_REGION` (domyślnie: `us-east-1`) |

## Pierwsze kroki

Wybierz preferowaną metodę uwierzytelniania i wykonaj kroki konfiguracji.

<Tabs>
  <Tab title="Klucze dostępu / zmienne środowiskowe">
    **Najlepsze do:** maszyn deweloperskich, CI lub hostów, na których bezpośrednio zarządzasz poświadczeniami AWS.

    <Steps>
      <Step title="Ustaw poświadczenia AWS na hoście Gateway">
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
      </Step>
      <Step title="Dodaj dostawcę Bedrock i model do swojej konfiguracji">
        `apiKey` nie jest wymagany. Skonfiguruj dostawcę z `auth: "aws-sdk"`:

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
      </Step>
      <Step title="Sprawdź, czy modele są dostępne">
        ```bash
        openclaw models list
        ```
      </Step>
    </Steps>

    <Tip>
    Przy uwierzytelnianiu opartym na znacznikach środowiskowych (`AWS_ACCESS_KEY_ID`, `AWS_PROFILE` lub `AWS_BEARER_TOKEN_BEDROCK`) OpenClaw automatycznie włącza niejawnnego dostawcę Bedrock do wykrywania modeli bez dodatkowej konfiguracji.
    </Tip>

  </Tab>

  <Tab title="Role instancji EC2 (IMDS)">
    **Najlepsze do:** instancji EC2 z przypisaną rolą IAM, używających usługi metadanych instancji do uwierzytelniania.

    <Steps>
      <Step title="Włącz wykrywanie jawnie">
        Przy korzystaniu z IMDS OpenClaw nie może wykryć uwierzytelniania AWS tylko na podstawie znaczników środowiskowych, więc musisz jawnie się zapisać:

        ```bash
        openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
        openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1
        ```
      </Step>
      <Step title="Opcjonalnie dodaj znacznik środowiskowy dla trybu auto">
        Jeśli chcesz też, aby działała ścieżka automatycznego wykrywania oparta na znacznikach środowiskowych (na przykład dla powierzchni `openclaw status`):

        ```bash
        export AWS_PROFILE=default
        export AWS_REGION=us-east-1
        ```

        Nie potrzebujesz fałszywego klucza API.
      </Step>
      <Step title="Sprawdź, czy modele są wykrywane">
        ```bash
        openclaw models list
        ```
      </Step>
    </Steps>

    <Warning>
    Rola IAM przypisana do Twojej instancji EC2 musi mieć następujące uprawnienia:

    - `bedrock:InvokeModel`
    - `bedrock:InvokeModelWithResponseStream`
    - `bedrock:ListFoundationModels` (dla automatycznego wykrywania)
    - `bedrock:ListInferenceProfiles` (dla wykrywania profili inferencji)

    Albo przypnij zarządzaną politykę `AmazonBedrockFullAccess`.
    </Warning>

    <Note>
    `AWS_PROFILE=default` jest potrzebne tylko wtedy, gdy konkretnie chcesz mieć znacznik środowiskowy dla trybu auto lub powierzchni statusu. Faktyczna ścieżka uwierzytelniania środowiska wykonawczego Bedrock używa domyślnego łańcucha AWS SDK, więc uwierzytelnianie rolą instancji przez IMDS działa nawet bez znaczników środowiskowych.
    </Note>

  </Tab>
</Tabs>

## Automatyczne wykrywanie modeli

OpenClaw może automatycznie wykrywać modele Bedrock obsługujące **streaming**
i **wyjście tekstowe**. Wykrywanie używa `bedrock:ListFoundationModels` i
`bedrock:ListInferenceProfiles`, a wyniki są cache’owane (domyślnie: 1 godzina).

Jak włączany jest niejawny dostawca:

- Jeśli `plugins.entries.amazon-bedrock.config.discovery.enabled` ma wartość `true`,
  OpenClaw spróbuje wykrywania nawet wtedy, gdy nie ma żadnego znacznika środowiskowego AWS.
- Jeśli `plugins.entries.amazon-bedrock.config.discovery.enabled` nie jest ustawione,
  OpenClaw automatycznie dodaje
  niejawnego dostawcę Bedrock tylko wtedy, gdy widzi jeden z tych znaczników uwierzytelniania AWS:
  `AWS_BEARER_TOKEN_BEDROCK`, `AWS_ACCESS_KEY_ID` +
  `AWS_SECRET_ACCESS_KEY` lub `AWS_PROFILE`.
- Faktyczna ścieżka uwierzytelniania środowiska wykonawczego Bedrock nadal używa domyślnego łańcucha AWS SDK, więc
  współdzielona konfiguracja, SSO i uwierzytelnianie rolą instancji IMDS mogą działać nawet wtedy, gdy do wykrywania
  trzeba było jawnie ustawić `enabled: true`.

<Note>
Dla jawnych wpisów `models.providers["amazon-bedrock"]` OpenClaw nadal może wcześnie rozwiązywać uwierzytelnianie Bedrock oparte na znacznikach środowiskowych z takich znaczników AWS jak `AWS_BEARER_TOKEN_BEDROCK`, bez wymuszania pełnego ładowania uwierzytelniania środowiska wykonawczego. Faktyczna ścieżka uwierzytelniania wywołań modelu nadal używa domyślnego łańcucha AWS SDK.
</Note>

<AccordionGroup>
  <Accordion title="Opcje konfiguracji wykrywania">
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

    | Opcja | Domyślnie | Opis |
    | ------ | --------- | ---- |
    | `enabled` | auto | W trybie auto OpenClaw włącza niejawnego dostawcę Bedrock tylko wtedy, gdy widzi obsługiwany znacznik środowiskowy AWS. Ustaw `true`, aby wymusić wykrywanie. |
    | `region` | `AWS_REGION` / `AWS_DEFAULT_REGION` / `us-east-1` | Region AWS używany do wywołań API wykrywania. |
    | `providerFilter` | (wszystkie) | Dopasowuje nazwy dostawców Bedrock (na przykład `anthropic`, `amazon`). |
    | `refreshInterval` | `3600` | Czas trwania cache w sekundach. Ustaw `0`, aby wyłączyć cache. |
    | `defaultContextWindow` | `32000` | Okno kontekstu używane dla wykrytych modeli (nadpisz, jeśli znasz limity swojego modelu). |
    | `defaultMaxTokens` | `4096` | Maksymalna liczba tokenów wyjściowych używana dla wykrytych modeli (nadpisz, jeśli znasz limity swojego modelu). |

  </Accordion>
</AccordionGroup>

## Szybka konfiguracja (ścieżka AWS)

Ten przewodnik tworzy rolę IAM, przypina uprawnienia Bedrock, wiąże
profil instancji i włącza wykrywanie OpenClaw na hoście EC2.

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

# 2. Przypnij do swojej instancji EC2
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxx \
  --iam-instance-profile Name=EC2-Bedrock-Access

# 3. Na instancji EC2 włącz wykrywanie jawnie
openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1

# 4. Opcjonalnie: dodaj znacznik środowiskowy, jeśli chcesz tryb auto bez jawnego włączenia
echo 'export AWS_PROFILE=default' >> ~/.bashrc
echo 'export AWS_REGION=us-east-1' >> ~/.bashrc
source ~/.bashrc

# 5. Sprawdź, czy modele są wykrywane
openclaw models list
```

## Konfiguracja zaawansowana

<AccordionGroup>
  <Accordion title="Profile inferencji">
    OpenClaw wykrywa **regionalne i globalne profile inferencji** razem z
    modelami bazowymi. Gdy profil mapuje się na znany model bazowy,
    profil dziedziczy możliwości tego modelu (okno kontekstu, maksymalna liczba tokenów,
    reasoning, vision), a poprawny region żądania Bedrock jest wstrzykiwany
    automatycznie. Oznacza to, że międzyregionalne profile Claude działają bez ręcznych
    nadpisań dostawcy.

    Identyfikatory profili inferencji wyglądają jak `us.anthropic.claude-opus-4-6-v1:0` (regionalne)
    albo `anthropic.claude-opus-4-6-v1:0` (globalne). Jeśli model bazowy jest już
    obecny w wynikach wykrywania, profil dziedziczy jego pełny zestaw możliwości;
    w przeciwnym razie stosowane są bezpieczne wartości domyślne.

    Nie jest potrzebna dodatkowa konfiguracja. O ile wykrywanie jest włączone, a podmiot IAM
    ma uprawnienie `bedrock:ListInferenceProfiles`, profile pojawiają się obok
    modeli bazowych w `openclaw models list`.

  </Accordion>

  <Accordion title="Guardrails">
    Możesz zastosować [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
    do wszystkich wywołań modeli Bedrock, dodając obiekt `guardrail` do
    konfiguracji Plugin `amazon-bedrock`. Guardrails pozwalają wymuszać filtrowanie treści,
    blokowanie tematów, filtry słów, filtry informacji wrażliwych oraz kontrole
    ugruntowania kontekstowego.

    ```json5
    {
      plugins: {
        entries: {
          "amazon-bedrock": {
            config: {
              guardrail: {
                guardrailIdentifier: "abc123", // ID guardrail lub pełny ARN
                guardrailVersion: "1", // numer wersji lub "DRAFT"
                streamProcessingMode: "sync", // opcjonalnie: "sync" lub "async"
                trace: "enabled", // opcjonalnie: "enabled", "disabled" lub "enabled_full"
              },
            },
          },
        },
      },
    }
    ```

    | Opcja | Wymagana | Opis |
    | ------ | -------- | ---- |
    | `guardrailIdentifier` | Tak | ID guardrail (np. `abc123`) lub pełny ARN (np. `arn:aws:bedrock:us-east-1:123456789012:guardrail/abc123`). |
    | `guardrailVersion` | Tak | Numer opublikowanej wersji lub `"DRAFT"` dla wersji roboczej. |
    | `streamProcessingMode` | Nie | `"sync"` lub `"async"` dla oceny guardrail podczas streamingu. Jeśli pominięte, Bedrock używa wartości domyślnej. |
    | `trace` | Nie | `"enabled"` lub `"enabled_full"` do debugowania; w środowisku produkcyjnym pomiń albo ustaw `"disabled"`. |

    <Warning>
    Podmiot IAM używany przez Gateway musi mieć uprawnienie `bedrock:ApplyGuardrail` oprócz standardowych uprawnień wywołania.
    </Warning>

  </Accordion>

  <Accordion title="Embeddingi do wyszukiwania pamięci">
    Bedrock może też służyć jako dostawca embeddingów dla
    [wyszukiwania pamięci](/pl/concepts/memory-search). Konfiguruje się to oddzielnie od
    dostawcy inferencji — ustaw `agents.defaults.memorySearch.provider` na `"bedrock"`:

    ```json5
    {
      agents: {
        defaults: {
          memorySearch: {
            provider: "bedrock",
            model: "amazon.titan-embed-text-v2:0", // domyślnie
          },
        },
      },
    }
    ```

    Embeddingi Bedrock używają tego samego łańcucha poświadczeń AWS SDK co inferencja (role
    instancji, SSO, klucze dostępu, współdzielona konfiguracja i web identity). Klucz API
    nie jest potrzebny. Gdy `provider` ma wartość `"auto"`, Bedrock jest wykrywany automatycznie, jeśli ten
    łańcuch poświadczeń zostanie pomyślnie rozwiązany.

    Obsługiwane modele embeddingów obejmują Amazon Titan Embed (v1, v2), Amazon Nova
    Embed, Cohere Embed (v3, v4) oraz TwelveLabs Marengo. Pełną listę modeli i opcje wymiarów znajdziesz w
    [referencji konfiguracji pamięci -- Bedrock](/pl/reference/memory-config#bedrock-embedding-config).

  </Accordion>

  <Accordion title="Uwagi i zastrzeżenia">
    - Bedrock wymaga włączenia **dostępu do modelu** w Twoim koncie/regionie AWS.
    - Automatyczne wykrywanie wymaga uprawnień `bedrock:ListFoundationModels` i
      `bedrock:ListInferenceProfiles`.
    - Jeśli polegasz na trybie auto, ustaw na
      hoście Gateway jeden z obsługiwanych znaczników środowiskowych uwierzytelniania AWS. Jeśli wolisz uwierzytelnianie IMDS/współdzieloną konfiguracją bez znaczników środowiskowych, ustaw
      `plugins.entries.amazon-bedrock.config.discovery.enabled: true`.
    - OpenClaw pokazuje źródło poświadczeń w tej kolejności: `AWS_BEARER_TOKEN_BEDROCK`,
      następnie `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`, potem `AWS_PROFILE`, a na końcu
      domyślny łańcuch AWS SDK.
    - Obsługa reasoning zależy od modelu; sprawdź kartę modelu Bedrock, aby poznać
      aktualne możliwości.
    - Jeśli wolisz zarządzany przepływ kluczy, możesz też umieścić zgodne z OpenAI
      proxy przed Bedrock i zamiast tego skonfigurować je jako dostawcę OpenAI.
  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, odwołań do modeli i zachowania failover.
  </Card>
  <Card title="Wyszukiwanie pamięci" href="/pl/concepts/memory-search" icon="magnifying-glass">
    Konfiguracja embeddingów Bedrock dla wyszukiwania pamięci.
  </Card>
  <Card title="Referencja konfiguracji pamięci" href="/pl/reference/memory-config#bedrock-embedding-config" icon="database">
    Pełna lista modeli embeddingów Bedrock i opcje wymiarów.
  </Card>
  <Card title="Rozwiązywanie problemów" href="/pl/help/troubleshooting" icon="wrench">
    Ogólne rozwiązywanie problemów i FAQ.
  </Card>
</CardGroup>
