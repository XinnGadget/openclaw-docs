---
read_when:
    - Chcesz używać Hugging Face Inference z OpenClaw
    - Potrzebujesz zmiennej środowiskowej tokenu HF lub opcji uwierzytelniania w CLI
summary: Konfiguracja Hugging Face Inference (uwierzytelnianie + wybór modelu)
title: Hugging Face (Inference)
x-i18n:
    generated_at: "2026-04-12T23:31:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7787fce1acfe81adb5380ab1c7441d661d03c574da07149c037d3b6ba3c8e52a
    source_path: providers/huggingface.md
    workflow: 15
---

# Hugging Face (Inference)

[Dostawcy Hugging Face Inference](https://huggingface.co/docs/inference-providers) oferują zgodne z OpenAI chat completions przez jedno API routera. Otrzymujesz dostęp do wielu modeli (DeepSeek, Llama i innych) za pomocą jednego tokenu. OpenClaw używa **endpointu zgodnego z OpenAI** (tylko chat completions); do text-to-image, embeddings lub mowy używaj bezpośrednio [klientów HF inference](https://huggingface.co/docs/api-inference/quicktour).

- Dostawca: `huggingface`
- Uwierzytelnianie: `HUGGINGFACE_HUB_TOKEN` lub `HF_TOKEN` (token o szczegółowych uprawnieniach z uprawnieniem **Make calls to Inference Providers**)
- API: zgodne z OpenAI (`https://router.huggingface.co/v1`)
- Rozliczanie: jeden token HF; [cennik](https://huggingface.co/docs/inference-providers/pricing) opiera się na stawkach dostawców i obejmuje darmowy poziom.

## Pierwsze kroki

<Steps>
  <Step title="Utwórz token o szczegółowych uprawnieniach">
    Przejdź do [Hugging Face Settings Tokens](https://huggingface.co/settings/tokens/new?ownUserPermissions=inference.serverless.write&tokenType=fineGrained) i utwórz nowy token o szczegółowych uprawnieniach.

    <Warning>
    Token musi mieć włączone uprawnienie **Make calls to Inference Providers**, w przeciwnym razie żądania API będą odrzucane.
    </Warning>

  </Step>
  <Step title="Uruchom onboarding">
    Wybierz **Hugging Face** z listy rozwijanej dostawców, a następnie podaj klucz API, gdy pojawi się monit:

    ```bash
    openclaw onboard --auth-choice huggingface-api-key
    ```

  </Step>
  <Step title="Wybierz model domyślny">
    Z listy rozwijanej **Default Hugging Face model** wybierz model, którego chcesz używać. Lista jest wczytywana z Inference API, gdy masz prawidłowy token; w przeciwnym razie pokazywana jest wbudowana lista. Twój wybór jest zapisywany jako model domyślny.

    Możesz też ustawić lub zmienić model domyślny później w konfiguracji:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/deepseek-ai/DeepSeek-R1" },
        },
      },
    }
    ```

  </Step>
  <Step title="Sprawdź, czy model jest dostępny">
    ```bash
    openclaw models list --provider huggingface
    ```
  </Step>
</Steps>

### Konfiguracja nieinteraktywna

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice huggingface-api-key \
  --huggingface-api-key "$HF_TOKEN"
```

To ustawi `huggingface/deepseek-ai/DeepSeek-R1` jako model domyślny.

## Identyfikatory modeli

Referencje modeli używają formatu `huggingface/<org>/<model>` (identyfikatory w stylu Hub). Poniższa lista pochodzi z **GET** `https://router.huggingface.co/v1/models`; Twój katalog może zawierać więcej.

