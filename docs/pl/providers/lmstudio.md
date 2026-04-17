---
read_when:
    - Chcesz uruchomić OpenClaw z modelami open source za pośrednictwem LM Studio.
    - Chcesz skonfigurować LM Studio.
summary: Uruchom OpenClaw z LM Studio
title: LM Studio
x-i18n:
    generated_at: "2026-04-13T08:50:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 11264584e8277260d4215feb7c751329ce04f59e9228da1c58e147c21cd9ac2c
    source_path: providers/lmstudio.md
    workflow: 15
---

# LM Studio

LM Studio to przyjazna, a zarazem potężna aplikacja do uruchamiania modeli o otwartych wagach na własnym sprzęcie. Umożliwia uruchamianie modeli llama.cpp (GGUF) lub MLX (Apple Silicon). Jest dostępna jako pakiet GUI lub daemon bez interfejsu (`llmster`). Dokumentację produktu i konfiguracji znajdziesz na stronie [lmstudio.ai](https://lmstudio.ai/).

## Szybki start

1. Zainstaluj LM Studio (wersja desktopowa) lub `llmster` (wersja bez interfejsu), a następnie uruchom lokalny serwer:

```bash
curl -fsSL https://lmstudio.ai/install.sh | bash
```

2. Uruchom serwer

Upewnij się, że uruchamiasz aplikację desktopową albo daemon za pomocą następującego polecenia:

```bash
lms daemon up
```

```bash
lms server start --port 1234
```

Jeśli używasz aplikacji, upewnij się, że masz włączone JIT, aby zapewnić płynne działanie. Więcej informacji znajdziesz w [przewodniku LM Studio dotyczącym JIT i TTL](https://lmstudio.ai/docs/developer/core/ttl-and-auto-evict).

3. OpenClaw wymaga wartości tokena LM Studio. Ustaw `LM_API_TOKEN`:

```bash
export LM_API_TOKEN="your-lm-studio-api-token"
```

Jeśli uwierzytelnianie LM Studio jest wyłączone, użyj dowolnej niepustej wartości tokena:

```bash
export LM_API_TOKEN="placeholder-key"
```

Szczegóły konfiguracji uwierzytelniania LM Studio znajdziesz w [LM Studio Authentication](https://lmstudio.ai/docs/developer/core/authentication).

4. Uruchom onboarding i wybierz `LM Studio`:

```bash
openclaw onboard
```

5. Podczas onboardingu użyj monitu `Default model`, aby wybrać model LM Studio.

Możesz też ustawić go lub zmienić później:

```bash
openclaw models set lmstudio/qwen/qwen3.5-9b
```

Klucze modeli LM Studio mają format `author/model-name` (na przykład `qwen/qwen3.5-9b`). Odwołania do modeli OpenClaw poprzedzają je nazwą dostawcy: `lmstudio/qwen/qwen3.5-9b`. Dokładny klucz modelu możesz znaleźć, uruchamiając `curl http://localhost:1234/api/v1/models` i sprawdzając pole `key`.

## Onboarding nieinteraktywny

Użyj nieinteraktywnego onboardingu, jeśli chcesz zautomatyzować konfigurację (CI, provisioning, zdalny bootstrap):

```bash
openclaw onboard \
  --non-interactive \
  --accept-risk \
  --auth-choice lmstudio
```

Możesz też podać bazowy URL lub model wraz z kluczem API:

```bash
openclaw onboard \
  --non-interactive \
  --accept-risk \
  --auth-choice lmstudio \
  --custom-base-url http://localhost:1234/v1 \
  --lmstudio-api-key "$LM_API_TOKEN" \
  --custom-model-id qwen/qwen3.5-9b
```

`--custom-model-id` przyjmuje klucz modelu zwracany przez LM Studio (na przykład `qwen/qwen3.5-9b`), bez prefiksu dostawcy `lmstudio/`.

Nieinteraktywny onboarding wymaga `--lmstudio-api-key` (lub `LM_API_TOKEN` w zmiennych środowiskowych).
W przypadku nieuwierzytelnionych serwerów LM Studio działa dowolna niepusta wartość tokena.

`--custom-api-key` nadal jest obsługiwane ze względu na zgodność, ale dla LM Studio zalecane jest `--lmstudio-api-key`.

Spowoduje to zapisanie `models.providers.lmstudio`, ustawienie domyślnego modelu na
`lmstudio/<custom-model-id>` oraz zapisanie profilu uwierzytelniania `lmstudio:default`.

Konfiguracja interaktywna może poprosić o opcjonalną preferowaną długość kontekstu ładowania i zastosuje ją do wykrytych modeli LM Studio zapisywanych w konfiguracji.

## Konfiguracja

### Jawna konfiguracja

```json5
{
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "${LM_API_TOKEN}",
        api: "openai-completions",
        models: [
          {
            id: "qwen/qwen3-coder-next",
            name: "Qwen 3 Coder Next",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

## Rozwiązywanie problemów

### Nie wykryto LM Studio

Upewnij się, że LM Studio jest uruchomione i że ustawiono `LM_API_TOKEN` (w przypadku serwerów nieuwierzytelnionych działa dowolna niepusta wartość tokena):

```bash
# Uruchom przez aplikację desktopową lub bez interfejsu:
lms server start --port 1234
```

Sprawdź, czy API jest dostępne:

```bash
curl http://localhost:1234/api/v1/models
```

### Błędy uwierzytelniania (HTTP 401)

Jeśli podczas konfiguracji pojawia się HTTP 401, sprawdź swój klucz API:

- Sprawdź, czy `LM_API_TOKEN` odpowiada kluczowi skonfigurowanemu w LM Studio.
- Szczegóły konfiguracji uwierzytelniania LM Studio znajdziesz w [LM Studio Authentication](https://lmstudio.ai/docs/developer/core/authentication).
- Jeśli serwer nie wymaga uwierzytelniania, użyj dowolnej niepustej wartości tokena dla `LM_API_TOKEN`.

### Ładowanie modeli just-in-time

LM Studio obsługuje ładowanie modeli just-in-time (JIT), w którym modele są ładowane przy pierwszym żądaniu. Upewnij się, że ta opcja jest włączona, aby uniknąć błędów „Model not loaded”.
