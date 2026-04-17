---
read_when:
    - Chcesz korzystać z inferencji skoncentrowanej na prywatności w OpenClaw
    - Potrzebujesz wskazówek dotyczących konfiguracji Venice AI
summary: Używanie modeli Venice AI skoncentrowanych na prywatności w OpenClaw
title: Venice AI
x-i18n:
    generated_at: "2026-04-12T23:33:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6f8005edb1d7781316ce8b5432bf4f9375c16113594a2a588912dce82234a9e5
    source_path: providers/venice.md
    workflow: 15
---

# Venice AI

Venice AI zapewnia **inferencję AI skoncentrowaną na prywatności** z obsługą nieocenzurowanych modeli oraz dostępem do głównych modeli zamkniętych przez ich anonimizujące proxy. Cała inferencja jest domyślnie prywatna — bez trenowania na Twoich danych i bez logowania.

## Dlaczego Venice w OpenClaw

- **Prywatna inferencja** dla modeli open source (bez logowania).
- **Nieocenzurowane modele**, gdy ich potrzebujesz.
- **Anonimizowany dostęp** do modeli zamkniętych (Opus/GPT/Gemini), gdy liczy się jakość.
- Endpointy `/v1` zgodne z OpenAI.

## Tryby prywatności

Venice oferuje dwa poziomy prywatności — zrozumienie tej różnicy jest kluczowe przy wyborze modelu:

| Tryb            | Opis                                                                                                                              | Modele                                                        |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Prywatny**    | W pełni prywatny. Prompty/odpowiedzi **nigdy nie są przechowywane ani logowane**. Efemeryczny.                                   | Llama, Qwen, DeepSeek, Kimi, MiniMax, Venice Uncensored itd.  |
| **Anonimizowany** | Przekazywany przez Venice z usuniętymi metadanymi. Bazowy dostawca (OpenAI, Anthropic, Google, xAI) widzi zanonimizowane żądania. | Claude, GPT, Gemini, Grok                                     |

<Warning>
Modele anonimizowane **nie są** w pełni prywatne. Venice usuwa metadane przed przekazaniem dalej, ale bazowy dostawca (OpenAI, Anthropic, Google, xAI) nadal przetwarza żądanie. Wybieraj modele **Prywatne**, gdy wymagana jest pełna prywatność.
</Warning>

## Funkcje

- **Podejście skoncentrowane na prywatności**: wybór między trybami „prywatnym” (w pełni prywatny) i „anonimizowanym” (przez proxy)
- **Nieocenzurowane modele**: dostęp do modeli bez ograniczeń treści
- **Dostęp do głównych modeli**: używaj Claude, GPT, Gemini i Grok przez anonimizujące proxy Venice
- **API zgodne z OpenAI**: standardowe endpointy `/v1` dla łatwej integracji
- **Streaming**: obsługiwany we wszystkich modelach
- **Function calling**: obsługiwane w wybranych modelach (sprawdź możliwości modelu)
- **Vision**: obsługiwane w modelach z możliwością vision
- **Brak twardych limitów szybkości**: przy skrajnym użyciu może obowiązywać dławienie fair-use

## Pierwsze kroki