| Model                  | Ref (z prefiksem `huggingface/`)    |
| ---------------------- | ----------------------------------- |
| DeepSeek R1            | `deepseek-ai/DeepSeek-R1`           |
| DeepSeek V3.2          | `deepseek-ai/DeepSeek-V3.2`         |
| Qwen3 8B               | `Qwen/Qwen3-8B`                     |
| Qwen2.5 7B Instruct    | `Qwen/Qwen2.5-7B-Instruct`          |
| Qwen3 32B              | `Qwen/Qwen3-32B`                    |
| Llama 3.3 70B Instruct | `meta-llama/Llama-3.3-70B-Instruct` |
| Llama 3.1 8B Instruct  | `meta-llama/Llama-3.1-8B-Instruct`  |
| GPT-OSS 120B           | `openai/gpt-oss-120b`               |
| GLM 4.7                | `zai-org/GLM-4.7`                   |
| Kimi K2.5              | `moonshotai/Kimi-K2.5`              |

<Tip>
Możesz dodać `:fastest` lub `:cheapest` do dowolnego identyfikatora modelu. Ustaw domyślną kolejność w [ustawieniach Inference Provider](https://hf.co/settings/inference-providers); pełną listę znajdziesz w [Inference Providers](https://huggingface.co/docs/inference-providers) oraz pod **GET** `https://router.huggingface.co/v1/models`.
</Tip>

## Szczegóły zaawansowane

<AccordionGroup>
  <Accordion title="Wykrywanie modeli i lista rozwijana onboardingu">
    OpenClaw wykrywa modele, wywołując **bezpośrednio endpoint Inference**:

    ```bash
    GET https://router.huggingface.co/v1/models
    ```

    (Opcjonalnie: wyślij `Authorization: Bearer $HUGGINGFACE_HUB_TOKEN` lub `$HF_TOKEN`, aby uzyskać pełną listę; niektóre endpointy bez uwierzytelniania zwracają podzbiór). Odpowiedź ma format w stylu OpenAI: `{ "object": "list", "data": [ { "id": "Qwen/Qwen3-8B", "owned_by": "Qwen", ... }, ... ] }`.

    Gdy skonfigurujesz klucz API Hugging Face (przez onboarding, `HUGGINGFACE_HUB_TOKEN` lub `HF_TOKEN`), OpenClaw używa tego żądania GET do wykrywania dostępnych modeli chat-completion. Podczas **konfiguracji interaktywnej**, po podaniu tokenu zobaczysz listę rozwijaną **Default Hugging Face model** wypełnioną tą listą (lub wbudowanym katalogiem, jeśli żądanie się nie powiedzie). W runtime (na przykład przy uruchamianiu Gateway), gdy klucz jest obecny, OpenClaw ponownie wywołuje **GET** `https://router.huggingface.co/v1/models`, aby odświeżyć katalog. Lista jest łączona z wbudowanym katalogiem (dla metadanych, takich jak okno kontekstu i koszt). Jeśli żądanie się nie powiedzie lub klucz nie jest ustawiony, używany jest tylko wbudowany katalog.

  </Accordion>

  <Accordion title="Nazwy modeli, aliasy i sufiksy polityk">
    - **Nazwa z API:** Wyświetlana nazwa modelu jest **uzupełniana z GET /v1/models**, gdy API zwraca `name`, `title` lub `display_name`; w przeciwnym razie jest wyprowadzana z identyfikatora modelu (na przykład `deepseek-ai/DeepSeek-R1` staje się „DeepSeek R1”).
    - **Nadpisanie wyświetlanej nazwy:** Możesz ustawić niestandardową etykietę dla każdego modelu w konfiguracji, aby była wyświetlana tak, jak chcesz w CLI i UI:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "huggingface/deepseek-ai/DeepSeek-R1": { alias: "DeepSeek R1 (fast)" },
            "huggingface/deepseek-ai/DeepSeek-R1:cheapest": { alias: "DeepSeek R1 (cheap)" },
          },
        },
      },
    }
    ```

    - **Sufiksy polityk:** Dołączona dokumentacja i helpery OpenClaw dla Hugging Face obecnie traktują te dwa sufiksy jako wbudowane warianty polityk:
      - **`:fastest`** — najwyższa przepustowość.
      - **`:cheapest`** — najniższy koszt na token wyjściowy.

      Możesz dodać je jako osobne wpisy w `models.providers.huggingface.models` albo ustawić `model.primary` z sufiksem. Możesz też ustawić domyślną kolejność dostawców w [ustawieniach Inference Provider](https://hf.co/settings/inference-providers) (brak sufiksu = użyj tej kolejności).

    - **Łączenie konfiguracji:** Istniejące wpisy w `models.providers.huggingface.models` (na przykład w `models.json`) są zachowywane podczas łączenia konfiguracji. Oznacza to, że wszelkie niestandardowe `name`, `alias` lub opcje modelu, które tam ustawisz, zostaną zachowane.

  </Accordion>

  <Accordion title="Konfiguracja środowiska i demona">
    Jeśli Gateway działa jako demon (launchd/systemd), upewnij się, że `HUGGINGFACE_HUB_TOKEN` lub `HF_TOKEN` jest dostępny dla tego procesu (na przykład w `~/.openclaw/.env` lub przez `env.shellEnv`).

    <Note>
    OpenClaw akceptuje zarówno `HUGGINGFACE_HUB_TOKEN`, jak i `HF_TOKEN` jako aliasy zmiennych środowiskowych. Każda z nich działa; jeśli ustawione są obie, pierwszeństwo ma `HUGGINGFACE_HUB_TOKEN`.
    </Note>

  </Accordion>

  <Accordion title="Konfiguracja: DeepSeek R1 z fallbackiem Qwen">
    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "huggingface/deepseek-ai/DeepSeek-R1",
            fallbacks: ["huggingface/Qwen/Qwen3-8B"],
          },
          models: {
            "huggingface/deepseek-ai/DeepSeek-R1": { alias: "DeepSeek R1" },
            "huggingface/Qwen/Qwen3-8B": { alias: "Qwen3 8B" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="Konfiguracja: Qwen z wariantami cheapest i fastest">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/Qwen/Qwen3-8B" },
          models: {
            "huggingface/Qwen/Qwen3-8B": { alias: "Qwen3 8B" },
            "huggingface/Qwen/Qwen3-8B:cheapest": { alias: "Qwen3 8B (cheapest)" },
            "huggingface/Qwen/Qwen3-8B:fastest": { alias: "Qwen3 8B (fastest)" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="Konfiguracja: DeepSeek + Llama + GPT-OSS z aliasami">
    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "huggingface/deepseek-ai/DeepSeek-V3.2",
            fallbacks: [
              "huggingface/meta-llama/Llama-3.3-70B-Instruct",
              "huggingface/openai/gpt-oss-120b",
            ],
          },
          models: {
            "huggingface/deepseek-ai/DeepSeek-V3.2": { alias: "DeepSeek V3.2" },
            "huggingface/meta-llama/Llama-3.3-70B-Instruct": { alias: "Llama 3.3 70B" },
            "huggingface/openai/gpt-oss-120b": { alias: "GPT-OSS 120B" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="Konfiguracja: Wiele modeli Qwen i DeepSeek z sufiksami polityk">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/Qwen/Qwen2.5-7B-Instruct:cheapest" },
          models: {
            "huggingface/Qwen/Qwen2.5-7B-Instruct": { alias: "Qwen2.5 7B" },
            "huggingface/Qwen/Qwen2.5-7B-Instruct:cheapest": { alias: "Qwen2.5 7B (cheap)" },
            "huggingface/deepseek-ai/DeepSeek-R1:fastest": { alias: "DeepSeek R1 (fast)" },
            "huggingface/meta-llama/Llama-3.1-8B-Instruct": { alias: "Llama 3.1 8B" },
          },
        },
      },
    }
    ```
  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Dostawcy modeli" href="/pl/concepts/model-providers" icon="layers">
    Przegląd wszystkich dostawców, referencji modeli i zachowania failover.
  </Card>
  <Card title="Wybór modelu" href="/pl/concepts/models" icon="brain">
    Jak wybierać i konfigurować modele.
  </Card>
  <Card title="Dokumentacja Inference Providers" href="https://huggingface.co/docs/inference-providers" icon="book">
    Oficjalna dokumentacja Hugging Face Inference Providers.
  </Card>
  <Card title="Konfiguracja" href="/pl/gateway/configuration" icon="gear">
    Pełna dokumentacja konfiguracji.
  </Card>
</CardGroup>