<Steps>
  <Step title="Pobierz swój klucz API">
    1. Zarejestruj się na [venice.ai](https://venice.ai)
    2. Przejdź do **Settings > API Keys > Create new key**
    3. Skopiuj swój klucz API (format: `vapi_xxxxxxxxxxxx`)
  </Step>
  <Step title="Skonfiguruj OpenClaw">
    Wybierz preferowaną metodę konfiguracji:

    <Tabs>
      <Tab title="Interaktywnie (zalecane)">
        ```bash
        openclaw onboard --auth-choice venice-api-key
        ```

        To:
        1. Poprosi o Twój klucz API (lub użyje istniejącego `VENICE_API_KEY`)
        2. Pokaże wszystkie dostępne modele Venice
        3. Pozwoli wybrać domyślny model
        4. Automatycznie skonfiguruje dostawcę
      </Tab>
      <Tab title="Zmienna środowiskowa">
        ```bash
        export VENICE_API_KEY="vapi_xxxxxxxxxxxx"
        ```
      </Tab>
      <Tab title="Nieinteraktywnie">
        ```bash
        openclaw onboard --non-interactive \
          --auth-choice venice-api-key \
          --venice-api-key "vapi_xxxxxxxxxxxx"
        ```
      </Tab>
    </Tabs>

  </Step>
  <Step title="Zweryfikuj konfigurację">
    ```bash
    openclaw agent --model venice/kimi-k2-5 --message "Hello, are you working?"
    ```
  </Step>
</Steps>

## Wybór modelu

Po konfiguracji OpenClaw pokazuje wszystkie dostępne modele Venice. Wybierz je zależnie od swoich potrzeb:

- **Model domyślny**: `venice/kimi-k2-5` dla mocnego prywatnego rozumowania plus vision.
- **Opcja o najwyższych możliwościach**: `venice/claude-opus-4-6` dla najmocniejszej anonimizowanej ścieżki Venice.
- **Prywatność**: wybieraj modele „private” dla w pełni prywatnej inferencji.
- **Możliwości**: wybieraj modele „anonymized”, aby uzyskać dostęp do Claude, GPT i Gemini przez proxy Venice.

W każdej chwili możesz zmienić swój domyślny model:

```bash
openclaw models set venice/kimi-k2-5
openclaw models set venice/claude-opus-4-6
```

Wyświetl wszystkie dostępne modele:

```bash
openclaw models list | grep venice
```

Możesz też uruchomić `openclaw configure`, wybrać **Model/auth** i następnie **Venice AI**.

<Tip>
Użyj poniższej tabeli, aby wybrać właściwy model do swojego zastosowania.

| Zastosowanie                | Zalecany model                   | Dlaczego                                     |
| --------------------------- | -------------------------------- | -------------------------------------------- |
| **Ogólny czat (domyślnie)** | `kimi-k2-5`                      | Mocne prywatne rozumowanie plus vision       |
| **Najlepsza ogólna jakość** | `claude-opus-4-6`                | Najmocniejsza anonimizowana opcja Venice     |
| **Prywatność + kodowanie**  | `qwen3-coder-480b-a35b-instruct` | Prywatny model do kodowania z dużym kontekstem |
| **Prywatne vision**         | `kimi-k2-5`                      | Obsługa vision bez opuszczania trybu prywatnego |
| **Szybko i tanio**          | `qwen3-4b`                       | Lekki model rozumujący                       |
| **Złożone zadania prywatne**| `deepseek-v3.2`                  | Mocne rozumowanie, ale bez obsługi narzędzi Venice |
| **Nieocenzurowany**         | `venice-uncensored`              | Bez ograniczeń treści                        |

</Tip>

## Dostępne modele (łącznie 41)

<AccordionGroup>
  <Accordion title="Modele prywatne (26) — w pełni prywatne, bez logowania">
    | ID modelu                              | Nazwa                               | Kontekst | Funkcje                    |
    | -------------------------------------- | ----------------------------------- | -------- | -------------------------- |
    | `kimi-k2-5`                            | Kimi K2.5                           | 256k     | Domyślny, rozumowanie, vision |
    | `kimi-k2-thinking`                     | Kimi K2 Thinking                    | 256k     | Rozumowanie                |
    | `llama-3.3-70b`                        | Llama 3.3 70B                       | 128k     | Ogólne                     |
    | `llama-3.2-3b`                         | Llama 3.2 3B                        | 128k     | Ogólne                     |
    | `hermes-3-llama-3.1-405b`              | Hermes 3 Llama 3.1 405B             | 128k     | Ogólne, narzędzia wyłączone |
    | `qwen3-235b-a22b-thinking-2507`        | Qwen3 235B Thinking                 | 128k     | Rozumowanie                |
    | `qwen3-235b-a22b-instruct-2507`        | Qwen3 235B Instruct                 | 128k     | Ogólne                     |
    | `qwen3-coder-480b-a35b-instruct`       | Qwen3 Coder 480B                    | 256k     | Kodowanie                  |
    | `qwen3-coder-480b-a35b-instruct-turbo` | Qwen3 Coder 480B Turbo              | 256k     | Kodowanie                  |
    | `qwen3-5-35b-a3b`                      | Qwen3.5 35B A3B                     | 256k     | Rozumowanie, vision        |
    | `qwen3-next-80b`                       | Qwen3 Next 80B                      | 256k     | Ogólne                     |
    | `qwen3-vl-235b-a22b`                   | Qwen3 VL 235B (Vision)              | 256k     | Vision                     |
    | `qwen3-4b`                             | Venice Small (Qwen3 4B)             | 32k      | Szybki, rozumowanie        |
    | `deepseek-v3.2`                        | DeepSeek V3.2                       | 160k     | Rozumowanie, narzędzia wyłączone |
    | `venice-uncensored`                    | Venice Uncensored (Dolphin-Mistral) | 32k      | Nieocenzurowany, narzędzia wyłączone |
    | `mistral-31-24b`                       | Venice Medium (Mistral)             | 128k     | Vision                     |
    | `google-gemma-3-27b-it`                | Google Gemma 3 27B Instruct         | 198k     | Vision                     |
    | `openai-gpt-oss-120b`                  | OpenAI GPT OSS 120B                 | 128k     | Ogólne                     |
    | `nvidia-nemotron-3-nano-30b-a3b`       | NVIDIA Nemotron 3 Nano 30B          | 128k     | Ogólne                     |
    | `olafangensan-glm-4.7-flash-heretic`   | GLM 4.7 Flash Heretic               | 128k     | Rozumowanie                |
    | `zai-org-glm-4.6`                      | GLM 4.6                             | 198k     | Ogólne                     |
    | `zai-org-glm-4.7`                      | GLM 4.7                             | 198k     | Rozumowanie                |
    | `zai-org-glm-4.7-flash`                | GLM 4.7 Flash                       | 128k     | Rozumowanie                |
    | `zai-org-glm-5`                        | GLM 5                               | 198k     | Rozumowanie                |
    | `minimax-m21`                          | MiniMax M2.1                        | 198k     | Rozumowanie                |
    | `minimax-m25`                          | MiniMax M2.5                        | 198k     | Rozumowanie                |
  </Accordion>

  <Accordion title="Modele anonimizowane (15) — przez proxy Venice">
    | ID modelu                       | Nazwa                          | Kontekst | Funkcje                    |
    | ------------------------------- | ------------------------------ | -------- | -------------------------- |
    | `claude-opus-4-6`               | Claude Opus 4.6 (przez Venice) | 1M       | Rozumowanie, vision        |
    | `claude-opus-4-5`               | Claude Opus 4.5 (przez Venice) | 198k     | Rozumowanie, vision        |
    | `claude-sonnet-4-6`             | Claude Sonnet 4.6 (przez Venice) | 1M     | Rozumowanie, vision        |
    | `claude-sonnet-4-5`             | Claude Sonnet 4.5 (przez Venice) | 198k   | Rozumowanie, vision        |
    | `openai-gpt-54`                 | GPT-5.4 (przez Venice)         | 1M       | Rozumowanie, vision        |
    | `openai-gpt-53-codex`           | GPT-5.3 Codex (przez Venice)   | 400k     | Rozumowanie, vision, kodowanie |
    | `openai-gpt-52`                 | GPT-5.2 (przez Venice)         | 256k     | Rozumowanie                |
    | `openai-gpt-52-codex`           | GPT-5.2 Codex (przez Venice)   | 256k     | Rozumowanie, vision, kodowanie |
    | `openai-gpt-4o-2024-11-20`      | GPT-4o (przez Venice)          | 128k     | Vision                     |
    | `openai-gpt-4o-mini-2024-07-18` | GPT-4o Mini (przez Venice)     | 128k     | Vision                     |
    | `gemini-3-1-pro-preview`        | Gemini 3.1 Pro (przez Venice)  | 1M       | Rozumowanie, vision        |
    | `gemini-3-pro-preview`          | Gemini 3 Pro (przez Venice)    | 198k     | Rozumowanie, vision        |
    | `gemini-3-flash-preview`        | Gemini 3 Flash (przez Venice)  | 256k     | Rozumowanie, vision        |
    | `grok-41-fast`                  | Grok 4.1 Fast (przez Venice)   | 1M       | Rozumowanie, vision        |
    | `grok-code-fast-1`              | Grok Code Fast 1 (przez Venice)| 256k     | Rozumowanie, kodowanie     |
  </Accordion>
</AccordionGroup>

## Wykrywanie modeli

OpenClaw automatycznie wykrywa modele z API Venice, gdy ustawione jest `VENICE_API_KEY`. Jeśli API jest nieosiągalne, następuje fallback do statycznego katalogu.

Endpoint `/models` jest publiczny (nie wymaga uwierzytelniania do listowania), ale inferencja wymaga prawidłowego klucza API.

## Streaming i obsługa narzędzi

| Funkcja              | Obsługa                                              |
| -------------------- | ---------------------------------------------------- |
| **Streaming**        | Wszystkie modele                                     |
| **Function calling** | Większość modeli (sprawdź `supportsFunctionCalling` w API) |
| **Vision/Images**    | Modele oznaczone funkcją „Vision”                    |
| **Tryb JSON**        | Obsługiwany przez `response_format`                  |

## Ceny

Venice używa systemu opartego na kredytach. Aktualne stawki sprawdzisz na [venice.ai/pricing](https://venice.ai/pricing):

- **Modele prywatne**: zazwyczaj niższy koszt
- **Modele anonimizowane**: ceny zbliżone do bezpośredniego API + niewielka opłata Venice

### Venice (anonimizowane) vs bezpośrednie API

| Aspekt       | Venice (anonimizowane)         | Bezpośrednie API    |
| ------------ | ------------------------------ | ------------------- |
| **Prywatność** | Metadane usunięte, anonimizacja | Twoje konto powiązane |
| **Opóźnienie** | +10-50 ms (proxy)              | Bezpośrednio        |
| **Funkcje**    | Obsługiwana większość funkcji  | Pełne funkcje       |
| **Rozliczenia**| Kredyty Venice                 | Rozliczenia dostawcy |

## Przykłady użycia

```bash
# Użyj domyślnego modelu prywatnego
openclaw agent --model venice/kimi-k2-5 --message "Quick health check"

# Użyj Claude Opus przez Venice (anonimizowane)
openclaw agent --model venice/claude-opus-4-6 --message "Summarize this task"

# Użyj nieocenzurowanego modelu
openclaw agent --model venice/venice-uncensored --message "Draft options"

# Użyj modelu vision z obrazem
openclaw agent --model venice/qwen3-vl-235b-a22b --message "Review attached image"

# Użyj modelu do kodowania
openclaw agent --model venice/qwen3-coder-480b-a35b-instruct --message "Refactor this function"
```

## Rozwiązywanie problemów

<AccordionGroup>
  <Accordion title="Klucz API nie jest rozpoznawany">
    ```bash
    echo $VENICE_API_KEY
    openclaw models list | grep venice
    ```

    Upewnij się, że klucz zaczyna się od `vapi_`.

  </Accordion>

  <Accordion title="Model jest niedostępny">
    Katalog modeli Venice aktualizuje się dynamicznie. Uruchom `openclaw models list`, aby zobaczyć aktualnie dostępne modele. Niektóre modele mogą być tymczasowo offline.
  </Accordion>

  <Accordion title="Problemy z połączeniem">
    API Venice znajduje się pod adresem `https://api.venice.ai/api/v1`. Upewnij się, że Twoja sieć pozwala na połączenia HTTPS.
  </Accordion>
</AccordionGroup>

<Note>
Więcej pomocy: [Rozwiązywanie problemów](/pl/help/troubleshooting) i [FAQ](/pl/help/faq).
</Note>

## Konfiguracja zaawansowana

<AccordionGroup>
  <Accordion title="Przykład pliku konfiguracyjnego">
    ```json5
    {
      env: { VENICE_API_KEY: "vapi_..." },
      agents: { defaults: { model: { primary: "venice/kimi-k2-5" } } },
      models: {
        mode: "merge",
        providers: {
          venice: {
            baseUrl: "https://api.venice.ai/api/v1",
            apiKey: "${VENICE_API_KEY}",
            api: "openai-completions",
            models: [
              {
                id: "kimi-k2-5",
                name: "Kimi K2.5",
                reasoning: true,
                input: ["text", "image"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 256000,
                maxTokens: 65536,
              },
            ],
          },
        },
      },
    }
    ```
  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, referencji modeli i zachowania failover.
  </Card>
  <Card title="Venice AI" href="https://venice.ai" icon="globe">
    Strona główna Venice AI i rejestracja konta.
  </Card>
  <Card title="Dokumentacja API" href="https://docs.venice.ai" icon="book">
    Dokumentacja API Venice i materiały dla deweloperów.
  </Card>
  <Card title="Cennik" href="https://venice.ai/pricing" icon="credit-card">
    Aktualne stawki kredytowe i plany Venice.
  </Card>
</CardGroup>
